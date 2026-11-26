"""
Fonte de cada figura e tabela: link exato + passo a passo sintético de extração.
Usado no rodapé das figuras, na base organizada e nas fontes do artigo.
"""

SEEG_MUN = ("SEEG Municípios, Observatório do Clima (https://plataforma.seeg.eco.br/cities/statistics). "
            "Extração: setor Mudança de Uso da Terra e Florestas; emissões (desmatamento, outras mudanças de uso e "
            "regeneração) e remoções por município, CO₂e (t), 2006–2017; emissão líquida = emissões + remoções.")
PRODES_MUN = ("PRODES municipal, INPE (http://www.dpi.inpe.br/prodesdigital/prodesmunicipal.php). "
              "Extração: Amazônia Legal, ano 2017; colunas \"Desflorestamento até 2017\" e \"Área\" por município.")
MALHA = "Malha municipal IBGE via https://github.com/tbrugz/geodata-br (arquivos geojs-UF-mun.json)."

FONTES = {
    "01_ods13_desastres": (
        "ODS Brasil/IBGE, indicador 13.1.1 (https://odsbrasil.gov.br/objetivo13/indicador1311), com dados do S2ID/MIDR. "
        "Extração: Download Indicadores → Exportar em Xlsx; média simples das 9 UFs da Amazônia Legal e valor Brasil, "
        "2015–2022 (acesso em ago. 2024)."),
    "02_ods15_kba_protegidas": (
        "IBGE/SIDRA, Tabela 4962 (https://sidra.ibge.gov.br/tabela/4962). "
        "Extração: variável \"Proporção de sítios importantes para a biodiversidade terrestre cobertos por áreas "
        "protegidas\"; níveis Brasil e Bioma = Amazônia; anos 2015–2023."),
    "03_ucs_por_uf": (
        "CNUC/MMA, Painel de UCs (https://cnuc.mma.gov.br/powerbi). "
        "Extração: filtros Bioma = Amazônia, esfera (federal, estadual, municipal) e UF; área das UCs (km²) ÷ área "
        "do bioma na UF; acesso em jul. 2025."),
    "05_mapas_emissao_desmatamento": (
        "A: " + SEEG_MUN + " Média 2015–2017 ÷ área do município (km²). B: " + PRODES_MUN + " " + MALHA),
    "06_recorrencia_sumidouros_emissores": (
        SEEG_MUN + " Para cada ano, ordenação dos 760 municípios pela emissão líquida; contagem dos anos entre os 12 "
        "menores (sumidouros) e os 12 maiores (emissores)."),
    "07_sao_felix_do_xingu": (
        "A: " + SEEG_MUN.replace("por município", "de São Félix do Xingu (PA), cód. 1507300") + " "
        "B: IBGE/SIDRA, Pesquisa da Pecuária Municipal, Tabela 3939 (https://sidra.ibge.gov.br/tabela/3939). "
        "Extração: variável Efetivo dos rebanhos, tipo Bovino, município 1507300, 2006–2017."),
    "08_seeg_estados_2025": (
        "SEEG 14, Observatório do Clima (https://plataforma.seeg.eco.br/), arquivo Dados-nacionais-14_0.xlsx, aba "
        "Dados. Extração: Gás = CO2e (t) GWP-AR5; Estado = 9 UFs da Amazônia Legal; colunas 2006 e 2025; tipos Emissão "
        "e Remoção (exclui NCI); soma por setor."),
    "09_icms_verde": (
        "SEMAS-PA, ICMS Verde, Índice Definitivo (https://icmsverde.semas.pa.gov.br/indice.php). Extração: tabela "
        "\"Índice Definitivo\", uma linha por município e uma coluna por ano de repasse (2014–2024; total de 2, 4, 6 e 8 "
        "de 2014 a 2017); participação = índice ÷ total do ano, média 2015–2017. " + SEEG_MUN + " Média 2015–2017; "
        "sumidouro líquido = emissão líquida média < 0."),
    "10_risco_inundacoes": (
        "AdaptaBrasil MCTI (https://adaptabrasil.mcti.gov.br). Extração: setor Desastres geo-hidrológicos → Índice de "
        "risco para inundações, enxurradas e alagamentos; recorte Brasil, resolução município, ano 2015; download em "
        "xlsx (colunas geocod_ibge, valor, classe); filtro dos 772 municípios da Amazônia Legal (IBGE, 2022). "
        "Grupos: " + SEEG_MUN + " Sumidouro líquido = emissão líquida média 2015–2017 < 0."),
}

FONTES_TABELAS = {
    "t01_ucs": FONTES["03_ucs_por_uf"],
    "t02_perda": ("PRODES municipal, INPE (http://www.dpi.inpe.br/prodesdigital/prodesmunicipal.php). "
                  "Extração: Amazônia Legal, anos 2006 e 2017; colunas \"Desflorestamento até o ano\" e \"Floresta\"; "
                  "perda = (desmatamento acumulado 2017 − 2006) ÷ floresta de 2006."),
    "t03_e1e5": (SEEG_MUN + " IBGE, Censos Agropecuários 2006 e 2017 (https://sidra.ibge.gov.br/pesquisa/censo-agropecuario), "
                 "utilização das terras por município: área de lavouras permanentes, temporárias e pastagens; "
                 "PPM, Tabela 3939 (https://sidra.ibge.gov.br/tabela/3939): efetivo bovino."),
    "t04_perfil": (SEEG_MUN + " " + PRODES_MUN + " PPM, Tabela 3939 (https://sidra.ibge.gov.br/tabela/3939); PIB dos "
                   "Municípios, Tabela 5938 (https://sidra.ibge.gov.br/tabela/5938), variável PIB per capita, 2017; "
                   "famílias no Bolsa Família, MDS. Medianas de cada grupo."),
    "t05_seeg": FONTES["08_seeg_estados_2025"],
    "t06_desastres": FONTES["01_ods13_desastres"],
    "t07_risco": ("AdaptaBrasil MCTI (https://adaptabrasil.mcti.gov.br). Extração: setor Desastres geo-hidrológicos → "
                  "Índice de risco para inundações, enxurradas e alagamentos; resolução município; 2015; contagem por "
                  "classe nos municípios da Amazônia Legal (lista IBGE, 2022)."),
}
