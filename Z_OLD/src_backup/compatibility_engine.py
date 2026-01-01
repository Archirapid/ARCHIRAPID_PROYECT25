"""Compatibility Engine for matching projects to plots.

This module provides a transparent, explainable scoring system (0-100)
for how well an architectural project fits a given plot.

Criteria & Weights (max 100):
- Parcel size fit (0-50)
- Built area efficiency (0-30)
- Program density (rooms per 100m² built) (0-10)
- Type synergy & basic style alignment (0-10)

The engine is intentionally simple (rule-based) for MVP demonstration.
Future extensions can plug into these hooks without breaking API.
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import pandas as pd

# ----------------------------- Core Scoring ----------------------------- #

def compute_project_score(plot: Dict, project: Dict) -> Tuple[int, List[str]]:
    """Compute compatibility score and list of human-readable reasons.

    Inputs:
        plot: dict row from plots table
        project: dict row from projects table
    Returns:
        (score:int 0..100, reasons: List[str])
    Safety:
        All numeric conversions are guarded; missing fields reduce weight
        but never raise errors.
    """
    reasons: List[str] = []
    score = 0

    plot_m2 = safe_int(plot.get('m2'))
    proj_min = safe_int(project.get('m2_parcela_minima'))
    proj_max = safe_int(project.get('m2_parcela_maxima'))
    proj_built = safe_int(project.get('m2_construidos'))
    proj_rooms = safe_int(project.get('habitaciones'))
    plot_type = (plot.get('type') or '').lower()
    proj_type = (project.get('tipo_proyecto') or '').lower()
    style = (project.get('style') or '').lower()

    # 1. Parcel size fit (0-50)
    if proj_min and proj_max and plot_m2:
        if proj_min <= plot_m2 <= proj_max:
            score += 50
            reasons.append(f"Tamaño de parcela dentro del rango ideal ({proj_min}-{proj_max} m²)")
        elif plot_m2 < proj_min:
            # proportion penalty
            diff_pct = 1 - (plot_m2 / proj_min) if proj_min else 1
            partial = max(15, int(35 * (1 - min(diff_pct, 0.8))))  # floor
            score += partial
            reasons.append(f"Parcela algo pequeña (requiere ajustes). Min ideal {proj_min} m²")
        else:  # plot larger than max
            diff_pct = (plot_m2 - proj_max) / proj_max if proj_max else 1
            partial = max(20, int(40 * (1 - min(diff_pct, 1))))
            score += partial
            reasons.append(f"Parcela más grande de lo ideal (posible ampliación). Máx ideal {proj_max} m²")
    else:
        reasons.append("Proyecto sin rango de parcela definido (compatibilidad limitada)")
        score += 25  # neutral baseline when project missing data

    # 2. Built area efficiency (0-30)
    if plot_m2 and proj_built:
        ratio = proj_built / plot_m2  # built vs available
        if 0.15 <= ratio <= 0.40:
            score += 30
            reasons.append(f"Uso eficiente de la parcela (ratio construido {ratio:.2f})")
        elif ratio < 0.15:
            score += 18
            reasons.append(f"Edificación muy pequeña respecto a parcela (ratio {ratio:.2f})")
        else:  # ratio > 0.40
            score += 15
            reasons.append(f"Edificación densa (ratio {ratio:.2f}); revisar retranqueos y ocupación")
    else:
        score += 12
        reasons.append("Datos incompletos para evaluar eficiencia (se requieren m² construidos)")

    # 3. Program density - rooms per 100 m² built (0-10)
    if proj_built and proj_rooms:
        density = proj_rooms / (proj_built / 100)
        if 0.5 <= density <= 1.2:
            score += 10
            reasons.append(f"Densidad habitacional equilibrada ({density:.2f} hab / 100m²)")
        elif density < 0.5:
            score += 6
            reasons.append(f"Densidad baja ({density:.2f}); posible infrautilización")
        else:
            score += 5
            reasons.append(f"Densidad alta ({density:.2f}); puede requerir optimización")
    else:
        score += 4
        reasons.append("Sin datos completos para calcular densidad (habitaciones / m² construidos)")

    # 4. Type & style synergy (0-10)
    # Basic heuristics for MVP
    synergy = 0
    if plot_type:
        if not proj_type:
            synergy += 3
            reasons.append("Tipo de proyecto no especificado — asignar tras revisión")
        else:
            if plot_type == 'urban' and 'vivienda' in proj_type:
                synergy += 8
                reasons.append("Tipología vivienda adecuada para parcela urbana")
            elif plot_type == 'industrial' and 'nave' in proj_type:
                synergy += 8
                reasons.append("Proyecto industrial apropiado para parcela industrial")
            else:
                synergy += 5
                reasons.append("Tipología potencialmente compatible (revisar normativa específica)")

    if style in {'mediterraneo','moderno','minimalista'}:
        synergy += 2
        reasons.append("Estilo demandado por mercado (valor añadido)")

    synergy = min(synergy, 10)
    score += synergy

    final = min(int(score), 100)
    return final, reasons

# ----------------------------- Ranking Interface ----------------------------- #

def rank_projects_for_plot(plot: Dict, projects_df: pd.DataFrame) -> pd.DataFrame:
    """Return projects ranked with score & explanation columns.
    Keeps original columns; adds 'score' and 'explanation'.
    """
    if projects_df is None or projects_df.empty:
        return pd.DataFrame(columns=['id','title','score','explanation'])

    rows = []
    for _, proj in projects_df.iterrows():
        score, reasons = compute_project_score(plot, proj.to_dict())
        rows.append({**proj.to_dict(), 'score': score, 'explanation': '\n'.join(f'• {r}' for r in reasons)})

    ranked = pd.DataFrame(rows).sort_values(by='score', ascending=False).reset_index(drop=True)
    return ranked

# ----------------------------- Safe helpers ----------------------------- #

def safe_int(val) -> int:
    try:
        if val is None:
            return 0
        return int(val)
    except Exception:
        return 0

__all__ = [
    'compute_project_score',
    'rank_projects_for_plot'
]
