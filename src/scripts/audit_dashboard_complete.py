"""
Script principal de auditoría completa del dashboard
Ejecuta todas las auditorías y genera reporte consolidado
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Scripts de auditoría individuales
AUDIT_SCRIPTS = [
    ('Genotipos', 'audit_dashboard_genotypes.py'),
    ('Estadísticas', 'audit_dashboard_statistics.py'),
    ('Hallazgos', 'audit_dashboard_findings.py'),
    ('Farmacogenómica', 'audit_dashboard_pharmacogenomics.py'),
    ('PRS', 'audit_dashboard_prs.py'),
    ('Mapa de Riesgo', 'audit_dashboard_risk_map.py'),
    ('Biomarcadores', 'audit_dashboard_biomarkers.py'),
    ('Visualizaciones', 'audit_dashboard_visualizations.py'),
]


class CompleteAuditor:
    """Auditor completo del dashboard"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.scripts_dir = base_dir / "src" / "scripts"
        self.results: Dict[str, Dict] = {}
        
    def run_individual_audit(self, name: str, script: str) -> Dict:
        """Ejecuta una auditoría individual"""
        console.print(f"\n[bold cyan]Ejecutando auditoría: {name}[/bold cyan]")
        
        script_path = self.scripts_dir / script
        
        if not script_path.exists():
            return {
                'status': 'error',
                'message': f'Script no encontrado: {script}',
                'issues_count': 0
            }
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            if result.returncode == 0:
                # Buscar el reporte generado más reciente
                output_dir = self.base_dir / "outputs" / "analisis"
                pattern = f"auditoria_{script.replace('audit_dashboard_', '').replace('.py', '')}_dashboard_*.md"
                report_files = list(output_dir.glob(pattern))
                
                if report_files:
                    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                    report_content = latest_report.read_text(encoding='utf-8')
                    
                    # Contar problemas (heurística simple)
                    issues_count = report_content.count('**Problema:**') + report_content.count('**Problemas encontrados:**')
                    
                    return {
                        'status': 'success',
                        'report_file': latest_report,
                        'issues_count': issues_count,
                        'output': result.stdout
                    }
                else:
                    return {
                        'status': 'success',
                        'message': 'Auditoría completada pero no se encontró reporte',
                        'issues_count': 0,
                        'output': result.stdout
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'Error ejecutando script: {result.stderr}',
                    'issues_count': 0,
                    'output': result.stdout,
                    'error': result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'message': 'Auditoría excedió el tiempo límite',
                'issues_count': 0
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'issues_count': 0
            }
    
    def run_all_audits(self):
        """Ejecuta todas las auditorías"""
        console.print("\n[bold blue]Iniciando Auditoría Completa del Dashboard[/bold blue]\n")
        
        total_issues = 0
        
        for name, script in AUDIT_SCRIPTS:
            result = self.run_individual_audit(name, script)
            self.results[name] = result
            
            if result['status'] == 'success':
                issues = result.get('issues_count', 0)
                total_issues += issues
                status_icon = "[OK]" if issues == 0 else "[WARN]"
                console.print(f"{status_icon} {name}: {issues} problemas encontrados")
            else:
                console.print(f"[ERROR] {name}: {result.get('message', 'Error desconocido')}")
        
        return total_issues
    
    def generate_consolidated_report(self) -> str:
        """Genera reporte consolidado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = [
            "# Auditoría Completa del Dashboard",
            f"**Generado el:** {timestamp}",
            "",
            "---",
            "",
            "## Resumen Ejecutivo",
            "",
        ]
        
        # Calcular totales
        total_audits = len(self.results)
        successful_audits = sum(1 for r in self.results.values() if r['status'] == 'success')
        failed_audits = total_audits - successful_audits
        total_issues = sum(r.get('issues_count', 0) for r in self.results.values())
        
        report_lines.append(f"- **Total de auditorías:** {total_audits}")
        report_lines.append(f"- **Auditorías exitosas:** {successful_audits}")
        report_lines.append(f"- **Auditorías fallidas:** {failed_audits}")
        report_lines.append(f"- **Total de problemas encontrados:** {total_issues}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # Detalles por auditoría
        report_lines.append("## Detalles por Auditoría")
        report_lines.append("")
        
        for name, result in self.results.items():
            report_lines.append(f"### {name}")
            report_lines.append("")
            
            if result['status'] == 'success':
                issues_count = result.get('issues_count', 0)
                report_lines.append(f"- **Estado:** OK - Completada")
                report_lines.append(f"- **Problemas encontrados:** {issues_count}")
                
                if 'report_file' in result:
                    report_file = result['report_file']
                    report_lines.append(f"- **Reporte detallado:** `{report_file.name}`")
                
                if issues_count > 0:
                    report_lines.append(f"- **Recomendación:** Revisar reporte detallado para más información")
            else:
                report_lines.append(f"- **Estado:** ERROR")
                report_lines.append(f"- **Mensaje:** {result.get('message', 'Error desconocido')}")
            
            report_lines.append("")
        
        # Recomendaciones generales
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## Recomendaciones Generales")
        report_lines.append("")
        
        if total_issues == 0:
            report_lines.append("**OK - Excelente:** No se encontraron problemas en ninguna auditoría.")
            report_lines.append("El dashboard está funcionando correctamente.")
        elif total_issues < 10:
            report_lines.append("**WARN - Atención:** Se encontraron algunos problemas menores.")
            report_lines.append("Revisar los reportes detallados y corregir los problemas identificados.")
        else:
            report_lines.append("**CRITICAL - Crítico:** Se encontraron múltiples problemas.")
            report_lines.append("Revisar urgentemente los reportes detallados y corregir los problemas identificados.")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## Próximos Pasos")
        report_lines.append("")
        report_lines.append("1. Revisar cada reporte detallado individual")
        report_lines.append("2. Corregir los problemas identificados")
        report_lines.append("3. Ejecutar nuevamente la auditoría para verificar correcciones")
        report_lines.append("4. Integrar auditorías en el pipeline de CI/CD si es posible")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("**Fin del Reporte de Auditoría Completa**")
        
        return '\n'.join(report_lines)
    
    def display_summary(self):
        """Muestra resumen en consola"""
        table = Table(title="Resumen de Auditoría")
        table.add_column("Auditoría", style="cyan")
        table.add_column("Estado", style="magenta")
        table.add_column("Problemas", justify="right", style="yellow")
        
        for name, result in self.results.items():
            if result['status'] == 'success':
                issues = result.get('issues_count', 0)
                status = "[OK]" if issues == 0 else f"[WARN] {issues} problemas"
                table.add_row(name, status, str(issues))
            else:
                table.add_row(name, "[ERROR]", "-")
        
        console.print("\n")
        console.print(table)
        
        total_issues = sum(r.get('issues_count', 0) for r in self.results.values())
        console.print(f"\n[bold]Total de problemas encontrados: {total_issues}[/bold]")


def main():
    """Función principal"""
    base_dir = Path(__file__).parent.parent.parent
    auditor = CompleteAuditor(base_dir)
    
    # Ejecutar todas las auditorías
    total_issues = auditor.run_all_audits()
    
    # Mostrar resumen
    auditor.display_summary()
    
    # Generar reporte consolidado
    report = auditor.generate_consolidated_report()
    
    # Guardar reporte
    output_dir = base_dir / "outputs" / "analisis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_file = output_dir / f"auditoria_completa_dashboard_{timestamp}.md"
    
    output_file.write_text(report, encoding='utf-8')
    console.print(f"\n[green]Reporte consolidado guardado en: {output_file}[/green]")
    
    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

