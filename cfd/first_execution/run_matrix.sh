#!/usr/bin/env bash
# Shared-server runner for the V25 NACA 0012 matrix (host).
# - CPU only, nice 10, at most 24 cores (4 angles concurrently x ranks per grid)
# - grid sequencing: each grid starts from the converged solution of the next coarser grid
#   (mapFields -consistent); this changes the initial guess only, not the converged solution
# - p solver: GAMG/DICGaussSeidel, relTol 0.05 (benchmark in logs/psolver_benchmark.txt)
cd "$(dirname "$0")"
source ./env.sh            # OpenFOAM bashrc reads unset variables: source before enabling -u
set -uo pipefail
GRIDS=(n0012_225-65 n0012_449-129 n0012_897-257 n0012_1793-513)
declare -A NP=( [n0012_225-65]=1 [n0012_449-129]=2 [n0012_897-257]=4 [n0012_1793-513]=6 )
declare -A IT=( [n0012_225-65]=10000 [n0012_449-129]=15000 [n0012_897-257]=25000 [n0012_1793-513]=30000 )
PSOLVER='    p               { solver GAMG; smoother DICGaussSeidel; nCellsInCoarsestLevel 50; tolerance 1e-10; relTol 0.05; maxIter 100; }'
mkdir -p logs
log() { echo "$(date -u +%FT%TZ) $*" | tee -a logs/scheduler.log; }

run_case() {
    local case=$1 np=$2 it=$3 prev=$4 name
    name=$(basename "$case")
    sed -i "s/^nIter .*/nIter $it;/" "$case/caseParameters"
    sed -i "s|^    p  .*|$PSOLVER|" "$case/system/fvSolution"
    checkMesh -case "$case" > "logs/$name.checkMesh.log" 2>&1
    if [ -n "$prev" ]; then
        mapFields "$prev" -case "$case" -consistent -sourceTime latestTime > "logs/$name.mapFields.log" 2>&1
    fi
    if [ "$np" -gt 1 ]; then
        sed -i "s/^numberOfSubdomains .*/numberOfSubdomains  $np;/" "$case/system/decomposeParDict"
        decomposePar -force -case "$case" > "logs/$name.decompose.log" 2>&1
        nice -n 10 mpiexec.openmpi -n "$np" --bind-to none simpleFoam -parallel -case "$case" > "$case/simpleFoam.log" 2>&1
        rc=$?
        reconstructPar -latestTime -case "$case" > "logs/$name.reconstruct.log" 2>&1 && rm -rf "$case"/processor*
    else
        nice -n 10 simpleFoam -case "$case" > "$case/simpleFoam.log" 2>&1
        rc=$?
    fi
    echo "$(date -u +%FT%TZ) exit=$rc" > "$case/DONE"
}

prevgrid=""
for grid in "${GRIDS[@]}"; do
    for case in runs/${grid}_a*; do
        if [ -f "$case/DONE" ]; then continue; fi
        alpha=${case##*_a}
        prev=""; [ -n "$prevgrid" ] && prev="runs/${prevgrid}_a${alpha}"
        run_case "$case" "${NP[$grid]}" "${IT[$grid]}" "$prev" &
        log "started $(basename "$case") np=${NP[$grid]} iters=${IT[$grid]} init=${prev:-freestream}"
    done
    wait
    log "finished grid $grid"
    prevgrid=$grid
done
log "all cases finished"
python3 tools/analyse_runs.py runs --out results | tee logs/analysis.log
