#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para parsear el archivo HTML de Promethease y generar un JSON estructurado.

Extrae datos comprimidos en JavaScript, los descomprime y genera un JSON
con todos los hallazgos genéticos organizados.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.dna_analyzer.pdf_extractor import PrometheaseHTMLParser


def parse_metadata_file(metadata_path: Path) -> Dict[str, Any]:
    """
    Parsea el archivo de metadatos de Promethease.
    
    Args:
        metadata_path: Ruta al archivo report_metadata.txt
        
    Returns:
        Diccionario con metadatos parseados
    """
    import re
    metadata = {}
    
    if not metadata_path.exists():
        return metadata
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parsear versión
        version_match = re.search(r'Version\s+([\d.]+)', content)
        if version_match:
            metadata['version'] = version_match.group(1)
        
        # Parsear archivo fuente
        source_match = re.search(r'Analyzed\s+([\w_\-\.]+\.txt)', content)
        if source_match:
            metadata['source_file'] = source_match.group(1)
        
        # Parsear fecha
        date_match = re.search(r'On\s+([\d\-\s:\.]+)\s+UTC', content)
        if date_match:
            metadata['analysis_date'] = date_match.group(1).strip()
        
        # Parsear número de genos
        genos_match = re.search(r'Found\s+(\d+)\s+SNPedia genos', content)
        if genos_match:
            metadata['total_snpedia_genos'] = int(genos_match.group(1))
    
    except Exception as e:
        print(f"⚠ Advertencia: Error parseando metadatos: {e}")
    
    return metadata


def extract_metadata_from_html(html_path: Path, parser: PrometheaseHTMLParser) -> Dict[str, Any]:
    """
    Extrae metadatos directamente del HTML.
    
    Args:
        html_path: Ruta al archivo HTML
        parser: Instancia del parser
        
    Returns:
        Diccionario con metadatos extraídos del HTML
    """
    import re
    metadata = {}
    
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extraer metainfo del JavaScript
        metainfo_data = parser._extract_js_variable(content, 'metainfo')
        if metainfo_data:
            parsed_metainfo = parser._parse_js_object(metainfo_data)
            metadata.update(parsed_metainfo)
        
        # Buscar información adicional en el HTML
        if 'generation_date' in content:
            # Extraer fecha de generación
            date_match = re.search(
                r'generation_date\.setUTCFullYear\((\d+)\).*?setUTCMonth\((\d+)\).*?setUTCDate\((\d+)\)',
                content,
                re.DOTALL
            )
            if date_match:
                year = date_match.group(1)
                month = int(date_match.group(2)) + 1  # JavaScript months are 0-indexed
                day = date_match.group(3)
                metadata['generation_date'] = f"{year}-{month:02d}-{day}"
        
        # Buscar versión
        version_match = re.search(r'version:\s*["\']([^"\']+)["\']', content)
        if version_match:
            metadata['version'] = version_match.group(1)
    
    except Exception as e:
        print(f"⚠ Advertencia: Error extrayendo metadatos del HTML: {e}")
    
    return metadata


def calculate_statistics(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula estadísticas sobre las entradas parseadas.
    
    Args:
        entries: Lista de entradas genéticas
        
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        'total_entries': len(entries),
        'snps': 0,
        'genosets': 0,
        'with_medical_conditions': 0,
        'with_repute_good': 0,
        'with_repute_bad': 0,
        'with_magnitude_high': 0,  # magnitude >= 3
    }
    
    for entry in entries:
        record_type = entry.get('record_type', '')
        if record_type == 'snp':
            stats['snps'] += 1
        elif record_type == 'genoset':
            stats['genosets'] += 1
        
        if entry.get('medical_conditions'):
            stats['with_medical_conditions'] += 1
        
        repute = entry.get('repute')
        if repute == 'Good':
            stats['with_repute_good'] += 1
        elif repute == 'Bad':
            stats['with_repute_bad'] += 1
        
        magnitude = entry.get('magnitude')
        if magnitude and isinstance(magnitude, (int, float)) and magnitude >= 3:
            stats['with_magnitude_high'] += 1
    
    return stats


