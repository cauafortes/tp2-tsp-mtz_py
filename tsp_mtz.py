"""
TP-II - Métodos Exatos: Problema do Caixeiro Viajante (TSP) via PLI (formulação MTZ).

Uso:
    python tsp_mtz.py instancias/burma14.tsp
    python tsp_mtz.py instancias/berlin52.tsp --solver highs --tempo 1800
    python tsp_mtz.py --todas --tempo 1800         # roda as 3 instâncias (fácil, média, difícil) e imprime a tabela
    python tsp_mtz.py instancias/berlin52.tsp --log   # --log mostra o log do solver (inclui o gap)

Solvers: cbc (padrão, vem com o PuLP), highs (requer `pip install highspy`), gurobi, scip.
"""
import argparse
import sys
import time

import pulp

from tsplib import ler_tsplib, matriz_distancias

INSTANCIAS = ["instancias/burma14.tsp", "instancias/ulysses16.tsp", "instancias/ulysses22.tsp"]  # fácil, média, difícil


def construir_modelo(d):
    """Formulação de Miller-Tucker-Zemlin.

    x[i][j] = 1 se a rota vai da cidade i para a cidade j (binária)
    u[i]    = posição da cidade i na rota (contínua, i = 1..n-1; cidade 0 é o depósito)

    min  sum c_ij x_ij
    s.a. sum_j x_ij = 1            para todo i    (uma saída por cidade)
         sum_i x_ij = 1            para todo j    (uma entrada por cidade)
         u_i - u_j + n x_ij <= n-1 para i != j, i,j >= 1   (elimina subciclos)
         1 <= u_i <= n-1
    """
    n = len(d)
    prob = pulp.LpProblem("TSP_MTZ", pulp.LpMinimize)

    # Variáveis criadas uma a uma (funciona em qualquer versão do PuLP)
    x = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", cat=pulp.LpBinary)
        for i in range(n) for j in range(n) if i != j
    }
    u = {
        i: pulp.LpVariable(f"u_{i}", lowBound=1, upBound=n - 1, cat=pulp.LpContinuous)
        for i in range(1, n)
    }

    prob += pulp.lpSum(d[i][j] * x[i, j] for i in range(n) for j in range(n) if i != j)

    for i in range(n):
        prob += pulp.lpSum(x[i, j] for j in range(n) if j != i) == 1, f"saida_{i}"
        prob += pulp.lpSum(x[j, i] for j in range(n) if j != i) == 1, f"entrada_{i}"

    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + n * x[i, j] <= n - 1, f"mtz_{i}_{j}"

    return prob, x


def escolher_solver(nome, tempo, gap, log=False):
    nome = nome.lower()
    if nome == "cbc":
        return pulp.PULP_CBC_CMD(msg=log, timeLimit=tempo, gapRel=gap)
    if nome == "highs":
        return pulp.HiGHS(msg=log, timeLimit=tempo, gapRel=gap)
    if nome == "gurobi":
        return pulp.GUROBI(msg=log, timeLimit=tempo, gapRel=gap)
    if nome == "scip":
        return pulp.SCIP_PY(msg=log, timeLimit=tempo, gapRel=gap)
    raise ValueError("solver inválido")


def extrair_rota(x, n):
    prox = {i: j for (i, j), var in x.items() if var.value() is not None and var.value() > 0.5}
    rota, atual = [0], prox[0]
    while atual != 0:
        rota.append(atual)
        atual = prox[atual]
    return rota


def resolver(caminho, solver="cbc", tempo=600, gap=0.0, log=False):
    nome, coords, tipo = ler_tsplib(caminho)
    d = matriz_distancias(coords, tipo)
    n = len(d)
    prob, x = construir_modelo(d)

    t0 = time.time()
    prob.solve(escolher_solver(solver, tempo, gap, log))
    dt = time.time() - t0

    status = pulp.LpStatus[prob.status]
    fo = pulp.value(prob.objective)
    try:
        rota = extrair_rota(x, n)
        rota = rota if len(rota) == n else None
    except (KeyError, TypeError):
        rota = None
    # sol_status: 1 = ótimo comprovado; 2 = solução inteira viável (ex.: parou no limite de tempo)
    sol = {1: "Otimo", 2: "Viavel"}.get(getattr(prob, "sol_status", None), status)
    return {
        "instancia": nome, "n": n, "variaveis": len(prob.variables()),
        "restricoes": len(prob.constraints), "status": sol,
        "fo": fo, "tempo": dt, "rota": rota,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--solver", default="cbc")
    ap.add_argument("--tempo", type=int, default=600, help="limite de tempo em segundos")
    ap.add_argument("--gap", type=float, default=0.0)
    ap.add_argument("--log", action="store_true", help="mostra o log do solver")
    a = ap.parse_args()

    alvos = INSTANCIAS if a.todas else [a.arquivo]
    if not alvos or alvos[0] is None:
        ap.error("informe um arquivo .tsp ou use --todas")

    print(f"{'Instância':<12}{'n':>4}{'Vars':>8}{'Restr':>8}{'Status':>12}{'FO':>10}{'Tempo(s)':>11}")
    for caminho in alvos:
        r = resolver(caminho, a.solver, a.tempo, a.gap, a.log)
        fo = f"{r['fo']:.0f}" if r["fo"] is not None else "-"
        print(f"{r['instancia']:<12}{r['n']:>4}{r['variaveis']:>8}{r['restricoes']:>8}{r['status']:>12}{fo:>10}{r['tempo']:>11.1f}")
        if r["rota"]:
            print("  rota:", " -> ".join(str(c + 1) for c in r["rota"]), "-> 1")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
