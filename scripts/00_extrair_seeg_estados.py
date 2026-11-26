"""
Extrai do arquivo nacional do SEEG as linhas dos 9 estados da Amazônia Legal (CO2e GWP-AR5).
Os arquivos originais (170–210 MB) não vão para o repositório: baixe-os em https://plataforma.seeg.eco.br/
Uso:
    python scripts/00_extrair_seeg_estados.py caminho/Dados-nacionais-14_0.xlsx seeg14
    python scripts/00_extrair_seeg_estados.py caminho/SEEG11-DADOS-NACIONAIS.xlsx seeg11
Saída: data/raw/<nome>_estados_amazonia_legal.csv (anos 2000 em diante)
"""
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AL = {"Acre", "Amapá", "Amazonas", "Maranhão", "Mato Grosso", "Pará", "Rondônia", "Roraima", "Tocantins"}

arq, nome = sys.argv[1], sys.argv[2]
it = openpyxl.load_workbook(arq, read_only=True)["Dados"].iter_rows(values_only=True)
hdr = [str(h) for h in next(it)]
col = {h: i for i, h in enumerate(hdr)}
anos = [h for h in hdr if h.isdigit() and int(h) >= 2000]
idx = [col[a] for a in anos]
linhas = []
for r in it:
    if r[col["Gás"]] != "CO2e (t) GWP-AR5" or r[col["Estado"]] not in AL:
        continue
    linhas.append([r[col["Emissão/Remoção/Bunker"]], r[col["Setor de emissão"]], r[col["Categoria emissora"]],
                   r[col["Estado"]], r[col["Bioma"]]] + [float(r[i] or 0) for i in idx])
df = pd.DataFrame(linhas, columns=["tipo", "setor", "categoria", "estado", "bioma"] + anos)
df.to_csv(ROOT / "data" / "raw" / f"{nome}_estados_amazonia_legal.csv", index=False)
print(len(df), "linhas;", anos[0], "a", anos[-1])
