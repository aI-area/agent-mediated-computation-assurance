#!/usr/bin/env bash
# Stage 2: 1793x513 grid, initialised by nested-grid injection from converged 897x257 fields
# (tools/inject_nested.py). Same solver settings and frozen acceptance rules as run_matrix.sh.
cd "$(dirname "$0")"
source ./env.sh            # OpenFOAM bashrc reads unset variables: source before enabling -u
set -uo pipefail
NP=6
IT=30000
PSOLVER='    p               { solver GAMG; smoother DICGaussSeidel; nCellsInCoarsestLevel 50; tolerance 1e-10; relTol 0.05; maxIter 100; }'
log() { echo "$(date -u +%FT%TZ) $*" | tee -a logs/scheduler.log; }

run_case() {
    local case=$1 name
    name=$(basename "$case")
    sed -i "s/^nIter .*/nIter $IT;/" "$case/caseParameters"
    sed -i "s|^    p  .*|$PSOLVER|" "$case/system/fvSolution"
    checkMesh -case "$case" > "logs/$name.checkMesh.log" 2>&1
    sed -i "s/^numberOfSubdomains .*/numberOfSubdomains  $NP;/" "$case/system/decomposeParDict"
    decomposePar -force -case "$case" > "logs/$name.decompose.log" 2>&1
    nice -n 10 mpiexec.openmpi -n "$NP" --bind-to none simpleFoam -parallel -case "$case" > "$case/simpleFoam.log" 2>&1
    rc=$?
    reconstructPar -latestTime -case "$case" > "logs/$name.reconstruct.log" 2>&1 && rm -rf "$case"/processor*
    echo "$(date -u +%FT%TZ) exit=$rc" > "$case/DONE"
}

for case in runs/n0012_1793-513_a*; do
    [ -f "$case/DONE" ] && continue
    run_case "$case" &
    log "started $(basename "$case") np=$NP iters=$IT init=nested injection from 897x257"
done
wait
log "finished grid n0012_1793-513"
python3 tools/analyse_runs.py runs --out results | tee logs/analysis.log
log "analysis written to results/dispositions.json"
