"""Verificação independente (scipy/HiGHS + cortes DFJ) dos ótimos conhecidos da TSPLIB."""
import sys, time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
from tsplib import ler_tsplib, matriz_distancias

OTIMOS = {"burma14": 3323, "ulysses16": 6859, "ulysses22": 7013, "berlin52": 7542}

c
def resolver_dfj(d):
    n = len(d)
    idx = {(i, j): k for k, (i, j) in enumerate((i, j) for i in range(n) for j in range(n) if i != j)}
    c = np.zeros(len(idx))
    for (i, j), k in idx.items():
        c[k] = d[i][j]
    A = lil_matrix((2 * n, len(idx)))
    for (i, j), k in idx.items():
        A[i, k] = 1          # saída de i
        A[n + j, k] = 1      # entrada em j
    cortes = []
    while True:
        Aall = A.tocsr()
        lo = [1] * (2 * n); hi = [1] * (2 * n)
        cons = [LinearConstraint(Aall, lo, hi)]
        if cortes:
            M = lil_matrix((len(cortes), len(idx)))
            for r, S in enumerate(cortes):
                for i in S:
                    for j in S:
                        if i != j:
                            M[r, idx[(i, j)]] = 1
            cons.append(LinearConstraint(M.tocsr(), -np.inf, [len(S) - 1 for S in cortes]))
        res = milp(c, constraints=cons, integrality=np.ones(len(idx)), bounds=Bounds(0, 1))
        x = res.x
        succ = {i: j for (i, j), k in idx.items() if x[k] > 0.5}
        vistos, subciclos = set(), []
        for s in range(n):
            if s in vistos:
                continue
            ciclo, u = [], s
            while u not in vistos:
                vistos.add(u); ciclo.append(u); u = succ[u]
            subciclos.append(ciclo)
        if len(subciclos) == 1:
            return round(res.fun)
        cortes.extend(subciclos)


if __name__ == "__main__":
    for nome in ["burma14", "ulysses16", "ulysses22", "berlin52"]:
        _, coords, tipo = ler_tsplib(f"instancias/{nome}.tsp")
        t = time.time()
        ot = resolver_dfj(matriz_distancias(coords, tipo))
        print(f"{nome}: ótimo obtido = {ot} | ótimo TSPLIB = {OTIMOS[nome]} | {'OK' if ot == OTIMOS[nome] else 'DIVERGE'} | {time.time()-t:.1f}s")
