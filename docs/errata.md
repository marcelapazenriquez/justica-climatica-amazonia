# Errata: problemas encontrados na monografia e como foram tratados

Os CSVs `data/processed/t01`…`t09` mantêm os números como publicados na monografia. As correções valem para o artigo.

| # | Onde | Problema | Tratamento |
|---|---|---|---|
| E1 | Tabela 1 | Os percentuais são área de UC ÷ área do bioma (1.197.746 ÷ 4.215.439 = 28,4%), não "% das UCs do Brasil". | Coluna renomeada; texto corrigido. |
| E2 | Tabela 6 (KBA) | A razão Amazônia/Brasil não "aumenta ano após ano": cai de 0,796 (2015) para 0,787 (2018–2021) e volta a 0,795. | Substituída pela % de KBAs protegidas (56,1% → 59,3% na Amazônia; 51,9% → 55,0% no Brasil). |
| E3 | Tabela 9 (risco) | A fonte é o AdaptaBrasil MCTI (índice de risco para inundações, enxurradas e alagamentos, 2015), não o CEMADEN. Comparando com o dado original: o "64" da linha de Roraima pertence ao Pará (classe Alto); AP tem 6, não 12, na classe Alto; MT tem 0 em Muito alto e 9 em Alto; o MA aparece com mais municípios do que os 181 da Amazônia Legal. | Refeita a partir do arquivo do AdaptaBrasil (`scripts/06_risco_inundacoes.py`); entra no artigo como Tabela 7. |
| E4 | Tabela 8 | "-283.25" (Novo Airão, 2015) com ponto decimal; listas em ordem crescente; coleção do SEEG não informada. | Substituída (ver E13). |
| E5 | Tabela 3 (ODS 13.1.1) | Título inconsistente com as linhas; 2016 (27,0) destoa; pico de 2020–21 inclui Covid registrada como desastre no S2ID. | Título corrigido e nota sobre a Covid; 2016 a conferir. |
| E6 | Tabela 4 | Série do Brasil, não da Amazônia Legal; fontes divergentes entre gráfico e tabela. | Fora do artigo. |
| E7 | Tabela 5 | Texto citava faixa "20 a 50%", inexistente. | Ver E12. |
| E8 | Numeração | Duas "Tabela 6", sem Tabela 7; listas de tabelas do modelo. | Renumerado no artigo. |
| E9 | Rankings E1–E5 | Comentados no texto sem tabela. | Tabela incluída no artigo. |
| E10 | Referências | DOI do RAD copiado de outro artigo; "Marcondes, 2022" é Coelho-Junior et al. (2022); números atribuídos ao RAD 2024 são do RAD 2022. | Corrigido. |
| E11 | Indicadores E2 e E3 | A emissão foi dividida pelo número de estabelecimentos (ESTAB2, ESTAB3), não pela área, gerando #DIV/0!. | Recalculados por hectare, com mínimo de 100 ha. |
| E12 | Tabela 5 | Media a variação da "floresta" do PRODES, que também muda por nuvem (por isso AP e RR apareciam). | Substituída por desmatamento novo 2006–2017 ÷ floresta de 2006. |
| E13 | Tabela 8 | Valores de outra coleção do SEEG, muito diferentes do painel (ex.: Japurá 2006: −0,33 Mt na tabela, −4,28 Mt no painel). | Artigo usa só o painel 2006–2017, com recorrência em 12 anos. |
| E14 | Painel municipal | As emissões municipais do painel cobrem só o setor Mudança de Uso da Terra (desmatamento, outras mudanças e regeneração); agropecuária e energia não entram. As remoções ficam próximas às da coleção 14 do SEEG, mas as emissões são, na maioria dos estados, 11% a 39% menores, sinal de uma coleção anterior. | Texto do artigo ajustado; coleção a confirmar com o organizador da base. |
| E15 | Bolsa Família no painel | FAM-BENEF-BF soma os 12 meses (família-mês): em 70% dos casos supera a população. VL-TOTAL-PAGBF tem unidade inconsistente entre anos (2006, 2008–2011 e 2016 fora de escala). | Dicionário corrigido; só a contagem de famílias de 2017 é usada, em comparação relativa. |
| E16 | Retrato estadual | A versão anterior do artigo usava o SEEG 11 (até 2022). | Atualizado para a coleção 14 (até 2025); as coleções não são comparáveis entre si, por mudança de método. |
