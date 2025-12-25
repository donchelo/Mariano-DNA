"""
Script principal para ejecutar el análisis genético completo
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Agregar el directorio src al path para importar dna_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.snp_database import SNPDatabase
from dna_analyzer.pdf_extractor import ReportExtractor
from dna_analyzer.analyzer import GeneticAnalyzer
from dna_analyzer.report_generator import ReportGenerator

console = Console()


def find_genome_file(base_dir: Path) -> Optional[Path]:
    """
    Busca automáticamente el archivo de genoma en el directorio de genoma
    
    Args:
        base_dir: Directorio base del proyecto
        
    Returns:
        Ruta al archivo de genoma encontrado, o None si no se encuentra
    """
    genome_dir = base_dir / "data" / "raw" / "genome"
    
    if not genome_dir.exists():
        return None
    
    # Buscar archivos .txt en el directorio y subdirectorios
    txt_files = list(genome_dir.rglob("*.txt"))
    
    # Filtrar archivos que parezcan ser genomas (contienen "genome" o tienen estructura 23andMe)
    for txt_file in txt_files:
        # Verificar si el archivo parece ser un genoma (contiene rsid en las primeras líneas)
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                first_lines = ''.join(f.readlines()[:10])
                if 'rsid' in first_lines.lower() or 'rs' in first_lines[:100]:
                    return txt_file
        except:
            continue
    
    # Si no encontramos uno específico, devolver el primero .txt encontrado
    if txt_files:
        return txt_files[0]
    
    return None


def discover_report_files(base_dir: Path) -> Dict[str, List[Path]]:
    """
    Descubre automáticamente archivos de reportes en el directorio de reportes
    
    Args:
        base_dir: Directorio base del proyecto
        
    Returns:
        Diccionario con listas de archivos por tipo
    """
    reports_dir = base_dir / "data" / "raw" / "reportes_proveedores"
    
    discovered = {
        'promethease_html': [],
        'promethease_json': [],
        'genetic_genie': [],
        'nutrahacker': [],
        'foundmyfitness': [],
        'epigenetic': [],
        'other': []
    }
    
    if not reports_dir.exists():
        return discovered
    
    # Buscar en el directorio principal y subdirectorios
    for file_path in reports_dir.rglob("*"):
        if not file_path.is_file():
            continue
        
        name_lower = file_path.name.lower()
        
        # Promethease
        if 'promethease' in name_lower:
            if file_path.suffix.lower() == '.html':
                discovered['promethease_html'].append(file_path)
            elif file_path.suffix.lower() == '.json':
                discovered['promethease_json'].append(file_path)
        
        # Genetic Genie
        elif 'genetic_genie' in name_lower or 'geneticgenie' in name_lower:
            if file_path.suffix.lower() == '.pdf':
                discovered['genetic_genie'].append(file_path)
        
        # NutraHacker
        elif 'nutrahacker' in name_lower or 'nutra_hacker' in name_lower:
            if file_path.suffix.lower() == '.pdf':
                discovered['nutrahacker'].append(file_path)
        
        # FoundMyFitness
        elif 'foundmyfitness' in name_lower or 'found_my_fitness' in name_lower:
            if file_path.suffix.lower() == '.pdf':
                discovered['foundmyfitness'].append(file_path)
        
        # Epigenetic
        elif any(kw in name_lower for kw in ['epigenetic', 'wellmultid', 'trudiagnostic', 'elysium']):
            if file_path.suffix.lower() == '.pdf':
                discovered['epigenetic'].append(file_path)
        
        # Otros PDFs
        elif file_path.suffix.lower() == '.pdf':
            discovered['other'].append(file_path)
    
    return discovered


def save_analysis_snapshot(findings: List, statistics: Dict, epigenetic_data: List, 
                          output_file: Path) -> None:
    """
    Guarda un snapshot JSON del análisis completo para comparaciones históricas
    
    Args:
        findings: Lista de hallazgos genéticos
        statistics: Estadísticas del análisis
        epigenetic_data: Datos epigenéticos encontrados
        output_file: Ruta al archivo JSON de salida
    """
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'statistics': statistics,
        'findings': [
            {
                'rsid': f.rsid,
                'genotype': f.genotype,
                'category': f.category,
                'importance': f.importance,
                'description': f.description,
                'implications': f.implications,
                'found_in_genome': f.found_in_genome,
                'found_in_reports': f.found_in_reports,
                'report_sources': f.report_sources,
                'magnitude': f.magnitude,
                'repute': f.repute,
                'genes': f.genes,
                'related_conditions': f.related_conditions
            }
            for f in findings
        ],
        'epigenetic_data': epigenetic_data
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green][OK] Snapshot JSON guardado: {output_file}[/green]")


def main():
    """Función principal"""
    console.print("\n[bold blue]Sistema de Analisis Genetico Integral[/bold blue]\n")
    
    # Rutas de archivos - base_dir apunta a la raíz del proyecto
    base_dir = Path(__file__).parent.parent.parent
    
    # Buscar archivo de genoma automáticamente
    console.print("[bold cyan]Buscando archivo de genoma...[/bold cyan]")
    genome_file = find_genome_file(base_dir)
    
    if not genome_file:
        console.print(f"[bold red][ERROR] No se encontró archivo de genoma[/bold red]")
        console.print(f"   Buscar en: {base_dir / 'data' / 'raw' / 'genome'}")
        sys.exit(1)
    
    console.print(f"[green][OK] Genoma encontrado: {genome_file.name}[/green]\n")
    
    # Descubrir archivos de reportes automáticamente
    console.print("[bold cyan]Descubriendo archivos de reportes...[/bold cyan]")
    discovered_reports = discover_report_files(base_dir)
    
    # Mostrar resumen de archivos encontrados
    total_found = sum(len(files) for files in discovered_reports.values())
    if total_found > 0:
        console.print(f"[green][OK] Encontrados {total_found} archivo(s) de reportes:[/green]")
        for report_type, files in discovered_reports.items():
            if files:
                console.print(f"  - {report_type}: {len(files)} archivo(s)")
    else:
        console.print("[yellow]⚠ No se encontraron archivos de reportes[/yellow]")
    console.print("")
    
    output_file = base_dir / "outputs" / "analisis" / "hallazgos_geneticos_completos.md"
    json_snapshot_file = base_dir / "data" / "processed" / "full_analysis_snapshot.json"
    
    # También buscar JSON de Promethease en processed
    promethease_json_processed = base_dir / "data" / "processed" / "hallazgos_geneticos.json"
    
    try:
        # Paso 1: Parsear genoma
        console.print("[bold cyan]Paso 1: Parseando archivo de genoma...[/bold cyan]")
        parser = GenomeParser(str(genome_file))
        parser.parse()
        console.print("[green][OK] Genoma parseado correctamente[/green]\n")
        
        # Paso 2: Cargar base de datos de SNPs
        console.print("[bold cyan]Paso 2: Cargando base de datos de SNPs importantes...[/bold cyan]")
        snp_db = SNPDatabase()
        console.print("[green][OK] Base de datos cargada[/green]\n")
        
        # Paso 3: Extraer información de reportes existentes
        console.print("[bold cyan]Paso 3: Extrayendo informacion de reportes existentes...[/bold cyan]")
        extractor = ReportExtractor()
        
        # Procesar Promethease JSON (prioritario, más completo)
        if promethease_json_processed.exists():
            console.print("  - Cargando Promethease JSON (processed)...")
            extractor.extract_file(str(promethease_json_processed))
        elif discovered_reports['promethease_json']:
            for json_file in discovered_reports['promethease_json']:
                console.print(f"  - Cargando Promethease JSON: {json_file.name}")
                extractor.extract_file(str(json_file))
        elif discovered_reports['promethease_html']:
            for html_file in discovered_reports['promethease_html']:
                console.print(f"  - Cargando Promethease HTML: {html_file.name}")
                extractor.extract_file(str(html_file))
        else:
            console.print("  - [WARN] Promethease no encontrado, omitiendo...")
        
        # Procesar Genetic Genie
        if discovered_reports['genetic_genie']:
            for pdf_file in discovered_reports['genetic_genie']:
                console.print(f"  - Extrayendo Genetic Genie: {pdf_file.name}")
                extractor.extract_file(str(pdf_file))
        else:
            console.print("  - [WARN] Genetic Genie no encontrado, omitiendo...")
        
        # Procesar NutraHacker
        if discovered_reports['nutrahacker']:
            for pdf_file in discovered_reports['nutrahacker']:
                console.print(f"  - Extrayendo NutraHacker: {pdf_file.name}")
                extractor.extract_file(str(pdf_file))
        else:
            console.print("  - [WARN] NutraHacker no encontrado, omitiendo...")
        
        # Procesar FoundMyFitness
        if discovered_reports['foundmyfitness']:
            for pdf_file in discovered_reports['foundmyfitness']:
                console.print(f"  - Extrayendo FoundMyFitness: {pdf_file.name}")
                extractor.extract_file(str(pdf_file))
        
        # Procesar datos epigenéticos
        epigenetic_data = []
        if discovered_reports['epigenetic']:
            for pdf_file in discovered_reports['epigenetic']:
                console.print(f"  - Extrayendo datos epigenéticos: {pdf_file.name}")
                findings = extractor.extract_file(str(pdf_file))
                epigenetic_data.extend(findings)
        else:
            console.print("  - [INFO] No se encontraron reportes epigenéticos")
        
        console.print("[green][OK] Extraccion de reportes completada[/green]\n")
        
        # Paso 4: Ejecutar análisis
        console.print("[bold cyan]Paso 4: Ejecutando analisis genetico...[/bold cyan]")
        analyzer = GeneticAnalyzer(parser, snp_db, extractor)
        findings = analyzer.analyze()
        statistics = analyzer.get_statistics()
        console.print("[green][OK] Analisis completado[/green]\n")
        
        # Paso 5: Generar reporte
        console.print("[bold cyan]Paso 5: Generando reporte...[/bold cyan]")
        generator = ReportGenerator(findings, statistics, epigenetic_data)
        report_content = generator.generate()
        
        # Asegurar que el directorio de salida existe
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        console.print(f"[green][OK] Reporte generado: {output_file}[/green]\n")
        
        # Paso 6: Guardar snapshot JSON
        console.print("[bold cyan]Paso 6: Guardando snapshot JSON...[/bold cyan]")
        save_analysis_snapshot(findings, statistics, epigenetic_data, json_snapshot_file)
        console.print("")
        
        # Resumen final
        console.print("[bold green]Analisis completado exitosamente![/bold green]\n")
        console.print(f"[bold]Resumen:[/bold]")
        console.print(f"  - Total de hallazgos: {statistics['total_findings']}")
        console.print(f"  - Encontrados en genoma: {statistics['found_in_genome']}")
        console.print(f"  - Solo en reportes: {statistics['found_in_reports_only']}")
        if epigenetic_data:
            console.print(f"  - Reportes epigenéticos procesados: {len(epigenetic_data)}")
        console.print(f"\n[bold]Reporte guardado en:[/bold] {output_file}")
        console.print(f"[bold]Snapshot JSON guardado en:[/bold] {json_snapshot_file}")
        console.print("\n")
        
    except Exception as e:
        console.print(f"[bold red][ERROR] Error durante el analisis:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
