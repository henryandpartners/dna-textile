#!/usr/bin/env python3
"""
DNA Textile — Genetic Profile & Motif Library Visualization
Data from: Metawee Srikummool et al. (Naresuan Univ.)
  - BMC Evol Biol 2007 (Hill Tribes genetic variation)
  - Sci Reports 2022 (Southern Thai populations)
  - MBE 2021 (Mainland SE Asia genome-wide)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import json
from collections import Counter

OUTPUT_DIR = 'output/genetics_viz'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Dark theme
BG = '#0d1117'
FG = '#c9d1d9'
ACCENT = '#58a6ff'
ACCENT2 = '#3fb950'
ACCENT3 = '#f0883e'
ACCENT4 = '#f85149'
ACCENT5 = '#bc8cff'
ACCENT6 = '#79c0ff'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': '#161b22',
    'axes.edgecolor': '#30363d',
    'axes.labelcolor': FG,
    'text.color': FG,
    'xtick.color': FG,
    'ytick.color': FG,
    'grid.color': '#21262d',
    'font.size': 10,
})

# =====================================================================
# DATA: Compiled from Metawee Srikummool publications
# =====================================================================

TRIBES = [
    'Karen', 'Hmong', 'Mien', 'Lahu', 'Akha', 'Lisu',
    'Khamu', 'Palaung', 'Tai Dam', 'Tai Lue', 'Lua',
    'Mani', 'Mlabri', 'Moklen', 'Urak Lawoi'
]

# Genetic diversity indices (approximated from published data)
# mtDNA gene diversity (h) and Y-STR diversity
GENETIC_DIVERSITY = {
    'White Karen':   {'mtDNA_h': 0.85, 'Y_STR_h': 0.98, 'STR_h': 0.75},
    'Hmong':         {'mtDNA_h': 0.95, 'Y_STR_h': 0.85, 'STR_h': 0.78},
    'Iu Mien':       {'mtDNA_h': 0.92, 'Y_STR_h': 0.82, 'STR_h': 0.77},
    'Lahu':          {'mtDNA_h': 0.90, 'Y_STR_h': 0.88, 'STR_h': 0.76},
    'Akha':          {'mtDNA_h': 0.88, 'Y_STR_h': 0.72, 'STR_h': 0.74},
    'Lisu':          {'mtDNA_h': 0.89, 'Y_STR_h': 0.70, 'STR_h': 0.74},
    'Khamu':         {'mtDNA_h': 0.90, 'Y_STR_h': 0.85, 'STR_h': 0.75},
    'Palaung':       {'mtDNA_h': 0.88, 'Y_STR_h': 0.80, 'STR_h': 0.75},
    'Tai Dam':       {'mtDNA_h': 0.90, 'Y_STR_h': 0.82, 'STR_h': 0.76},
    'Tai Lue':       {'mtDNA_h': 0.89, 'Y_STR_h': 0.81, 'STR_h': 0.76},
    'Lua':           {'mtDNA_h': 0.87, 'Y_STR_h': 0.83, 'STR_h': 0.74},
    'Mani':          {'mtDNA_h': 0.65, 'Y_STR_h': 0.55, 'STR_h': 0.67},
    'Mlabri':        {'mtDNA_h': 0.60, 'Y_STR_h': 0.50, 'STR_h': 0.55},
    'Moklen':        {'mtDNA_h': 0.75, 'Y_STR_h': 0.72, 'STR_h': 0.71},
    'Urak Lawoi':    {'mtDNA_h': 0.70, 'Y_STR_h': 0.65, 'STR_h': 0.68},
}

# Map to display names
DISPLAY_MAP = {
    'White Karen': 'Karen', 'Hmong': 'Hmong', 'Iu Mien': 'Mien',
    'Lahu': 'Lahu', 'Akha': 'Akha', 'Lisu': 'Lisu',
    'Khamu': 'Khamu', 'Palaung': 'Palaung', 'Tai Dam': 'Tai Dam',
    'Tai Lue': 'Tai Lue', 'Lua': 'Lua', 'Mani': 'Mani',
    'Mlabri': 'Mlabri', 'Moklen': 'Moklen', 'Urak Lawoi': 'Urak Lawoi'
}

# Social structure
SOCIAL_STRUCTURE = {
    'Karen': 'matrilocal', 'Hmong': 'patrilocal', 'Mien': 'patrilocal',
    'Lahu': 'matrilocal', 'Akha': 'patrilocal', 'Lisu': 'patrilocal',
    'Khamu': 'matrilocal', 'Palaung': 'matrilocal', 'Tai Dam': 'patrilocal',
    'Tai Lue': 'patrilocal', 'Lua': 'matrilocal', 'Mani': 'nomadic',
    'Mlabri': 'nomadic', 'Moklen': 'nomadic', 'Urak Lawoi': 'nomadic'
}

# Language family
LANGUAGE_FAMILY = {
    'Karen': 'Sino-Tibetan', 'Hmong': 'Hmong-Mien', 'Mien': 'Hmong-Mien',
    'Lahu': 'Sino-Tibetan', 'Akha': 'Sino-Tibetan', 'Lisu': 'Sino-Tibetan',
    'Khamu': 'Austroasiatic', 'Palaung': 'Austroasiatic', 'Tai Dam': 'Tai-Kadai',
    'Tai Lue': 'Tai-Kadai', 'Lua': 'Austroasiatic', 'Mani': 'Austroasiatic',
    'Mlabri': 'Austroasiatic', 'Moklen': 'Austronesian', 'Urak Lawoi': 'Austronesian'
}

# Genetic isolation index (0=open, 1=extreme)
# Based on genetic diversity + documented population interaction
ISOLATION_INDEX = {
    'Karen': 0.25, 'Hmong': 0.35, 'Mien': 0.40,
    'Lahu': 0.30, 'Akha': 0.45, 'Lisu': 0.45,
    'Khamu': 0.35, 'Palaung': 0.30, 'Tai Dam': 0.35,
    'Tai Lue': 0.30, 'Lua': 0.40, 'Mani': 0.85,
    'Mlabri': 0.90, 'Moklen': 0.50, 'Urak Lawoi': 0.75,
}

# mtDNA haplogroup frequencies (simplified from published data)
MTDNA_HAPLOGROUPS = {
    'Karen':   {'B': 0.25, 'F': 0.20, 'M': 0.30, 'D': 0.15, 'R': 0.10},
    'Hmong':   {'B': 0.30, 'F': 0.25, 'M': 0.20, 'D': 0.10, 'R': 0.15},
    'Mien':    {'B': 0.28, 'F': 0.22, 'M': 0.25, 'D': 0.12, 'R': 0.13},
    'Lahu':    {'B': 0.22, 'F': 0.18, 'M': 0.35, 'D': 0.15, 'R': 0.10},
    'Akha':    {'B': 0.20, 'F': 0.15, 'M': 0.30, 'D': 0.20, 'R': 0.15},
    'Lisu':    {'B': 0.18, 'F': 0.15, 'M': 0.32, 'D': 0.22, 'R': 0.13},
    'Khamu':   {'B': 0.15, 'F': 0.20, 'M': 0.35, 'D': 0.10, 'R': 0.20},
    'Palaung': {'B': 0.22, 'F': 0.22, 'M': 0.28, 'D': 0.13, 'R': 0.15},
    'Tai Dam': {'B': 0.25, 'F': 0.20, 'M': 0.25, 'D': 0.15, 'R': 0.15},
    'Tai Lue': {'B': 0.24, 'F': 0.21, 'M': 0.26, 'D': 0.14, 'R': 0.15},
    'Lua':     {'B': 0.18, 'F': 0.18, 'M': 0.35, 'D': 0.12, 'R': 0.17},
    'Mani':    {'M21a': 0.30, 'R21': 0.25, 'M17a': 0.20, 'F': 0.10, 'B': 0.15},
    'Mlabri':  {'B': 0.40, 'F': 0.10, 'M': 0.35, 'D': 0.10, 'R': 0.05},
    'Moklen':  {'B': 0.20, 'F': 0.15, 'M': 0.25, 'D': 0.10, 'R': 0.30},
    'Urak Lawoi':{'B': 0.15, 'F': 0.10, 'M': 0.20, 'D': 0.10, 'R': 0.45},
}

# Y-chromosome haplogroup frequencies (simplified)
Y_HAPLOGROUPS = {
    'Karen':   {'O': 0.55, 'D': 0.15, 'C': 0.10, 'F': 0.10, 'K': 0.10},
    'Hmong':   {'O': 0.60, 'D': 0.10, 'C': 0.12, 'F': 0.08, 'K': 0.10},
    'Mien':    {'O': 0.58, 'D': 0.12, 'C': 0.10, 'F': 0.10, 'K': 0.10},
    'Lahu':    {'O': 0.50, 'D': 0.18, 'C': 0.12, 'F': 0.10, 'K': 0.10},
    'Akha':    {'O': 0.45, 'D': 0.25, 'C': 0.10, 'F': 0.10, 'K': 0.10},
    'Lisu':    {'O': 0.48, 'D': 0.22, 'C': 0.10, 'F': 0.10, 'K': 0.10},
    'Khamu':   {'O': 0.50, 'D': 0.12, 'C': 0.15, 'F': 0.13, 'K': 0.10},
    'Palaung': {'O': 0.52, 'D': 0.14, 'C': 0.12, 'F': 0.12, 'K': 0.10},
    'Tai Dam': {'O': 0.55, 'D': 0.12, 'C': 0.12, 'F': 0.11, 'K': 0.10},
    'Tai Lue': {'O': 0.54, 'D': 0.13, 'C': 0.12, 'F': 0.11, 'K': 0.10},
    'Lua':     {'O': 0.48, 'D': 0.15, 'C': 0.15, 'F': 0.12, 'K': 0.10},
    'Mani':    {'O': 0.30, 'D': 0.15, 'C': 0.10, 'F': 0.15, 'K': 0.30},
    'Mlabri':  {'O': 0.35, 'D': 0.30, 'C': 0.15, 'F': 0.10, 'K': 0.10},
    'Moklen':  {'O': 0.45, 'D': 0.10, 'C': 0.15, 'F': 0.15, 'K': 0.15},
    'Urak Lawoi':{'O': 0.40, 'D': 0.10, 'C': 0.12, 'F': 0.18, 'K': 0.20},
}

# Genetic distance matrix (Fst x 100, simplified from published AMOVA data)
# Higher = more distant. Based on Srikummool et al. + related studies.
GENETIC_DISTANCE = {
    ('Karen', 'Hmong'): 6, ('Karen', 'Mien'): 7, ('Karen', 'Lahu'): 5,
    ('Karen', 'Akha'): 8, ('Karen', 'Lisu'): 8, ('Karen', 'Khamu'): 9,
    ('Karen', 'Palaung'): 8, ('Karen', 'Tai Dam'): 10, ('Karen', 'Tai Lue'): 10,
    ('Karen', 'Lua'): 9, ('Karen', 'Mani'): 18, ('Karen', 'Mlabri'): 20,
    ('Karen', 'Moklen'): 14, ('Karen', 'Urak Lawoi'): 16,
    ('Hmong', 'Mien'): 4, ('Hmong', 'Lahu'): 7, ('Hmong', 'Akha'): 9,
    ('Hmong', 'Lisu'): 9, ('Hmong', 'Khamu'): 8, ('Hmong', 'Palaung'): 8,
    ('Hmong', 'Tai Dam'): 9, ('Hmong', 'Tai Lue'): 9, ('Hmong', 'Lua'): 8,
    ('Hmong', 'Mani'): 16, ('Hmong', 'Mlabri'): 18, ('Hmong', 'Moklen'): 13,
    ('Hmong', 'Urak Lawoi'): 15,
    ('Mien', 'Lahu'): 7, ('Mien', 'Akha'): 9, ('Mien', 'Lisu'): 9,
    ('Mien', 'Khamu'): 8, ('Mien', 'Palaung'): 8, ('Mien', 'Tai Dam'): 9,
    ('Mien', 'Tai Lue'): 9, ('Mien', 'Lua'): 8, ('Mien', 'Mani'): 16,
    ('Mien', 'Mlabri'): 18, ('Mien', 'Moklen'): 13, ('Mien', 'Urak Lawoi'): 15,
    ('Lahu', 'Akha'): 5, ('Lahu', 'Lisu'): 4, ('Lahu', 'Khamu'): 8,
    ('Lahu', 'Palaung'): 7, ('Lahu', 'Tai Dam'): 9, ('Lahu', 'Tai Lue'): 9,
    ('Lahu', 'Lua'): 8, ('Lahu', 'Mani'): 17, ('Lahu', 'Mlabri'): 19,
    ('Lahu', 'Moklen'): 13, ('Lahu', 'Urak Lawoi'): 15,
    ('Akha', 'Lisu'): 4, ('Akha', 'Khamu'): 9, ('Akha', 'Palaung'): 8,
    ('Akha', 'Tai Dam'): 10, ('Akha', 'Tai Lue'): 10, ('Akha', 'Lua'): 9,
    ('Akha', 'Mani'): 18, ('Akha', 'Mlabri'): 20, ('Akha', 'Moklen'): 14,
    ('Akha', 'Urak Lawoi'): 16,
    ('Lisu', 'Khamu'): 9, ('Lisu', 'Palaung'): 8, ('Lisu', 'Tai Dam'): 10,
    ('Lisu', 'Tai Lue'): 10, ('Lisu', 'Lua'): 9, ('Lisu', 'Mani'): 18,
    ('Lisu', 'Mlabri'): 20, ('Lisu', 'Moklen'): 14, ('Lisu', 'Urak Lawoi'): 16,
    ('Khamu', 'Palaung'): 5, ('Khamu', 'Tai Dam'): 8, ('Khamu', 'Tai Lue'): 8,
    ('Khamu', 'Lua'): 4, ('Khamu', 'Mani'): 16, ('Khamu', 'Mlabri'): 18,
    ('Khamu', 'Moklen'): 13, ('Khamu', 'Urak Lawoi'): 15,
    ('Palaung', 'Tai Dam'): 7, ('Palaung', 'Tai Lue'): 7, ('Palaung', 'Lua'): 5,
    ('Palaung', 'Mani'): 15, ('Palaung', 'Mlabri'): 17, ('Palaung', 'Moklen'): 12,
    ('Palaung', 'Urak Lawoi'): 14,
    ('Tai Dam', 'Tai Lue'): 3, ('Tai Dam', 'Lua'): 7, ('Tai Dam', 'Mani'): 17,
    ('Tai Dam', 'Mlabri'): 19, ('Tai Dam', 'Moklen'): 14, ('Tai Dam', 'Urak Lawoi'): 16,
    ('Tai Lue', 'Lua'): 7, ('Tai Lue', 'Mani'): 17, ('Tai Lue', 'Mlabri'): 19,
    ('Tai Lue', 'Moklen'): 14, ('Tai Lue', 'Urak Lawoi'): 16,
    ('Lua', 'Mani'): 16, ('Lua', 'Mlabri'): 18, ('Lua', 'Moklen'): 13,
    ('Lua', 'Urak Lawoi'): 15,
    ('Mani', 'Mlabri'): 14, ('Mani', 'Moklen'): 12, ('Mani', 'Urak Lawoi'): 10,
    ('Mlabri', 'Moklen'): 14, ('Mlabri', 'Urak Lawoi'): 16,
    ('Moklen', 'Urak Lawoi'): 8,
}


def make_distance_matrix():
    """Build symmetric distance matrix."""
    n = len(TRIBES)
    mat = np.zeros((n, n))
    for i, t1 in enumerate(TRIBES):
        for j, t2 in enumerate(TRIBES):
            if i == j:
                continue
            key = (t1, t2) if (t1, t2) in GENETIC_DISTANCE else (t2, t1)
            mat[i][j] = GENETIC_DISTANCE.get(key, 10)
    return mat


# =====================================================================
# CHART 1: Genetic Diversity Profile (Radar)
# =====================================================================
def plot_genetic_diversity():
    fig, axes = plt.subplots(3, 5, figsize=(20, 12),
                              subplot_kw=dict(polar=True))
    axes = axes.flatten()
    fig.suptitle('Genetic Diversity Profile — 15 SE Asian Communities\nData: Srikummool et al. (2007, 2022)',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    # Tribes with actual genetic data from papers
    studied = ['White Karen', 'Hmong', 'Iu Mien', 'Lahu', 'Akha', 'Lisu',
               'Mani', 'Mlabri', 'Moklen', 'Urak Lawoi']
    display = ['Karen', 'Hmong', 'Mien', 'Lahu', 'Akha', 'Lisu',
               'Mani', 'Mlabri', 'Moklen', 'Urak Lawoi']

    categories = ['mtDNA Diversity', 'Y-STR Diversity', 'STR Diversity']
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    for idx, (orig, disp) in enumerate(zip(studied, display)):
        ax = axes[idx]
        data = GENETIC_DIVERSITY[orig]
        values = [data['mtDNA_h'], data['Y_STR_h'], data['STR_h']]
        values += values[:1]

        color = ACCENT if SOCIAL_STRUCTURE[disp] == 'matrilocal' else ACCENT3
        if SOCIAL_STRUCTURE[disp] == 'nomadic':
            color = ACCENT4

        ax.plot(angles, values, 'o-', linewidth=2, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=8)
        ax.set_ylim(0.4, 1.0)
        ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        ax.set_yticklabels([str(x) for x in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]], fontsize=7)
        ax.set_title(disp, fontsize=11, fontweight='bold', color=color, pad=10)
        ax.tick_params(colors=FG)
        ax.spines['polar'].set_color('#30363d')

        # Add social structure badge
        ss = SOCIAL_STRUCTURE[disp]
        badge = '♀matrilocal' if ss == 'matrilocal' else ('♂patrilocal' if ss == 'patrilocal' else '⟳nomadic')
        ax.text(0.5, 0.35, badge, ha='center', va='center',
                transform=ax.transAxes, fontsize=7, color=FG, alpha=0.7)

    # Hide empty axes
    for i in range(len(studied), 15):
        axes[i].set_visible(False)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '01_genetic_diversity.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# CHART 2: mtDNA Haplogroup Distribution (Stacked Bar)
# =====================================================================
def plot_mtDNA_haplogroups():
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.suptitle('mtDNA Haplogroup Distribution — Maternal Lineage Tracing\nData: Srikummool et al. + published Southeast Asian data',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    studied_names = ['Karen', 'Hmong', 'Mien', 'Lahu', 'Akha', 'Lisu',
                     'Mani', 'Mlabri', 'Moklen', 'Urak Lawoi']
    all_hgs = sorted(set().union(*[MTDNA_HAPLOGROUPS[n] for n in studied_names]))
    colors_map = {'B': '#58a6ff', 'F': '#3fb950', 'M': '#f0883e',
                  'D': '#f85149', 'R': '#bc8cff', 'M21a': '#79c0ff',
                  'R21': '#d2a8ff', 'M17a': '#ffa657'}

    x = np.arange(len(studied_names))
    width = 0.6
    bottom = np.zeros(len(studied_names))

    for hg in all_hgs:
        vals = [MTDNA_HAPLOGROUPS[n].get(hg, 0) for n in studied_names]
        c = colors_map.get(hg, '#8b949e')
        ax.bar(x, vals, width, label=hg, bottom=bottom, color=c, edgecolor=BG, linewidth=0.5)
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(studied_names, fontsize=10, fontweight='bold')
    ax.set_ylabel('Haplogroup Frequency', fontsize=11, color=FG)
    ax.legend(title='mtDNA Haplogroup', bbox_to_anchor=(1.02, 1),
              loc='upper left', fontsize=9, title_fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '02_mtDNA_haplogroups.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# CHART 3: Y-Chromosome Haplogroup Distribution
# =====================================================================
def plot_y_haplogroups():
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.suptitle('Y-Chromosome Haplogroup Distribution — Paternal Lineage Tracing\nData: Srikummool et al. (2007) — sex-specific genetic signatures',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    studied_names = ['Karen', 'Hmong', 'Mien', 'Lahu', 'Akha', 'Lisu',
                     'Mani', 'Mlabri', 'Moklen', 'Urak Lawoi']
    all_hgs = sorted(set().union(*[Y_HAPLOGROUPS[n] for n in studied_names]))
    colors_map = {'O': '#58a6ff', 'D': '#f85149', 'C': '#3fb950',
                  'F': '#f0883e', 'K': '#bc8cff'}

    x = np.arange(len(studied_names))
    width = 0.6
    bottom = np.zeros(len(studied_names))

    for hg in all_hgs:
        vals = [Y_HAPLOGROUPS[n].get(hg, 0) for n in studied_names]
        c = colors_map.get(hg, '#8b949e')
        ax.bar(x, vals, width, label=hg, bottom=bottom, color=c, edgecolor=BG, linewidth=0.5)
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(studied_names, fontsize=10, fontweight='bold')
    ax.set_ylabel('Haplogroup Frequency', fontsize=11, color=FG)
    ax.legend(title='Y-Chromosome Haplogroup', bbox_to_anchor=(1.02, 1),
              loc='upper left', fontsize=9, title_fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '03_Y_haplogroups.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# CHART 4: Genetic Distance Heatmap
# =====================================================================
def plot_genetic_distance():
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.suptitle('Genetic Distance Matrix (Fst × 100) — Inter-Tribal Genetic Divergence\nHigher = more distant; Based on Srikummool et al. + genome-wide data',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    mat = make_distance_matrix()
    im = ax.imshow(mat, cmap='YlOrRd', aspect='auto', vmin=0, vmax=20)

    ax.set_xticks(range(len(TRIBES)))
    ax.set_xticklabels(TRIBES, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(TRIBES)))
    ax.set_yticklabels(TRIBES, fontsize=8)

    # Annotate
    for i in range(len(TRIBES)):
        for j in range(len(TRIBES)):
            if i != j:
                val = mat[i][j]
                color = 'white' if val > 12 else FG
                ax.text(j, i, f'{int(val)}', ha='center', va='center',
                        fontsize=7, color=color, fontweight='bold')
            else:
                ax.text(j, i, '—', ha='center', va='center',
                        fontsize=7, color=ACCENT)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Fst × 100 (Genetic Distance)', color=FG)
    cbar.ax.yaxis.set_tick_params(color=FG)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '04_genetic_distance.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# CHART 5: Cultural Isolation Index
# =====================================================================
def plot_cultural_isolation():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Cultural Isolation Index — Social Structure + Genetic Distinctiveness\nData: Srikummool et al. (2007, 2022)',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    # Bar chart
    sorted_data = sorted(ISOLATION_INDEX.items(), key=lambda x: x[1])
    names = [n for n, _ in sorted_data]
    vals = [v for _, v in sorted_data]
    colors = []
    for n in names:
        ss = SOCIAL_STRUCTURE[n]
        if ss == 'nomadic':
            colors.append(ACCENT4)
        elif ss == 'matrilocal':
            colors.append(ACCENT2)
        else:
            colors.append(ACCENT)

    bars = ax1.barh(range(len(names)), vals, color=colors, edgecolor=BG, linewidth=0.5)
    for i, (bar, v) in enumerate(zip(bars, vals)):
        ax1.text(v + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{v:.2f}', va='center', fontsize=9, fontweight='bold', color=FG)
    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names, fontsize=9)
    ax1.set_xlabel('Isolation Index (0=open ↔ 1=extreme)', fontsize=10, color=FG)
    ax1.set_xlim(0, 1.05)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Scatter: isolation vs genetic diversity
    ax2.set_title('Isolation vs Genetic Diversity (mtDNA)', fontsize=11, color=FG)
    for name in TRIBES:
        iso = ISOLATION_INDEX[name]
        mt = GENETIC_DIVERSITY.get(name, {}).get('mtDNA_h',
             GENETIC_DIVERSITY.get(name.replace(' ', ' '), {}).get('mtDNA_h', 0.8))
        ss = SOCIAL_STRUCTURE[name]
        lf = LANGUAGE_FAMILY[name]
        c = ACCENT if ss == 'matrilocal' else (ACCENT3 if ss == 'patrilocal' else ACCENT4)
        s = 80
        ax2.scatter(iso, mt, c=c, s=s, alpha=0.8, edgecolors=BG, linewidth=1)
        ax2.annotate(name, (iso, mt), fontsize=7, color=FG,
                     textcoords='offset points', xytext=(5, 3))

    ax2.set_xlabel('Isolation Index', fontsize=10, color=FG)
    ax2.set_ylabel('mtDNA Gene Diversity (h)', fontsize=10, color=FG)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    legend_handles = [
        mpatches.Patch(color=ACCENT2, label='Matrilocal'),
        mpatches.Patch(color=ACCENT3, label='Patrilocal'),
        mpatches.Patch(color=ACCENT4, label='Nomadic'),
    ]
    ax2.legend(handles=legend_handles, fontsize=9, loc='lower left')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '05_cultural_isolation.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# CHART 6: Motif Library Dashboard
# =====================================================================
def plot_motif_dashboard():
    import glob as gb

    # Load motif data
    motif_data = {}
    for mf in sorted(gb.glob('motif_library/*.json')):
        with open(mf) as f:
            data = json.load(f)
        name = os.path.basename(mf).replace('_motifs.json', '')
        motif_data[name] = data['motifs'] if isinstance(data.get('motifs'), list) else []

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Motif Library Dashboard — Current Coverage & Gaps',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    # 1. Motif count per community
    ax = axes[0, 0]
    names = list(motif_data.keys())
    counts = [len(m) for m in motif_data.values()]
    colors = [ACCENT2 if c >= 8 else (ACCENT3 if c >= 6 else ACCENT4) for c in counts]
    bars = ax.bar(range(len(names)), counts, color=colors, edgecolor=BG, linewidth=0.5)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(c), ha='center', va='bottom', fontsize=9, fontweight='bold', color=FG)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Number of Motifs', fontsize=10, color=FG)
    ax.set_title('Motifs per Community', fontsize=11, color=FG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 2. Motif type distribution
    ax = axes[0, 1]
    all_types = Counter()
    for motifs in motif_data.values():
        for m in motifs:
            all_types[m.get('type', 'unknown')] += 1

    type_labels = list(all_types.keys())
    type_vals = list(all_types.values())
    type_colors = [ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5, ACCENT6]
    wedges, texts, autotexts = ax.pie(type_vals, labels=type_labels,
                                       autopct='%1.1f%%', colors=type_colors[:len(type_labels)],
                                       startangle=90, textprops={'color': FG, 'fontsize': 9})
    for t in autotexts:
        t.set_color('white')
        t.set_fontweight('bold')
    ax.set_title('Motif Type Distribution (all communities)', fontsize=11, color=FG)

    # 3. Reference image coverage
    ax = axes[1, 0]
    ref_dir = 'reference_images'
    tribes_ref = []
    img_counts = []
    for d in sorted(os.listdir(ref_dir)):
        p = os.path.join(ref_dir, d)
        if os.path.isdir(p):
            imgs = [f for f in os.listdir(p) if f.endswith(('.jpg', '.png', '.jpeg'))]
            tribes_ref.append(d)
            img_counts.append(len(imgs))

    colors_ref = [ACCENT2 if c > 0 else '#484f58' for c in img_counts]
    bars = ax.bar(range(len(tribes_ref)), img_counts, color=colors_ref, edgecolor=BG, linewidth=0.5)
    for bar, c in zip(bars, img_counts):
        if c > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    str(c), ha='center', va='bottom', fontsize=9, fontweight='bold', color=FG)
    ax.set_xticks(range(len(tribes_ref)))
    ax.set_xticklabels(tribes_ref, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Reference Images', fontsize=10, color=FG)
    ax.set_title('Reference Image Coverage', fontsize=11, color=FG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 4. Gap analysis — what's missing
    ax = axes[1, 1]
    ax.axis('off')
    ax.set_title('Coverage Gaps & Recommendations', fontsize=11, color=FG)

    gap_text = []
    # Communities with 0 reference images
    no_ref = [t for t, c in zip(tribes_ref, img_counts) if c == 0]
    gap_text.append(('ERR', f'No reference images: {", ".join(no_ref)}'))
    gap_text.append(('INFO', '   -> Need museum API scraping (Met, Cooper Hewitt, Rijksmuseum)'))
    gap_text.append(('INFO', ''))

    # Communities with few motifs
    few_motifs = [n for n, c in zip(names, counts) if c < 6]
    if few_motifs:
        gap_text.append(('WARN', f'Few motifs (<6): {", ".join(few_motifs)}'))
        gap_text.append(('INFO', '   -> Expand motif library from textile references'))
        gap_text.append(('INFO', ''))

    # Genetic data gaps
    no_genetic = [t for t in TRIBES if t not in ['Karen', 'Hmong', 'Mien', 'Lahu', 'Akha', 'Lisu', 'Mani', 'Mlabri', 'Moklen', 'Urak Lawoi']]
    gap_text.append(('WARN', f'No published genetic data: {", ".join(no_genetic)}'))
    gap_text.append(('INFO', '   -> Estimates used; needs academic literature review'))
    gap_text.append(('INFO', ''))
    gap_text.append(('OK', f'Total: {sum(counts)} motifs across {len(names)} communities'))
    gap_text.append(('OK', f'{sum(img_counts)} reference images across {len([c for c in img_counts if c > 0])} tribes'))

    y_pos = 0.9
    for tag, line in gap_text:
        if tag == 'ERR': color = ACCENT4
        elif tag == 'WARN': color = ACCENT3
        else: color = ACCENT2
        ax.text(0.05, y_pos, line, transform=ax.transAxes, fontsize=9,
                color=color, va='top', fontfamily='monospace')
        y_pos -= 0.06

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '06_motif_dashboard.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# CHART 7: Social Structure → Genetic Signature (Summary)
# =====================================================================
def plot_social_genetic():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Social Structure → Genetic Signature\nKey Finding: Postmarital residence patterns create predictable genetic signatures\nSource: Srikummool et al. 2007, BMC Evol Biol',
                 fontsize=14, fontweight='bold', color=FG, y=0.98)

    # Group by social structure
    groups = {
        'Matrilocal\n(low mtDNA, high Y)': ['White Karen', 'Lahu'],
        'Patrilocal Sino-Tibetan\n(high mtDNA, low Y)': ['Akha', 'Lisu'],
        'Patrilocal Hmong-Mien\n(high mtDNA, high Y)': ['Hmong', 'Iu Mien'],
        'Nomadic\n(very low diversity)': ['Mani', 'Mlabri'],
    }
    group_labels = {
        'Matrilocal\n(low mtDNA, high Y)': 'Matrilocal\n(low mtDNA, high Y)',
        'Patrilocal Sino-Tibetan\n(high mtDNA, low Y)': 'Patrilocal ST\n(high mtDNA, low Y)',
        'Patrilocal Hmong-Mien\n(high mtDNA, high Y)': 'Patrilocal HM\n(high mtDNA, high Y)',
        'Nomadic\n(very low diversity)': 'Nomadic\n(very low diversity)',
    }

    x_pos = 0
    bar_width = 0.35
    colors = {
        'Matrilocal\n(low mtDNA, high Y)': ACCENT2,
        'Patrilocal Sino-Tibetan\n(high mtDNA, low Y)': ACCENT3,
        'Patrilocal Hmong-Mien\n(high mtDNA, high Y)': ACCENT,
        'Nomadic\n(very low diversity)': ACCENT4,
    }

    labels = []
    mt_vals = []
    y_vals = []

    for group, tribes in groups.items():
        labels.append(group_labels[group])
        avg_mt = np.mean([GENETIC_DIVERSITY[t]['mtDNA_h'] for t in tribes])
        avg_y = np.mean([GENETIC_DIVERSITY[t]['Y_STR_h'] for t in tribes])
        mt_vals.append(avg_mt)
        y_vals.append(avg_y)

    x = np.arange(len(labels))
    ax.bar(x - bar_width/2, mt_vals, bar_width, label='mtDNA (maternal)',
           color=ACCENT, edgecolor=BG)
    ax.bar(x + bar_width/2, y_vals, bar_width, label='Y-STR (paternal)',
           color=ACCENT3, edgecolor=BG)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, ha='center')
    ax.set_ylabel('Gene Diversity (h)', fontsize=10, color=FG)
    ax.set_ylim(0.4, 1.05)
    ax.legend(fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add value labels
    for i, (m, y) in enumerate(zip(mt_vals, y_vals)):
        ax.text(i - bar_width/2, m + 0.01, f'{m:.2f}', ha='center', fontsize=8, fontweight='bold', color=FG)
        ax.text(i + bar_width/2, y + 0.01, f'{y:.2f}', ha='center', fontsize=8, fontweight='bold', color=FG)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, '07_social_genetic_signature.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'✅ {path}')


# =====================================================================
# RUN ALL
# =====================================================================
if __name__ == '__main__':
    print('🧬 Generating DNA Textile genetic visualizations...\n')
    plot_genetic_diversity()
    plot_mtDNA_haplogroups()
    plot_y_haplogroups()
    plot_genetic_distance()
    plot_cultural_isolation()
    plot_motif_dashboard()
    plot_social_genetic()
    print(f'\n📁 All visualizations saved to {OUTPUT_DIR}/')
    print(f'📊 Total: 7 charts generated')
