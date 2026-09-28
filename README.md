# Resolução do Problema do Caixeiro Viajante (TSP) - Métodos Exatos

Este repositório contém a implementação e validação de modelos de Programação Linear Inteira (PLI) para resolver o **Problema do Caixeiro Viajante (TSP)** utilizando instâncias padrão da biblioteca **TSPLIB**[cite: 1, 3].

## 📌 Sobre o Projeto

* **O Problema:** O Caixeiro Viajante busca encontrar a rota de menor custo/distância que visita um conjunto de cidades exatamente uma vez e retorna à cidade de origem.
* **Formulação Principal (MTZ):** Utiliza a formulação de Miller-Tucker-Zemlin com variáveis contínuas auxiliares $u_i$ para eliminação de subciclos em $O(n^2)$ restrições.
* **Validação Independente (DFJ):** Utiliza cortes dinâmicos de eliminação de subciclos (Dantzig-Fulkerson-Johnson) via `scipy.optimize.milp` para confirmar os valores ótimos conhecidos da TSPLIB.

## ⚠️ Requisito Importante de Versão (PuLP)

Utilize estritamente a versão **2.9.0** do PuLP (`pulp==2.9.0`). O uso de especificações como `pulp>=2.8` instala versões mais recentes (ex: 4.0.0+) que causam incompatibilidade com o código.

## 🚀 Como Executar
Bateria Completd (Modelagem MTZ)
Executa as instâncias padrão (burma14, ulysses16, ulysses22) com limite de tempo de 1800 segundos:   
Bash
python tsp_mtz.py --todas --tempo 1800

Execução Individual
Para rodar uma instância específica com suporte a solvers externos e logs detalhados:   

Bash
python tsp_mtz.py instancias/berlin52.tsp --solver highs --tempo 1800 --log

## 🛠️ Instalação

```bash
pip install "pulp==2.9.0" scipy nump

