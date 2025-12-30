"""
Script de auditoría de visualizaciones del dashboard
Valida que gráficos muestren datos correctos
"""

import sys
from pathlib import Path
from typing import Dict, List
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.snp_database import SNPDatabase
from dna_analyzer.pdf_extractor import ReportExtractor
from dna_analyzer.analyzer import GeneticAnalyzer

console = Console()


class VisualizationsAuditor:
    """Auditor de visualizaciones del dashboard"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.analyzer = None
        self.issues: List[Dict] = []
        
    def load_data(self) -> bool:
        try:
            genome_dir = self.base_dir / "data" / "raw" / "genome"
            txt_files = list(genome_dir.rglob("*.txt"))
            if not txt_files:
                return False
            
            genome_file = max(txt_files, key=lambda p: p.stat().st_mtime)
            parser = GenomeParser(str(genome_file))
            parser.parse()
            
            snp_db = SNPDatabase()
            report_extractor = ReportExtractor()
            self.analyzer = GeneticAnalyzer(parser, snp_db, report_extractor)
            return True
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return False
    
    def audit_statistics_data(self):
        """Valida que los datos para gráficos sean consistentes"""
        console.print("\n[bold blue]Auditando datos de estadísticas...[/bold blue]")
        
        if not self.analyzer:
            return
        
        findings = self.analyzer.analyze()
        stats = self.analyzer.get_statistics()
        
        # Validar que los datos para gráficos de categoría sean consistentes
        category_data = stats.get('by_category', {})
        if category_data:
            sum_categories = sum(category_data.values())
            total_findings = stats.get('total_findings', 0)
            
            if sum_categories != total_findings:
                self.issues.append({
                    'type': 'category_sum_mismatch',
                    'sum_categories': sum_categories,
                    'total_findings': total_findings,
                    'issue': f'Suma de categorías ({sum_categories}) != total_findings ({total_findings})'
                })
        
        # Validar que los datos para gráficos de importancia sean consistentes
        importance_data = stats.get('by_importance', {})
        if importance_data:
            sum_importance = sum(importance_data.values())
            total_findings = stats.get('total_findings', 0)
            
            if sum_importance != total_findings:
                self.issues.append({
                    'type': 'importance_sum_mismatch',
                    'sum_importance': sum_importance,
                    'total_findings': total_findings,
                    'issue': f'Suma de importancias ({sum_importance}) != total_findings ({total_findings})'
                })
    
    def generate_report(self) -> str:
        report_lines = [
            "# Auditoría de Visualizaciones del Dashboard",
            "",
            "## Resumen",
            f"- **Problemas encontrados:** {len(self.issues)}",
            "",
            "---",
            ""
        ]
        
        if self.issues:
            for issue in self.issues:
                report_lines.append(f"### {issue['type']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append("")
        else:
            report_lines.append("**✅ No se encontraron problemas**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        if not self.load_data():
            return False
        self.audit_statistics_data()
        return True


def main():
    base_dir = Path(__file__).parent.parent.parent
    auditor = VisualizationsAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_visualizations_dashboard_{timestamp}.md"
        output_file.write_text(report, encoding='utf-8')
        console.print(f"[green]Reporte guardado: {output_file}[/green]")
    return 0


if __name__ == '__main__':
    sys.exit(main())

