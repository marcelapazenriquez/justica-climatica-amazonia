# Origem de cada arquivo

| Arquivo | Conteúdo | Fonte |
|---|---|---|
| `raw/painel_municipal_2006_2017.xlsx` | 760 municípios × 2006–2017: SEEG municipal (emissões, remoções, líquida), PRODES, Censo Agropecuário 2006/2017, PPM, PIB per capita, Bolsa Família | Base de pesquisa da UFPA, montada a partir de SEEG Municípios, PRODES, IBGE e MDS |
| `raw/seeg14_estados_amazonia_legal.csv` | SEEG coleção 14, CO₂e GWP-AR5, por estado, setor e categoria, 2000–2025 | Extraído de Dados-nacionais-14_0.xlsx (https://plataforma.seeg.eco.br/) por `scripts/00_extrair_seeg_estados.py` |
| `raw/ibge_sidra_4962_kba.xlsx` | Indicador ODS 15.1.2 | https://sidra.ibge.gov.br/tabela/4962 |
| `raw/ibge_municipios_amazonia_legal_2022.xlsx` | Lista oficial dos 772 municípios da Amazônia Legal | IBGE |
| `raw/geo/` | Malha municipal em GeoJSON | https://github.com/tbrugz/geodata-br (base IBGE) |
| `raw/icms_verde_para_indice_2014_2024.tsv` | Índice do ICMS Verde por município do Pará, 2014–2024 | SEMAS-PA, https://icmsverde.semas.pa.gov.br/indice.php (tabela Índice Definitivo) |
| `raw/adaptabrasil_risco_*_2015.xlsx` | Índices de risco de impacto para inundações/enxurradas/alagamentos e deslizamentos, por município, 2015 | AdaptaBrasil MCTI, https://adaptabrasil.mcti.gov.br (Desastres geo-hidrológicos, resolução município) |
| `processed/t01`…`t09` | Tabelas da monografia | `scripts/01_tabelas_monografia.py` |
| `processed/municipal/` | Recorrência, perfis, E1–E5, perda florestal, São Félix do Xingu, SEEG 14 por estado, números do texto (`resumo_numeros.json`) | `scripts/03_analise_municipal.py` |
| `processed/municipal/icms_verde_*` | Cruzamento ICMS Verde x SEEG no Pará, 2015–2017 | `scripts/05_icms_verde.py` |

Links e passos de extração de cada figura e tabela: `scripts/fontes.py`.
