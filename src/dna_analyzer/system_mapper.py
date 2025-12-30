"""
Mapeador de SNPs a sistemas biológicos
Agrupa hallazgos genéticos por sistemas para visualización de riesgo
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .analyzer import Finding


@dataclass
class SystemRisk:
    """Riesgo calculado para un sistema biológico"""
    system_name: str
    total_snps: int
    risk_snps: int
    risk_score: float  # 0-1, normalizado
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    findings: List[Finding]


class SystemMapper:
    """Mapea hallazgos genéticos a sistemas biológicos"""
    
    # Mapeo de categorías y genes a sistemas biológicos
    SYSTEM_MAPPING = {
        'Metilación': {
            'categories': ['nutrigenomica'],
            'genes': ['MTHFR', 'MTR', 'MTRR', 'CBS', 'COMT', 'MAOA', 'MAOB', 'FUT2'],
            'keywords': ['metilación', 'metil', 'folato', 'homocisteína', 'b12', 'b6', 'tmg', 'betaine']
        },
        'Cardiovascular': {
            'categories': ['salud'],
            'genes': ['APOE', 'LDLR', 'PCSK9', 'CETP', 'LPA', 'FADS1', 'FADS2'],
            'keywords': ['colesterol', 'ldl', 'hdl', 'triglicéridos', 'cardiovascular', 'corazón', 'aterosclerosis']
        },
        'Desintoxicación': {
            'categories': ['salud', 'nutrigenomica'],
            'genes': ['GST', 'CYP1A2', 'CYP2D6', 'CYP2C19', 'CYP2C9', 'CYP3A4', 'NAT2', 'SOD2', 'GPX1'],
            'keywords': ['detox', 'desintoxicación', 'glutatión', 'citocromo', 'cyp', 'gst', 'sod', 'antioxidante']
        },
        'Inmunidad': {
            'categories': ['salud'],
            'genes': ['HLA', 'IL6', 'TNF', 'IFNG', 'VDR'],
            'keywords': ['inmunidad', 'inmune', 'hla', 'interleucina', 'infección', 'inflamación']
        },
        'Salud Ósea': {
            'categories': ['salud', 'nutrigenomica'],
            'genes': ['VDR', 'COL1A1', 'ESR1', 'LRP5'],
            'keywords': ['ósea', 'hueso', 'osteoporosis', 'calcio', 'vitamina d', 'vdr']
        },
        'Metabolismo': {
            'categories': ['salud', 'nutrigenomica'],
            'genes': ['MTNR1B', 'TCF7L2', 'CDKAL1', 'FTO', 'MC4R', 'PPARG', 'IRS1', 'IRS2'],
            'keywords': ['diabetes', 'glucosa', 'insulina', 'metabolismo', 'glicemia', 'hba1c', 'obesidad']
        },
        'Tiroides': {
            'categories': ['salud', 'nutrigenomica'],
            'genes': ['DIO1', 'DIO2', 'TSHR', 'THRB'],
            'keywords': ['tiroides', 'tsh', 't3', 't4', 'hipotiroidismo', 'hipertiroidismo']
        },
        'Longevidad': {
            'categories': ['longevidad'],
            'genes': ['FOXO3', 'APOE', 'SIRT1', 'IGF1'],
            'keywords': ['longevidad', 'envejecimiento', 'telómero', 'sirt']
        }
    }
    
    # Ponderación de importancia para cálculo de riesgo
    IMPORTANCE_WEIGHTS = {
        'alto': 3.0,
        'medio': 2.0,
        'bajo': 1.0
    }
    
    def __init__(self):
        """Inicializa el mapeador de sistemas"""
        self.system_risks: Dict[str, SystemRisk] = {}
    
    def map_findings_to_systems(self, findings: List[Finding]) -> Dict[str, SystemRisk]:
        """
        Mapea hallazgos genéticos a sistemas biológicos
        
        Args:
            findings: Lista de hallazgos genéticos
            
        Returns:
            Diccionario con sistemas y sus riesgos calculados
        """
        # Inicializar sistemas
        for system_name in self.SYSTEM_MAPPING.keys():
            self.system_risks[system_name] = SystemRisk(
                system_name=system_name,
                total_snps=0,
                risk_snps=0,
                risk_score=0.0,
                high_risk_count=0,
                medium_risk_count=0,
                low_risk_count=0,
                findings=[]
            )
        
        # Mapear cada hallazgo a sistemas
        for finding in findings:
            assigned_systems = self._assign_to_systems(finding)
            for system_name in assigned_systems:
                if system_name in self.system_risks:
                    self.system_risks[system_name].findings.append(finding)
                    self.system_risks[system_name].total_snps += 1
                    
                    # Contar solo si hay riesgo (no genotipos normales/protectores)
                    if finding.importance in ['alto', 'medio', 'bajo']:
                        self.system_risks[system_name].risk_snps += 1
                        
                        if finding.importance == 'alto':
                            self.system_risks[system_name].high_risk_count += 1
                        elif finding.importance == 'medio':
                            self.system_risks[system_name].medium_risk_count += 1
                        elif finding.importance == 'bajo':
                            self.system_risks[system_name].low_risk_count += 1
        
        # Calcular scores de riesgo para cada sistema
        for system_name, system_risk in self.system_risks.items():
            system_risk.risk_score = self._calculate_risk_score(system_risk)
        
        return self.system_risks
    
    def _assign_to_systems(self, finding: Finding) -> List[str]:
        """
        Asigna un hallazgo a uno o más sistemas biológicos
        
        Args:
            finding: Hallazgo genético
            
        Returns:
            Lista de nombres de sistemas asignados
        """
        assigned = []
        
        # Obtener información del hallazgo
        category = finding.category.lower() if finding.category else ''
        gene = finding.snp_info.gene if finding.snp_info else ''
        description = finding.description.lower() if finding.description else ''
        implications = finding.implications.lower() if finding.implications else ''
        related_conditions = [c.lower() for c in finding.related_conditions] if finding.related_conditions else []
        
        # Texto combinado para búsqueda de keywords
        combined_text = f"{description} {implications} {' '.join(related_conditions)}".lower()
        
        # Verificar cada sistema
        for system_name, criteria in self.SYSTEM_MAPPING.items():
            # Verificar categoría
            if category in [c.lower() for c in criteria['categories']]:
                assigned.append(system_name)
                continue
            
            # Verificar genes
            if gene and any(gene.upper().startswith(g.upper()) for g in criteria['genes']):
                assigned.append(system_name)
                continue
            
            # Verificar keywords en descripción/implicaciones
            if any(keyword in combined_text for keyword in criteria['keywords']):
                assigned.append(system_name)
                continue
        
        # Si no se asignó a ningún sistema, asignar a "Otros" (no incluido en el mapeo principal)
        if not assigned:
            # No agregamos "Otros" al mapeo principal, solo retornamos lista vacía
            # Los sistemas sin asignación no aparecerán en el mapa de calor
            pass
        
        return assigned
    
    def _calculate_risk_score(self, system_risk: SystemRisk) -> float:
        """
        Calcula el score de riesgo normalizado para un sistema (0-1)
        
        Args:
            system_risk: Información de riesgo del sistema
            
        Returns:
            Score normalizado entre 0 y 1
        """
        if system_risk.total_snps == 0:
            return 0.0
        
        # Calcular score ponderado
        weighted_score = (
            system_risk.high_risk_count * self.IMPORTANCE_WEIGHTS['alto'] +
            system_risk.medium_risk_count * self.IMPORTANCE_WEIGHTS['medio'] +
            system_risk.low_risk_count * self.IMPORTANCE_WEIGHTS['bajo']
        )
        
        # Normalizar: dividir por el máximo posible (todos alto riesgo)
        max_possible = system_risk.total_snps * self.IMPORTANCE_WEIGHTS['alto']
        
        if max_possible == 0:
            return 0.0
        
        # Normalizar a 0-1
        normalized = weighted_score / max_possible
        
        return min(1.0, max(0.0, normalized))
    
    def get_system_risk_dataframe(self) -> 'pd.DataFrame':
        """
        Retorna un DataFrame con los datos de riesgo por sistema
        
        Returns:
            DataFrame con columnas: Sistema, Total SNPs, SNPs de Riesgo, Score, Alto, Medio, Bajo
        """
        import pandas as pd
        
        data = []
        for system_name, system_risk in self.system_risks.items():
            if system_risk.total_snps > 0:  # Solo incluir sistemas con SNPs
                data.append({
                    'Sistema': system_name,
                    'Total SNPs': system_risk.total_snps,
                    'SNPs de Riesgo': system_risk.risk_snps,
                    'Score de Riesgo': round(system_risk.risk_score, 3),
                    'Alto Riesgo': system_risk.high_risk_count,
                    'Riesgo Medio': system_risk.medium_risk_count,
                    'Riesgo Bajo': system_risk.low_risk_count
                })
        
        return pd.DataFrame(data)

