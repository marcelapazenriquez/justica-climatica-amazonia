"""
Junta tudo na base organizada do projeto:
  data/base_justica_climatica_amazonia.xlsx  todas as tabelas em abas, com LEIA-ME e dicionário
  data/base/*.csv                            a mesma base em CSV
Rode depois dos scripts 01 a 03:
    python scripts/04_base_organizada.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
from openpyxl import load_workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402

from fontes import FONTES, FONTES_TABELAS, PRODES_MUN, SEEG_MUN  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC, MUN = ROOT / "data" / "raw", ROOT / "data" / "processed", ROOT / "data" / "processed" / "municipal"
BASE = ROOT / "data" / "base"; BASE.mkdir(parents=True, exist_ok=True)
XLSX = ROOT / "data" / "base_justica_climatica_amazonia.xlsx"

p = pd.read_excel(RAW / "painel_municipal_2006_2017.xlsx", sheet_name="dados")
p = p.loc[:, ~p.columns.duplicated()]
painel = pd.DataFrame({
    "cod_ibge": p.CodIbge, "municipio": p.Municipio, "uf": p.Estado, "ano": p.Ano, "area_km2": p.AreaKm2,
    "desmatamento_acumulado_km2": p.Desmatado, "desmatamento_ano_km2": p.Incremento, "floresta_km2": p.Floresta,
    "nao_floresta_km2": p.NaoFloresta, "hidrografia_km2": p.Hidrografia,
    "emissoes_tco2e": p["Total Geral (Emissoes)"], "remocoes_tco2e": p["Remocoes"],
    "emissao_liquida_tco2e": p["Emissoes Liquidas"], "emissao_desmatamento_tco2e": p["Desmatamento"],
    "emissao_outras_mut_tco2e": p["Outras mudanças de uso da terra"], "populacao": p["populacao"],
    "pib_per_capita_rs": p["PIB PerCap (r$1.000)"], "bovinos_cabecas": p["CABEC-Bovino"],
    "familias_bolsa_familia": p["FAM-BENEF-BF"], "valor_pago_bolsa_familia_rs": p["VL-TOTAL-PAGBF"],
    "censo_area_total_ha": p.AREA1, "censo_lavoura_permanente_ha": p.AREA2, "censo_lavoura_temporaria_ha": p.AREA3,
    "censo_pastagem_natural_ha": p.AREA4, "censo_pastagem_degradada_ha": p.AREA5, "censo_pastagem_boa_ha": p.AREA6,
    "censo_mata_app_rl_ha": p.AREA7, "censo_mata_natural_ha": p.AREA8, "censo_floresta_plantada_ha": p.AREA9,
})
censo = [c for c in painel if c.startswith("censo_")]
painel.loc[~painel.ano.isin([2006, 2017]), censo] = pd.NA
painel = painel.sort_values(["uf", "municipio", "ano"])

seeg = pd.read_csv(RAW / "seeg14_estados_amazonia_legal.csv")
seeg_long = seeg.melt(id_vars=["tipo", "setor", "categoria", "estado", "bioma"], var_name="ano", value_name="tco2e")
seeg_est = (seeg_long[seeg_long.tipo.isin(["Emissão", "Remoção"]) & (seeg_long.tco2e != 0)]
            .groupby(["estado", "ano", "tipo", "setor"], as_index=False).tco2e.sum())

k = pd.read_excel(RAW / "ibge_sidra_4962_kba.xlsx", sheet_name=None, header=None)
abas = list(k)
kba = pd.DataFrame({"ano": [int(a) for a in k[abas[1]].iloc[3, 3::2]]})
for i, nome in [(1, "pct_kba_em_uc"), (2, "area_kba_em_uc_km2"), (3, "area_total_kba_km2")]:
    kba[nome + "_brasil"] = k[abas[i]].iloc[4, 3::2].astype(float).values
    kba[nome + "_amazonia"] = k[abas[i]].iloc[5, 3::2].astype(float).values

T = {
    "painel_municipal": (painel, "Painel de 760 municípios da Amazônia Legal, 2006–2017 (dado de entrada). Variáveis censo_* só em 2006 e 2017.",
                         SEEG_MUN + " " + PRODES_MUN + " " + FONTES_TABELAS["t04_perfil"]),
    "seeg14_estados_serie": (seeg_est, "SEEG 14 por estado, ano (2000–2025), tipo e setor, t CO₂e GWP-AR5, sem NCI (dado de entrada).", FONTES["08_seeg_estados_2025"]),
    "ucs_por_categoria": (pd.read_csv(PROC / "t01_ucs_bioma_amazonia.csv"), "Área de UCs no bioma Amazônia por categoria (PI, US) e % da área do bioma.", FONTES["03_ucs_por_uf"]),
    "ucs_por_uf_esfera": (pd.read_csv(PROC / "t02_ucs_por_uf_esfera.csv"), "Nº e área de UCs por UF e esfera administrativa.", FONTES["03_ucs_por_uf"]),
    "ods15_1_2_kba": (kba, "Indicador 15.1.2: KBAs cobertas por UCs, Brasil e bioma Amazônia.", FONTES["02_ods15_kba_protegidas"]),
    "ods13_1_1_desastres": (pd.read_csv(PROC / "t03_ods13_1_1_desastres.csv"), "Indicador 13.1.1: mortos, desaparecidos e afetados por 100 mil hab.", FONTES["01_ods13_desastres"]),
    "perda_florestal_2006_2017": (pd.read_csv(MUN / "perda_florestal_faixas_2006_2017.csv"), "Nº de municípios por faixa de perda florestal (desmatamento 2006–2017 ÷ floresta de 2006).", FONTES_TABELAS["t02_perda"]),
    "recorrencia_top12": (pd.read_csv(MUN / "recorrencia_top12.csv"), "Anos (de 12) entre os 12 maiores sumidouros/emissores líquidos.", FONTES["06_recorrencia_sumidouros_emissores"]),
    "perfil_grupos": (pd.read_csv(MUN / "perfil_grupos_2017.csv"), "Medianas por grupo: sumidouros recorrentes, emissores recorrentes, demais.", FONTES_TABELAS["t04_perfil"]),
    "perfil_recorrentes": (pd.read_csv(MUN / "perfil_municipios_recorrentes.csv"), "Os 15 municípios recorrentes, um a um.", FONTES_TABELAS["t04_perfil"]),
    "rankings_E1_E5": (pd.read_csv(MUN / "rankings_E1_E5.csv"), "Dez municípios de menor emissão líquida por indicador E1–E5, 2006 e 2017.", FONTES_TABELAS["t03_e1e5"]),
    "sao_felix_do_xingu": (pd.read_csv(MUN / "sao_felix_do_xingu_2006_2017.csv"), "São Félix do Xingu (PA): emissões, rebanho, desmatamento, PIB per capita.", FONTES["07_sao_felix_do_xingu"]),
    "seeg14_estados_2025": (pd.read_csv(MUN / "seeg14_estados_2025_MtCO2e.csv"), "Emissões por setor, remoções e emissão líquida por estado, 2025 e 2006 (Mt CO₂e).", FONTES["08_seeg_estados_2025"]),
    "icms_verde_indice": (pd.read_csv(RAW / "icms_verde_para_indice_2014_2024.tsv", sep="\t"), "Índice do ICMS Verde por município do Pará (SEMAS-PA), 2014–2024 (% da cota-parte distribuída pelo critério ecológico; o total sobe de 2 a 8).", FONTES["09_icms_verde"]),
    "icms_verde_x_seeg": (pd.read_csv(MUN / "icms_verde_x_seeg_2015_2017.csv"), "Pará, média 2015–2017: participação no ICMS Verde, remoções e emissão líquida por município.", FONTES["09_icms_verde"]),
    "icms_verde_grupos": (pd.read_csv(MUN / "icms_verde_grupos_2015_2017.csv"), "Pará, 2015–2017: sumidouros x emissores líquidos, parte das remoções e do ICMS Verde.", FONTES["09_icms_verde"]),
    "risco_inundacoes_uf": (pd.read_csv(MUN / "risco_inundacoes_por_uf_2015.csv"), "Municípios da Amazônia Legal por classe de risco de impacto para inundações, enxurradas e alagamentos, 2015 (substitui a Tabela 9 da monografia).", FONTES_TABELAS["t07_risco"]),
    "risco_inundacoes_grupos": (pd.read_csv(MUN / "risco_inundacoes_por_grupo_2015.csv"), "% de municípios por classe de risco: sumidouros recorrentes, sumidouros líquidos e emissores líquidos.", FONTES["10_risco_inundacoes"]),
    "risco_inundacoes_municipios": (pd.read_csv(MUN / "risco_inundacoes_municipios.csv"), "Índice e classe de risco por município do painel, com o grupo de emissão.", FONTES["10_risco_inundacoes"]),
}

dic = pd.DataFrame([
    ("cod_ibge", "Código IBGE do município (7 dígitos)", "—", "IBGE"),
    ("municipio, uf, ano", "Identificação", "—", "—"),
    ("area_km2", "Área do município", "km²", "PRODES"),
    ("desmatamento_acumulado_km2", "Desmatamento acumulado até o ano", "km²", "PRODES"),
    ("desmatamento_ano_km2", "Desmatamento no ano", "km²", "PRODES"),
    ("floresta_km2, nao_floresta_km2, hidrografia_km2", "Cobertura no ano", "km²", "PRODES"),
    ("emissoes_tco2e", "Emissões brutas do setor Mudança de Uso da Terra (desmatamento + outras mudanças + regeneração)", "t CO₂e", "SEEG Municípios"),
    ("remocoes_tco2e", "Remoções (valor negativo)", "t CO₂e", "SEEG Municípios"),
    ("emissao_liquida_tco2e", "Emissões + remoções; negativo = sumidouro", "t CO₂e", "SEEG Municípios"),
    ("emissao_desmatamento_tco2e, emissao_outras_mut_tco2e", "Emissões de desmatamento e de outras mudanças de uso da terra", "t CO₂e", "SEEG Municípios"),
    ("populacao", "População estimada", "habitantes", "IBGE"),
    ("pib_per_capita_rs", "PIB per capita, valores correntes", "R$", "IBGE, PIB dos Municípios (tab. 5938)"),
    ("bovinos_cabecas", "Efetivo bovino", "cabeças", "IBGE, PPM (tab. 3939)"),
    ("familias_bolsa_familia, valor_pago_bolsa_familia_rs", "Famílias: soma dos 12 meses (família-mês; ÷ 12 = média mensal). Valor pago: unidade inconsistente entre anos (2006, 2008–2011 e 2016 fora de escala); não usar", "família-mês; R$", "MDS"),
    ("censo_*_ha", "Utilização das terras nos estabelecimentos (só 2006 e 2017)", "ha", "IBGE, Censo Agropecuário"),
], columns=["variavel", "descricao", "unidade", "fonte"])

leia = pd.DataFrame(
    [("Projeto", "Quem mitiga, quem emite, quem é compensado: justiça climática entre os municípios da Amazônia Legal"),
     ("Autoria", "Marcela Paz da Silva Enriquez; Marcelo Bentes Diniz (UFPA)"),
     ("Como usar", "Cada aba é uma tabela. painel_municipal e seeg14_estados_serie são dados de entrada; as demais são resultados gerados pelos scripts do repositório."),
     ("Licença", "Dados próprios: CC BY 4.0. Dados de terceiros seguem as licenças das fontes."), ("", "")]
    + [(n, f"{desc}  FONTE: {fonte}") for n, (_, desc, fonte) in T.items()],
    columns=["aba", "conteúdo e fonte"])

for n, (df, _, _) in T.items():
    df.to_csv(BASE / f"{n}.csv", index=False)
dic.to_csv(BASE / "dicionario_painel.csv", index=False)
leia.to_csv(BASE / "LEIA-ME.csv", index=False)

with pd.ExcelWriter(XLSX, engine="openpyxl") as w:
    leia.to_excel(w, sheet_name="LEIA-ME", index=False)
    dic.to_excel(w, sheet_name="dicionario_painel", index=False)
    for n, (df, _, _) in T.items():
        df.to_excel(w, sheet_name=n[:31], index=False)

wb = load_workbook(XLSX)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            c.font = Font(name="Arial", size=10, bold=(c.row == 1))
    for c in ws[1]:
        c.fill = PatternFill("solid", fgColor="E6E5E0")
    ws.freeze_panes = "A2"
    for col in ws.columns:
        larg = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200])
        ws.column_dimensions[col[0].column_letter].width = min(max(10, larg + 2), 60)
    if ws.title in ("LEIA-ME", "dicionario_painel"):
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions["B"].width = 110 if ws.title == "LEIA-ME" else 60
wb.save(XLSX)
print("Base:", XLSX)
