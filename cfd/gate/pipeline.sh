#!/usr/bin/env bash
# Gated execution of the preregistered NACA 0012 case (claim c1). Launched only by gate.py (action run_pipeline).
# Reads the frozen inputs under ROOT (read-only) and writes only under ROOT/gated/work.
# Procedure identical to the frozen runners: grids 225, 449, 897 started from the next-coarser solution by
# mapFields; grid 1793 started by nested-grid injection from the converged 897 solution; same solver settings,
# iteration counts and decomposition; frozen analysis applied at the end.
ROOT=/path/to/project/v19_cfd
WORK=$ROOT/gated/work
PY=/path/to/python-env/bin/python3
source "$ROOT/env.sh" >/dev/null 2>&1
set -uo pipefail
cd "$WORK" || exit 2
mkdir -p logs runs results scratch
log() { echo "$(date -u +%FT%TZ) $*" | tee -a logs/scheduler.log; }

GRIDS=(n0012_225-65 n0012_449-129 n0012_897-257 n0012_1793-513)
declare -A NP=( [n0012_225-65]=1 [n0012_449-129]=2 [n0012_897-257]=4 [n0012_1793-513]=6 )
declare -A IT=( [n0012_225-65]=10000 [n0012_449-129]=15000 [n0012_897-257]=25000 [n0012_1793-513]=30000 )
PSOLVER='    p               { solver GAMG; smoother DICGaussSeidel; nCellsInCoarsestLevel 50; tolerance 1e-10; relTol 0.05; maxIter 100; }'

# The frozen tools and case template are read-only; the setup script copies the template together with its
# permissions. Run setup and analysis from a working copy of tools/, case_template/ and PREREGISTRATION.md whose every file is verified against
# the frozen protected-input manifest; abort on any mismatch.
log "setup: verified working copy of tools and case template"
rm -rf frozen_copy && mkdir -p frozen_copy
cp -r "$ROOT/tools" "$ROOT/case_template" "$ROOT/PREREGISTRATION.md" frozen_copy/ && chmod -R u+w frozen_copy
$PY - "$ROOT" "$WORK/frozen_copy" > logs/frozen_copy_check.log 2>&1 <<'PYEOF' || { log "working copy does not match the frozen manifest"; exit 2; }
import hashlib, json, sys
from pathlib import Path
root, copy = Path(sys.argv[1]), Path(sys.argv[2])
frozen = json.load(open(root / "gated/log/protected_manifest.json"))["files"]
n = 0
for rel, digest in frozen.items():
    if (rel.split("/")[0] in ("tools", "case_template") or rel == "PREREGISTRATION.md") and "__pycache__" not in rel:
        got = hashlib.sha256((copy / rel).read_bytes()).hexdigest()
        assert got == digest, f"mismatch {rel}"
        n += 1
print(f"{n} files verified against the frozen manifest")
PYEOF
log "setup: cases from TMR grids"
$PY "$WORK/frozen_copy/tools/setup_cases.py" --grids "$ROOT/grids" --out "$WORK/runs" > logs/setup.log 2>&1 || { log "setup failed"; exit 2; }

run_case() {
    local case=$1 np=$2 it=$3 prev=$4 name
    name=$(basename "$case")
    sed -i "s/^nIter .*/nIter $it;/" "$case/caseParameters"
    sed -i "s|^    p  .*|$PSOLVER|" "$case/system/fvSolution"
    checkMesh -case "$case" > "logs/$name.checkMesh.log" 2>&1
    if [ "$prev" = "inject" ]; then
        :
    elif [ -n "$prev" ]; then
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
    if [ "$grid" = "n0012_1793-513" ]; then
        for c897 in runs/n0012_897-257_a*; do
            alpha=${c897##*_a}
            s="scratch/c897_a$alpha"
            mkdir -p "$s"
            cp -r "$c897/constant" "$c897/system" "$c897/caseParameters" "$s/"
            latest=$(ls -d "$c897"/[0-9]* | sort -t/ -k3 -g | tail -1)
            cp -r "$latest" "$s/"
            sed -i "s/^writeFormat .*/writeFormat     ascii;/" "$s/system/controlDict"
            foamFormatConvert -case "$s" -latestTime > "logs/c897_a$alpha.convert.log" 2>&1
            $PY "$WORK/frozen_copy/tools/inject_nested.py" "$s" "runs/n0012_1793-513_a$alpha" 897 257 >> logs/inject.log 2>&1
        done
        log "1793 cases initialised by nested-grid injection from converged 897 solutions"
    fi
    for case in runs/${grid}_a*; do
        alpha=${case##*_a}
        if [ "$grid" = "n0012_1793-513" ]; then prev="inject"
        elif [ -n "$prevgrid" ]; then prev="runs/${prevgrid}_a${alpha}"
        else prev=""; fi
        run_case "$case" "${NP[$grid]}" "${IT[$grid]}" "$prev" &
        log "started $(basename "$case") np=${NP[$grid]} iters=${IT[$grid]} init=${prev:-freestream}"
    done
    wait
    log "finished grid $grid"
    prevgrid=$grid
done
rm -rf scratch
$PY "$WORK/frozen_copy/tools/analyse_runs.py" "$WORK/runs" --out "$WORK/results" --refs "$ROOT/reference_values.csv" > logs/analysis.log 2>&1
log "analysis written to results/dispositions.json"
