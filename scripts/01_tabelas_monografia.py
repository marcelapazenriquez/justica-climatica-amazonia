"""
Extrai as tabelas da monografia (.docx) para CSVs em data/processed/ (t01…t09).
Os números ficam como publicados na monografia; problemas conhecidos estão em docs/errata.md.

Uso:
    python scripts/01_tabelas_monografia.py caminho/MONOGRAFIA.docx
"""
import sys
from pathlib import Path

import docx
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
UFS = ["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]


def num(s):
    s = (s or "").strip().replace("−", "-")
    if s in {"", "...", "…", "\\..."}:
        return float("nan")
    return float(s.replace(".", "").replace(",", "."))


def cel(t):
    return [[c.text.strip() for c in r.cells] for r in t.rows]


def main(path):
    t = docx.Document(path).tables
    OUT.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([{"categoria": r[0], "area_km2": num(r[1]), "pct_area_bioma": num(r[2])} for r in cel(t[0])[1:]]) \
        .to_csv(OUT / "t01_ucs_bioma_amazonia.csv", index=False)

    recs, esfera = [], None
    for r in cel(t[1]):
        if r[0].startswith("Amazônia"):
            esfera = r[0].split("Esfera")[-1].strip().lower()
        elif r[0] in UFS:
            recs.append({"esfera": esfera, "uf": r[0], "area_bioma_uf_km2": num(r[1]), "n_pi": num(r[2]),
                         "pi_km2": num(r[3]), "n_us": num(r[5]), "us_km2": num(r[6]), "n_total": num(r[8]),
                         "total_km2": num(r[9]), "pct_bioma_da_uf": num(r[11])})
    pd.DataFrame(recs).to_csv(OUT / "t02_ucs_por_uf_esfera.csv", index=False)

    rows = cel(t[2]); anos = [int(a) for a in rows[0][1:]]; recs = []
    for r in rows[1:]:
        reg = "Amazônia Legal" if "Amaz" in r[0] else "Brasil"
        recs += [{"regiao": reg, "ano": a, "afetados_100mil": num(v)} for a, v in zip(anos, r[1:])]
    pd.DataFrame(recs).to_csv(OUT / "t03_ods13_1_1_desastres.csv", index=False)

    pd.DataFrame([{"ano": int(r[0]), "area_floresta_ha": num(r[1]), "pct_territorio": num(r[2])} for r in cel(t[3])[1:]]) \
        .to_csv(OUT / "t04_ods15_1_1_area_floresta_brasil.csv", index=False)

    rows = cel(t[4]); ufs = rows[0][1:]; recs = []
    for r in rows[1:]:
        recs += [{"faixa_perda_pct": r[0], "uf": u, "n_municipios": num(v)} for u, v in zip(ufs, r[1:])]
    pd.DataFrame(recs).to_csv(OUT / "t05_perda_florestal_faixas.csv", index=False)

    pd.DataFrame([{"ano": int(r[0]), "kba_em_uc_brasil_km2": num(r[1]), "kba_em_uc_amazonia_km2": num(r[2])}
                  for r in cel(t[5])[1:]]).to_csv(OUT / "t06_ods15_1_2_kba.csv", index=False)

    pd.DataFrame([{"ano": int(r[0]), "biomassa_t_ha": num(r[1]), "taxa_alteracao_area_florestal_pct": num(r[2]),
                   "pct_floresta_em_area_protegida": num(r[3]), "pct_floresta_com_plano_manejo": num(r[4]),
                   "area_certificada_mil_ha": num(r[5])} for r in cel(t[6])[1:]]) \
        .to_csv(OUT / "t07_ods15_2_1_gestao_florestal.csv", index=False)

    recs, anos = [], None
    for r in cel(t[7]):
        if r[0].isdigit():
            anos = (int(r[0]), int(r[3])); continue
        for k, ano in enumerate(anos):
            mun, uf, v = r[3 * k: 3 * k + 3]
            recs.append({"ano": ano, "municipio": mun, "uf": uf, "emissao_liquida_tco2e": num(v)})
    pd.DataFrame(recs).to_csv(OUT / "t08_seeg_remocao_liquida_top12.csv", index=False)

    rows = cel(t[8]); classes = rows[1][1:]; recs = []
    for r in rows[2:]:
        recs += [{"uf": r[0], "classe_risco": c, "n": num(v)} for c, v in zip(classes, r[1:])]
    pd.DataFrame(recs).to_csv(OUT / "t09_risco_geohidrologico.csv", index=False)
    print("CSVs em", OUT)


if __name__ == "__main__":
    main(sys.argv[1])
