"""
Script de auditoría de biomarcadores del dashboard
Valida datos de exámenes de sangre
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


class BiomarkersAuditor:
    """Auditor de biomarcadores del dashboard"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.issues: List[Dict] = []
        
    def audit_parsed_files(self):
        """Valida archivos JSON parseados"""
        console.print("\n[bold blue]Auditando archivos parseados...[/bold blue]")
        
        blood_test_dir = self.base_dir / "data" / "raw" / "examenes_sangre"
        if not blood_test_dir.exists():
            self.issues.append({
                'type': 'missing_directory',
                'issue': 'No se encontró directorio de exámenes de sangre'
            })
            return
        
        json_files = list(blood_test_dir.glob("*_parsed.json"))
        if not json_files:
            self.issues.append({
                'type': 'no_parsed_files',
                'issue': 'No se encontraron archivos JSON parseados'
            })
            return
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validar estructura básica
                if not isinstance(data, dict):
                    self.issues.append({
                        'file': json_file.name,
                        'type': 'invalid_structure',
                        'issue': 'Archivo JSON no es un diccionario'
                    })
                    continue
                
                # Validar que tenga fecha
                if 'date' not in data and 'fecha' not in data:
                    self.issues.append({
                        'file': json_file.name,
                        'type': 'missing_date',
                        'issue': 'Archivo no tiene campo de fecha'
                    })
                
                # Validar que tenga resultados
                if 'results' not in data and 'resultados' not in data:
                    self.issues.append({
                        'file': json_file.name,
                        'type': 'missing_results',
                        'issue': 'Archivo no tiene campo de resultados'
                    })
                
            except json.JSONDecodeError as e:
                self.issues.append({
                    'file': json_file.name,
                    'type': 'json_error',
                    'issue': f'Error parseando JSON: {e}'
                })
            except Exception as e:
                self.issues.append({
                    'file': json_file.name,
                    'type': 'error',
                    'issue': f'Error: {e}'
                })
    
    def generate_report(self) -> str:
        report_lines = [
            "# Auditoría de Biomarcadores del Dashboard",
            "",
            "## Resumen",
            f"- **Problemas encontrados:** {len(self.issues)}",
            "",
            "---",
            ""
        ]
        
        if self.issues:
            for issue in self.issues:
                report_lines.append(f"### {issue.get('file', 'General')}")
                report_lines.append(f"- **Tipo:** {issue['type']}")
                report_lines.append(f"- **Problema:** {issue['issue']}")
                report_lines.append("")
        else:
            report_lines.append("**✅ No se encontraron problemas**")
        
        return '\n'.join(report_lines)
    
    def run_audit(self) -> bool:
        self.audit_parsed_files()
        return True


def main():
    base_dir = Path(__file__).parent.parent.parent
    auditor = BiomarkersAuditor(base_dir)
    
    if auditor.run_audit():
        report = auditor.generate_report()
        output_dir = base_dir / "outputs" / "analisis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"auditoria_biomarkers_dashboard_{timestamp}.md"
        output_file.write_text(report, encoding='utf-8')
        console.print(f"[green]Reporte guardado: {output_file}[/green]")
    return 0


if __name__ == '__main__':
    sys.exit(main())

