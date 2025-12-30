"""
Script de auditoría de genotipos del dashboard
Compara genotipos mostrados en el dashboard con el genoma raw
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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


class GenotypeAuditor:
    """Auditor de genotipos del dashboard"""
    
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
        
        # Resultados de auditoría
        self.genotype_mismatches: List[Dict] = []
        self.missing_genotypes: List[Dict] = []
        self.special_cases_issues: List[Dict] = []
        self.normalization_issues: List[Dict] = []
        
    def _complement_allele(self, allele: str) -> str:
        """Convierte un alelo a su complemento"""
        complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return complement_map.get(allele, allele)
    
    def _complement_genotype(self, genotype: str) -> str:
        """Convierte un genotipo a su complemento"""
        if not genotype:
            return genotype
        return ''.join(self._complement_allele(allele) for allele in genotype)
    
    def _normalize_genotype(self, genotype: str) -> str:
        """Normaliza un genotipo para comparación (ordena alelos)"""
        if not genotype:
            return genotype
        if len(genotype) == 1:
            genotype = genotype * 2
        return ''.join(sorted(genotype))
    
    def _genotypes_match(self, gt1: Optional[str], gt2: Optional[str]) -> bool:
        """
        Verifica si dos genotipos coinciden (considerando complemento y normalización)
        
        Args:
            gt1: Primer genotipo
            gt2: Segundo genotipo
            
        Returns:
            True si coinciden
        """
        if gt1 is None and gt2 is None:
            return True
        if gt1 is None or gt2 is None:
            return False
        
        # Normalizar ambos genotipos
        norm1 = self._normalize_genotype(gt1)
        norm2 = self._normalize_genotype(gt2)
        
        # Comparar directamente
        if norm1 == norm2:
            return True
        
        # Comparar con complemento
        complement1 = self._complement_genotype(norm1)
        if complement1 == norm2:
            return True
        
        complement2 = self._complement_genotype(norm2)
        if norm1 == complement2:
            return True
        
        return False
    
    def load_data(self) -> bool:
        """Carga los datos necesarios para la auditoría"""
        try:
            # Encontrar archivo de genoma
            genome_dir = self.base_dir / "data" / "raw" / "genome"
            if not genome_dir.exists():
                console.print("[red]Error: No se encontró directorio de genoma[/red]")
                return False
            
            txt_files = list(genome_dir.rglob("*.txt"))
            if not txt_files:
                console.print("[red]Error: No se encontraron archivos de genoma[/red]")
                return False
            
            genome_file = max(txt_files, key=lambda p: p.stat().st_mtime)
            console.print(f"[green]Genoma encontrado: {genome_file.name}[/green]")
            
            # Inicializar componentes
            self.genome_parser = GenomeParser(str(genome_file))
            self.genome_parser.parse()
            
            self.snp_database = SNPDatabase()
            self.report_extractor = ReportExtractor()
            self.analyzer = GeneticAnalyzer(self.genome_parser, self.snp_database, self.report_extractor)
            
            return True
        except Exception as e:
            console.print(f"[red]Error cargando datos: {e}[/red]")
            return False
    
    def audit_genotype_consistency(self):
        """Audita la consistencia de genotipos entre dashboard y genoma raw"""
        console.print("\n[bold blue]Auditando consistencia de genotipos...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        # Obtener hallazgos del analizador (simula lo que muestra el dashboard)
        findings = self.analyzer.analyze()
        
        mismatches = []
        
        for finding in findings:
            rsid = finding.rsid
            dashboard_genotype = finding.genotype
            
            # Obtener genotipo directamente del genoma raw
            raw_genotype = self.genome_parser.get_genotype(rsid)
            
            # Verificar si coinciden
            if not self._genotypes_match(dashboard_genotype, raw_genotype):
                mismatches.append({
                    'rsid': rsid,
                    'dashboard_genotype': dashboard_genotype,
                    'raw_genotype': raw_genotype,
                    'gene': finding.snp_info.gene if finding.snp_info else 'N/A',
                    'category': finding.category,
                    'importance': finding.importance
                })
        
        self.genotype_mismatches = mismatches
        
        if mismatches:
            console.print(f"[yellow]Se encontraron {len(mismatches)} discrepancias de genotipo[/yellow]")
        else:
            console.print("[green]Todos los genotipos son consistentes[/green]")
    
    def audit_missing_genotypes(self):
        """Audita genotipos que deberían estar pero no se encontraron"""
        console.print("\n[bold blue]Auditando genotipos faltantes...[/bold blue]")
        
        if not self.analyzer or not self.snp_database:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        missing = []
        
        for finding in findings:
            # Si el hallazgo indica que está en el genoma pero no tiene genotipo
            if finding.found_in_genome and not finding.genotype:
                missing.append({
                    'rsid': finding.rsid,
                    'gene': finding.snp_info.gene if finding.snp_info else 'N/A',
                    'category': finding.category,
                    'found_in_genome': finding.found_in_genome,
                    'found_in_reports': finding.found_in_reports
                })
        
        self.missing_genotypes = missing
        
        if missing:
            console.print(f"[yellow]Se encontraron {len(missing)} genotipos faltantes[/yellow]")
        else:
            console.print("[green]No hay genotipos faltantes[/green]")
    
    def audit_special_cases(self):
        """Audita casos especiales como APOE y MTHFR combinados"""
        console.print("\n[bold blue]Auditando casos especiales...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        issues = []
        
        # Caso especial: APOE (rs429358 y rs7412)
        apoe_rsids = ['rs429358', 'rs7412']
        apoe_findings = {rsid: None for rsid in apoe_rsids}
        
        for finding in findings:
            if finding.rsid in apoe_rsids:
                apoe_findings[finding.rsid] = finding
        
        # Verificar que ambos SNPs de APOE estén presentes si uno está
        if any(apoe_findings.values()):
            for rsid in apoe_rsids:
                if not apoe_findings[rsid]:
                    issues.append({
                        'type': 'APOE incompleto',
                        'rsid': rsid,
                        'issue': f'APOE requiere ambos SNPs (rs429358 y rs7412), pero {rsid} no está presente'
                    })
        
        # Caso especial: MTHFR (rs1801133 y rs1801131)
        mthfr_rsids = ['rs1801133', 'rs1801131']
        mthfr_findings = {rsid: None for rsid in mthfr_rsids}
        
        for finding in findings:
            if finding.rsid in mthfr_rsids:
                mthfr_findings[finding.rsid] = finding
        
        # Verificar combinaciones de MTHFR
        if all(mthfr_findings.values()):
            gt1 = mthfr_findings['rs1801133'].genotype
            gt2 = mthfr_findings['rs1801131'].genotype
            
            # Verificar que ambos genotipos sean válidos
            if not gt1 or not gt2:
                issues.append({
                    'type': 'MTHFR genotipo faltante',
                    'issue': 'MTHFR requiere ambos genotipos para análisis completo'
                })
        
        self.special_cases_issues = issues
        
        if issues:
            console.print(f"[yellow]Se encontraron {len(issues)} problemas en casos especiales[/yellow]")
        else:
            console.print("[green]Casos especiales validados correctamente[/green]")
    
    def audit_normalization(self):
        """Audita la normalización de genotipos"""
        console.print("\n[bold blue]Auditando normalización de genotipos...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        issues = []
        
        for finding in findings:
            if not finding.genotype:
                continue
            
            # Verificar que el genotipo esté normalizado (ordenado)
            normalized = self._normalize_genotype(finding.genotype)
            
            # Si el genotipo original no está normalizado, podría ser un problema
            # (aunque esto es aceptable si se normaliza internamente)
            if finding.genotype != normalized and len(finding.genotype) == 2:
                # Verificar si es un problema real o solo orden diferente
                if set(finding.genotype) == set(normalized):
                    # Es solo orden, no es un problema crítico
                    pass
                else:
                    issues.append({
                        'rsid': finding.rsid,
                        'original_genotype': finding.genotype,
                        'normalized_genotype': normalized,
                        'gene': finding.snp_info.gene if finding.snp_info else 'N/A',
                        'issue': 'Genotipo no normalizado correctamente'
                    })
        
        self.normalization_issues = issues
        
        if issues:
            console.print(f"[yellow]Se encontraron {len(issues)} problemas de normalización[/yellow]")
        else:
            console.print("[green]Normalización de genotipos correcta[/green]")
    
    def generate_report(self) -> str:
        """Genera un reporte de auditoría en Markdown"""
        report_lines = [
            "# Auditoría de Genotipos del Dashboard",
            f"**Generado el:** {Path(__file__).stat().st_mtime}",
            "",
            "---",
            "",
            "## Resumen Ejecutivo",
            "",
            f"- **Discrepancias de genotipo:** {len(self.genotype_mismatches)}",
            f"- **Genotipos faltantes:** {len(self.missing_genotypes)}",
            f"- **Problemas en casos especiales:** {len(self.special_cases_issues)}",
            f"- **Problemas de normalización:** {len(self.normalization_issues)}",
            "",
            "---",
            ""
        ]
        
        # Discrepancias de genotipo
        if self.genotype_mismatches:
            report_lines.append("## Discrepancias de Genotipo")
            report_lines.append("")
            for mismatch in self.genotype_mismatches[:20]:  # Limitar a 20
                report_lines.append(f"### {mismatch['rsid']}")
                report_lines.append(f"- **Gen:** {mismatch['gene']}")
                report_lines.append(f"- **Genotipo en Dashboard:** {mismatch['dashboard_genotype']}")
                report_lines.append(f"- **Genotipo en Genoma Raw:** {mismatch['raw_genotype']}")
                report_lines.append(f"- **Categoría:** {mismatch['category']}")
                report_lines.append(f"- **Importancia:** {mismatch['importance']}")
                report_lines.append("")
            if len(self.genotype_mismatches) > 20:
                report_lines.append(f"*... y {len(self.genotype_mismatches) - 20} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # Genotipos faltantes
        if self.missing_genotypes:
            report_lines.append("## Genotipos Faltantes")
            report_lines.append("")
            for missing in self.missing_genotypes[:20]:
                report_lines.append(f"- **{missing['rsid']}** ({missing['gene']}) - {missing['category']}")
            if len(self.missing_genotypes) > 20:
                report_lines.append(f"*... y {len(self.missing_genotypes) - 20} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # Casos especiales
        if self.special_cases_issues:
            report_lines.append("## Problemas en Casos Especiales")
            report_lines.append("")
            for issue in self.special_cases_issues:
                report_lines.append(f"- **{issue.get('type', 'Problema')}:** {issue.get('issue', 'N/A')}")
                if 'rsid' in issue:
                    report_lines.append(f"  - RSID: {issue['rsid']}")
            report_lines.append("---")
            report_lines.append("")
        
        # Normalización
        if self.normalization_issues:
            report_lines.append("## Problemas de Normalización")
            report_lines.append("")
            for issue in self.normalization_issues[:10]:
                report_lines.append(f"- **{issue['rsid']}** ({issue['gene']}):")
                report_lines.append(f"  - Original: {issue['original_genotype']}")
                report_lines.append(f"  - Normalizado: {issue['normalized_genotype']}")
            if len(self.normalization_issues) > 10:
                report_lines.append(f"*... y {len(self.normalization_issues) - 10} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # Recomendaciones
        report_lines.append("## Recomendaciones")
        report_lines.append("")
        
        if self.genotype_mismatches:
            report_lines.append("1. **Revisar discrepancias de genotipo:** Verificar orientación de hebra y normalización.")
        
        if self.missing_genotypes:
            report_lines.append("2. **Investigar genotipos faltantes:** Verificar por qué se reportan como encontrados pero no tienen genotipo.")
        
        if self.special_cases_issues:
            report_lines.append("3. **Corregir casos especiales:** Asegurar que APOE y MTHFR tengan todos los SNPs necesarios.")
        
        if not self.genotype_mismatches and not self.missing_genotypes and not self.special_cases_issues:
            report_lines.append("**✅ Genotipos validados correctamente:** No se encontraron problemas críticos.")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("**Fin del Reporte de Auditoría**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        """Ejecuta la auditoría completa"""
        console.print("\n[bold blue]Auditoría de Genotipos del Dashboard[/bold blue]\n")
        
        if not self.load_data():
            return False
        
        self.audit_genotype_consistency()
        self.audit_missing_genotypes()
        self.audit_special_cases()
        self.audit_normalization()
        
        return True


def main():
    """Función principal"""
    base_dir = Path(__file__).parent.parent.parent
    auditor = GenotypeAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        
        # Guardar reporte
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_genotipos_dashboard_{timestamp}.md"
        
        output_file.write_text(report, encoding='utf-8')
        console.print(f"\n[green]Reporte guardado en: {output_file}[/green]")
        
        # Mostrar resumen
        console.print("\n[bold]Resumen:[/bold]")
        console.print(f"  - Discrepancias: {len(auditor.genotype_mismatches)}")
        console.print(f"  - Faltantes: {len(auditor.missing_genotypes)}")
        console.print(f"  - Casos especiales: {len(auditor.special_cases_issues)}")
        console.print(f"  - Normalización: {len(auditor.normalization_issues)}")
    else:
        console.print("[red]Error ejecutando auditoría[/red]")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

