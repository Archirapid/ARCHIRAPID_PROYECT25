"""
ARCHIRAPID - Matching Engine
Motor de compatibilidad finca-proyecto con scoring inteligente
"""
import pandas as pd
from typing import Dict, List, Tuple


class MatchingEngine:
    """
    Motor de matching que evalúa compatibilidad entre fincas y proyectos arquitectónicos
    """
    
    def __init__(self):
        self.EDIFICABILITY_MAX = 0.33  # 33% máximo edificable
        
    def calculate_compatibility(self, plot_data: Dict, project_data: Dict) -> Tuple[bool, float, Dict]:
        """
        Calcula compatibilidad entre una finca y un proyecto
        
        Args:
            plot_data: dict con datos de la finca (m2, price, type, province)
            project_data: dict con datos del proyecto (area_m2, style, price)
            
        Returns:
            (is_compatible: bool, score: float 0-100, details: dict)
        """
        details = {
            'checks': [],
            'warnings': [],
            'optimizations': []
        }
        
        plot_m2 = float(plot_data.get('m2', 0))
        project_m2 = float(project_data.get('area_m2', 0))
        
        # CHECK 1: Superficie mínima
        min_plot_m2 = project_m2 / self.EDIFICABILITY_MAX  # m² necesarios para 33%
        
        if plot_m2 < min_plot_m2:
            details['checks'].append({
                'name': 'Superficie mínima',
                'passed': False,
                'message': f'Finca demasiado pequeña. Necesitas mínimo {min_plot_m2:.0f} m²'
            })
            return False, 0.0, details
        else:
            details['checks'].append({
                'name': 'Superficie mínima',
                'passed': True,
                'message': f'✓ Finca suficientemente grande ({plot_m2:.0f} m² > {min_plot_m2:.0f} m²)'
            })
        
        # CHECK 2: Edificabilidad
        edificability_ratio = project_m2 / plot_m2
        
        if edificability_ratio > self.EDIFICABILITY_MAX:
            details['checks'].append({
                'name': 'Edificabilidad',
                'passed': False,
                'message': f'Supera el 33% edificable ({edificability_ratio*100:.1f}%)'
            })
            return False, 0.0, details
        else:
            details['checks'].append({
                'name': 'Edificabilidad',
                'passed': True,
                'message': f'✓ Cumple normativa ({edificability_ratio*100:.1f}% < 33%)'
            })
        
        # SCORING (0-100)
        score = 0.0
        
        # Factor 1: Aprovechamiento óptimo (40 puntos)
        # Ideal: usar entre 20-30% del terreno
        optimal_ratio = 0.25  # 25% ideal
        ratio_diff = abs(edificability_ratio - optimal_ratio)
        
        if ratio_diff < 0.05:  # Dentro de ±5%
            score += 40
            details['optimizations'].append('⭐ Aprovechamiento óptimo del terreno')
        elif ratio_diff < 0.10:  # Dentro de ±10%
            score += 30
            details['optimizations'].append('✓ Buen aprovechamiento del terreno')
        else:
            score += 20
            if edificability_ratio < optimal_ratio:
                details['warnings'].append('⚠️ Terreno infrautilizado - Podrías construir más')
            else:
                details['warnings'].append('⚠️ Construcción grande - Poco espacio libre')
        
        # Factor 2: Proporción precio proyecto/finca (30 puntos)
        plot_price = float(plot_data.get('price', 0))
        project_price = float(project_data.get('price', 0))
        
        if plot_price > 0 and project_price > 0:
            price_ratio = project_price / plot_price
            
            # Ideal: proyecto cuesta entre 0.5x y 2x el precio de la finca
            if 0.5 <= price_ratio <= 2.0:
                score += 30
                details['optimizations'].append('💰 Relación precio proyecto/finca equilibrada')
            elif 0.3 <= price_ratio <= 3.0:
                score += 20
                details['warnings'].append('⚠️ Considera el coste total (finca + proyecto)')
            else:
                score += 10
                if price_ratio < 0.3:
                    details['warnings'].append('⚠️ Proyecto muy económico vs finca - Verifica calidades')
                else:
                    details['warnings'].append('⚠️ Proyecto muy costoso vs finca - Alto presupuesto total')
        else:
            score += 15  # Puntuación neutral si no hay precios
        
        # Factor 3: Compatibilidad tipológica (20 puntos)
        plot_type = str(plot_data.get('type', '')).lower()
        project_style = str(project_data.get('style', '')).lower()
        
        # Matriz de compatibilidad tipo-estilo
        compatibility_matrix = {
            'urbana': ['moderno', 'minimalista', 'industrial'],
            'playa': ['moderno', 'minimalista'],
            'montaña': ['rústico', 'tradicional'],
            'campo': ['rústico', 'tradicional']
        }
        
        matched = False
        for ptype, styles in compatibility_matrix.items():
            if ptype in plot_type:
                if any(style in project_style for style in styles):
                    score += 20
                    details['optimizations'].append(f'🎨 Estilo {project_data.get("style")} ideal para {plot_data.get("type")}')
                    matched = True
                    break
        
        if not matched:
            score += 10
            details['warnings'].append('ℹ️ Verifica que el estilo encaje con el entorno')
        
        # Factor 4: Espacio libre restante (10 puntos)
        free_space_m2 = plot_m2 - project_m2
        free_space_percent = (free_space_m2 / plot_m2) * 100
        
        if free_space_percent >= 70:
            score += 10
            details['optimizations'].append(f'🌳 Amplio espacio libre ({free_space_percent:.0f}%) para jardín/piscina')
        elif free_space_percent >= 60:
            score += 8
            details['optimizations'].append(f'✓ Buen espacio libre ({free_space_percent:.0f}%)')
        else:
            score += 5
            details['warnings'].append(f'⚠️ Espacio libre limitado ({free_space_percent:.0f}%)')
        
        return True, round(score, 1), details
    
    
    def find_compatible_projects(self, plot_data: Dict, all_projects: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """
        Encuentra los N proyectos más compatibles con una finca
        
        Args:
            plot_data: dict con datos de la finca
            all_projects: DataFrame con todos los proyectos
            top_n: número máximo de proyectos a retornar
            
        Returns:
            Lista de dicts con project data + compatibility score + details
        """
        if all_projects.empty:
            return []
        
        compatible = []
        
        for idx, project in all_projects.iterrows():
            project_dict = project.to_dict()
            
            is_compatible, score, details = self.calculate_compatibility(plot_data, project_dict)
            
            if is_compatible:
                compatible.append({
                    'project': project_dict,
                    'score': score,
                    'details': details,
                    'rank': None  # Se asignará después de ordenar
                })
        
        # Ordenar por score descendente
        compatible.sort(key=lambda x: x['score'], reverse=True)
        
        # Asignar ranking
        for i, item in enumerate(compatible[:top_n], 1):
            item['rank'] = i
        
        return compatible[:top_n]
    
    
    def get_score_badge(self, score: float) -> str:
        """
        Retorna badge HTML según score
        
        Args:
            score: 0-100
            
        Returns:
            str con emoji y texto
        """
        if score >= 80:
            return "🏆 EXCELENTE"
        elif score >= 60:
            return "⭐ MUY BUENO"
        elif score >= 40:
            return "✓ BUENO"
        else:
            return "⚠️ ACEPTABLE"
    
    
    def get_score_color(self, score: float) -> str:
        """
        Retorna color hex según score para UI
        
        Args:
            score: 0-100
            
        Returns:
            str color hex
        """
        if score >= 80:
            return "#28a745"  # Verde
        elif score >= 60:
            return "#17a2b8"  # Azul
        elif score >= 40:
            return "#ffc107"  # Amarillo
        else:
            return "#fd7e14"  # Naranja
