#!/usr/bin/env bash
# Benchmark p-solver settings on one case (execution-level choice; no QoI is examined).
cd "$(dirname "$0")/.."
source ./env.sh
SRC=${SRC:-runs/n0012_897-257_a10.00}
NP=${NP:-6}
declare -A CFG
CFG[A_gamg_rel001]='p { solver GAMG; smoother GaussSeidel; tolerance 1e-12; relTol 0.01; }'
CFG[B_gamg_dicgs_rel005]='p { solver GAMG; smoother DICGaussSeidel; nCellsInCoarsestLevel 50; tolerance 1e-10; relTol 0.05; maxIter 100; }'
CFG[C_pcg_dic_rel005]='p { solver PCG; preconditioner DIC; tolerance 1e-10; relTol 0.05; maxIter 500; }'
for k in ${CFGS:-A_gamg_rel001 B_gamg_dicgs_rel005 C_pcg_dic_rel005}; do
    d=bench/$k; rm -rf "$d"; mkdir -p bench; cp -r "$SRC" "$d"; rm -rf "$d"/postProcessing "$d"/DONE "$d"/processor*
    sed -i "s/^nIter .*/nIter ${NIT:-150};/" "$d/caseParameters"
    sed -i "s|^    p .*|    ${CFG[$k]}|" "$d/system/fvSolution"
    sed -i "s/^numberOfSubdomains .*/numberOfSubdomains  $NP;/" "$d/system/decomposeParDict"
    decomposePar -force -case "$d" > "$d/decompose.log" 2>&1
    s=$(date +%s)
    nice -n 10 mpiexec.openmpi -n $NP --bind-to none simpleFoam -parallel -case "$d" > "$d/log" 2>&1
    e=$(date +%s)
    echo "$k seconds=$((e - s)) last_p: $(grep 'Solving for p' "$d/log" | tail -1 | cut -c1-110)"
    rm -rf "$d"/processor*
done
