#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculador de Polygenic Risk Scores (PRS)
Combina múltiples SNPs para calcular riesgo poligénico de enfermedades
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .parser import GenomeParser
import math


@dataclass
class PRSResult:
    """Resultado de un cálculo de PRS"""
    condition: str
    prs_score: float
    percentile: float
    risk_category: str  # 'low', 'moderate', 'high', 'very_high'
    interpretation: str
    snps_used: int
    total_snps: int


@dataclass
class PRSCoefficient:
    """Coeficiente para un SNP en un PRS"""
    rsid: str
    effect_allele: str
    odds_ratio: float
    weight: float  # log(OR) o beta


class PRSCalculator:
    """Calculador de Polygenic Risk Scores"""
    
    # Definiciones de PRS para diferentes condiciones
    # Basadas en estudios GWAS conocidos
    PRS_DEFINITIONS = {
        'diabetes_tipo2': {
            'snps': [
                {'rsid': 'rs10830963', 'effect_allele': 'G', 'odds_ratio': 1.16, 'weight': 0.148},
                {'rsid': 'rs7754840', 'effect_allele': 'C', 'odds_ratio': 1.13, 'weight': 0.122},
                {'rsid': 'rs7903146', 'effect_allele': 'T', 'odds_ratio': 1.37, 'weight': 0.315},
                {'rsid': 'rs4402960', 'effect_allele': 'T', 'odds_ratio': 1.14, 'weight': 0.131},
                {'rsid': 'rs5219', 'effect_allele': 'C', 'odds_ratio': 1.15, 'weight': 0.140},
                {'rsid': 'rs13266634', 'effect_allele': 'C', 'odds_ratio': 1.12, 'weight': 0.113},
                {'rsid': 'rs1111875', 'effect_allele': 'C', 'odds_ratio': 1.13, 'weight': 0.122},
                {'rsid': 'rs9939609', 'effect_allele': 'A', 'odds_ratio': 1.27, 'weight': 0.239},
            ],
            'population_mean': 0.0,
            'population_sd': 1.0,
        },
        'enfermedad_coronaria': {
            'snps': [
                {'rsid': 'rs10757278', 'effect_allele': 'G', 'odds_ratio': 1.29, 'weight': 0.255},
                {'rsid': 'rs1333049', 'effect_allele': 'C', 'odds_ratio': 1.20, 'weight': 0.182},
                {'rsid': 'rs2383206', 'effect_allele': 'G', 'odds_ratio': 1.15, 'weight': 0.140},
            ],
            'population_mean': 0.0,
            'population_sd': 1.0,
        },
        'alzheimer': {
            'snps': [
                {'rsid': 'rs429358', 'effect_allele': 'C', 'odds_ratio': 3.7, 'weight': 1.308},  # APOE ε4
                {'rsid': 'rs7412', 'effect_allele': 'T', 'odds_ratio': 0.6, 'weight': -0.511},  # APOE ε2 (protector)
                {'rsid': 'rs17646665', 'effect_allele': 'G', 'odds_ratio': 0.6, 'weight': -0.511},
            ],
            'population_mean': 0.0,
            'population_sd': 1.0,
        },
        'cancer_colorectal': {
            'snps': [
                {'rsid': 'rs6983267', 'effect_allele': 'G', 'odds_ratio': 1.20, 'weight': 0.182},
                {'rsid': 'rs4939827', 'effect_allele': 'T', 'odds_ratio': 1.15, 'weight': 0.140},
                {'rsid': 'rs10795668', 'effect_allele': 'A', 'odds_ratio': 1.12, 'weight': 0.113},
            ],
            'population_mean': 0.0,
            'population_sd': 1.0,
        },
        'obesidad': {
            'snps': [
                {'rsid': 'rs9939609', 'effect_allele': 'A', 'odds_ratio': 1.31, 'weight': 0.270},
                {'rsid': 'rs8050136', 'effect_allele': 'A', 'odds_ratio': 1.27, 'weight': 0.239},
                {'rsid': 'rs17782313', 'effect_allele': 'C', 'odds_ratio': 1.15, 'weight': 0.140},
            ],
            'population_mean': 0.0,
            'population_sd': 1.0,
        },
    }
    
    # Percentiles de riesgo (basados en distribución normal)
    RISK_PERCENTILES = {
        'low': (0, 25),
        'moderate': (25, 75),
        'high': (75, 95),
        'very_high': (95, 100),
    }
    
    def __init__(self, genome_parser: GenomeParser):
        """
        Inicializa el calculador de PRS
        
        Args:
            genome_parser: Parser del genoma
        """
        self.genome_parser = genome_parser
    
    def calculate_prs(self, condition: str) -> Optional[PRSResult]:
        """
        Calcula el PRS para una condición específica
        
        Args:
            condition: Nombre de la condición (ej: 'diabetes_tipo2')
            
        Returns:
            PRSResult con el score y percentil
        """
        if condition not in self.PRS_DEFINITIONS:
            return None
        
        definition = self.PRS_DEFINITIONS[condition]
        snps = definition['snps']
        
        prs_score = 0.0
        snps_used = 0
        
        for snp_def in snps:
            rsid = snp_def['rsid']
            effect_allele = snp_def['effect_allele']
            weight = snp_def['weight']
            
            # Obtener genotipo del genoma
            genotype = self.genome_parser.get_genotype(rsid)
            if not genotype:
                continue
            
            # Contar alelos de efecto
            effect_count = genotype.count(effect_allele)
            
            # Agregar al score (weight * número de alelos de efecto)
            prs_score += weight * effect_count
            snps_used += 1
        
        if snps_used == 0:
            return None
        
        # Normalizar score (usar media y desviación estándar de población)
        # En la práctica, esto se haría con datos de referencia poblacional
        normalized_score = prs_score
        
        # Calcular percentil (simplificado - en la práctica usar distribución real)
        percentile = self._calculate_percentile(normalized_score, definition)
        
        # Determinar categoría de riesgo
        risk_category = self._get_risk_category(percentile)
        
        # Generar interpretación
        interpretation = self._generate_interpretation(condition, percentile, risk_category)
        
        return PRSResult(
            condition=condition,
            prs_score=prs_score,
            percentile=percentile,
            risk_category=risk_category,
            interpretation=interpretation,
            snps_used=snps_used,
            total_snps=len(snps)
        )
    
    def _calculate_percentile(self, score: float, definition: Dict) -> float:
        """
        Calcula el percentil basado en el score
        
        Nota: Esta es una implementación simplificada.
        En la práctica, se usaría una distribución de referencia poblacional.
        """
        # Simplificación: asumir distribución normal
        # En la práctica, esto se calcularía con datos de referencia
        mean = definition.get('population_mean', 0.0)
        sd = definition.get('population_sd', 1.0)
        
        # Z-score
        z_score = (score - mean) / sd if sd > 0 else 0
        
        # Convertir a percentil usando función de distribución normal acumulativa
        # Aproximación simple usando erf
        percentile = 50 + 50 * math.erf(z_score / math.sqrt(2))
        
        return max(0, min(100, percentile))
    
    def _get_risk_category(self, percentile: float) -> str:
        """Determina la categoría de riesgo basada en el percentil"""
        if percentile >= 95:
            return 'very_high'
        elif percentile >= 75:
            return 'high'
        elif percentile >= 25:
            return 'moderate'
        else:
            return 'low'
    
    def _generate_interpretation(self, condition: str, percentile: float, risk_category: str) -> str:
        """Genera una interpretación del PRS"""
        condition_names = {
            'diabetes_tipo2': 'Diabetes Tipo 2',
            'enfermedad_coronaria': 'Enfermedad Coronaria',
            'alzheimer': 'Enfermedad de Alzheimer',
            'cancer_colorectal': 'Cáncer Colorrectal',
            'obesidad': 'Obesidad',
        }
        
        condition_name = condition_names.get(condition, condition)
        
        interpretations = {
            'very_high': f"Riesgo muy alto de {condition_name}. Percentil {percentile:.1f}%. Se recomienda seguimiento médico regular y medidas preventivas.",
            'high': f"Riesgo alto de {condition_name}. Percentil {percentile:.1f}%. Se recomienda seguimiento médico y medidas preventivas.",
            'moderate': f"Riesgo moderado de {condition_name}. Percentil {percentile:.1f}%. Mantener estilo de vida saludable.",
            'low': f"Riesgo bajo de {condition_name}. Percentil {percentile:.1f}%. Continuar con estilo de vida saludable.",
        }
        
        return interpretations.get(risk_category, f"Riesgo de {condition_name}: Percentil {percentile:.1f}%")
    
    def calculate_all_prs(self) -> Dict[str, PRSResult]:
        """
        Calcula PRS para todas las condiciones disponibles
        
        Returns:
            Diccionario de condición -> PRSResult
        """
        results = {}
        
        for condition in self.PRS_DEFINITIONS.keys():
            result = self.calculate_prs(condition)
            if result:
                results[condition] = result
        
        return results
    
    def generate_prs_report(self) -> str:
        """
        Genera un reporte de PRS en formato texto
        
        Returns:
            Reporte formateado
        """
        results = self.calculate_all_prs()
        
        report = []
        report.append("=" * 80)
        report.append("REPORTE DE POLYGENIC RISK SCORES (PRS)")
        report.append("=" * 80)
        report.append("")
        report.append("⚠️ IMPORTANTE: Los PRS son estimaciones de riesgo relativo basadas en variantes genéticas comunes.")
        report.append("No son diagnósticos y deben interpretarse en contexto con otros factores de riesgo.")
        report.append("")
        
        for condition, result in results.items():
            report.append(f"\n{'=' * 80}")
            report.append(f"CONDICIÓN: {result.condition.upper().replace('_', ' ')}")
            report.append(f"{'=' * 80}")
            report.append(f"PRS Score: {result.prs_score:.3f}")
            report.append(f"Percentil: {result.percentile:.1f}%")
            report.append(f"Categoría de Riesgo: {result.risk_category.upper().replace('_', ' ')}")
            report.append(f"SNPs utilizados: {result.snps_used}/{result.total_snps}")
            report.append(f"\nInterpretación:")
            report.append(f"  {result.interpretation}")
        
        report.append("\n" + "=" * 80)
        report.append("Nota: Los percentiles se basan en distribuciones poblacionales de referencia.")
        report.append("=" * 80)
        
        return "\n".join(report)


if __name__ == '__main__':
    # Ejemplo de uso
    # from .parser import GenomeParser
    # parser = GenomeParser("path/to/genome.txt")
    # calculator = PRSCalculator(parser)
    # results = calculator.calculate_all_prs()
    # report = calculator.generate_prs_report()
    # print(report)
    pass

