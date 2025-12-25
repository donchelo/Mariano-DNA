"""
Script principal para ejecutar el análisis genético completo
"""

import sys
from pathlib import Path
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


def main():
    """Función principal"""
    console.print("\n[bold blue]Sistema de Analisis Genetico Integral[/bold blue]\n")
    
    # Rutas de archivos - base_dir apunta a la raíz del proyecto
    base_dir = Path(__file__).parent.parent.parent
    genome_file = base_dir / "data" / "raw" / "genome" / "genome_Mariano_GarciaPosada_v5_Full_20251222055341" / "genome_Mariano_GarciaPosada_v5_Full_20251224060852.txt"
    promethease_html = base_dir / "data" / "raw" / "reports" / "promethease" / "promethease.html"
    genetic_genie_methylation = base_dir / "data" / "raw" / "reports" / "Genetic_Genie_Methylation_Profile_Mariano_GarciaPosada.pdf"
    genetic_genie_detox = base_dir / "data" / "raw" / "reports" / "Genetic_Genie_Detox_Profile_Mariano_GarciaPosada.pdf"
    nutrahacker_pdf = base_dir / "data" / "raw" / "reports" / "NutraHacker_Detox_and_Methylation_Report_Customer_c7a04215-7b3e-4dd0-879e-c9bb5eb35d4a.pdf"
    output_file = base_dir / "reports" / "Hallazgos_Geneticos_Completos.md"
    
    # Verificar que existan los archivos necesarios
    if not genome_file.exists():
        console.print(f"[bold red][ERROR] Error: No se encuentra el archivo de genoma[/bold red]")
        console.print(f"   Buscado en: {genome_file}")
        sys.exit(1)
    
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
        
        # Cargar JSON de Promethease (prioritario, más completo)
        promethease_json = base_dir / "data" / "processed" / "hallazgos_geneticos.json"
        if promethease_json.exists():
            console.print("  - Cargando Promethease JSON...")
            extractor.extract_promethease_json(str(promethease_json))
        elif promethease_html.exists():
            console.print("  - [WARN] JSON no encontrado, usando Promethease HTML...")
            extractor.extract_promethease_html(str(promethease_html))
        else:
            console.print("  - [WARN] Promethease no encontrado (ni JSON ni HTML), omitiendo...")
        
        if genetic_genie_methylation.exists():
            console.print("  - Extrayendo Genetic Genie Methylation...")
            extractor.extract_genetic_genie(str(genetic_genie_methylation))
        else:
            console.print("  - [WARN] Genetic Genie Methylation no encontrado, omitiendo...")
        
        if genetic_genie_detox.exists():
            console.print("  - Extrayendo Genetic Genie Detox...")
            extractor.extract_genetic_genie(str(genetic_genie_detox))
        else:
            console.print("  - [WARN] Genetic Genie Detox no encontrado, omitiendo...")
        
        if nutrahacker_pdf.exists():
            console.print("  - Extrayendo NutraHacker...")
            extractor.extract_nutrahacker(str(nutrahacker_pdf))
        else:
            console.print("  - [WARN] NutraHacker PDF no encontrado, omitiendo...")
        
        console.print("[green][OK] Extraccion de reportes completada[/green]\n")
        
        # Paso 4: Ejecutar análisis
        console.print("[bold cyan]Paso 4: Ejecutando analisis genetico...[/bold cyan]")
        analyzer = GeneticAnalyzer(parser, snp_db, extractor)
        findings = analyzer.analyze()
        statistics = analyzer.get_statistics()
        console.print("[green][OK] Analisis completado[/green]\n")
        
        # Paso 5: Generar reporte
        console.print("[bold cyan]Paso 5: Generando reporte...[/bold cyan]")
        generator = ReportGenerator(findings, statistics)
        report_content = generator.generate()
        
        # Asegurar que el directorio de salida existe
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        console.print(f"[green][OK] Reporte generado: {output_file}[/green]\n")
        
        # Resumen final
        console.print("[bold green]Analisis completado exitosamente![/bold green]\n")
        console.print(f"[bold]Resumen:[/bold]")
        console.print(f"  - Total de hallazgos: {statistics['total_findings']}")
        console.print(f"  - Encontrados en genoma: {statistics['found_in_genome']}")
        console.print(f"  - Solo en reportes: {statistics['found_in_reports_only']}")
        console.print(f"\n[bold]Reporte guardado en:[/bold] {output_file}")
        console.print("\n")
        
    except Exception as e:
        console.print(f"[bold red][ERROR] Error durante el analisis:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

