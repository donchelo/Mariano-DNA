from typing import Dict, List, Optional
import os
import json
from src.dna_analyzer.analyzer import GeneticAnalyzer, Finding
from src.dna_analyzer.parser import GenomeParser
from src.dna_analyzer.snp_database import SNPDatabase
from src.dna_analyzer.pdf_extractor import ReportExtractor
from .state import AgentState

class GenomicsAgent:
    """
    Agente especializado en análisis de genómica.
    Utiliza el motor de análisis existente para identificar variantes críticas.
    """
    
    def __init__(self, db_path: str = None):
        self.snp_db = SNPDatabase()
        
    def analyze(self, state: AgentState) -> Dict:
        print("[GenomicsAgent] Analizando datos genómicos...")
        
        dna_path = state.get("dna_file_path")
        
        # Si no hay path pero hay hallazgos previos, podemos cargarlos
        if not dna_path:
            # Intentar cargar hallazgos procesados si existen
            processed_path = "data/processed/hallazgos_geneticos.json"
            if os.path.exists(processed_path):
                with open(processed_path, 'r', encoding='utf-8') as f:
                    findings_data = json.load(f)
                return {
                    "genomic_findings": findings_data,
                    "next_step": "biomarkers"
                }
            return {"errors": ["No se proporcionaron datos de ADN ni hallazgos previos"]}
        
        # Ejecutar el análisis completo si tenemos el archivo raw
        parser = GenomeParser(dna_path)
        parser.parse()
        
        # Opcional: Extraer datos de reportes existentes para enriquecer
        report_extractor = None
        reportes_dir = "data/raw/reportes_proveedores"
        if os.path.exists(reportes_dir):
            report_extractor = ReportExtractor(reportes_dir)
            report_extractor.extract_all()
        
        analyzer = GeneticAnalyzer(parser, self.snp_db, report_extractor)
        findings = analyzer.analyze()
        
        # Convertir hallazgos a formato serializable
        serialized_findings = []
        for f in findings:
            finding_dict = {
                "rsid": f.rsid,
                "genotype": f.genotype,
                "category": f.category,
                "importance": f.importance,
                "description": f.description,
                "implications": f.implications,
                "gene": f.genes[0] if f.genes else "N/A",
                "magnitude": f.magnitude,
                "repute": f.repute
            }
            serialized_findings.append(finding_dict)
            
        return {
            "genomic_findings": serialized_findings,
            "next_step": "biomarkers"
        }
