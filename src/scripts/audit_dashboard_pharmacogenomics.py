"""
Script de auditoría de farmacogenómica del dashboard
Valida diplotipos y fenotipos
"""

import sys
from pathlib import Path
from typing import Dict, List
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.pharmacogenomics import PharmacogenomicsAnalyzer

console = Console()


class PharmacogenomicsAuditor:
    """Auditor de farmacogenómica del dashboard"""
    
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
    
    def audit_genotypes(self):
        """Valida que los genotipos usados sean correctos"""
        console.print("\n[bold blue]Auditando genotipos farmacogenómicos...[/bold blue]")
        
        if not self.genome_parser:
            return
        
        analyzer = PharmacogenomicsAnalyzer(self.genome_parser)
        
        for gene, snps in analyzer.GENE_SNPS.items():
            missing_snps = []
            for rsid in snps:
                genotype = self.genome_parser.get_genotype(rsid)
                if not genotype:
                    missing_snps.append(rsid)
            
            if missing_snps:
                self.issues.append({
                    'gene': gene,
                    'type': 'missing_snps',
                    'missing_snps': missing_snps,
                    'issue': f'{gene}: Faltan {len(missing_snps)} SNPs necesarios'
                })
    
    def audit_profiles(self):
        """Valida que los perfiles sean consistentes"""
        console.print("\n[bold blue]Auditando perfiles farmacogenómicos...[/bold blue]")
        
        if not self.genome_parser:
            return
        
        analyzer = PharmacogenomicsAnalyzer(self.genome_parser)
        profiles = analyzer.analyze_all_genes()
        
        for gene, profile in profiles.items():
            # Validar que diplotipo y fenotipo sean consistentes
            if profile.diplotype and not profile.phenotype:
                self.issues.append({
                    'gene': gene,
                    'type': 'missing_phenotype',
                    'issue': f'{gene}: Tiene diplotipo pero no fenotipo'
                })
    
    def generate_report(self) -> str:
        report_lines = [
            "# Auditoría de Farmacogenómica del Dashboard",
            "",
            "## Resumen",
            f"- **Problemas encontrados:** {len(self.issues)}",
            "",
            "---",
            ""
        ]
        
        if self.issues:
            for issue in self.issues:
                report_lines.append(f"### {issue['gene']}")
                report_lines.append(f"- **Tipo:** {issue['type']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append("")
        else:
            report_lines.append("**✅ No se encontraron problemas**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        if not self.load_data():
            return False
        self.audit_genotypes()
        self.audit_profiles()
        return True


def main():
    base_dir = Path(__file__).parent.parent.parent
    auditor = PharmacogenomicsAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_farmacogenomica_dashboard_{timestamp}.md"
        output_file.write_text(report, encoding='utf-8')
        console.print(f"[green]Reporte guardado: {output_file}[/green]")
    return 0


if __name__ == '__main__':
    sys.exit(main())

