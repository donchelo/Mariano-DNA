"""
Script de auditoría de PRS del dashboard
Valida cálculos y percentiles
"""

import sys
from pathlib import Path
from typing import Dict, List
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.prs_calculator import PRSCalculator

console = Console()


class PRSAuditor:
    """Auditor de PRS del dashboard"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.genome_parser = None
        self.issues: List[Dict] = []
        
    def load_data(self) -> bool:
        try:
            genome_dir = self.base_dir / "data" / "raw" / "genome"
            txt_files = list(genome_dir.rglob("*.txt"))
            if not txt_files:
                return False
            
            genome_file = max(txt_files, key=lambda p: p.stat().st_mtime)
            self.genome_parser = GenomeParser(str(genome_file))
            self.genome_parser.parse()
            return True
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return False
    
    def audit_snps_presence(self):
        """Valida que los SNPs usados en PRS estén presentes"""
        console.print("\n[bold blue]Auditando presencia de SNPs en PRS...[/bold blue]")
        
        if not self.genome_parser:
            return
        
        calculator = PRSCalculator(self.genome_parser)
        
        for condition, definition in calculator.PRS_DEFINITIONS.items():
            missing_snps = []
            for snp_def in definition['snps']:
                rsid = snp_def['rsid']
                genotype = self.genome_parser.get_genotype(rsid)
                if not genotype:
                    missing_snps.append(rsid)
            
            if missing_snps:
                # Esto no es necesariamente un error - los SNPs pueden no estar en el genoma
                # Solo reportar como advertencia si faltan muchos SNPs
                if len(missing_snps) < len(definition['snps']) * 0.5:  # Si faltan menos del 50%
                    # Es normal que algunos SNPs no estén en el genoma
                    pass
                else:
                    self.issues.append({
                        'condition': condition,
                        'type': 'missing_snps',
                        'missing_snps': missing_snps,
                        'issue': f'{condition}: Faltan {len(missing_snps)} de {len(definition["snps"])} SNPs (puede afectar precisión del PRS)'
                    })
    
    def audit_calculations(self):
        """Valida cálculos de PRS"""
        console.print("\n[bold blue]Auditando cálculos de PRS...[/bold blue]")
        
        if not self.genome_parser:
            return
        
        calculator = PRSCalculator(self.genome_parser)
        results = calculator.calculate_all_prs()
        
        for condition, result in results.items():
            # Validar que percentil esté en rango válido
            if result.percentile < 0 or result.percentile > 100:
                self.issues.append({
                    'condition': condition,
                    'type': 'invalid_percentile',
                    'percentile': result.percentile,
                    'issue': f'{condition}: Percentil fuera de rango ({result.percentile})'
                })
            
            # Validar que snps_used <= total_snps
            if result.snps_used > result.total_snps:
                self.issues.append({
                    'condition': condition,
                    'type': 'invalid_count',
                    'issue': f'{condition}: SNPs usados ({result.snps_used}) > total ({result.total_snps})'
                })
    
    def generate_report(self) -> str:
        report_lines = [
            "# Auditoría de PRS del Dashboard",
            "",
            "## Resumen",
            f"- **Problemas encontrados:** {len(self.issues)}",
            "",
            "---",
            ""
        ]
        
        if self.issues:
            for issue in self.issues:
                report_lines.append(f"### {issue['condition']}")
                report_lines.append(f"- **Tipo:** {issue['type']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append("")
        else:
            report_lines.append("**✅ No se encontraron problemas**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        if not self.load_data():
            return False
        self.audit_snps_presence()
        self.audit_calculations()
        return True


def main():
    base_dir = Path(__file__).parent.parent.parent
    auditor = PRSAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_prs_dashboard_{timestamp}.md"
        output_file.write_text(report, encoding='utf-8')
        console.print(f"[green]Reporte guardado: {output_file}[/green]")
    return 0


if __name__ == '__main__':
    sys.exit(main())

