"""
Exposição a desastres: índice de risco de impacto para inundações, enxurradas e alagamentos (AdaptaBrasil MCTI, 2015)
nos municípios da Amazônia Legal, por UF e por grupo (sumidouros x emissores líquidos).

Entradas: data/raw/adaptabrasil_risco_inundacoes_2015.xlsx, ibge_municipios_amazonia_legal_2022.xlsx,
          painel_municipal_2006_2017.xlsx, data/processed/municipal/recorrencia_top12.csv
Saídas:   data/processed/municipal/risco_*.csv, figures/10_risco_inundacoes.png

Uso:
    python scripts/06_risco_inundacoes.py
    ARTIGO=1 python scripts/06_risco_inundacoes.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

from estilo import FUNDO, ROOT, TINTA, molde, salvar  # noqa: E402

RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed" / "municipal"
ORDEM = ["Muito alto", "Alto", "Médio", "Baixo", "Muito baixo"]

ri = pd.read_excel(RAW / "adaptabrasil_risco_inundacoes_2015.xlsx").set_index("geocod_ibge")
al = pd.read_excel(RAW / "ibge_municipios_amazonia_legal_2022.xlsx")
uf = pd.Series(al.SIGLA_UF.values, index=al.CD_MUN.astype(int))
x = ri[ri.index.isin(uf.index)].join(uf.rename("uf"))

por_uf = pd.crosstab(x.uf, x.classe).reindex(columns=ORDEM, fill_value=0)
por_uf["Total"] = por_uf.sum(axis=1)
por_uf.to_csv(OUT / "risco_inundacoes_por_uf_2015.csv")

comp = pd.DataFrame({"Brasil": ri.classe.value_counts(normalize=True).reindex(ORDEM),
                     "Amazônia Legal": x.classe.value_counts(normalize=True).reindex(ORDEM)}) * 100

d = pd.read_excel(RAW / "painel_municipal_2006_2017.xlsx", sheet_name="dados")
d = d.loc[:, ~d.columns.duplicated()]
med = d[d.Ano >= 2015].groupby("CodIbge")["Emissoes Liquidas"].mean()
grupo = pd.Series("Emissores líquidos", index=med.index)
grupo[med < 0] = "Sumidouros líquidos"
rec = pd.read_csv(OUT / "recorrencia_top12.csv", index_col=0)
sumid = rec[rec.anos_top12_sumidouro >= 10].index
grupo_rec = pd.Series("Demais", index=med.index)
grupo_rec[grupo_rec.index.isin(sumid)] = "Sumidouros recorrentes"

g = ri.loc[med.index].assign(grupo=grupo, recorrente=grupo_rec)
tab = (pd.crosstab(g.grupo, g.classe, normalize="index") * 100).reindex(columns=ORDEM, fill_value=0)
tab.loc["Sumidouros recorrentes"] = (g[g.recorrente == "Sumidouros recorrentes"].classe.value_counts(normalize=True)
                                     .reindex(ORDEM, fill_value=0) * 100)
tab = tab.loc[["Sumidouros recorrentes", "Sumidouros líquidos", "Emissores líquidos"]]
tab.round(1).to_csv(OUT / "risco_inundacoes_por_grupo_2015.csv")
g[["nome", "classe", "valor", "grupo", "recorrente"]].to_csv(OUT / "risco_inundacoes_municipios.csv")

alto = lambda s: s.isin(["Muito alto", "Alto"]).mean()  # noqa: E731
res = {
    "pct_alto_muito_alto_brasil": float(alto(ri.classe) * 100),
    "pct_alto_muito_alto_amazonia_legal": float(alto(x.classe) * 100),
    "pct_alto_muito_alto_sumidouros": float(alto(g[g.grupo == "Sumidouros líquidos"].classe) * 100),
    "pct_alto_muito_alto_emissores": float(alto(g[g.grupo == "Emissores líquidos"].classe) * 100),
    "recorrentes_alto_muito_alto": int(g[g.recorrente == "Sumidouros recorrentes"].classe.isin(["Muito alto", "Alto"]).sum()),
    "indice_medio_sumidouros": float(g[g.grupo == "Sumidouros líquidos"].valor.mean()),
    "indice_medio_emissores": float(g[g.grupo == "Emissores líquidos"].valor.mean()),
    "mann_whitney_p": float(mannwhitneyu(g[g.grupo == "Sumidouros líquidos"].valor.dropna(),
                                         g[g.grupo == "Emissores líquidos"].valor.dropna(), alternative="greater").pvalue),
}
json.dump(res, open(OUT / "risco_inundacoes_resumo.json", "w"), indent=1, ensure_ascii=False)

# figura: barras 100% empilhadas, classes ordenadas (rampa sequencial)
cores = {"Muito alto": "#a8401c", "Alto": "#eb6834", "Médio": "#f7c4a8", "Baixo": "#d9d8d2", "Muito baixo": "#efeee9"}
linhas = pd.concat([comp.T, tab])[ORDEM]
linhas = linhas.loc[["Brasil", "Amazônia Legal", "Emissores líquidos", "Sumidouros líquidos", "Sumidouros recorrentes"]]
fig, ax = plt.subplots(figsize=(12, 6.5))
molde(fig, "Quem remove carbono está mais exposto a inundações",
      "Municípios por classe de risco de impacto para inundações, enxurradas e alagamentos, 2015 (%)",
      "10_risco_inundacoes", top=0.80, bottom=0.16, left=0.20, right=0.97)
ax.grid(False)
esq = pd.Series(0.0, index=linhas.index)
for c in ORDEM:
    ax.barh(linhas.index, linhas[c], left=esq, color=cores[c], edgecolor=FUNDO, linewidth=2, height=0.62, label=c)
    for i, (v, l0) in enumerate(zip(linhas[c], esq)):
        if v >= 7:
            ax.text(l0 + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=10,
                    color="white" if c in ("Muito alto", "Alto") else TINTA)
    esq += linhas[c]
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel("% dos municípios do grupo")
ax.legend(ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.12), fontsize=10)
ax.spines["bottom"].set_visible(False); ax.tick_params(axis="y", length=0)
salvar(fig, "10_risco_inundacoes")
print(json.dumps(res, indent=1, ensure_ascii=False))
