#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir el reporte de texto de Promethease a formato JSON estructurado.
"""

import re
import json
from typing import Dict, List, Optional, Any

def parse_genetic_data(input_file: str, output_file: str) -> None:
    """
    Procesa el archivo de texto de Promethease y genera un JSON estructurado.
    
    Args:
        input_file: Ruta al archivo de texto de entrada
        output_file: Ruta al archivo JSON de salida
    """
    entries = []
    current_entry: Optional[Dict[str, Any]] = None
    description_lines = []
    in_description = False
    skip_population_freq = False
    
    # Patrones para identificar campos
    field_patterns = {
        'repute': re.compile(r'^(Good|Bad|Not Set)\s+Repute$', re.IGNORECASE),
        'magnitude': re.compile(r'^([\d.]+)\s+Magnitude$', re.IGNORECASE),
        'frequency': re.compile(r'^([\d.%]+)\s+Frequency$', re.IGNORECASE),
        'chromosome': re.compile(r'^([\dXY]+)\s+Chromosome$', re.IGNORECASE),
        'position': re.compile(r'^(\d+)\s+Position$', re.IGNORECASE),
        'genes': re.compile(r'^(.+?)\s+Genes$', re.IGNORECASE),
        'publications': re.compile(r'^(\d+)\s+Publications$', re.IGNORECASE),
        'gmaf': re.compile(r'^([\d.]+)\s+GMAF$', re.IGNORECASE),
        'max_magnitude': re.compile(r'^([\d.]+)\s+Max Magnitude$', re.IGNORECASE),
        'geno_modified': re.compile(r'^(\d{4}-\d{2}-\d{2})\s+Geno (modified|Modified)$', re.IGNORECASE),
        'rs_modified': re.compile(r'^(\d{4}-\d{2}-\d{2})\s+Rs Modified$', re.IGNORECASE),
        'stabilized': re.compile(r'^(plus|minus)\s+Stabilized$', re.IGNORECASE),
        'orientation': re.compile(r'^(plus|minus)\s+Orientation$', re.IGNORECASE),
        'clinvar': re.compile(r'^(.+?)\s+ClinVar Significance$', re.IGNORECASE),
    }
    
    # Patrones para identificar IDs de registros (solo al inicio de línea, no dentro de texto)
    record_id_pattern = re.compile(r'^(rs\d+|gs\d+)(\([^)]+\))?\s*$')
    
    # Poblaciones conocidas (para saltar estas líneas)
    known_populations = {'TSI', 'MKK', 'MEX', 'LWK', 'GIH', 'CHD', 'ASW', 'YRI', 
                        'JPT', 'HCB', 'CEU'}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Saltar líneas vacías y encabezados
        if not line or line.startswith('×') or line in ['Genes', 'Search', 'Promethease', 
                                                        'Main', 'Blood', 'Show:', 'Repute:', 
                                                        'Magnitude:', 'Publications:', 
                                                        'Frequency:', 'Require:', 'UI:', 
                                                        'Allow', 'Visible', 'Offscreen', 
                                                        'Vision:', 'Normal', 'increase minimum mag']:
            i += 1
            continue
        
        # Detectar inicio de nuevo registro
        match = record_id_pattern.match(line)
        if match:
            # Guardar entrada anterior si existe
            if current_entry is not None:
                if description_lines:
                    current_entry['description'] = ' '.join(description_lines).strip()
                entries.append(current_entry)
            
            # Inicializar nueva entrada
            record_id = match.group(1)
            genotype = match.group(2) if match.group(2) else ''
            current_entry = {
                'id': record_id + genotype,
                'record_id': record_id,
                'genotype': genotype.strip('()') if genotype else None,
                'summary': '',
                'description': '',
                'repute': None,
                'magnitude': None,
                'frequency': None,
                'chromosome': None,
                'position': None,
                'genes': [],
                'publications': None,
                'gmaf': None,
                'max_magnitude': None,
                'geno_modified': None,
                'rs_modified': None,
                'stabilized': None,
                'orientation': None,
                'clinvar_significance': None,
                'topics': [],
                'medical_conditions': [],
                'other_fields': {}
            }
            description_lines = []
            in_description = False
            skip_population_freq = False
            i += 1
            continue
        
        # Si no hay entrada actual, saltar
        if current_entry is None:
            i += 1
            continue
        
        # Detectar línea de Topics
        if line.startswith('Topics '):
            topics = line.replace('Topics ', '').split()
            current_entry['topics'] = topics
            i += 1
            continue
        
        # Detectar líneas de poblaciones (saltar estas secciones)
        if line in known_populations:
            skip_population_freq = True
            i += 1
            continue
        
        if skip_population_freq:
            # Saltar números de frecuencia poblacional
            if re.match(r'^[\d.]+$', line) or line == '0' or line == '100':
                i += 1
                continue
            else:
                skip_population_freq = False
        
        # Intentar hacer match con patrones de campos
        matched = False
        for field_name, pattern in field_patterns.items():
            match = pattern.match(line)
            if match:
                matched = True
                value = match.group(1)
                
                # Procesar según el tipo de campo
                if field_name == 'genes':
                    # Los genes pueden estar separados por espacios
                    genes = [g.strip() for g in value.split() if g.strip()]
                    current_entry['genes'].extend(genes)
                elif field_name == 'magnitude':
                    try:
                        current_entry['magnitude'] = float(value)
                    except ValueError:
                        pass
                elif field_name == 'max_magnitude':
                    try:
                        current_entry['max_magnitude'] = float(value)
                    except ValueError:
                        pass
                elif field_name == 'frequency':
                    current_entry['frequency'] = value
                elif field_name == 'position':
                    try:
                        current_entry['position'] = int(value)
                    except ValueError:
                        current_entry['position'] = value
                elif field_name == 'publications':
                    try:
                        current_entry['publications'] = int(value)
                    except ValueError:
                        pass
                elif field_name == 'gmaf':
                    try:
                        current_entry['gmaf'] = float(value)
                    except ValueError:
                        pass
                elif field_name == 'chromosome':
                    current_entry['chromosome'] = value
                else:
                    current_entry[field_name] = value
                break
        
        if not matched:
            # Si no coincide con ningún patrón, es parte de la descripción
            # Detectar si es un resumen corto (primera línea después del ID)
            if not current_entry['summary'] and line and not line.startswith(' more info'):
                # Verificar si parece un resumen (línea corta, no fecha, no número solo)
                if len(line) < 200 and not re.match(r'^\d{4}-\d{2}-\d{2}', line) and not re.match(r'^[\d.]+$', line):
                    current_entry['summary'] = line
                else:
                    description_lines.append(line)
            elif not line.startswith(' more info'):
                description_lines.append(line)
        
        i += 1
    
    # Guardar última entrada
    if current_entry is not None:
        if description_lines:
            current_entry['description'] = ' '.join(description_lines).strip()
        entries.append(current_entry)
    
    # Extraer condiciones médicas de topics y descripciones
    medical_keywords = [
        'Alzheimer', 'diabetes', 'cancer', 'carcinoma', 'leukemia', 'tumor',
        'disease', 'syndrome', 'disorder', 'allergy', 'asthma', 'arthritis',
        'sclerosis', 'baldness', 'gout', 'obesity', 'hypertension', 'stroke',
        'heart', 'cardiovascular', 'coronary', 'myocardial', 'infarction',
        'glaucoma', 'macular', 'degeneration', 'thyroid', 'prostate', 'breast',
        'colorectal', 'pancreatic', 'lung', 'bladder', 'ovarian', 'endometrial',
        'Crohn', 'ulcerative', 'colitis', 'lupus', 'Graves', 'Parkinson',
        'bipolar', 'autism', 'schizophrenia', 'migraine', 'depression', 'dementia',
        'osteoporosis', 'osteoarthritis', 'anemia', 'homocysteine', 'prion',
        'narcolepsy', 'restless', 'legs', 'scoliosis', 'otosclerosis', 'myopia'
    ]
    
    for entry in entries:
        medical_conditions = set()
        
        # Buscar en topics
        for topic in entry.get('topics', []):
            for keyword in medical_keywords:
                if keyword.lower() in topic.lower():
                    medical_conditions.add(topic)
        
        # Buscar en descripción
        desc = entry.get('description', '').lower()
        summary = entry.get('summary', '').lower()
        combined_text = desc + ' ' + summary
        
        for keyword in medical_keywords:
            if keyword.lower() in combined_text:
                # Intentar extraer el término completo
                pattern = re.compile(rf'\b\w*{keyword}\w*\b', re.IGNORECASE)
                matches = pattern.findall(combined_text)
                medical_conditions.update([m.title() for m in matches])
        
        entry['medical_conditions'] = sorted(list(medical_conditions))
    
    # Guardar JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    
    print(f"Procesadas {len(entries)} entradas geneticas")
    print(f"Archivo JSON guardado en: {output_file}")

if __name__ == '__main__':
    from pathlib import Path
    
    # Rutas relativas a la raíz del proyecto
    base_dir = Path(__file__).parent.parent.parent
    input_file = base_dir / "data" / "raw" / "reportes_proveedores" / "promethease" / "prometheus txt.txt"
    output_file = base_dir / "data" / "processed" / "hallazgos_geneticos.json"
    
    # Asegurar que el directorio de salida existe
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        parse_genetic_data(str(input_file), str(output_file))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file}")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        import traceback
        traceback.print_exc()

