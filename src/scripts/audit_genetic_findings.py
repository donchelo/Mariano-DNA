"""
Script de auditoría de hallazgos genéticos
Verifica consistencia, precisión y cobertura de los hallazgos genéticos
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Agregar el directorio src al path para importar dna_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.snp_database import SNPDatabase
from dna_analyzer.pdf_extractor import ReportExtractor
from dna_analyzer.analyzer import GeneticAnalyzer

console = Console()


class GeneticFindingsAuditor:
    """Auditor de hallazgos genéticos"""
    
    def __init__(self, base_dir: Path):
        """
        Inicializa el auditor
        
        Args:
            base_dir: Directorio base del proyecto
        """
        self.base_dir = base_dir
        self.genome_parser = None
        self.snp_database = None
        self.report_extractor = None
        self.analyzer = None
        
        # Datos cargados
        self.raw_genome_genotypes: Dict[str, str] = {}
        self.promethease_data: Dict[str, Dict] = {}
        self.curated_snps: Set[str] = set()
        
        # Resultados de auditoría
        self.genotype_mismatches: List[Dict] = []
        self.missing_in_genome: List[Dict] = []
        self.missing_in_curated_db: List[Dict] = []
        self.risk_validation_issues: List[Dict] = []
        self.high_magnitude_snps: List[Dict] = []
        
    def _complement_allele(self, allele: str) -> str:
        """Convierte un alelo a su complemento"""
        complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return complement_map.get(allele, allele)
    
    def _complement_genotype(self, genotype: str) -> str:
        """Convierte un genotipo a su complemento"""
        if not genotype or len(genotype) < 2:
            return genotype
        return ''.join(self._complement_allele(allele) for allele in genotype)
    
    def _normalize_genotype(self, genotype: str) -> str:
        """Normaliza genotipo para comparación (ordena alelos y maneja hemocigosis)"""
        if not genotype:
            return genotype
            
        # Limpiar separadores comunes
        clean_genotype = genotype.replace(';', '').replace(',', '').replace('/', '').strip()
        
        # Manejar hemocigosis (ej: "T" -> "TT")
        if len(clean_genotype) == 1:
            clean_genotype = clean_genotype * 2
            
        return ''.join(sorted(clean_genotype))
    
    def _genotypes_match(self, geno1: Optional[str], geno2: Optional[str]) -> bool:
        """
        Verifica si dos genotipos coinciden (considerando hebras opuestas y hemocigosis)
        
        Args:
            geno1: Primer genotipo
            geno2: Segundo genotipo
            
        Returns:
            True si coinciden (directamente o por complemento)
        """
        if not geno1 or not geno2:
            return False
        
        # Normalizar ambos genotipos
        norm1 = self._normalize_genotype(geno1)
        norm2 = self._normalize_genotype(geno2)
        
        # Comparar directamente
        if norm1 == norm2:
            return True
        
        # Comparar con complemento de uno de ellos
        complement1 = self._normalize_genotype(self._complement_genotype(norm1))
        if complement1 == norm2:
            return True
            
        return False
    
    def load_raw_genome(self) -> bool:
        """Carga el genoma raw como fuente de verdad"""
        console.print("[bold cyan]Cargando genoma raw...[/bold cyan]")
        
        genome_dir = self.base_dir / "data" / "raw" / "genome"
        if not genome_dir.exists():
            console.print("[red]ERROR: Directorio de genoma no encontrado[/red]")
            return False
        
        # Buscar archivo de genoma
        txt_files = list(genome_dir.rglob("*.txt"))
        genome_file = None
        
        for txt_file in txt_files:
            if 'copia' not in txt_file.name.lower():
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        first_lines = ''.join(f.readlines()[:10])
                        if 'rsid' in first_lines.lower() or '23andme' in first_lines.lower():
                            genome_file = txt_file
                            break
                except:
                    continue
        
        if not genome_file:
            console.print("[red]ERROR: No se encontró archivo de genoma válido[/red]")
            return False
        
        console.print(f"  Archivo: {genome_file.name}")
        
        try:
            self.genome_parser = GenomeParser(str(genome_file))
            self.genome_parser.parse()
            self.raw_genome_genotypes = {
                rsid: data.get('genotype') if isinstance(data, dict) else data
                for rsid, data in self.genome_parser.genome_index.items()
            }
            console.print(f"[green][OK] Genoma cargado: {len(self.raw_genome_genotypes):,} SNPs[/green]\n")
            return True
        except Exception as e:
            console.print(f"[red]ERROR cargando genoma: {e}[/red]")
            return False
    
    def load_promethease_data(self) -> bool:
        """Carga datos de Promethease desde JSON"""
        console.print("[bold cyan]Cargando datos de Promethease...[/bold cyan]")
        
        promethease_json = self.base_dir / "data" / "processed" / "hallazgos_geneticos.json"
        
        if not promethease_json.exists():
            console.print("[yellow][WARN] Archivo de Promethease no encontrado[/yellow]\n")
            return False
        
        try:
            with open(promethease_json, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            for entry in entries:
                record_id = entry.get('record_id', '')
                if record_id.startswith('rs'):
                    rsid = record_id
                    self.promethease_data[rsid] = {
                        'genotype': entry.get('genotype'),
                        'magnitude': entry.get('magnitude'),
                        'repute': entry.get('repute'),
                        'summary': entry.get('summary', ''),
                        'description': entry.get('description', ''),
                        'frequency': entry.get('frequency'),
                        'genes': entry.get('genes', []),
                        'medical_conditions': entry.get('medical_conditions', []),
                        'publications': entry.get('publications')
                    }
            
            console.print(f"[green][OK] Promethease cargado: {len(self.promethease_data)} SNPs[/green]\n")
            return True
        except Exception as e:
            console.print(f"[red]ERROR cargando Promethease: {e}[/red]")
            return False
    
    def load_curated_database(self) -> bool:
        """Carga la base de datos curada de SNPs"""
        console.print("[bold cyan]Cargando base de datos curada...[/bold cyan]")
        
        try:
            self.snp_database = SNPDatabase()
            self.curated_snps = set(self.snp_database.get_all_rsids())
            console.print(f"[green][OK] Base de datos curada: {len(self.curated_snps)} SNPs[/green]\n")
            return True
        except Exception as e:
            console.print(f"[red]ERROR cargando base de datos: {e}[/red]")
            return False
    
    def audit_genotype_consistency(self):
        """Audita consistencia de genotipos entre fuentes"""
        console.print("[bold cyan]Auditando consistencia de genotipos...[/bold cyan]")
        
        # Comparar Promethease vs Genoma Raw
        mismatches = []
        
        for rsid, prom_data in self.promethease_data.items():
            prom_genotype = prom_data.get('genotype')
            raw_genotype = self.raw_genome_genotypes.get(rsid)
            
            if prom_genotype and raw_genotype:
                # Normalizar genotipos de Promethease (pueden venir como "A;G")
                prom_genotype_clean = prom_genotype.replace(';', '').replace(',', '')
                
                if not self._genotypes_match(prom_genotype_clean, raw_genotype):
                    mismatches.append({
                        'rsid': rsid,
                        'source1': 'Promethease',
                        'genotype1': prom_genotype_clean,
                        'source2': 'Genoma Raw',
                        'genotype2': raw_genotype,
                        'magnitude': prom_data.get('magnitude'),
                        'genes': prom_data.get('genes', [])
                    })
        
        self.genotype_mismatches = mismatches
        
        if mismatches:
            console.print(f"[yellow][WARN] Encontradas {len(mismatches)} discrepancias de genotipo[/yellow]")
        else:
            console.print("[green][OK] Todos los genotipos son consistentes[/green]")
        console.print("")
    
    def audit_missing_in_genome(self):
        """Identifica SNPs en reportes que no están en el genoma raw"""
        console.print("[bold cyan]Identificando SNPs faltantes en genoma...[/bold cyan]")
        
        missing = []
        
        for rsid, prom_data in self.promethease_data.items():
            if rsid not in self.raw_genome_genotypes:
                missing.append({
                    'rsid': rsid,
                    'magnitude': prom_data.get('magnitude'),
                    'repute': prom_data.get('repute'),
                    'summary': prom_data.get('summary', '')[:100],
                    'genes': prom_data.get('genes', []),
                    'source': 'Promethease'
                })
        
        self.missing_in_genome = sorted(
            missing, 
            key=lambda x: x.get('magnitude', 0) or 0, 
            reverse=True
        )
        
        console.print(f"[yellow][WARN] {len(missing)} SNPs en Promethease no están en genoma raw[/yellow]\n")
    
    def audit_missing_in_curated_db(self):
        """Identifica SNPs de alta importancia que no están en la base de datos curada"""
        console.print("[bold cyan]Identificando SNPs faltantes en base de datos curada...[/bold cyan]")
        
        missing = []
        
        for rsid, prom_data in self.promethease_data.items():
            if rsid not in self.curated_snps:
                magnitude = prom_data.get('magnitude', 0) or 0
                # Solo considerar SNPs con magnitud >= 3.0 o repute "Bad"
                if magnitude >= 3.0 or prom_data.get('repute') == 'Bad':
                    missing.append({
                        'rsid': rsid,
                        'magnitude': magnitude,
                        'repute': prom_data.get('repute'),
                        'summary': prom_data.get('summary', '')[:200],
                        'description': prom_data.get('description', '')[:300],
                        'genes': prom_data.get('genes', []),
                        'medical_conditions': prom_data.get('medical_conditions', []),
                        'frequency': prom_data.get('frequency'),
                        'publications': prom_data.get('publications'),
                        'in_genome': rsid in self.raw_genome_genotypes
                    })
        
        self.missing_in_curated_db = sorted(
            missing,
            key=lambda x: x.get('magnitude', 0) or 0,
            reverse=True
        )
        
        console.print(f"[yellow][WARN] {len(missing)} SNPs de alta importancia no están en base de datos curada[/yellow]\n")
    
    def audit_high_magnitude_snps(self):
        """Identifica SNPs de alta magnitud en Promethease"""
        console.print("[bold cyan]Identificando SNPs de alta magnitud...[/bold cyan]")
        
        high_mag = []
        
        for rsid, prom_data in self.promethease_data.items():
            magnitude = prom_data.get('magnitude', 0) or 0
            if magnitude >= 3.5:
                high_mag.append({
                    'rsid': rsid,
                    'magnitude': magnitude,
                    'repute': prom_data.get('repute'),
                    'summary': prom_data.get('summary', '')[:200],
                    'genes': prom_data.get('genes', []),
                    'in_curated_db': rsid in self.curated_snps,
                    'in_genome': rsid in self.raw_genome_genotypes
                })
        
        self.high_magnitude_snps = sorted(
            high_mag,
            key=lambda x: x.get('magnitude', 0) or 0,
            reverse=True
        )
        
        console.print(f"[green][OK] Encontrados {len(high_mag)} SNPs con magnitud >= 3.5[/green]\n")
    
    def audit_risk_validation(self):
        """Valida que la lógica de riesgo sea correcta"""
        console.print("[bold cyan]Validando lógica de riesgo...[/bold cyan]")
        
        if not self.genome_parser or not self.snp_database:
            console.print("[yellow][WARN] No se puede validar riesgo sin genoma y base de datos[/yellow]\n")
            return
        
        # Cargar extractor de reportes para análisis completo
        self.report_extractor = ReportExtractor()
        promethease_json = self.base_dir / "data" / "processed" / "hallazgos_geneticos.json"
        if promethease_json.exists():
            self.report_extractor.extract_file(str(promethease_json))
        
        self.analyzer = GeneticAnalyzer(self.genome_parser, self.snp_database, self.report_extractor)
        findings = self.analyzer.analyze()
        
        issues = []
        
        for finding in findings:
            # Verificar si la importancia asignada es consistente con la magnitud
            if finding.magnitude and finding.magnitude >= 3.5:
                # Si es un hallazgo protector o normal, la importancia BAJA es aceptable
                # pero si es de riesgo, debería ser ALTA
                is_protective = finding.snp_info and any(kw in finding.implications.lower() for kw in ['protector', 'protección', 'normal', 'bajo riesgo'])
                
                if finding.importance == 'bajo' and not is_protective:
                    issues.append({
                        'rsid': finding.rsid,
                        'issue': 'Alta magnitud pero importancia baja',
                        'magnitude': finding.magnitude,
                        'assigned_importance': finding.importance,
                        'expected_importance': 'alto',
                        'genotype': finding.genotype
                    })
            
            # Verificar si genotipo normal tiene importancia incorrecta
            if finding.genotype:
                snp_info = self.snp_database.get_snp(finding.rsid)
                if snp_info and snp_info.genotype_interpretation:
                    interpretation = snp_info.genotype_interpretation.get(finding.genotype, '')
                    if 'normal' in interpretation.lower() and finding.importance != 'bajo':
                        issues.append({
                            'rsid': finding.rsid,
                            'issue': 'Genotipo normal con importancia incorrecta',
                            'genotype': finding.genotype,
                            'interpretation': interpretation,
                            'assigned_importance': finding.importance,
                            'expected_importance': 'bajo'
                        })
        
        self.risk_validation_issues = issues
        
        if issues:
            console.print(f"[yellow][WARN] Encontrados {len(issues)} problemas de validación de riesgo[/yellow]")
        else:
            console.print("[green][OK] Validación de riesgo correcta[/green]")
        console.print("")
    
    def generate_audit_report(self) -> str:
        """Genera el reporte de auditoría en Markdown"""
        report_lines = []
        
        report_lines.append("# Reporte de Auditoría de Hallazgos Genéticos")
        report_lines.append(f"**Generado el:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")
        
        # Resumen ejecutivo
        report_lines.append("## Resumen Ejecutivo\n")
        report_lines.append(f"- **Total SNPs en genoma raw:** {len(self.raw_genome_genotypes):,}")
        report_lines.append(f"- **Total SNPs en Promethease:** {len(self.promethease_data)}")
        report_lines.append(f"- **Total SNPs en base de datos curada:** {len(self.curated_snps)}")
        report_lines.append(f"- **Discrepancias de genotipo:** {len(self.genotype_mismatches)}")
        report_lines.append(f"- **SNPs faltantes en genoma:** {len(self.missing_in_genome)}")
        report_lines.append(f"- **SNPs faltantes en BD curada:** {len(self.missing_in_curated_db)}")
        report_lines.append(f"- **Problemas de validación de riesgo:** {len(self.risk_validation_issues)}")
        report_lines.append(f"- **SNPs de alta magnitud (≥3.5):** {len(self.high_magnitude_snps)}\n")
        report_lines.append("---\n")
        
        # Discrepancias de genotipo
        if self.genotype_mismatches:
            report_lines.append("## Discrepancias de Genotipo\n")
            report_lines.append("SNPs donde los genotipos no coinciden entre fuentes:\n")
            
            for mismatch in self.genotype_mismatches[:20]:  # Limitar a 20
                report_lines.append(f"### {mismatch['rsid']}")
                report_lines.append(f"- **Promethease:** `{mismatch['genotype1']}`")
                report_lines.append(f"- **Genoma Raw:** `{mismatch['genotype2']}`")
                if mismatch.get('magnitude'):
                    report_lines.append(f"- **Magnitud:** {mismatch['magnitude']}")
                if mismatch.get('genes'):
                    report_lines.append(f"- **Genes:** {', '.join(mismatch['genes'])}")
                report_lines.append("")
            
            if len(self.genotype_mismatches) > 20:
                report_lines.append(f"*... y {len(self.genotype_mismatches) - 20} más*\n")
            report_lines.append("---\n")
        else:
            report_lines.append("## Consistencia de Genotipos\n")
            report_lines.append("Todos los genotipos son consistentes entre fuentes.\n")
            report_lines.append("---\n")
        
        # SNPs faltantes en genoma
        if self.missing_in_genome:
            report_lines.append("## SNPs Faltantes en Genoma Raw\n")
            report_lines.append("SNPs presentes en Promethease pero no en el genoma raw:\n")
            
            for missing in self.missing_in_genome[:30]:  # Top 30
                report_lines.append(f"### {missing['rsid']}")
                if missing.get('magnitude'):
                    report_lines.append(f"- **Magnitud:** {missing['magnitude']}")
                if missing.get('repute'):
                    report_lines.append(f"- **Repute:** {missing['repute']}")
                if missing.get('summary'):
                    report_lines.append(f"- **Resumen:** {missing['summary']}")
                if missing.get('genes'):
                    report_lines.append(f"- **Genes:** {', '.join(missing['genes'])}")
                report_lines.append("")
            
            if len(self.missing_in_genome) > 30:
                report_lines.append(f"*... y {len(self.missing_in_genome) - 30} más*\n")
            report_lines.append("---\n")
        
        # SNPs faltantes en BD curada
        if self.missing_in_curated_db:
            report_lines.append("## SNPs Faltantes en Base de Datos Curada\n")
            report_lines.append("SNPs de alta importancia que deberían estar en `snps.json`:\n")
            
            for missing in self.missing_in_curated_db[:20]:  # Top 20
                report_lines.append(f"### {missing['rsid']}")
                report_lines.append(f"- **Magnitud:** {missing.get('magnitude', 'N/A')}")
                report_lines.append(f"- **Repute:** {missing.get('repute', 'N/A')}")
                if missing.get('summary'):
                    report_lines.append(f"- **Resumen:** {missing['summary']}")
                if missing.get('genes'):
                    report_lines.append(f"- **Genes:** {', '.join(missing['genes'])}")
                if missing.get('medical_conditions'):
                    report_lines.append(f"- **Condiciones:** {', '.join(missing['medical_conditions'][:5])}")
                report_lines.append(f"- **En genoma:** {'Sí' if missing.get('in_genome') else 'No'}")
                report_lines.append("")
            
            if len(self.missing_in_curated_db) > 20:
                report_lines.append(f"*... y {len(self.missing_in_curated_db) - 20} más*\n")
            report_lines.append("---\n")
        
        # Problemas de validación de riesgo
        if self.risk_validation_issues:
            report_lines.append("## Problemas de Validación de Riesgo\n")
            
            for issue in self.risk_validation_issues:
                report_lines.append(f"### {issue['rsid']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append(f"- **Importancia asignada:** {issue['assigned_importance']}")
                report_lines.append(f"- **Importancia esperada:** {issue.get('expected_importance', 'N/A')}")
                if issue.get('genotype'):
                    report_lines.append(f"- **Genotipo:** {issue['genotype']}")
                report_lines.append("")
            
            report_lines.append("---\n")
        
        # SNPs de alta magnitud
        if self.high_magnitude_snps:
            report_lines.append("## SNPs de Alta Magnitud (>=3.5)\n")
            report_lines.append("SNPs con mayor impacto según Promethease:\n")
            
            for snp in self.high_magnitude_snps[:15]:  # Top 15
                report_lines.append(f"### {snp['rsid']}")
                report_lines.append(f"- **Magnitud:** {snp['magnitude']}")
                report_lines.append(f"- **Repute:** {snp.get('repute', 'N/A')}")
                if snp.get('summary'):
                    report_lines.append(f"- **Resumen:** {snp['summary']}")
                if snp.get('genes'):
                    report_lines.append(f"- **Genes:** {', '.join(snp['genes'])}")
                report_lines.append(f"- **En BD curada:** {'Sí' if snp.get('in_curated_db') else 'No'}")
                report_lines.append(f"- **En genoma:** {'Sí' if snp.get('in_genome') else 'No'}")
                report_lines.append("")
            
            if len(self.high_magnitude_snps) > 15:
                report_lines.append(f"*... y {len(self.high_magnitude_snps) - 15} más*\n")
            report_lines.append("---\n")
        
        # Recomendaciones
        report_lines.append("## Recomendaciones\n")
        
        if self.genotype_mismatches:
            report_lines.append("1. **Revisar discrepancias de genotipo:** Verificar orientación de hebra y formato de genotipos.")
        
        if self.missing_in_curated_db:
            report_lines.append(f"2. **Agregar SNPs faltantes:** Considerar agregar los {len(self.missing_in_curated_db)} SNPs de alta importancia a `snps.json`.")
        
        if self.risk_validation_issues:
            report_lines.append("3. **Corregir validación de riesgo:** Revisar la lógica de asignación de importancia en `analyzer.py`.")
        
        if not self.genotype_mismatches and not self.risk_validation_issues:
            report_lines.append("**Sistema funcionando correctamente:** No se encontraron problemas críticos.")
        
        report_lines.append("\n---\n")
        report_lines.append("**Fin del Reporte de Auditoría**")
        
        return '\n'.join(report_lines)
    
    def run_full_audit(self) -> bool:
        """Ejecuta la auditoría completa"""
        console.print("\n[bold blue]Auditoría de Hallazgos Genéticos[/bold blue]\n")
        
        # Cargar datos
        if not self.load_raw_genome():
            return False
        if not self.load_promethease_data():
            return False
        if not self.load_curated_database():
            return False
        
        # Ejecutar auditorías
        self.audit_genotype_consistency()
        self.audit_missing_in_genome()
        self.audit_missing_in_curated_db()
        self.audit_high_magnitude_snps()
        self.audit_risk_validation()
        
        return True


def main():
    """Función principal"""
    base_dir = Path(__file__).parent.parent.parent
    
    auditor = GeneticFindingsAuditor(base_dir)
    
    if not auditor.run_full_audit():
        console.print("[bold red]ERROR: No se pudo completar la auditoría[/bold red]")
        sys.exit(1)
    
    # Generar reporte
    console.print("[bold cyan]Generando reporte de auditoría...[/bold cyan]")
    report_content = auditor.generate_audit_report()
    
    # Guardar reporte
    output_file = base_dir / "outputs" / "analisis" / "auditoria_hallazgos.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    console.print(f"[green][OK] Reporte guardado: {output_file}[/green]\n")
    
    # Mostrar resumen
    console.print("[bold]Resumen de Auditoría:[/bold]")
    console.print(f"  - Discrepancias de genotipo: {len(auditor.genotype_mismatches)}")
    console.print(f"  - SNPs faltantes en genoma: {len(auditor.missing_in_genome)}")
    console.print(f"  - SNPs faltantes en BD curada: {len(auditor.missing_in_curated_db)}")
    console.print(f"  - Problemas de validación: {len(auditor.risk_validation_issues)}")
    console.print(f"  - SNPs de alta magnitud: {len(auditor.high_magnitude_snps)}")
    console.print("")


if __name__ == "__main__":
    main()

