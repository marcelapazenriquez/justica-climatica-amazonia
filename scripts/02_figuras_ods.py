"""
Figuras dos indicadores ODS e das Unidades de Conservação (01, 02, 03).

Uso:
    python scripts/02_figuras_ods.py            # versões para redes/site
    ARTIGO=1 python scripts/02_figuras_ods.py   # versões para o artigo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from estilo import AZUL, FUNDO, GRADE, LARANJA, ROOT, TINTA, TINTA2, VERDE, molde, salvar  # noqa: E402

P, RAW = ROOT / "data" / "processed", ROOT / "data" / "raw"

# 01 — ODS 13.1.1
d = pd.read_csv(P / "t03_ods13_1_1_desastres.csv").pivot(index="ano", columns="regiao", values="afetados_100mil")
fig, ax = plt.subplots(figsize=(12, 6.75))
molde(fig, "ODS 13.1.1 — a Amazônia Legal é mais afetada por desastres",
      "Mortos, desaparecidos e afetados por 100 mil habitantes, média das UFs, 2015–2022",
      "01_ods13_desastres", left=0.08, right=0.86)
ax.axvspan(2019.6, 2021.4, color=GRADE, alpha=0.6, lw=0)
ax.text(2020.5, 2050, "Covid-19 registrada\ncomo desastre no S2ID", ha="center", fontsize=9, color=TINTA2)
for col, cor in [("Amazônia Legal", LARANJA), ("Brasil", AZUL)]:
    ax.plot(d.index, d[col], color=cor, lw=2.4, marker="o", ms=7)
    ax.annotate(col, (d.index[-1], d[col].iloc[-1]), xytext=(10, 0), textcoords="offset points",
                color=TINTA, fontsize=12, va="center", weight="bold")
ax.set_ylim(0, 2300); ax.set_ylabel("pessoas afetadas por 100 mil hab.")
salvar(fig, "01_ods13_desastres")

# 02 — ODS 15.1.2
raw = pd.read_excel(RAW / "ibge_sidra_4962_kba.xlsx", sheet_name=1, header=None)
anos = [int(a) for a in raw.iloc[3, 3::2]]
br, am = raw.iloc[4, 3::2].astype(float).values, raw.iloc[5, 3::2].astype(float).values
fig, ax = plt.subplots(figsize=(12, 6.75))
molde(fig, "ODS 15.1.2 — áreas-chave para a biodiversidade protegidas",
      "Proporção da área de KBAs coberta por Unidades de Conservação, 2015–2023",
      "02_ods15_kba_protegidas", left=0.08, right=0.86)
for serie, nome, cor in [(am, "Amazônia", VERDE), (br, "Brasil", AZUL)]:
    ax.plot(anos, serie, color=cor, lw=2.4, marker="o", ms=7)
    ax.annotate(f"{nome}  {serie[-1]:.1f}%".replace(".", ","), (anos[-1], serie[-1]), xytext=(10, 0),
                textcoords="offset points", color=TINTA, fontsize=12, va="center", weight="bold")
ax.set_ylim(45, 65); ax.set_ylabel("% da área de KBAs dentro de UCs")
salvar(fig, "02_ods15_kba_protegidas")

# 03 — UCs por UF
d = pd.read_csv(P / "t02_ucs_por_uf_esfera.csv")
w = d.pivot(index="uf", columns="esfera", values="pct_bioma_da_uf")[["federal", "estadual", "municipal"]]
w = w.loc[w.sum(axis=1).sort_values().index]
fig, ax = plt.subplots(figsize=(12, 6.75))
molde(fig, "Quem guarda a floresta? Unidades de Conservação por estado",
      "Área de UCs no bioma Amazônia, por esfera administrativa", "03_ucs_por_uf", left=0.08, right=0.95)
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
left = pd.Series(0.0, index=w.index)
for col, cor in [("federal", AZUL), ("estadual", VERDE), ("municipal", LARANJA)]:
    ax.barh(w.index, w[col], left=left, color=cor, height=0.62, edgecolor=FUNDO, linewidth=2, label=col.capitalize())
    left += w[col]
for uf, tot in left.items():
    ax.text(tot + 0.8, uf, f"{tot:.1f}%".replace(".", ","), va="center", fontsize=11, color=TINTA)
ax.set_xlabel("% da área do bioma Amazônia na UF coberta por UCs (pode haver sobreposição)")
ax.legend(frameon=False, loc="lower right")
salvar(fig, "03_ucs_por_uf")
print("ok")
