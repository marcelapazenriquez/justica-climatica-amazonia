"""
Teste da tese: o ICMS Verde do Pará segue quem remove carbono?
Cruza o índice do critério ecológico do ICMS (2014–2024) com o painel SEEG municipal (anos comuns: 2015–2017).

Entradas: data/raw/icms_verde_para_indice_2014_2024.tsv, data/raw/painel_municipal_2006_2017.xlsx
Saídas:   data/processed/municipal/icms_verde_*.csv, figures/09_icms_verde.png

Uso:
    python scripts/05_icms_verde.py
    ARTIGO=1 python scripts/05_icms_verde.py
"""
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from estilo import GRADE, LARANJA, ROOT, TINTA, TINTA2, VERDE, molde, salvar  # noqa: E402

RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed" / "municipal"


def chave(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return s.replace("’", "").replace("'", "").replace("-", " ").strip()


ic = pd.read_csv(RAW / "icms_verde_para_indice_2014_2024.tsv", sep="\t")
ic = ic[ic["Município"] != "TOTAL"].copy()
ic["k"] = ic["Município"].map(chave).replace({"eldorado do carajas": "eldorado dos carajas",
                                               "santa izabel do para": "santa isabel do para"})
ANOS = ["2015", "2016", "2017"]
for a in ANOS:
    ic["p" + a] = ic[a] / ic[a].sum()  # participação no total distribuído pelo critério ecológico
ic["part_icms_verde"] = ic[["p" + a for a in ANOS]].mean(axis=1)

d = pd.read_excel(RAW / "painel_municipal_2006_2017.xlsx", sheet_name="dados")
d = d.loc[:, ~d.columns.duplicated()]
pa = d[(d.Estado == "PA") & (d.Ano.isin([2015, 2016, 2017]))].copy()
pa["k"] = pa.Municipio.map(chave)
g = pa.groupby("k").agg(municipio=("Municipio", "first"), emissao_liquida_t=("Emissoes Liquidas", "mean"),
                        remocoes_t=("Remocoes", "mean"), emissoes_t=("Total Geral (Emissoes)", "mean"))
m = g.join(ic.set_index("k")[["part_icms_verde"]], how="inner")  # Mojuí dos Campos (criado em 2013) fica fora
m["part_icms_verde"] /= m.part_icms_verde.sum()
m["part_remocoes"] = m.remocoes_t / m.remocoes_t.sum()
m["sumidouro_liquido"] = m.emissao_liquida_t < 0
m.sort_values("part_icms_verde", ascending=False).to_csv(OUT / "icms_verde_x_seeg_2015_2017.csv")

grupos = m.groupby("sumidouro_liquido").agg(municipios=("municipio", "size"), part_remocoes=("part_remocoes", "sum"),
                                            part_icms_verde=("part_icms_verde", "sum"))
grupos.index = grupos.index.map({True: "Sumidouros líquidos", False: "Emissores líquidos"})
grupos.to_csv(OUT / "icms_verde_grupos_2015_2017.csv")
t10 = m.nsmallest(10, "remocoes_t")
res = {
    "municipios": int(len(m)),
    "sumidouros": int(m.sumidouro_liquido.sum()),
    "sumidouros_part_remocoes": float(grupos.loc["Sumidouros líquidos", "part_remocoes"]),
    "sumidouros_part_icms": float(grupos.loc["Sumidouros líquidos", "part_icms_verde"]),
    "top10_removedores_part_remocoes": float(t10.part_remocoes.sum()),
    "top10_removedores_part_icms": float(t10.part_icms_verde.sum()),
    "spearman_icms_remocoes": float(spearmanr(m.part_icms_verde, -m.remocoes_t).statistic),
    "spearman_icms_emissao_liquida": float(spearmanr(m.part_icms_verde, m.emissao_liquida_t).statistic),
    "spearman_icms_emissao_liquida_p": float(spearmanr(m.part_icms_verde, m.emissao_liquida_t).pvalue),
    "maior_recebedor": m.part_icms_verde.idxmax(),
}
json.dump(res, open(OUT / "icms_verde_resumo.json", "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------ figura
fig, axs = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={"width_ratios": [1, 1.6]})
molde(fig, "Quem remove carbono não é quem recebe o ICMS Verde",
      "Pará, média 2015–2017: participação nas remoções de GEE e no ICMS Verde",
      "09_icms_verde", top=0.80, bottom=0.12, left=0.06, right=0.97, wspace=0.28)
ax = axs[0]
x = [0, 1]
for i, (nome, cor) in enumerate([("Sumidouros líquidos", VERDE), ("Emissores líquidos", LARANJA)]):
    r = grupos.loc[nome]
    ax.bar([i - 0.18], [r.part_remocoes * 100], width=0.34, color=cor)
    ax.bar([i + 0.18], [r.part_icms_verde * 100], width=0.34, color=cor, alpha=0.45, hatch="//", edgecolor=cor)
    ax.text(i - 0.18, r.part_remocoes * 100 + 1.5, f"{r.part_remocoes * 100:.0f}%", ha="center", fontsize=11, color=TINTA)
    ax.text(i + 0.18, r.part_icms_verde * 100 + 1.5, f"{r.part_icms_verde * 100:.0f}%", ha="center", fontsize=11, color=TINTA)
ax.set_xticks(x)
ax.set_xticklabels([f"{n}\n({int(grupos.loc[n].municipios)} municípios)" for n in ("Sumidouros líquidos", "Emissores líquidos")])
ax.set_ylim(0, 85); ax.set_ylabel("% do total do Pará")
ax.set_title("A. Remoções (cheio) e ICMS Verde (hachurado)", loc="left", fontsize=12, color=TINTA)

ax = axs[1]
ax.axvline(0, color=TINTA2, lw=1)
cores = m.sumidouro_liquido.map({True: VERDE, False: LARANJA})
ax.scatter(m.emissao_liquida_t / 1e6, m.part_icms_verde * 100, s=46, c=cores, edgecolor="white", linewidth=0.8, zorder=3)
dest = ["São Félix do Xingu", "Oriximiná", "Altamira", "Almeirim", "Jacareacanga", "Novo Repartimento", "Pacajá", "Faro"]
for _, r in m[m.municipio.isin(dest)].iterrows():
    dx, ha = ((-8, "right") if r.emissao_liquida_t > 5e6 else (6, "left"))
    ax.annotate(r.municipio, (r.emissao_liquida_t / 1e6, r.part_icms_verde * 100), xytext=(dx, 4),
                textcoords="offset points", fontsize=9.5, color=TINTA, ha=ha)
ax.set_xlabel("emissão líquida média 2015–2017 (milhões de t CO₂e; negativo = remove)")
ax.set_ylabel("participação no ICMS Verde (%)")
ax.text(-15.5, 0.05, "← removem", fontsize=10, color=VERDE); ax.text(5.5, 0.05, "emitem →", fontsize=10, color=LARANJA)
ax.set_title("B. Cada ponto é um município", loc="left", fontsize=12, color=TINTA)
ax.grid(axis="x", visible=True, color=GRADE)
salvar(fig, "09_icms_verde")
print(json.dumps(res, indent=1, ensure_ascii=False))
