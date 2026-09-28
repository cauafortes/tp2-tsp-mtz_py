import math


def ler_tsplib(caminho):
    """Retorna (nome, coordenadas, tipo_de_distancia)."""
    nome, tipo, coords, em_coords = None, None, [], False
    with open(caminho) as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha == "EOF":
                continue
            if linha.startswith("NODE_COORD_SECTION"):
                em_coords = True
                continue
            if em_coords:
                _, x, y = linha.split()[:3]
                coords.append((float(x), float(y)))
            elif ":" in linha:
                chave, valor = [p.strip() for p in linha.split(":", 1)]
                if chave == "NAME":
                    nome = valor
                elif chave == "EDGE_WEIGHT_TYPE":
                    tipo = valor
    return nome, coords, tipo


def _geo_rad(v):
    graus = int(v)
    minutos = v - graus
    return math.pi_tsplib * (graus + 5.0 * minutos / 3.0) / 180.0


math.pi_tsplib = 3.141592  # constante usada pela TSPLIB


def distancia(tipo, a, b):
    if tipo == "EUC_2D":
        return int(math.hypot(a[0] - b[0], a[1] - b[1]) + 0.5)
    if tipo == "ATT":
        r = math.sqrt(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) / 10.0)
        t = int(r + 0.5)
        return t + 1 if t < r else t
    if tipo == "GEO":
        lat_a, lon_a = _geo_rad(a[0]), _geo_rad(a[1])
        lat_b, lon_b = _geo_rad(b[0]), _geo_rad(b[1])
        q1 = math.cos(lon_a - lon_b)
        q2 = math.cos(lat_a - lat_b)
        q3 = math.cos(lat_a + lat_b)
        return int(6378.388 * math.acos(0.5 * ((1 + q1) * q2 - (1 - q1) * q3)) + 1.0)
    raise ValueError(f"EDGE_WEIGHT_TYPE não suportado: {tipo}")


def matriz_distancias(coords, tipo):
    n = len(coords)
    return [[0 if i == j else distancia(tipo, coords[i], coords[j]) for j in range(n)] for i in range(n)]
