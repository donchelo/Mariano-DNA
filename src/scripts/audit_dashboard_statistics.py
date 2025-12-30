"""
Script de auditoría de estadísticas del dashboard
Valida consistencia de conteos y métricas del resumen
"""

import sys
from pathlib import Path
from typing import Dict, List
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


class StatisticsAuditor:
    """Auditor de estadísticas del dashboard"""
    
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
        self.consistency_issues: List[Dict] = []
        self.count_mismatches: List[Dict] = []
        
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
    
    def audit_total_findings(self):
        """Valida que total_findings coincida con el número real de hallazgos"""
        console.print("\n[bold blue]Auditando total_findings...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        actual_count = len(findings)
        reported_count = stats.get('total_findings', 0)
        
        if actual_count != reported_count:
            self.count_mismatches.append({
                'metric': 'total_findings',
                'reported': reported_count,
                'actual': actual_count,
                'difference': actual_count - reported_count,
                'issue': f'total_findings reporta {reported_count} pero hay {actual_count} hallazgos reales'
            })
            console.print(f"[yellow]Discrepancia: reportado={reported_count}, real={actual_count}[/yellow]")
        else:
            console.print(f"[green]total_findings correcto: {actual_count}[/green]")
    
    def audit_found_in_genome(self):
        """Valida que found_in_genome coincida con hallazgos reales en genoma"""
        console.print("\n[bold blue]Auditando found_in_genome...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        actual_count = sum(1 for f in findings if f.found_in_genome)
        reported_count = stats.get('found_in_genome', 0)
        
        if actual_count != reported_count:
            self.count_mismatches.append({
                'metric': 'found_in_genome',
                'reported': reported_count,
                'actual': actual_count,
                'difference': actual_count - reported_count,
                'issue': f'found_in_genome reporta {reported_count} pero hay {actual_count} hallazgos reales en genoma'
            })
            console.print(f"[yellow]Discrepancia: reportado={reported_count}, real={actual_count}[/yellow]")
        else:
            console.print(f"[green]found_in_genome correcto: {actual_count}[/green]")
    
    def audit_found_in_reports_only(self):
        """Valida que found_in_reports_only coincida con hallazgos solo en reportes"""
        console.print("\n[bold blue]Auditando found_in_reports_only...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        # Hallazgos que están en reportes pero NO en genoma
        actual_count = sum(1 for f in findings if f.found_in_reports and not f.found_in_genome)
        reported_count = stats.get('found_in_reports_only', 0)
        
        if actual_count != reported_count:
            self.count_mismatches.append({
                'metric': 'found_in_reports_only',
                'reported': reported_count,
                'actual': actual_count,
                'difference': actual_count - reported_count,
                'issue': f'found_in_reports_only reporta {reported_count} pero hay {actual_count} hallazgos reales solo en reportes'
            })
            console.print(f"[yellow]Discrepancia: reportado={reported_count}, real={actual_count}[/yellow]")
        else:
            console.print(f"[green]found_in_reports_only correcto: {actual_count}[/green]")
    
    def audit_category_counts(self):
        """Valida que los conteos por categoría sumen total_findings"""
        console.print("\n[bold blue]Auditando conteos por categoría...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        # Calcular conteos reales por categoría
        actual_by_category = {}
        for finding in findings:
            cat = finding.category
            actual_by_category[cat] = actual_by_category.get(cat, 0) + 1
        
        # Comparar con reportados
        reported_by_category = stats.get('by_category', {})
        
        # Verificar que cada categoría reportada coincida
        all_categories = set(actual_by_category.keys()) | set(reported_by_category.keys())
        
        for cat in all_categories:
            actual = actual_by_category.get(cat, 0)
            reported = reported_by_category.get(cat, 0)
            
            if actual != reported:
                self.count_mismatches.append({
                    'metric': f'by_category[{cat}]',
                    'reported': reported,
                    'actual': actual,
                    'difference': actual - reported,
                    'issue': f'Categoría {cat}: reportado={reported}, real={actual}'
                })
        
        # Verificar que la suma coincida con total_findings
        sum_categories = sum(reported_by_category.values())
        total_findings = stats.get('total_findings', 0)
        
        if sum_categories != total_findings:
            self.consistency_issues.append({
                'type': 'suma_categorias',
                'sum_categories': sum_categories,
                'total_findings': total_findings,
                'difference': total_findings - sum_categories,
                'issue': f'Suma de categorías ({sum_categories}) no coincide con total_findings ({total_findings})'
            })
            console.print(f"[yellow]Suma de categorías no coincide con total_findings[/yellow]")
        else:
            console.print(f"[green]Suma de categorías correcta: {sum_categories}[/green]")
    
    def audit_importance_counts(self):
        """Valida que los conteos por importancia sumen total_findings"""
        console.print("\n[bold blue]Auditando conteos por importancia...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        # Calcular conteos reales por importancia
        actual_by_importance = {}
        for finding in findings:
            imp = finding.importance
            actual_by_importance[imp] = actual_by_importance.get(imp, 0) + 1
        
        # Comparar con reportados
        reported_by_importance = stats.get('by_importance', {})
        
        # Verificar que cada importancia reportada coincida
        all_importances = set(actual_by_importance.keys()) | set(reported_by_importance.keys())
        
        for imp in all_importances:
            actual = actual_by_importance.get(imp, 0)
            reported = reported_by_importance.get(imp, 0)
            
            if actual != reported:
                self.count_mismatches.append({
                    'metric': f'by_importance[{imp}]',
                    'reported': reported,
                    'actual': actual,
                    'difference': actual - reported,
                    'issue': f'Importancia {imp}: reportado={reported}, real={actual}'
                })
        
        # Verificar que la suma coincida con total_findings
        sum_importances = sum(reported_by_importance.values())
        total_findings = stats.get('total_findings', 0)
        
        if sum_importances != total_findings:
            self.consistency_issues.append({
                'type': 'suma_importancias',
                'sum_importances': sum_importances,
                'total_findings': total_findings,
                'difference': total_findings - sum_importances,
                'issue': f'Suma de importancias ({sum_importances}) no coincide con total_findings ({total_findings})'
            })
            console.print(f"[yellow]Suma de importancias no coincide con total_findings[/yellow]")
        else:
            console.print(f"[green]Suma de importancias correcta: {sum_importances}[/green]")
    
    def audit_mutual_exclusivity(self):
        """Valida que found_in_genome y found_in_reports_only sean mutuamente excluyentes"""
        console.print("\n[bold blue]Auditando exclusividad mutua...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        # Un hallazgo puede estar en genoma Y en reportes, pero found_in_reports_only
        # debe ser solo los que están en reportes pero NO en genoma
        
        found_in_both = sum(1 for f in findings if f.found_in_genome and f.found_in_reports)
        found_in_genome_only = sum(1 for f in findings if f.found_in_genome and not f.found_in_reports)
        found_in_reports_only = sum(1 for f in findings if f.found_in_reports and not f.found_in_genome)
        found_in_neither = sum(1 for f in findings if not f.found_in_genome and not f.found_in_reports)
        
        # Verificar que la suma sea total_findings
        total_calculated = found_in_both + found_in_genome_only + found_in_reports_only + found_in_neither
        total_findings = stats.get('total_findings', 0)
        
        if total_calculated != total_findings:
            self.consistency_issues.append({
                'type': 'exclusividad_mutua',
                'total_calculated': total_calculated,
                'total_findings': total_findings,
                'issue': f'Suma de categorías de ubicación ({total_calculated}) no coincide con total_findings ({total_findings})'
            })
        
        # Verificar que found_in_reports_only sea correcto
        reported_reports_only = stats.get('found_in_reports_only', 0)
        if found_in_reports_only != reported_reports_only:
            self.count_mismatches.append({
                'metric': 'found_in_reports_only (validación)',
                'reported': reported_reports_only,
                'actual': found_in_reports_only,
                'difference': found_in_reports_only - reported_reports_only,
                'issue': f'found_in_reports_only no coincide con conteo real'
            })
        
        console.print(f"[green]Exclusividad mutua validada:[/green]")
        console.print(f"  - En ambos: {found_in_both}")
        console.print(f"  - Solo en genoma: {found_in_genome_only}")
        console.print(f"  - Solo en reportes: {found_in_reports_only}")
        console.print(f"  - En ninguno: {found_in_neither}")
    
    def generate_report(self) -> str:
        """Genera un reporte de auditoría en Markdown"""
        report_lines = [
            "# Auditoría de Estadísticas del Dashboard",
            f"**Generado el:** {Path(__file__).stat().st_mtime}",
            "",
            "---",
            "",
            "## Resumen Ejecutivo",
            "",
            f"- **Discrepancias de conteo:** {len(self.count_mismatches)}",
            f"- **Problemas de consistencia:** {len(self.consistency_issues)}",
            "",
            "---",
            ""
        ]
        
        # Discrepancias de conteo
        if self.count_mismatches:
            report_lines.append("## Discrepancias de Conteo")
            report_lines.append("")
            report_lines.append("| Métrica | Reportado | Real | Diferencia |")
            report_lines.append("|---------|-----------|------|------------|")
            for mismatch in self.count_mismatches:
                report_lines.append(
                    f"| {mismatch['metric']} | {mismatch['reported']} | {mismatch['actual']} | {mismatch['difference']} |"
                )
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        # Problemas de consistencia
        if self.consistency_issues:
            report_lines.append("## Problemas de Consistencia")
            report_lines.append("")
            for issue in self.consistency_issues:
                report_lines.append(f"### {issue['type']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                if 'difference' in issue:
                    report_lines.append(f"- **Diferencia:** {issue['difference']}")
                report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        # Recomendaciones
        report_lines.append("## Recomendaciones")
        report_lines.append("")
        
        if self.count_mismatches:
            report_lines.append("1. **Corregir discrepancias de conteo:** Revisar la lógica de conteo en `get_statistics()`.")
        
        if self.consistency_issues:
            report_lines.append("2. **Corregir problemas de consistencia:** Asegurar que las sumas coincidan con total_findings.")
        
        if not self.count_mismatches and not self.consistency_issues:
            report_lines.append("**✅ Estadísticas validadas correctamente:** No se encontraron problemas.")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("**Fin del Reporte de Auditoría**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        """Ejecuta la auditoría completa"""
        console.print("\n[bold blue]Auditoría de Estadísticas del Dashboard[/bold blue]\n")
        
        if not self.load_data():
            return False
        
        self.audit_total_findings()
        self.audit_found_in_genome()
        self.audit_found_in_reports_only()
        self.audit_category_counts()
        self.audit_importance_counts()
        self.audit_mutual_exclusivity()
        
        return True


def main():
    """Función principal"""
    base_dir = Path(__file__).parent.parent.parent
    auditor = StatisticsAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        
        # Guardar reporte
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_estadisticas_dashboard_{timestamp}.md"
        
        output_file.write_text(report, encoding='utf-8')
        console.print(f"\n[green]Reporte guardado en: {output_file}[/green]")
        
        # Mostrar resumen
        console.print("\n[bold]Resumen:[/bold]")
        console.print(f"  - Discrepancias: {len(auditor.count_mismatches)}")
        console.print(f"  - Consistencia: {len(auditor.consistency_issues)}")
    else:
        console.print("[red]Error ejecutando auditoría[/red]")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

