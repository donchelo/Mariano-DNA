"""
Script de auditoría de mapa de riesgo del dashboard
Valida mapeo de sistemas y scores
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
from dna_analyzer.system_mapper import SystemMapper

console = Console()


class RiskMapAuditor:
    """Auditor de mapa de riesgo del dashboard"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.genome_parser = None
        self.analyzer = None
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
            
            snp_db = SNPDatabase()
            report_extractor = ReportExtractor()
            self.analyzer = GeneticAnalyzer(self.genome_parser, snp_db, report_extractor)
            return True
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return False
    
    def audit_mapping(self):
        """Valida que el mapeo de hallazgos a sistemas sea correcto"""
        console.print("\n[bold blue]Auditando mapeo de sistemas...[/bold blue]")
        
        if not self.analyzer:
            return
        
        findings = self.analyzer.analyze()
        system_mapper = SystemMapper()
        system_risks = system_mapper.map_findings_to_systems(findings)
        
        # Verificar que cada sistema tenga conteos consistentes
        for system_name, system_risk in system_risks.items():
            # Verificar que total_snps = suma de conteos de riesgo
            calculated_total = (system_risk.high_risk_count + 
                              system_risk.medium_risk_count + 
                              system_risk.low_risk_count)
            
            if system_risk.total_snps != calculated_total and system_risk.total_snps > 0:
                self.issues.append({
                    'system': system_name,
                    'type': 'count_mismatch',
                    'total_snps': system_risk.total_snps,
                    'calculated_total': calculated_total,
                    'issue': f'Total SNPs ({system_risk.total_snps}) no coincide con suma de riesgos ({calculated_total})'
                })
            
            # Verificar que risk_score esté en rango 0-1
            if system_risk.risk_score < 0 or system_risk.risk_score > 1:
                self.issues.append({
                    'system': system_name,
                    'type': 'invalid_score',
                    'risk_score': system_risk.risk_score,
                    'issue': f'Score de riesgo fuera de rango (0-1): {system_risk.risk_score}'
                })
    
    def audit_findings_assignment(self):
        """Valida que los hallazgos se asignen correctamente a sistemas"""
        console.print("\n[bold blue]Auditando asignación de hallazgos...[/bold blue]")
        
        if not self.analyzer:
            return
        
        findings = self.analyzer.analyze()
        system_mapper = SystemMapper()
        system_risks = system_mapper.map_findings_to_systems(findings)
        
        # Verificar que hallazgos con genes conocidos se asignen correctamente
        for finding in findings:
            if finding.snp_info and finding.snp_info.gene:
                gene = finding.snp_info.gene
                assigned_systems = [name for name, risk in system_risks.items() 
                                  if finding in risk.findings]
                
                # Verificar si el gen debería estar en algún sistema
                expected_systems = []
                for system_name, criteria in system_mapper.SYSTEM_MAPPING.items():
                    if gene in criteria['genes']:
                        expected_systems.append(system_name)
                
                if expected_systems:
                    missing = [s for s in expected_systems if s not in assigned_systems]
                    if missing:
                        self.issues.append({
                            'rsid': finding.rsid,
                            'gene': gene,
                            'type': 'missing_assignment',
                            'expected_systems': expected_systems,
                            'assigned_systems': assigned_systems,
                            'issue': f'Gen {gene} debería estar en {missing} pero no está asignado'
                        })
    
    def generate_report(self) -> str:
        report_lines = [
            "# Auditoría de Mapa de Riesgo del Dashboard",
            "",
            "## Resumen",
            f"- **Problemas encontrados:** {len(self.issues)}",
            "",
            "---",
            ""
        ]
        
        if self.issues:
            for issue in self.issues:
                report_lines.append(f"### {issue.get('system', issue.get('rsid', 'N/A'))}")
                report_lines.append(f"- **Tipo:** {issue['type']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append("")
        else:
            report_lines.append("**✅ No se encontraron problemas**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        if not self.load_data():
            return False
        self.audit_mapping()
        self.audit_findings_assignment()
        return True


def main():
    base_dir = Path(__file__).parent.parent.parent
    auditor = RiskMapAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_risk_map_dashboard_{timestamp}.md"
        output_file.write_text(report, encoding='utf-8')
        console.print(f"[green]Reporte guardado: {output_file}[/green]")
    return 0


if __name__ == '__main__':
    sys.exit(main())

