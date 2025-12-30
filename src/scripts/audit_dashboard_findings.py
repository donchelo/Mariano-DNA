"""
Script de auditoría de hallazgos del dashboard
Compara con Promethease y valida importancia asignada
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table

# Agregar el directorio src al path para importar dna_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.snp_database import SNPDatabase
from dna_analyzer.pdf_extractor import ReportExtractor
from dna_analyzer.analyzer import GeneticAnalyzer

console = Console()


class FindingsAuditor:
    """Auditor de hallazgos del dashboard"""
    
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
        self.promethease_data: Dict[str, Dict] = {}
        
        # Resultados de auditoría
        self.importance_issues: List[Dict] = []
        self.promethease_mismatches: List[Dict] = []
        self.missing_in_curated_db: List[Dict] = []
        self.normal_protective_issues: List[Dict] = []
        
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
            
            # Cargar datos de Promethease
            self.load_promethease_data()
            
            return True
        except Exception as e:
            console.print(f"[red]Error cargando datos: {e}[/red]")
            return False
    
    def load_promethease_data(self):
        """Carga datos de Promethease desde JSON"""
        promethease_file = self.base_dir / "data" / "processed" / "hallazgos_geneticos.json"
        
        if not promethease_file.exists():
            # Buscar en reportes_proveedores
            promethease_dir = self.base_dir / "data" / "raw" / "reportes_proveedores" / "promethease"
            if promethease_dir.exists():
                json_files = list(promethease_dir.glob("*.json"))
                if json_files:
                    promethease_file = max(json_files, key=lambda p: p.stat().st_mtime)
        
        if promethease_file.exists():
            try:
                with open(promethease_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convertir a diccionario por rsid
                for entry in data:
                    rsid = entry.get('record_id', '').replace('rs', '')
                    if rsid.startswith('rs'):
                        rsid = rsid[2:]
                    if rsid.startswith('rs'):
                        rsid = rsid[2:]
                    if not rsid.startswith('rs') and rsid:
                        rsid = f"rs{rsid}"
                    
                    if rsid and rsid.startswith('rs'):
                        self.promethease_data[rsid] = entry
                
                console.print(f"[green]Cargados {len(self.promethease_data)} SNPs de Promethease[/green]")
            except Exception as e:
                console.print(f"[yellow]Error cargando Promethease: {e}[/yellow]")
        else:
            console.print("[yellow]No se encontró archivo de Promethease[/yellow]")
    
    def audit_importance_consistency(self):
        """Valida que la importancia asignada sea consistente con la magnitud"""
        console.print("\n[bold blue]Auditando consistencia de importancia...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        issues = []
        
        for finding in findings:
            magnitude = finding.magnitude
            importance = finding.importance
            
            if magnitude is None:
                continue
            
            # Si tiene alta magnitud (>= 3.5) y no es protector/normal, debería ser alta importancia
            if magnitude >= 3.5:
                # Verificar si es protector o normal
                is_protective = any(kw in finding.implications.lower() for kw in [
                    'protector', 'protección', 'reduced risk', 'lower risk', 'bajo riesgo'
                ])
                is_normal = any(kw in finding.implications.lower() for kw in [
                    'normal', 'función normal', 'riesgo bajo'
                ])
                
                if not is_protective and not is_normal:
                    # Debería ser alta importancia si es de riesgo
                    if importance != 'alto':
                        issues.append({
                            'rsid': finding.rsid,
                            'gene': finding.snp_info.gene if finding.snp_info else 'N/A',
                            'magnitude': magnitude,
                            'assigned_importance': importance,
                            'expected_importance': 'alto',
                            'issue': f'Alta magnitud ({magnitude}) pero importancia {importance}'
                        })
        
        self.importance_issues = issues
        
        if issues:
            console.print(f"[yellow]Se encontraron {len(issues)} problemas de importancia[/yellow]")
        else:
            console.print("[green]Importancia consistente con magnitud[/green]")
    
    def audit_normal_protective_genotypes(self):
        """Valida que genotipos normales/protectores no tengan importancia alta"""
        console.print("\n[bold blue]Auditando genotipos normales/protectores...[/bold blue]")
        
        if not self.analyzer:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        issues = []
        
        for finding in findings:
            if not finding.genotype or not finding.snp_info:
                continue
            
            # Verificar interpretación del genotipo
            if finding.snp_info.genotype_interpretation:
                interpretation = finding.snp_info.genotype_interpretation.get(finding.genotype, '')
                interpretation_lower = interpretation.lower()
                
                # Si es normal o protector, no debería tener importancia alta
                is_normal = any(kw in interpretation_lower for kw in [
                    'normal', 'función normal', 'riesgo bajo'
                ])
                is_protective = any(kw in interpretation_lower for kw in [
                    'protector', 'protección', 'reduced risk'
                ])
                
                if (is_normal or is_protective) and finding.importance == 'alto':
                    issues.append({
                        'rsid': finding.rsid,
                        'gene': finding.snp_info.gene,
                        'genotype': finding.genotype,
                        'interpretation': interpretation,
                        'assigned_importance': finding.importance,
                        'expected_importance': 'bajo',
                        'issue': f'Genotipo normal/protector con importancia alta'
                    })
        
        self.normal_protective_issues = issues
        
        if issues:
            console.print(f"[yellow]Se encontraron {len(issues)} genotipos normales/protectores con importancia alta[/yellow]")
        else:
            console.print("[green]Genotipos normales/protectores validados correctamente[/green]")
    
    def audit_promethease_comparison(self):
        """Compara hallazgos del dashboard con Promethease"""
        console.print("\n[bold blue]Comparando con Promethease...[/bold blue]")
        
        if not self.analyzer or not self.promethease_data:
            console.print("[yellow]No hay datos de Promethease para comparar[/yellow]")
            return
        
        findings = self.analyzer.analyze()
        mismatches = []
        
        for finding in findings:
            rsid = finding.rsid
            promethease_entry = self.promethease_data.get(rsid)
            
            if not promethease_entry:
                continue
            
            # Comparar genotipos
            dashboard_genotype = finding.genotype
            promethease_genotype = promethease_entry.get('genotype')
            
            # Normalizar genotipos de Promethease (formato "A;G" -> "AG")
            if promethease_genotype and ';' in promethease_genotype:
                promethease_genotype = promethease_genotype.replace(';', '')
            
            # Comparar magnitudes
            dashboard_magnitude = finding.magnitude
            promethease_magnitude = promethease_entry.get('magnitude')
            
            # Comparar repute
            promethease_repute = promethease_entry.get('repute')
            
            issues = []
            
            # Verificar genotipo
            if dashboard_genotype and promethease_genotype:
                # Normalizar para comparación
                dash_norm = ''.join(sorted(dashboard_genotype.replace(';', '')))
                prom_norm = ''.join(sorted(promethease_genotype.replace(';', '')))
                
                if dash_norm != prom_norm:
                    issues.append(f"Genotipo: dashboard={dashboard_genotype}, promethease={promethease_genotype}")
            
            # Verificar magnitud (con tolerancia)
            if dashboard_magnitude is not None and promethease_magnitude is not None:
                if abs(dashboard_magnitude - promethease_magnitude) > 0.1:
                    issues.append(f"Magnitud: dashboard={dashboard_magnitude}, promethease={promethease_magnitude}")
            
            if issues:
                mismatches.append({
                    'rsid': rsid,
                    'gene': finding.snp_info.gene if finding.snp_info else 'N/A',
                    'issues': issues,
                    'dashboard_magnitude': dashboard_magnitude,
                    'promethease_magnitude': promethease_magnitude,
                    'promethease_repute': promethease_repute
                })
        
        self.promethease_mismatches = mismatches
        
        if mismatches:
            console.print(f"[yellow]Se encontraron {len(mismatches)} discrepancias con Promethease[/yellow]")
        else:
            console.print("[green]Hallazgos consistentes con Promethease[/green]")
    
    def audit_curated_database(self):
        """Valida que los SNPs mostrados existan en la base de datos curada"""
        console.print("\n[bold blue]Auditando base de datos curada...[/bold blue]")
        
        if not self.analyzer or not self.snp_database:
            console.print("[red]Error: Datos no cargados[/red]")
            return
        
        findings = self.analyzer.analyze()
        missing = []
        
        for finding in findings:
            rsid = finding.rsid
            snp_info = self.snp_database.get_snp(rsid)
            
            if not snp_info:
                missing.append({
                    'rsid': rsid,
                    'gene': finding.snp_info.gene if finding.snp_info else 'N/A',
                    'category': finding.category,
                    'importance': finding.importance,
                    'magnitude': finding.magnitude,
                    'issue': f'SNP {rsid} no está en la base de datos curada (snps.json)'
                })
        
        self.missing_in_curated_db = missing
        
        if missing:
            console.print(f"[yellow]Se encontraron {len(missing)} SNPs no en base de datos curada[/yellow]")
        else:
            console.print("[green]Todos los SNPs están en la base de datos curada[/green]")
    
    def generate_report(self) -> str:
        """Genera un reporte de auditoría en Markdown"""
        report_lines = [
            "# Auditoría de Hallazgos del Dashboard",
            f"**Generado el:** {Path(__file__).stat().st_mtime}",
            "",
            "---",
            "",
            "## Resumen Ejecutivo",
            "",
            f"- **Problemas de importancia:** {len(self.importance_issues)}",
            f"- **Discrepancias con Promethease:** {len(self.promethease_mismatches)}",
            f"- **SNPs faltantes en BD curada:** {len(self.missing_in_curated_db)}",
            f"- **Genotipos normales/protectores con importancia alta:** {len(self.normal_protective_issues)}",
            "",
            "---",
            ""
        ]
        
        # Problemas de importancia
        if self.importance_issues:
            report_lines.append("## Problemas de Importancia")
            report_lines.append("")
            for issue in self.importance_issues[:20]:
                report_lines.append(f"### {issue['rsid']}")
                report_lines.append(f"- **Gen:** {issue['gene']}")
                report_lines.append(f"- **Magnitud:** {issue['magnitude']}")
                report_lines.append(f"- **Importancia asignada:** {issue['assigned_importance']}")
                report_lines.append(f"- **Importancia esperada:** {issue['expected_importance']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append("")
            if len(self.importance_issues) > 20:
                report_lines.append(f"*... y {len(self.importance_issues) - 20} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # Discrepancias con Promethease
        if self.promethease_mismatches:
            report_lines.append("## Discrepancias con Promethease")
            report_lines.append("")
            for mismatch in self.promethease_mismatches[:20]:
                report_lines.append(f"### {mismatch['rsid']}")
                report_lines.append(f"- **Gen:** {mismatch['gene']}")
                for issue in mismatch['issues']:
                    report_lines.append(f"- {issue}")
                report_lines.append("")
            if len(self.promethease_mismatches) > 20:
                report_lines.append(f"*... y {len(self.promethease_mismatches) - 20} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # SNPs faltantes en BD curada
        if self.missing_in_curated_db:
            report_lines.append("## SNPs Faltantes en Base de Datos Curada")
            report_lines.append("")
            report_lines.append("SNPs que aparecen en hallazgos pero no están en `snps.json`:")
            report_lines.append("")
            for missing in self.missing_in_curated_db[:20]:
                report_lines.append(f"- **{missing['rsid']}** ({missing['gene']}) - {missing['category']} - Magnitud: {missing.get('magnitude', 'N/A')}")
            if len(self.missing_in_curated_db) > 20:
                report_lines.append(f"*... y {len(self.missing_in_curated_db) - 20} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # Genotipos normales/protectores
        if self.normal_protective_issues:
            report_lines.append("## Genotipos Normales/Protectores con Importancia Alta")
            report_lines.append("")
            for issue in self.normal_protective_issues[:20]:
                report_lines.append(f"- **{issue['rsid']}** ({issue['gene']}):")
                report_lines.append(f"  - Genotipo: {issue['genotype']}")
                report_lines.append(f"  - Interpretación: {issue['interpretation']}")
                report_lines.append(f"  - Importancia asignada: {issue['assigned_importance']}")
            if len(self.normal_protective_issues) > 20:
                report_lines.append(f"*... y {len(self.normal_protective_issues) - 20} más*")
            report_lines.append("---")
            report_lines.append("")
        
        # Recomendaciones
        report_lines.append("## Recomendaciones")
        report_lines.append("")
        
        if self.importance_issues:
            report_lines.append("1. **Corregir importancia:** Revisar lógica de asignación de importancia basada en magnitud.")
        
        if self.promethease_mismatches:
            report_lines.append("2. **Revisar discrepancias con Promethease:** Verificar normalización de genotipos y magnitudes.")
        
        if self.missing_in_curated_db:
            report_lines.append("3. **Agregar SNPs faltantes:** Considerar agregar SNPs importantes a `snps.json`.")
        
        if self.normal_protective_issues:
            report_lines.append("4. **Corregir importancia de genotipos normales:** Asegurar que genotipos normales/protectores tengan importancia baja.")
        
        if not self.importance_issues and not self.promethease_mismatches and not self.missing_in_curated_db and not self.normal_protective_issues:
            report_lines.append("**✅ Hallazgos validados correctamente:** No se encontraron problemas.")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("**Fin del Reporte de Auditoría**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        """Ejecuta la auditoría completa"""
        console.print("\n[bold blue]Auditoría de Hallazgos del Dashboard[/bold blue]\n")
        
        if not self.load_data():
            return False
        
        self.audit_importance_consistency()
        self.audit_normal_protective_genotypes()
        self.audit_promethease_comparison()
        self.audit_curated_database()
        
        return True


def main():
    """Función principal"""
    base_dir = Path(__file__).parent.parent.parent
    auditor = FindingsAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        
        # Guardar reporte
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_hallazgos_dashboard_{timestamp}.md"
        
        output_file.write_text(report, encoding='utf-8')
        console.print(f"\n[green]Reporte guardado en: {output_file}[/green]")
        
        # Mostrar resumen
        console.print("\n[bold]Resumen:[/bold]")
        console.print(f"  - Importancia: {len(auditor.importance_issues)}")
        console.print(f"  - Promethease: {len(auditor.promethease_mismatches)}")
        console.print(f"  - BD curada: {len(auditor.missing_in_curated_db)}")
        console.print(f"  - Normal/protector: {len(auditor.normal_protective_issues)}")
    else:
        console.print("[red]Error ejecutando auditoría[/red]")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

