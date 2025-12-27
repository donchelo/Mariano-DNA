"""
Script para comparar análisis genéticos históricos
Permite ver qué hay de nuevo entre diferentes ejecuciones del análisis
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


def load_snapshot(file_path: Path) -> Optional[Dict]:
    """
    Carga un snapshot JSON de análisis
    
    Args:
        file_path: Ruta al archivo JSON
        
    Returns:
        Diccionario con los datos del snapshot o None si hay error
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error cargando snapshot: {e}[/red]")
        return None


def is_valid_snapshot(file_path: Path) -> bool:
    """
    Verifica si un archivo JSON es un snapshot válido de análisis
    
    Args:
        file_path: Ruta al archivo JSON
        
    Returns:
        True si es un snapshot válido
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Un snapshot válido debe ser un diccionario con 'findings' y 'statistics'
        return isinstance(data, dict) and 'findings' in data and 'statistics' in data
    except:
        return False


def find_all_snapshots(base_dir: Path) -> List[Path]:
    """
    Encuentra todos los snapshots JSON disponibles
    
    Args:
        base_dir: Directorio base del proyecto
        
    Returns:
        Lista de rutas a snapshots, ordenados por fecha (más reciente primero)
    """
    snapshot_dir = base_dir / "data" / "processed"
    snapshots = []
    
    # Buscar todos los archivos JSON que parezcan snapshots
    for json_file in snapshot_dir.glob("*.json"):
        # Solo incluir snapshots válidos (con formato correcto)
        if 'snapshot' in json_file.name.lower() and is_valid_snapshot(json_file):
            snapshots.append(json_file)
    
    # Ordenar por fecha de modificación (más reciente primero)
    snapshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    return snapshots


def compare_snapshots(old_snapshot: Dict, new_snapshot: Dict) -> Dict:
    """
    Compara dos snapshots y encuentra diferencias
    
    Args:
        old_snapshot: Snapshot anterior
        new_snapshot: Snapshot nuevo
        
    Returns:
        Diccionario con las diferencias encontradas
    """
    old_findings = {f['rsid']: f for f in old_snapshot.get('findings', [])}
    new_findings = {f['rsid']: f for f in new_snapshot.get('findings', [])}
    
    old_rsids = set(old_findings.keys())
    new_rsids = set(new_findings.keys())
    
    # Hallazgos nuevos (solo en el nuevo snapshot)
    new_rsids_only = new_rsids - old_rsids
    
    # Hallazgos que desaparecieron (solo en el viejo)
    removed_rsids = old_rsids - new_rsids
    
    # Hallazgos que cambiaron
    common_rsids = old_rsids & new_rsids
    changed_findings = []
    
    for rsid in common_rsids:
        old_f = old_findings[rsid]
        new_f = new_findings[rsid]
        
        changes = []
        
        # Verificar cambios en genotipo
        if old_f.get('genotype') != new_f.get('genotype'):
            changes.append({
                'field': 'genotipo',
                'old': old_f.get('genotype'),
                'new': new_f.get('genotype')
            })
        
        # Verificar cambios en importancia
        if old_f.get('importance') != new_f.get('importance'):
            changes.append({
                'field': 'importancia',
                'old': old_f.get('importance'),
                'new': new_f.get('importance')
            })
        
        # Verificar cambios en categoría
        if old_f.get('category') != new_f.get('category'):
            changes.append({
                'field': 'categoría',
                'old': old_f.get('category'),
                'new': new_f.get('category')
            })
        
        # Verificar si ahora está en el genoma cuando antes no
        if not old_f.get('found_in_genome') and new_f.get('found_in_genome'):
            changes.append({
                'field': 'encontrado_en_genoma',
                'old': False,
                'new': True
            })
        
        if changes:
            changed_findings.append({
                'rsid': rsid,
                'changes': changes
            })
    
    # Comparar estadísticas
    old_stats = old_snapshot.get('statistics', {})
    new_stats = new_snapshot.get('statistics', {})
    
    stats_changes = {}
    for key in ['total_findings', 'found_in_genome', 'found_in_reports_only']:
        old_val = old_stats.get(key, 0)
        new_val = new_stats.get(key, 0)
        if old_val != new_val:
            stats_changes[key] = {'old': old_val, 'new': new_val}
    
    # Comparar datos epigenéticos
    old_epi = old_snapshot.get('epigenetic_data', [])
    new_epi = new_snapshot.get('epigenetic_data', [])
    epigenetic_changes = len(new_epi) - len(old_epi)
    
    return {
        'new_findings': [new_findings[rsid] for rsid in new_rsids_only],
        'removed_findings': [old_findings[rsid] for rsid in removed_rsids],
        'changed_findings': changed_findings,
        'stats_changes': stats_changes,
        'epigenetic_changes': epigenetic_changes,
        'old_timestamp': old_snapshot.get('timestamp'),
        'new_timestamp': new_snapshot.get('timestamp')
    }


def display_comparison(comparison: Dict):
    """
    Muestra la comparación en formato legible
    
    Args:
        comparison: Diccionario con los resultados de la comparación
    """
    console.print("\n[bold blue]Comparación de Análisis Genéticos[/bold blue]\n")
    
    # Información de fechas
    old_date = comparison.get('old_timestamp', 'Desconocida')
    new_date = comparison.get('new_timestamp', 'Desconocida')
    
    if old_date != 'Desconocida':
        try:
            old_dt = datetime.fromisoformat(old_date.replace('Z', '+00:00'))
            old_date = old_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    if new_date != 'Desconocida':
        try:
            new_dt = datetime.fromisoformat(new_date.replace('Z', '+00:00'))
            new_date = new_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    console.print(f"[dim]Análisis anterior:[/dim] {old_date}")
    console.print(f"[dim]Análisis nuevo:[/dim] {new_date}\n")
    
    # Hallazgos nuevos
    new_findings = comparison.get('new_findings', [])
    if new_findings:
        console.print(Panel.fit(
            f"[green][bold]{len(new_findings)} Hallazgos Nuevos[/bold][/green]",
            border_style="green"
        ))
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("rsID", style="cyan")
        table.add_column("Genotipo")
        table.add_column("Categoría")
        table.add_column("Importancia")
        
        for finding in new_findings[:10]:  # Mostrar máximo 10
            importance_marker = {
                'alto': '[red]ALTO[/red]',
                'medio': '[yellow]MEDIO[/yellow]',
                'bajo': '[green]BAJO[/green]'
            }.get(finding.get('importance', ''), finding.get('importance', 'N/A'))
            
            table.add_row(
                finding.get('rsid', 'N/A'),
                finding.get('genotype', 'N/A') or 'N/A',
                finding.get('category', 'N/A'),
                importance_marker
            )
        
        console.print(table)
        
        if len(new_findings) > 10:
            console.print(f"[dim]... y {len(new_findings) - 10} más[/dim]\n")
        else:
            console.print("")
    else:
        console.print("[dim]No hay hallazgos nuevos\n[/dim]")
    
    # Hallazgos que cambiaron
    changed = comparison.get('changed_findings', [])
    if changed:
        console.print(Panel.fit(
            f"[yellow][bold]{len(changed)} Hallazgos Modificados[/bold][/yellow]",
            border_style="yellow"
        ))
        
        for item in changed[:5]:  # Mostrar máximo 5
            rsid = item['rsid']
            changes = item['changes']
            
            console.print(f"\n[bold cyan]{rsid}[/bold cyan]")
            for change in changes:
                field = change['field']
                old_val = change.get('old', 'N/A')
                new_val = change.get('new', 'N/A')
                console.print(f"  • {field}: {old_val} → {new_val}")
        
        if len(changed) > 5:
            console.print(f"\n[dim]... y {len(changed) - 5} más modificados[/dim]")
        console.print("")
    else:
        console.print("[dim]No hay hallazgos modificados\n[/dim]")
    
    # Hallazgos removidos
    removed = comparison.get('removed_findings', [])
    if removed:
        console.print(Panel.fit(
            f"[red][bold]{len(removed)} Hallazgos Removidos[/bold][/red]",
            border_style="red"
        ))
        
        for finding in removed[:5]:  # Mostrar máximo 5
            console.print(f"  • {finding.get('rsid', 'N/A')} - {finding.get('category', 'N/A')}")
        
        if len(removed) > 5:
            console.print(f"[dim]... y {len(removed) - 5} más[/dim]")
        console.print("")
    else:
        console.print("[dim]No hay hallazgos removidos\n[/dim]")
    
    # Cambios en estadísticas
    stats_changes = comparison.get('stats_changes', {})
    if stats_changes:
        console.print(Panel.fit(
            "[bold]Cambios en Estadísticas[/bold]",
            border_style="blue"
        ))
        
        for key, change in stats_changes.items():
            key_name = {
                'total_findings': 'Total de hallazgos',
                'found_in_genome': 'Encontrados en genoma',
                'found_in_reports_only': 'Solo en reportes'
            }.get(key, key)
            
            old_val = change.get('old', 0)
            new_val = change.get('new', 0)
            diff = new_val - old_val
            
            if diff > 0:
                console.print(f"  • {key_name}: {old_val} → {new_val} ([green]+{diff}[/green])")
            elif diff < 0:
                console.print(f"  • {key_name}: {old_val} → {new_val} ([red]{diff}[/red])")
            else:
                console.print(f"  • {key_name}: {old_val} → {new_val}")
        
        console.print("")
    
    # Cambios en datos epigenéticos
    epi_changes = comparison.get('epigenetic_changes', 0)
    if epi_changes != 0:
        console.print(Panel.fit(
            f"[bold]Datos Epigenéticos[/bold]: {epi_changes:+d} reporte(s)",
            border_style="magenta"
        ))
        console.print("")


def main():
    """Función principal"""
    base_dir = Path(__file__).parent.parent.parent
    
    # Encontrar todos los snapshots
    snapshots = find_all_snapshots(base_dir)
    
    if len(snapshots) < 2:
        console.print("[yellow][WARN] Se necesitan al menos 2 snapshots para comparar[/yellow]")
        console.print(f"\nSnapshots encontrados: {len(snapshots)}")
        
        if snapshots:
            console.print("\nSnapshots disponibles:")
            for i, snapshot in enumerate(snapshots, 1):
                mtime = datetime.fromtimestamp(snapshot.stat().st_mtime)
                console.print(f"  {i}. {snapshot.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        
        console.print("\n[dim]Ejecuta el análisis primero para generar snapshots:[/dim]")
        console.print("[dim]  python src/scripts/run_analysis.py[/dim]\n")
        return
    
    # Cargar los dos más recientes
    console.print(f"[bold]Encontrados {len(snapshots)} snapshot(s)[/bold]\n")
    
    # Mostrar snapshots disponibles
    console.print("Snapshots disponibles:")
    for i, snapshot in enumerate(snapshots[:5], 1):  # Mostrar máximo 5
        mtime = datetime.fromtimestamp(snapshot.stat().st_mtime)
        console.print(f"  {i}. {snapshot.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    if len(snapshots) > 5:
        console.print(f"  ... y {len(snapshots) - 5} más\n")
    else:
        console.print("")
    
    # Comparar los dos más recientes
    old_snapshot_path = snapshots[1] if len(snapshots) > 1 else snapshots[0]
    new_snapshot_path = snapshots[0]
    
    console.print(f"[dim]Comparando:[/dim]")
    console.print(f"[dim]  Anterior: {old_snapshot_path.name}[/dim]")
    console.print(f"[dim]  Nuevo: {new_snapshot_path.name}[/dim]\n")
    
    old_snapshot = load_snapshot(old_snapshot_path)
    new_snapshot = load_snapshot(new_snapshot_path)
    
    if not old_snapshot or not new_snapshot:
        console.print("[red]Error: No se pudieron cargar los snapshots[/red]")
        return
    
    # Comparar
    comparison = compare_snapshots(old_snapshot, new_snapshot)
    
    # Mostrar resultados
    display_comparison(comparison)
    
    # Resumen final
    total_changes = (
        len(comparison.get('new_findings', [])) +
        len(comparison.get('removed_findings', [])) +
        len(comparison.get('changed_findings', []))
    )
    
    if total_changes == 0:
        console.print("[green][OK] No hay cambios entre los analisis[/green]\n")
    else:
        console.print(f"[bold]Resumen: {total_changes} cambio(s) detectado(s)[/bold]\n")


if __name__ == "__main__":
    main()

