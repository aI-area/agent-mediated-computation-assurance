#!/usr/bin/env bash
# V19 NACA 0012 rerun on the NASA TMR grid family (OpenFOAM v2312).
# Usage: NPROCS=32 ./Allrun.sh            (source the OpenFOAM v2312 bashrc first)
set -euo pipefail
cd "$(dirname "$0")"
NPROCS=${NPROCS:-32}
ITERS=${ITERS:-60000}
GRID_URL=https://www.nasa.gov/wp-content/uploads/2026/02/naca0012-grids.zip

mkdir -p grids runs logs
if [ ! -f grids/naca0012-grids.zip ]; then
    curl -fL -o grids/naca0012-grids.zip "$GRID_URL"
fi
sha256sum grids/naca0012-grids.zip | tee logs/grid_archive.sha256
(cd grids && unzip -o -j -q naca0012-grids.zip '*p2dfmt*')

python3 tools/test_p2d_cgrid_to_foam.py
python3 tools/setup_cases.py --grids grids --out runs --nprocs "$NPROCS" --iters "$ITERS"
foamVersion | tee logs/foam_version.txt

# coarse-to-fine so problems surface early; one case at a time uses all cores
for case in $(ls -d runs/n0012_225-65_* runs/n0012_449-129_* runs/n0012_897-257_* runs/n0012_1793-513_*); do
    name=$(basename "$case")
    [ -f "$case/DONE" ] && continue
    checkMesh -case "$case" > "logs/$name.checkMesh.log" 2>&1
    if [ "$NPROCS" -gt 1 ]; then
        decomposePar -force -case "$case" > "logs/$name.decompose.log" 2>&1
        mpirun -np "$NPROCS" simpleFoam -parallel -case "$case" > "$case/simpleFoam.log" 2>&1
    else
        simpleFoam -case "$case" > "$case/simpleFoam.log" 2>&1
    fi
    touch "$case/DONE"
done
python3 tools/analyse_runs.py runs --out results