def main():
    """Función principal del script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Parsea archivo HTML de Promethease y genera JSON estructurado'
    )
    parser.add_argument(
        'html_file',
        type=str,
        help='Ruta al archivo HTML de Promethease'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Ruta del archivo JSON de salida (por defecto: data/processed/promethease_parsed_[timestamp].json)'
    )
    parser.add_argument(
        '--metadata-file',
        type=str,
        default=None,
        help='Ruta al archivo de metadatos report_metadata.txt (opcional)'
    )
    
    args = parser.parse_args()
    
    # Resolver rutas
    base_dir = Path(__file__).parent.parent.parent
    html_path = Path(args.html_file)
    
    if not html_path.is_absolute():
        html_path = base_dir / html_path
    
    if not html_path.exists():
        print(f"[ERROR] No se encontro el archivo HTML: {html_path}")
        sys.exit(1)
    
    # Determinar ruta de metadatos
    if args.metadata_file:
        metadata_path = Path(args.metadata_file)
        if not metadata_path.is_absolute():
            metadata_path = base_dir / metadata_path
    else:
        # Buscar en el mismo directorio que el HTML
        metadata_path = html_path.parent / 'report_metadata.txt'
    
    # Determinar ruta de salida
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = base_dir / output_path
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = base_dir / 'data' / 'processed' / f'promethease_parsed_{timestamp}.json'
    
    # Asegurar que el directorio de salida existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Parseando archivo HTML: {html_path}")
    print(f"[*] Generando JSON en: {output_path}")
    
    # Parsear metadatos
    print("\n[*] Extrayendo metadatos...")
    metadata = {}
    
    # Metadatos del archivo de texto
    if metadata_path.exists():
        print(f"  - Leyendo metadatos de: {metadata_path}")
        file_metadata = parse_metadata_file(metadata_path)
        metadata.update(file_metadata)
    
    # Parsear HTML
    print("\n[*] Parseando HTML y extrayendo datos genéticos...")
    promethease_parser = PrometheaseHTMLParser()
    
    try:
        entries = promethease_parser.parse(str(html_path))
        print(f"  [OK] {len(entries)} entradas extraidas")
        
        # Extraer metadatos adicionales del HTML
        html_metadata = extract_metadata_from_html(html_path, promethease_parser)
        if html_metadata:
            metadata.update(html_metadata)
            print(f"  [OK] Metadatos adicionales extraidos del HTML")
        
    except Exception as e:
        print(f"[ERROR] Error parseando HTML: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Calcular estadísticas
    print("\n[*] Calculando estadisticas...")
    stats = calculate_statistics(entries)
    print(f"  - Total de entradas: {stats['total_entries']}")
    print(f"  - SNPs: {stats['snps']}")
    print(f"  - Genosets: {stats['genosets']}")
    print(f"  - Con condiciones medicas: {stats['with_medical_conditions']}")
    
    # Construir estructura JSON final
    print("\n[*] Generando JSON estructurado...")
    result = {
        'metadata': {
            'source': 'promethease',
            'version': metadata.get('version', 'unknown'),
            'analysis_date': metadata.get('analysis_date') or metadata.get('generation_date'),
            'source_file': metadata.get('source_file') or html_path.name,
            'total_snpedia_genos': metadata.get('total_snpedia_genos', len(entries)),
            'parsed_date': datetime.now().isoformat(),
            'html_file': str(html_path.relative_to(base_dir)) if html_path.is_relative_to(base_dir) else str(html_path),
        },
        'entries': entries,
        'statistics': stats
    }
    
    # Guardar JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] JSON generado exitosamente: {output_path}")
        print(f"   - {len(entries)} entradas guardadas")
        print(f"   - Tamano del archivo: {output_path.stat().st_size / 1024:.2f} KB")
        
    except Exception as e:
        print(f"[ERROR] Error guardando JSON: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

