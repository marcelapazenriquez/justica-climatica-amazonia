"""
Análises municipais do artigo: recorrência de sumidouros/emissores, perfis, indicadores E1–E5,
perda florestal, São Félix do Xingu, SEEG 14 por estado e figuras 05–08.

Entradas (data/raw): painel_municipal_2006_2017.xlsx, seeg14_estados_amazonia_legal.csv, geo/
Saídas: data/processed/municipal/*.csv e figures/

Uso:
    python scripts/03_analise_municipal.py
    ARTIGO=1 python scripts/03_analise_municipal.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.collections import PatchCollection  # noqa: E402
from matplotlib.patches import Patch, Polygon  # noqa: E402

from estilo import (AMARELO, AZUL, CINZA, FUNDO, LARANJA, ROOT, TINTA, TINTA2, VERDE,  # noqa: E402
                    molde, salvar)

RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed" / "municipal"
OUT.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ dados
d = pd.read_excel(RAW / "painel_municipal_2006_2017.xlsx", sheet_name="dados")
d = d.loc[:, ~d.columns.duplicated()].rename(columns={
    "Emissoes Liquidas": "EL", "Total Geral (Emissoes)": "EMI", "Remocoes": "REM", "CABEC-Bovino": "bov",
    "PIB PerCap (r$1.000)": "pibpc", "FAM-BENEF-BF": "fam_bf", "populacao": "pop", "Estado": "uf", "Municipio": "mun"})
d["nome"] = d["mun"] + " (" + d["uf"] + ")"

# ------------------------------------------------------------------ 1. recorrência (12 maiores por ano)
TOP = 12
rank_s = d.sort_values("EL").groupby("Ano").head(TOP)
rank_e = d.sort_values("EL", ascending=False).groupby("Ano").head(TOP)
med = d[d.Ano >= 2015].groupby("CodIbge").EL.mean()
base17 = d[d.Ano == 2017].set_index("CodIbge")
rec = pd.DataFrame({"anos_top12_sumidouro": rank_s.groupby("CodIbge").size(),
                    "anos_top12_emissor": rank_e.groupby("CodIbge").size()}).fillna(0).astype(int)
rec = rec.join(base17[["nome", "uf", "AreaKm2"]]).join(med.rename("EL_media_2015_2017"))
rec.sort_values(["anos_top12_sumidouro", "EL_media_2015_2017"], ascending=[False, True]).to_csv(OUT / "recorrencia_top12.csv")
sumid = rec[rec.anos_top12_sumidouro >= 10].index
emiss = rec[rec.anos_top12_emissor >= 10].index

# ------------------------------------------------------------------ 2. perfil dos grupos (2017)
d17 = base17.copy()
d17["EL_med"] = med
d17["pct_desmatado"] = d17.Desmatado / d17.AreaKm2 * 100
d17["bf_por_mil"] = d17.fam_bf / d17["pop"] * 1000
d17["grupo"] = "Demais municípios"
d17.loc[d17.index.isin(sumid), "grupo"] = "Sumidouros recorrentes"
d17.loc[d17.index.isin(emiss), "grupo"] = "Emissores recorrentes"
perfil = d17.groupby("grupo").agg(
    municipios=("nome", "size"), area_km2_mediana=("AreaKm2", "median"), populacao_mediana=("pop", "median"),
    EL_media_2015_2017_mil_t=("EL_med", lambda s: s.median() / 1e3), pib_pc_2017_mediana=("pibpc", "median"),
    bovinos_2017_mediana=("bov", "median"), pct_area_desmatada_mediana=("pct_desmatado", "median"),
    familias_bf_por_mil_hab_mediana=("bf_por_mil", "median"),
).reindex(["Sumidouros recorrentes", "Emissores recorrentes", "Demais municípios"])
perfil.to_csv(OUT / "perfil_grupos_2017.csv")
d17[d17.grupo != "Demais municípios"][["nome", "grupo", "AreaKm2", "pop", "EL_med", "pibpc", "bov", "pct_desmatado",
                                       "bf_por_mil"]].sort_values(["grupo", "EL_med"]).to_csv(OUT / "perfil_municipios_recorrentes.csv")

# resumo numérico usado no texto
neg = med[med < 0]
resumo = {
    "municipios": int(d.CodIbge.nunique()),
    "sumidouros_liquidos_2015_2017": int((med < 0).sum()),
    "sumidouros_recorrentes": int(len(sumid)),
    "emissores_recorrentes": int(len(emiss)),
    "parte_das_remocoes_dos_sumidouros_recorrentes": float(med[sumid].sum() / neg.sum()),
    "parte_da_area_dos_sumidouros_recorrentes": float(base17.loc[sumid, "AreaKm2"].sum() / base17.AreaKm2.sum()),
}

# ------------------------------------------------------------------ 3. E1–E5 (anos do Censo)
ind = {"E1": ("emissão líquida / km² do município", lambda x: x.AreaKm2, 0),
       "E2": ("emissão líquida / ha de lavoura permanente", lambda x: x.AREA2, 100),
       "E3": ("emissão líquida / ha de lavoura temporária", lambda x: x.AREA3, 100),
       "E4": ("emissão líquida / cabeça de bovino", lambda x: x.bov, 1000),
       "E5": ("emissão líquida / ha de pastagem", lambda x: x.AREA4 + x.AREA5 + x.AREA6, 100)}
linhas, persist = [], {}
for k, (desc, den, lim) in ind.items():
    tops = {}
    for a in (2006, 2017):
        x = d[d.Ano == a].copy(); x["den"] = den(x); x = x[x.den > lim]; x["val"] = x.EL / x.den
        tops[a] = x.nsmallest(10, "val")
        linhas += [{"indicador": k, "descricao": desc, "ano": a, "posicao": i, "municipio": r.nome, "valor": r.val}
                   for i, r in enumerate(tops[a].itertuples(), 1)]
    persist[k] = sorted(set(tops[2006].nome) & set(tops[2017].nome))
pd.DataFrame(linhas).to_csv(OUT / "rankings_E1_E5.csv", index=False)
pd.Series({k: "; ".join(v) for k, v in persist.items()}, name="persistentes_2006_e_2017").to_csv(OUT / "rankings_E1_E5_persistentes.csv")

# ------------------------------------------------------------------ 4. perda florestal 2006–2017
a6, a17 = d[d.Ano == 2006].set_index("CodIbge"), d[d.Ano == 2017].set_index("CodIbge")
perda = (a17.Desmatado - a6.Desmatado) / a6.Floresta * 100
faixa = pd.cut(perda, [10, 30, 50, np.inf], right=False, labels=["10 a 30%", "30 a 50%", "50% ou mais"])
pd.crosstab(faixa, a6.uf).reindex(columns=["MA", "PA", "MT", "RO", "TO", "AC", "AM", "AP", "RR"], fill_value=0) \
    .to_csv(OUT / "perda_florestal_faixas_2006_2017.csv")

# ------------------------------------------------------------------ 5. São Félix do Xingu
sfx = d[d.mun == "São Félix do Xingu"].set_index("Ano")[["EL", "EMI", "REM", "bov", "Incremento", "pibpc"]]
sfx.columns = ["emissao_liquida_t", "emissoes_t", "remocoes_t", "bovinos", "desmatamento_prodes_km2", "pib_pc"]
sfx.to_csv(OUT / "sao_felix_do_xingu_2006_2017.csv")

# ------------------------------------------------------------------ 6. SEEG 14 por estado (2025 x 2006)
s = pd.read_csv(RAW / "seeg14_estados_amazonia_legal.csv")
s = s[s.tipo.isin(["Emissão", "Remoção"])]
s["grupo"] = np.select([s.tipo == "Remoção", s.setor == "Mudança de Uso da Terra e Floresta", s.setor == "Agropecuária"],
                       ["remocoes", "mudanca_uso_terra", "agropecuaria"], "energia_industria_residuos")
est = s.pivot_table(index="estado", columns="grupo", values="2025", aggfunc="sum") / 1e6
est["liquida_2025"] = est.sum(axis=1)
est["liquida_2006"] = s.groupby("estado")["2006"].sum() / 1e6
est = est.sort_values("liquida_2025", ascending=False)
est.round(1).to_csv(OUT / "seeg14_estados_2025_MtCO2e.csv")
resumo["seeg14_liquida_2025_Mt"] = float(est.liquida_2025.sum())
resumo["seeg14_liquida_2006_Mt"] = float(est.liquida_2006.sum())
json.dump(resumo, open(OUT / "resumo_numeros.json", "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ figuras
geoms = {}
for c in (11, 12, 13, 14, 15, 16, 17, 21, 51):
    for f in json.load(open(RAW / "geo" / f"geojs-{c}-mun.json"))["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        geoms[int(f["properties"]["id"])] = [np.array(max(p, key=len)) for p in polys]  # maior anel = contorno


def mapa(ax, valores, classes, cores, rotulos, leg):
    pats, cs = [], []
    for cod, polys in geoms.items():
        if cod in valores.index:
            k = np.digitize(valores[cod], classes)
            for p in polys:
                pats.append(Polygon(p, closed=True)); cs.append(cores[k])
    ax.add_collection(PatchCollection(pats, facecolor=cs, edgecolor=FUNDO, linewidth=0.15))
    ax.autoscale_view(); ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    ax.legend(handles=[Patch(color=c, label=r) for c, r in zip(cores, rotulos)], title=leg, loc="upper center",
              bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=9, title_fontsize=9)


el_km2 = d[d.Ano >= 2015].assign(v=lambda x: x.EL / x.AreaKm2).groupby("CodIbge").v.mean()
desm = a17.Desmatado / a17.AreaKm2 * 100
fig, axs = plt.subplots(1, 2, figsize=(14, 8))
molde(fig, "A Amazônia Legal tem dois territórios", "Sumidouros no oeste e no norte; emissões no arco do desmatamento",
      "05_mapas_emissao_desmatamento", top=0.84, bottom=0.2, left=0.01, right=0.99, wspace=0.02)
mapa(axs[0], el_km2, [-100, -25, 25, 100, 250, 500],
     ["#0f6e4f", "#1baf7a", "#e9e8e2", "#f7c4a8", "#f1915f", "#eb6834", "#a8401c"],
     ["remove > 100", "remove 25 a 100", "−25 a 25", "emite 25 a 100", "emite 100 a 250", "emite 250 a 500", "emite > 500"],
     "Emissão líquida, t CO₂e/km²/ano (média 2015–2017)")
mapa(axs[1], desm, [10, 25, 50, 75], ["#f3f2ee", "#d9e6f5", "#9fc3ec", "#5a98e0", "#1f5fae"],
     ["até 10%", "10 a 25%", "25 a 50%", "50 a 75%", "mais de 75%"], "Área municipal desmatada até 2017 (PRODES)")
axs[0].set_title("A. Quem emite e quem remove", loc="left", fontsize=12, color=TINTA)
axs[1].set_title("B. Quanto do município já foi desmatado", loc="left", fontsize=12, color=TINTA)
salvar(fig, "05_mapas_emissao_desmatamento")

fig, axs = plt.subplots(1, 2, figsize=(13, 7.5))
molde(fig, "Os mesmos municípios, ano após ano",
      "Anos, entre 2006 e 2017, em que cada município esteve entre os 12 maiores sumidouros ou emissores",
      "06_recorrencia_sumidouros_emissores", top=0.80, bottom=0.14, left=0.25, right=0.97, wspace=0.85)
for ax, col, cor, tit in [(axs[0], "anos_top12_sumidouro", VERDE, "Maiores sumidouros"),
                          (axs[1], "anos_top12_emissor", LARANJA, "Maiores emissores")]:
    r = rec[rec[col] >= 6].sort_values([col, "EL_media_2015_2017"], ascending=[True, col == "anos_top12_sumidouro"])
    ax.barh(r.nome, r[col], color=cor, height=0.62)
    for y, v in enumerate(r[col]):
        ax.text(v + 0.2, y, str(v), va="center", fontsize=10, color=TINTA)
    ax.set_xlim(0, 13); ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    ax.set_xticks([0, 4, 8, 12]); ax.tick_params(axis="y", length=0, labelsize=10)
    ax.set_title(tit, loc="left", fontsize=12, color=TINTA); ax.set_xlabel("anos entre os 12 maiores (de 12)")
salvar(fig, "06_recorrencia_sumidouros_emissores")

fig, axs = plt.subplots(1, 2, figsize=(13, 6))
molde(fig, "São Félix do Xingu: menos desmatamento, mais boi",
      "A emissão líquida caiu 86% entre 2006 e 2017; o rebanho cresceu 40%",
      "07_sao_felix_do_xingu", top=0.78, bottom=0.12, left=0.07, right=0.97, wspace=0.25)
axs[0].bar(sfx.index, sfx.emissao_liquida_t / 1e6, color=LARANJA, width=0.65)
axs[0].set_title("A. Emissão líquida (milhões de t CO₂e)", loc="left", fontsize=12, color=TINTA)
axs[1].plot(sfx.index, sfx.bovinos / 1e6, color=AZUL, lw=2.4, marker="o", ms=7); axs[1].set_ylim(0, 2.6)
axs[1].set_title("B. Rebanho bovino (milhões de cabeças)", loc="left", fontsize=12, color=TINTA)
for ax in axs:
    ax.set_xticks([2006, 2009, 2012, 2015, 2017])
salvar(fig, "07_sao_felix_do_xingu")

e = est.sort_values("liquida_2025")
fig, ax = plt.subplots(figsize=(12, 6.75))
molde(fig, "Emissões e remoções dos estados da Amazônia Legal em 2025",
      "Só Amazonas e Amapá removem mais do que emitem", "08_seeg_estados_2025",
      top=0.80, bottom=0.14, left=0.12, right=0.95)
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
pos = pd.Series(0.0, index=e.index)
for col, cor, lab in [("mudanca_uso_terra", LARANJA, "Mudança de uso da terra"), ("agropecuaria", AMARELO, "Agropecuária"),
                      ("energia_industria_residuos", CINZA, "Energia, indústria e resíduos")]:
    ax.barh(e.index, e[col], left=pos, color=cor, height=0.62, edgecolor=FUNDO, linewidth=2, label=lab)
    pos += e[col]
ax.barh(e.index, e.remocoes, color=VERDE, height=0.62, edgecolor=FUNDO, linewidth=2, label="Remoções")
ax.scatter(e.liquida_2025, e.index, color=TINTA, zorder=5, s=36, label="Emissão líquida")
ax.axvline(0, color=TINTA2, lw=1); ax.set_xlabel("milhões de t CO₂e (GWP-AR5), 2025")
ax.legend(frameon=False, loc="lower right", fontsize=10)
salvar(fig, "08_seeg_estados_2025")
print(json.dumps(resumo, indent=1, ensure_ascii=False))
