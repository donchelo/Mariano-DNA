"""
Motor de análisis genético principal
Cruza el genoma con la base de datos de SNPs importantes
"""

from typing import Dict, List, Optional, Tuple
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
    
    def _complement_allele(self, allele: str) -> str:
        """
        Convierte un alelo a su complemento en la hebra opuesta
        
        Args:
            allele: Alelo (A, C, G, T)
            
        Returns:
            Alelo complementario (A↔T, C↔G)
        """
        complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return complement_map.get(allele, allele)
    
    def _complement_genotype(self, genotype: str) -> str:
        """
        Convierte un genotipo completo a su complemento en la hebra opuesta
        
        Args:
            genotype: Genotipo (ej: "AA", "AG", "TT", "T")
            
        Returns:
            Genotipo complementario (ej: "TT", "TC", "AA", "A")
        """
        if not genotype:
            return genotype
        return ''.join(self._complement_allele(allele) for allele in genotype)
    
    def _normalize_genotype_for_comparison(self, genotype: str) -> str:
        """
        Normaliza un genotipo para comparación (ordena alelos y maneja hemocigosis)
        
        Args:
            genotype: Genotipo (ej: "AG", "GA", "T")
            
        Returns:
            Genotipo normalizado (ej: "AG", "TT")
        """
        if not genotype:
            return genotype
        
        # Manejar hemocigosis (ej: "T" -> "TT")
        if len(genotype) == 1:
            genotype = genotype * 2
            
        return ''.join(sorted(genotype))
    
    def _validate_genotype(self, genotype: Optional[str], snp_info: SNPInfo, 
                          genome_genotypes: Dict[str, str]) -> Tuple[bool, str, str]:
        """
        Valida si el genotipo del usuario indica riesgo real
        
        Args:
            genotype: Genotipo del usuario (ej: "AA", "AG", "GG")
            snp_info: Información del SNP desde la base de datos
            genome_genotypes: Diccionario con todos los genotipos del genoma
            
        Returns:
            Tupla (has_risk, risk_level, interpretation):
            - has_risk: True si hay riesgo, False si es normal
            - risk_level: 'alto', 'medio', 'bajo', 'normal', 'protector'
            - interpretation: Descripción del genotipo
        """
        if not genotype or not snp_info:
            return False, 'normal', 'Genotipo no disponible'
        
        # Normalizar genotipo (ordenar alelos para comparación y manejar hemocigosis)
        normalized_geno = self._normalize_genotype_for_comparison(genotype)
        
        # Si requiere combinación (ej: APOE necesita rs429358 + rs7412)
        if snp_info.requires_combination and snp_info.combination_snp:
            combo_genotype = genome_genotypes.get(snp_info.combination_snp)
            if not combo_genotype:
                return False, 'normal', 'Genotipo de combinación no disponible'
            
            # Lógica especial para APOE
            if snp_info.rsid == 'rs429358' and snp_info.combination_snp == 'rs7412':
                # rs429358: T = ε3, C = ε4
                # rs7412: C = ε3, T = ε2
                rs429358_geno = genotype
                rs7412_geno = combo_genotype
                
                # Determinar haplotipo
                if rs429358_geno == 'TT' and rs7412_geno == 'CC':
                    return False, 'normal', 'APOE ε3/ε3 (genotipo normal)'
                elif rs429358_geno == 'CT' and rs7412_geno == 'CC':
                    return True, 'medio', 'APOE ε3/ε4 (riesgo moderado de Alzheimer)'
                elif rs429358_geno == 'CC' and rs7412_geno == 'CC':
                    return True, 'alto', 'APOE ε4/ε4 (alto riesgo de Alzheimer)'
                elif rs429358_geno == 'TT' and rs7412_geno == 'CT':
                    return False, 'protector', 'APOE ε2/ε3 (protección contra Alzheimer)'
                elif rs429358_geno == 'CT' and rs7412_geno == 'CT':
                    return False, 'protector', 'APOE ε2/ε4 (protección parcial)'
                elif rs429358_geno == 'TT' and rs7412_geno == 'TT':
                    return False, 'protector', 'APOE ε2/ε2 (protección contra Alzheimer)'
                else:
                    return False, 'normal', f'APOE combinación no estándar ({rs429358_geno}/{rs7412_geno})'
            
            elif snp_info.rsid == 'rs7412' and snp_info.combination_snp == 'rs429358':
                # Ya procesado en rs429358, no duplicar
                return False, 'normal', 'Procesado en combinación con rs429358'
        
        # Validación estándar usando genotype_interpretation
        # Intentar primero con el genotipo original, luego con el complemento
        genotypes_to_try = [genotype, self._complement_genotype(genotype)]
        
        for test_genotype in genotypes_to_try:
            if snp_info.genotype_interpretation:
                interpretation = snp_info.genotype_interpretation.get(test_genotype)
                if interpretation:
                    # Determinar nivel de riesgo basado en la interpretación
                    interpretation_lower = interpretation.lower()
                    # Primero verificar si es normal o protector (tiene prioridad)
                    if 'normal' in interpretation_lower or 'función normal' in interpretation_lower or 'riesgo bajo' in interpretation_lower:
                        return False, 'normal', interpretation
                    elif 'protección' in interpretation_lower or 'protector' in interpretation_lower:
                        return False, 'protector', interpretation
                    # Luego verificar si hay riesgo
                    # Homocigoto con reducción significativa de actividad es riesgo alto
                    elif 'homocigoto' in interpretation_lower:
                        if 'mayor riesgo' in interpretation_lower or ('riesgo' in interpretation_lower and 'bajo' not in interpretation_lower):
                            return True, 'alto', interpretation
                        elif 'reducción' in interpretation_lower and ('70%' in interpretation_lower or '60%' in interpretation_lower or '50%' in interpretation_lower):
                            # Reducción significativa de actividad enzimática es riesgo alto
                            return True, 'alto', interpretation
                        elif 'riesgo' in interpretation_lower and 'bajo' not in interpretation_lower:
                            return True, 'alto', interpretation
                        else:
                            # Homocigoto sin indicador claro de riesgo, asumir medio
                            return True, 'medio', interpretation
                    elif 'heterocigoto' in interpretation_lower and ('riesgo' in interpretation_lower and 'bajo' not in interpretation_lower):
                        return True, 'medio', interpretation
                    elif 'riesgo' in interpretation_lower and 'bajo' not in interpretation_lower:
                        return True, 'medio', interpretation
                    else:
                        return False, 'bajo', interpretation
        
        # Fallback: validar usando risk_allele
        # Intentar con genotipo original y complemento
        for test_genotype in genotypes_to_try:
            if snp_info.risk_allele and snp_info.normal_allele:
                # Intentar con alelo de riesgo original
                risk_count = test_genotype.count(snp_info.risk_allele)
                if risk_count > 0:
                    if risk_count == 2:
                        return True, 'alto', f'Homocigoto para alelo de riesgo ({snp_info.risk_allele})'
                    elif risk_count == 1:
                        return True, 'medio', f'Heterocigoto portador de alelo de riesgo ({snp_info.risk_allele})'
                
                # Intentar con alelo de riesgo complementario
                complement_risk_allele = self._complement_allele(snp_info.risk_allele)
                risk_count = test_genotype.count(complement_risk_allele)
                if risk_count > 0:
                    if risk_count == 2:
                        return True, 'alto', f'Homocigoto para alelo de riesgo ({snp_info.risk_allele})'
                    elif risk_count == 1:
                        return True, 'medio', f'Heterocigoto portador de alelo de riesgo ({snp_info.risk_allele})'
        
        # Si no se encontró riesgo en ninguna hebra, es normal
        return False, 'normal', f'Genotipo normal (sin alelo de riesgo)'
        
        # Si no hay información de validación, asumir que hay riesgo (comportamiento anterior)
        # pero marcar como 'bajo' para ser conservador
        return True, 'bajo', 'Genotipo presente pero sin validación específica'
    
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
            
            # VALIDACIÓN DE GENOTIPO: Verificar si realmente hay riesgo
            has_risk, validated_risk_level, genotype_interpretation = self._validate_genotype(
                genotype, snp_info, genome_genotypes
            )
            
            # Verificar si está en reportes
            found_in_reports = rsid in report_rsids
            report_sources = []
            if found_in_reports and rsid in report_data:
                report_sources = [item['source'] for item in report_data[rsid]]
            
            # Obtener datos enriquecidos de Promethease si están disponibles
            promethease_info = promethease_data.get(rsid, {})
            promethease_repute = promethease_info.get('repute')
            
            # Determinar categoría e importancia
            category = snp_info.category if snp_info else 'salud'
            
            # IMPORTANTE: Considerar REPUTE de Promethease para determinar si es protector o de riesgo
            # El repute tiene alta prioridad, pero el genotipo validado puede sobrescribirlo si es más específico
            
            # Si repute es "Good", es protector (independientemente de magnitud)
            if promethease_repute == 'Good':
                # Es un hallazgo protector, no de riesgo
                # Sobrescribir has_risk y validated_risk_level solo si no hay validación de genotipo más específica
                if validated_risk_level not in ['normal', 'protector']:
                    validated_risk_level = 'protector'
                has_risk = False
            # Si repute es "Bad", es de riesgo (a menos que el genotipo validado sea normal/protector)
            elif promethease_repute == 'Bad':
                # Es de riesgo, pero verificar si el genotipo validado indica lo contrario
                if validated_risk_level not in ['normal', 'protector']:
                    # Confirmar que es de riesgo
                    has_risk = True
            
            # IMPORTANTE: La importancia debe reflejar el riesgo REAL del usuario
            # Si el genotipo es normal o protector, siempre debe ser "bajo" (🟢)
            if validated_risk_level == 'normal' or validated_risk_level == 'protector':
                importance = 'bajo'
            elif has_risk:
                # Si hay riesgo, usar la magnitud de Promethease si está disponible
                # o el nivel de riesgo validado
                if promethease_info.get('magnitude'):
                    magnitude = promethease_info.get('magnitude', 0)
                    # Ajustar importancia basada en magnitud, pero respetando el nivel de riesgo validado
                    if validated_risk_level == 'alto':
                        importance = 'alto'
                    elif validated_risk_level == 'medio':
                        # Si la magnitud es muy alta, puede subir a alto
                        if magnitude >= 3.5:
                            importance = 'alto'
                        else:
                            importance = 'medio'
                    else:
                        # Si la magnitud es alta, puede subir a medio o alto
                        if magnitude >= 3.5:
                            importance = 'alto'
                        elif magnitude >= 2.5:
                            importance = 'medio'
                        else:
                            importance = 'bajo'
                else:
                    # Usar el nivel de riesgo validado directamente
                    importance = validated_risk_level if validated_risk_level in ['alto', 'medio', 'bajo'] else 'medio'
            else:
                # Sin riesgo validado, usar magnitud de Promethease o bajo por defecto
                if promethease_info.get('magnitude'):
                    magnitude = promethease_info.get('magnitude', 0)
                    if magnitude >= 3.5:
                        importance = 'alto'
                    elif magnitude >= 2.5:
                        importance = 'medio'
                    else:
                        importance = 'bajo'
                else:
                    importance = 'bajo'
            
            # Construir descripción combinada
            description = snp_info.description if snp_info else ''
            if promethease_info.get('summary'):
                # Si es protector (repute Good), agregar prefijo para claridad
                if promethease_repute == 'Good':
                    summary = promethease_info['summary']
                    # Verificar si el summary ya indica protección
                    if 'reduced risk' not in summary.lower() and 'protection' not in summary.lower() and 'lower risk' not in summary.lower():
                        summary = f"Protección: {summary}"
                    if description:
                        description = f"{summary}. {description}"
                    else:
                        description = summary
                else:
                    if description:
                        description = f"{promethease_info['summary']}. {description}"
                    else:
                        description = promethease_info['summary']
            
            # Construir implicaciones (añadir interpretación del genotipo)
            implications = snp_info.implications if snp_info else ''
            if genotype_interpretation and genotype_interpretation != 'Genotipo no disponible':
                if implications:
                    implications = f"{genotype_interpretation}. {implications}"
                else:
                    implications = genotype_interpretation
            if promethease_info.get('description') and not implications:
                implications = promethease_info['description'][:500]  # Limitar longitud
            
            # Si es protector por repute, asegurar que las implicaciones reflejen protección
            if promethease_repute == 'Good' and validated_risk_level == 'protector':
                if 'protección' not in implications.lower() and 'reduced risk' not in implications.lower() and 'lower risk' not in implications.lower():
                    if implications:
                        implications = f"Protección: {implications}"
                    else:
                        implications = "Este genotipo confiere protección según Promethease"
            
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
            
            # FILTRAR: Solo incluir si realmente hay riesgo o si es de interés especial
            # Excepciones: SNPs de rasgos (siempre mostrar) o si está en reportes externos
            should_include = False
            
            if category == 'rasgos':
                # Siempre mostrar rasgos heredados
                should_include = found_in_genome or found_in_reports
            elif has_risk:
                # Incluir si hay riesgo validado
                should_include = True
            elif found_in_reports:
                # Incluir si está en reportes externos (puede tener información adicional)
                should_include = True
            elif promethease_repute == 'Good':
                # Incluir SNPs protectores (repute Good) - información valiosa
                should_include = True
                if not found_in_reports:
                    found_in_reports = True
                    report_sources = ['promethease']
            elif promethease_info.get('magnitude', 0) >= 3.0:
                # Incluir SNPs de alta magnitud en Promethease
                should_include = True
                found_in_reports = True
                report_sources = ['promethease']
            elif validated_risk_level == 'protector':
                # Incluir genotipos protectores (información útil)
                should_include = True
            # Si no hay riesgo y no es de interés especial, NO incluir
            
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

