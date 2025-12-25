"""
Motor de análisis genético principal
Cruza el genoma con la base de datos de SNPs importantes
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .parser import GenomeParser
from .snp_database import SNPDatabase, SNPInfo
from .pdf_extractor import ReportExtractor


@dataclass
class Finding:
    """Hallazgo genético identificado"""
    rsid: str
    genotype: Optional[str]
    snp_info: Optional[SNPInfo]
    category: str
    importance: str
    description: str
    implications: str
    found_in_genome: bool
    found_in_reports: bool
    report_sources: List[str]
    snpedia_url: str
    related_conditions: List[str]
    # Campos adicionales de Promethease
    magnitude: Optional[float] = None
    max_magnitude: Optional[float] = None
    repute: Optional[str] = None
    summary: Optional[str] = None
    frequency: Optional[str] = None
    chromosome: Optional[str] = None
    position: Optional[int] = None
    genes: List[str] = None
    publications: Optional[int] = None
    gmaf: Optional[float] = None
    topics: List[str] = None
    medical_conditions_from_reports: List[str] = None
    
    def __post_init__(self):
        """Inicializar listas si son None"""
        if self.genes is None:
            self.genes = []
        if self.topics is None:
            self.topics = []
        if self.medical_conditions_from_reports is None:
            self.medical_conditions_from_reports = []


class GeneticAnalyzer:
    """Motor de análisis genético que cruza genoma con base de datos"""
    
    def __init__(self, genome_parser: GenomeParser, snp_database: SNPDatabase, 
                 report_extractor: Optional[ReportExtractor] = None):
        """
        Inicializa el analizador
        
        Args:
            genome_parser: Parser del genoma raw
            snp_database: Base de datos de SNPs importantes
            report_extractor: Extractor de reportes existentes (opcional)
        """
        self.genome_parser = genome_parser
        self.snp_database = snp_database
        self.report_extractor = report_extractor
        self.findings: List[Finding] = []
    
    def analyze(self) -> List[Finding]:
        """
        Ejecuta el análisis completo
        
        Returns:
            Lista de hallazgos encontrados
        """
        print("\n[ANALISIS] Iniciando analisis genetico...")
        
        # Obtener todos los rsIDs de la base de datos
        important_rsids = self.snp_database.get_all_rsids()
        print(f"  Buscando {len(important_rsids)} SNPs importantes en el genoma...")
        
        # Obtener genotipos del genoma
        genome_genotypes = self.genome_parser.get_snps(important_rsids)
        
        # Obtener rsIDs de reportes existentes (si hay extractor)
        report_rsids = set()
        report_data = {}
        promethease_data = {}  # Datos enriquecidos de Promethease
        
        if self.report_extractor:
            report_rsids = self.report_extractor.get_rsids_from_all_sources()
            all_findings = self.report_extractor.get_all_findings()
            
            for source, findings in all_findings.items():
                for finding in findings:
                    if 'rsid' in finding:
                        rsid = finding['rsid']
                        if rsid not in report_data:
                            report_data[rsid] = []
                        report_data[rsid].append({
                            'source': source,
                            'data': finding
                        })
                        
                        # Si es de Promethease, guardar datos enriquecidos
                        if source == 'promethease' and 'magnitude' in finding:
                            promethease_data[rsid] = finding
        
        # Analizar cada SNP importante
        findings = []
        found_count = 0
        
        for rsid in important_rsids:
            genotype = genome_genotypes.get(rsid)
            snp_info = self.snp_database.get_snp(rsid)
            
            if not snp_info:
                continue
            
            # Verificar si está en el genoma
            found_in_genome = genotype is not None
            
            # Verificar si está en reportes
            found_in_reports = rsid in report_rsids
            report_sources = []
            if found_in_reports and rsid in report_data:
                report_sources = [item['source'] for item in report_data[rsid]]
            
            # Obtener datos enriquecidos de Promethease si están disponibles
            promethease_info = promethease_data.get(rsid, {})
            
            # Determinar categoría e importancia
            # Si hay datos de Promethease, usar su información para enriquecer
            category = snp_info.category if snp_info else 'salud'
            importance = snp_info.importance if snp_info else 'medio'
            
            # Ajustar importancia basada en magnitude de Promethease
            if promethease_info.get('magnitude'):
                magnitude = promethease_info.get('magnitude', 0)
                if magnitude >= 3.5:
                    importance = 'alto'
                elif magnitude >= 2.5:
                    importance = 'medio'
                else:
                    importance = 'bajo'
            
            # Construir descripción combinada
            description = snp_info.description if snp_info else ''
            if promethease_info.get('summary'):
                if description:
                    description = f"{promethease_info['summary']}. {description}"
                else:
                    description = promethease_info['summary']
            
            # Construir implicaciones
            implications = snp_info.implications if snp_info else ''
            if promethease_info.get('description') and not implications:
                implications = promethease_info['description'][:500]  # Limitar longitud
            
            # Obtener genes (priorizar Promethease si tiene más información)
            genes_list = promethease_info.get('genes', [])
            if not genes_list and snp_info:
                genes_list = [snp_info.gene] if snp_info.gene else []
            
            # Condiciones médicas combinadas
            related_conditions = snp_info.related_conditions.copy() if snp_info else []
            medical_conditions_from_reports = promethease_info.get('medical_conditions', [])
            # Evitar duplicados
            for cond in medical_conditions_from_reports:
                if cond not in related_conditions:
                    related_conditions.append(cond)
            
            # Solo incluir si está en el genoma o en reportes
            # O si tiene magnitud alta en Promethease (aunque no esté en la BD local)
            should_include = found_in_genome or found_in_reports
            if not should_include and promethease_info.get('magnitude', 0) >= 3.0:
                # Incluir SNPs de alta magnitud aunque no estén en la BD local
                should_include = True
                found_in_reports = True
                report_sources = ['promethease']
            
            if should_include:
                finding = Finding(
                    rsid=rsid,
                    genotype=genotype,
                    snp_info=snp_info,
                    category=category,
                    importance=importance,
                    description=description,
                    implications=implications,
                    found_in_genome=found_in_genome,
                    found_in_reports=found_in_reports,
                    report_sources=report_sources,
                    snpedia_url=snp_info.snpedia_url if snp_info else f'https://www.snpedia.com/index.php/{rsid}',
                    related_conditions=related_conditions,
                    # Campos de Promethease
                    magnitude=promethease_info.get('magnitude'),
                    max_magnitude=promethease_info.get('max_magnitude'),
                    repute=promethease_info.get('repute'),
                    summary=promethease_info.get('summary'),
                    frequency=promethease_info.get('frequency'),
                    chromosome=promethease_info.get('chromosome'),
                    position=promethease_info.get('position'),
                    genes=genes_list,
                    publications=promethease_info.get('publications'),
                    gmaf=promethease_info.get('gmaf'),
                    topics=promethease_info.get('topics', []),
                    medical_conditions_from_reports=medical_conditions_from_reports
                )
                findings.append(finding)
                found_count += 1
        
        print(f"[OK] Encontrados {found_count} hallazgos importantes")
        
        self.findings = findings
        return findings
    
    def get_findings_by_category(self, category: str) -> List[Finding]:
        """Obtiene hallazgos por categoría"""
        return [f for f in self.findings if f.category == category]
    
    def get_findings_by_importance(self, importance: str) -> List[Finding]:
        """Obtiene hallazgos por nivel de importancia"""
        return [f for f in self.findings if f.importance == importance]
    
    def get_statistics(self) -> Dict:
        """Retorna estadísticas del análisis"""
        stats = {
            'total_findings': len(self.findings),
            'by_category': {},
            'by_importance': {},
            'found_in_genome': 0,
            'found_in_reports_only': 0
        }
        
        for finding in self.findings:
            # Por categoría
            cat = finding.category
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
            
            # Por importancia
            imp = finding.importance
            stats['by_importance'][imp] = stats['by_importance'].get(imp, 0) + 1
            
            # En genoma vs solo en reportes
            if finding.found_in_genome:
                stats['found_in_genome'] += 1
            elif finding.found_in_reports:
                stats['found_in_reports_only'] += 1
        
        return stats

