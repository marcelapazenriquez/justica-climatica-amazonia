"""Estilo comum das figuras: paleta, fontes e cabeçalho/rodapé com a fonte exata."""
import os
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt

from fontes import FONTES

ROOT = Path(__file__).resolve().parents[1]
ARTIGO = os.environ.get("ARTIGO") == "1"  # 1 = versão sem título embutido, para o artigo
FIG = ROOT / "figures" / ("artigo" if ARTIGO else "")
FIG.mkdir(parents=True, exist_ok=True)

AZUL, LARANJA, VERDE, CINZA, AMARELO = "#2a78d6", "#eb6834", "#1baf7a", "#b4b2a9", "#eda100"
TINTA, TINTA2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": GRADE,
    "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRADE, "grid.linewidth": 0.8,
    "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
})


def molde(fig, titulo, subtitulo, chave, top=0.78, bottom=0.12, **kw):
    """Margens + título, subtítulo e rodapé com a fonte (link e extração). No modo ARTIGO, só margens."""
    if ARTIGO:
        fig.subplots_adjust(top=0.95, bottom=bottom, **kw)
        return
    linhas = textwrap.wrap("Fonte: " + FONTES[chave], 175)
    fig.subplots_adjust(top=top, bottom=bottom + 0.028 * len(linhas), **kw)
    fig.text(0.04, 0.955, titulo, fontsize=17, weight="bold", color=TINTA, va="top")
    fig.text(0.04, 0.895, subtitulo, fontsize=12, color=TINTA2, va="top")
    fig.text(0.04, 0.015, "\n".join(linhas), fontsize=8.5, color=TINTA2, va="bottom", linespacing=1.4)


def salvar(fig, chave):
    fig.savefig(FIG / f"{chave}.png", dpi=150)
    plt.close(fig)
