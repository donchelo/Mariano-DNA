"""
Parser para exámenes de sangre (laboratorios clínicos)
Extrae resultados de exámenes de sangre en formato organizado
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import pdfplumber


class BloodTestParser:
    """Parser para exámenes de sangre de laboratorios clínicos (Vitalea, etc.)"""
    
    def __init__(self):
        self.patient_info = {}
        self.test_results = []
        self.laboratory_info = {}
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parsea un PDF de examen de sangre y extrae toda la información
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con información del paciente, laboratorio y resultados
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                    
                    # Intentar extraer tablas (más preciso que texto plano)
                    tables = page.extract_tables()
                    if tables:
                        self._parse_tables(tables)
            
            # Extraer información del paciente
            self._extract_patient_info(full_text)
            
            # Extraer información del laboratorio
            self._extract_laboratory_info(full_text)
            
            # Extraer resultados de exámenes del texto (si no se encontraron en tablas)
            if not self.test_results:
                self._extract_test_results(full_text)
            
            return {
                'patient': self.patient_info,
                'laboratory': self.laboratory_info,
                'test_results': self.test_results,
                'metadata': {
                    'file_name': Path(pdf_path).name,
                    'parsed_date': datetime.now().isoformat(),
                    'total_tests': len(self.test_results)
                }
            }
            
        except Exception as e:
            print(f"[ERROR] Error parseando PDF: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _parse_tables(self, tables: List):
        """Intenta parsear tablas extraídas del PDF"""
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Buscar header con "Examen", "Resultado", "Unidades", "Valores de referencia"
            header_row = None
            for i, row in enumerate(table):
                if row and any(cell and ('examen' in str(cell).lower() or 'resultado' in str(cell).lower()) for cell in row):
                    header_row = i
                    break
            
            if header_row is None:
                continue
            
            # Procesar filas después del header
            for row in table[header_row + 1:]:
                if not row or len(row) < 3:
                    continue
                
                # Intentar extraer: nombre, valor, unidades, referencia
                cells = [str(cell).strip() if cell else '' for cell in row]
                
                # Buscar fila con datos válidos (tiene nombre y valor numérico)
                test_name = None
                value = None
                units = None
                reference = None
                
                for cell in cells:
                    if not cell or len(cell) < 2:
                        continue
                    
                    # Si la celda contiene un número, podría ser el valor
                    value_match = re.search(r'^([\d,\.]+)$', cell)
                    if value_match and value is None:
                        value = value_match.group(1)
                        continue
                    
                    # Si contiene "a" o "hasta", podría ser referencia
                    if re.search(r'\d.*(?:a|hasta)', cell, re.IGNORECASE):
                        reference = cell
                        continue
                    
                    # Si es texto largo sin números al inicio, podría ser nombre
                    if len(cell) > 5 and not re.match(r'^[\d,\.]', cell) and test_name is None:
                        # Verificar que no sea método o otra cosa
                        if 'método' not in cell.lower() and 'método' not in cell.lower():
                            test_name = cell
                            continue
                    
                    # Unidades típicas
                    if re.match(r'^(mg/dL|pg/mL|ng/mL|μmol/L|μIU/mL|nmol/L|%|fL|pg|g/dL|miles/mm|10/mm)', cell, re.IGNORECASE):
                        units = cell
                        continue
                
                # Si encontramos nombre y valor, crear resultado
                if test_name and value:
                    try:
                        numeric_value = float(value.replace(',', '.'))
                    except ValueError:
                        numeric_value = None
                    
                    test_result = {
                        'test_name': test_name,
                        'value': value.replace(',', '.'),
                        'numeric_value': numeric_value,
                        'units': units or '',
                        'reference_range': self._parse_reference_range(reference) if reference else {},
                        'reference_text': reference or ''
                    }
                    
                    # Evitar duplicados
                    existing = any(
                        r.get('test_name', '').upper() == test_name.upper() and
                        r.get('value') == value.replace(',', '.')
                        for r in self.test_results
                    )
                    
                    if not existing:
                        self.test_results.append(test_result)
    
    def _extract_patient_info(self, text: str):
        """Extrae información del paciente del texto"""
        # Nombre
        name_match = re.search(r'Nombre:\s*([A-ZÁÉÍÓÚÑ\s]+)', text)
        if name_match:
            self.patient_info['name'] = name_match.group(1).strip()
        
        # Identificación
        id_match = re.search(r'Identificaci[oó]n:\s*(CC|TI|CE|PA)\s*(\d+)', text, re.IGNORECASE)
        if id_match:
            self.patient_info['id_type'] = id_match.group(1).upper()
            self.patient_info['id_number'] = id_match.group(2)
        
        # Teléfono
        phone_match = re.search(r'Tel:\s*(\d+)', text)
        if phone_match:
            self.patient_info['phone'] = phone_match.group(1)
        
        # Edad
        age_match = re.search(r'Edad de ingreso:\s*(\d+)\s*A[ñn]os,\s*(\d+)\s*Meses,\s*(\d+)\s*D[ií]as', text)
        if age_match:
            self.patient_info['age'] = {
                'years': int(age_match.group(1)),
                'months': int(age_match.group(2)),
                'days': int(age_match.group(3))
            }
        
        # Fecha de nacimiento
        birth_match = re.search(r'Fecha de nacimiento:\s*(\d{2}/\d{2}/\d{4})', text)
        if birth_match:
            self.patient_info['birth_date'] = birth_match.group(1)
        
        # Sexo
        sex_match = re.search(r'Sexo:\s*(Masculino|Femenino)', text)
        if sex_match:
            self.patient_info['sex'] = sex_match.group(1)
        
        # Fecha de toma de muestra
        sample_match = re.search(r'Fecha toma muestra:\s*(\d{2}/\d{2}/\d{4})', text)
        if sample_match:
            self.patient_info['sample_date'] = sample_match.group(1)
        
        # Fecha de recepción
        reception_match = re.search(r'Fecha de recepci[oó]n:\s*(\d{2}/\d{2}/\d{4})', text)
        if reception_match:
            self.patient_info['reception_date'] = reception_match.group(1)
    
    def _extract_laboratory_info(self, text: str):
        """Extrae información del laboratorio"""
        # Nombre del laboratorio/empresa
        lab_match = re.search(r'Empresa:\s*([^\n]+)', text)
        if lab_match:
            self.laboratory_info['name'] = lab_match.group(1).strip()
        
        # Sede
        sede_match = re.search(r'Sede:\s*([^\n]+)', text)
        if sede_match:
            self.laboratory_info['location'] = sede_match.group(1).strip()
        
        # Médico
        doctor_match = re.search(r'M[ée]dico:\s*([^\n]+)', text)
        if doctor_match:
            self.laboratory_info['doctor'] = doctor_match.group(1).strip()
    
    def _extract_test_results(self, text: str):
        """Extrae resultados de exámenes del texto"""
        # Patrón para identificar líneas de resultados
        # Formato típico: "NOMBRE_EXAMEN valor unidades rango_referencia"
        
        # Dividir en secciones por líneas que contienen "Exámen Resultado Unidades Valores de referencia"
        sections = re.split(r'Ex[áa]men\s+Resultado\s+Unidades\s+Valores de referencia', text, re.IGNORECASE)
        
        # Procesar cada sección
        for section in sections[1:]:  # Saltar la primera (antes del header)
            self._parse_section(section)
        
        # También buscar patrones directos de resultados
        self._parse_direct_results(text)
    
    def _parse_section(self, section: str):
        """Parsea una sección del PDF para extraer resultados"""
        lines = section.split('\n')
        current_method = None
        
        # Patrón mejorado para capturar: TEST_NAME valor unidades referencia
        # El patrón busca: texto en mayúsculas (nombre), número (valor), texto (unidades), texto (referencia)
        # Ejemplo: "ERITROCITOS 5,51 millones 4,50 a 6,10"
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Detectar método
            if 'Método:' in line or 'Mtodo:' in line:
                method_match = re.search(r'M[ée]todo:\s*([^\n]+)', line)
                if method_match:
                    current_method = method_match.group(1).strip()
                i += 1
                continue
            
            # Detectar secciones (como CUADRO HEMATICO) - saltar
            if line.isupper() and len(line) > 5 and not re.search(r'[\d,\.]', line):
                i += 1
                continue
            
            # Saltar líneas que son solo números o fechas
            if re.match(r'^\d{8}$|^\d{2}/\d{2}/\d{4}', line):
                i += 1
                continue
            
            # Saltar líneas con CC (cédulas)
            if re.match(r'^CC\s+\d+', line):
                i += 1
                continue
            
            # Patrón mejorado: busca nombre del test (texto en mayúsculas), valor numérico, unidades, referencia
            # El patrón debe manejar casos como:
            # "ERITROCITOS 5,51 millones 4,50 a 6,10"
            # "HOMOCISTEINA EN SUERO (CARDIOVASCULAR) 31,9 μmol/L 3,7 a 13,9"
            
            # Primero intentar patrón completo en una línea
            # Formato: NOMBRE valor unidades referencia
            pattern1 = r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\(\)\-\d]+?)\s+([\d,\.]+)\s+([a-zA-Zμ%°\/\s²³]+?)\s+([\d,\.]+\s*(?:a|hasta|más de|menor de|mayor de)\s*[\d,\.]+|[^\n]+?)(?:\s*$|\s+M[ée]todo:)'
            match = re.match(pattern1, line, re.IGNORECASE)
            
            if not match:
                # Patrón alternativo: nombre puede estar en múltiples palabras
                # Buscar: texto seguido de número seguido de unidades seguido de referencia
                pattern2 = r'^([A-ZÁÉÍÓÚÑ][^0-9]+?)\s+([\d,\.]+)\s+([a-zA-Zμ%°\/\s²³µ]+?)\s+([\d,\.\sa-z]+?)(?:\s*$|\s+M[ée]todo:|$)'
                match = re.match(pattern2, line)
            
            if match:
                test_name = match.group(1).strip()
                value = match.group(2).strip().replace(',', '.')
                units = match.group(3).strip()
                reference = match.group(4).strip()
                
                # Limpiar nombre del test
                test_name = re.sub(r'\s+', ' ', test_name)
                
                # Limpiar unidades (puede contener parte de la referencia)
                # Si las unidades contienen números, probablemente incluyen parte de la referencia
                units_clean = units
                if re.search(r'\d', units):
                    # Intentar separar unidades de referencia
                    parts = units.split()
                    if len(parts) > 1 and re.match(r'[\d,\.]+', parts[-1]):
                        # El último elemento es parte de la referencia
                        reference = parts[-1] + ' ' + reference
                        units_clean = ' '.join(parts[:-1])
                
                # Procesar valor numérico
                try:
                    numeric_value = float(value)
                except ValueError:
                    numeric_value = None
                
                # Procesar rango de referencia
                reference_range = self._parse_reference_range(reference)
                
                # Verificar si este test ya existe (evitar duplicados)
                existing = any(
                    r.get('test_name', '').upper() == test_name.upper() and
                    r.get('value') == value
                    for r in self.test_results
                )
                
                if not existing:
                    test_result = {
                        'test_name': test_name,
                        'value': value,
                        'numeric_value': numeric_value,
                        'units': units_clean,
                        'reference_range': reference_range,
                        'reference_text': reference,
                        'method': current_method
                    }
                    
                    self.test_results.append(test_result)
            
            i += 1
    
    def _parse_direct_results(self, text: str):
        """Busca resultados directamente en el texto usando patrones específicos"""
        # Lista de tests conocidos con sus patrones
        known_tests = {
            'HOMOCISTEINA': r'HOMOCISTE[IÍ]NA[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'VITAMINA B-12': r'VITAMINA B-12\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'VITAMINA D': r'VITAMINA D[^\n]*?\s+([\d,\.]+)\s+([^\s]+)',
            'ÁCIDO FÓLICO': r'[ÁA]CIDO F[ÓO]LICO\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'TSH': r'TSH[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'T3 LIBRE': r'T3 LIBRE[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'T4 LIBRE': r'T4 LIBRE[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'GLICEMIA': r'GLICEMIA[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'HbA1C': r'HEMOGLOBINA GLICOSILADA[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'COLESTEROL TOTAL': r'COLESTEROL TOTAL[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'COLESTEROL HDL': r'COLESTEROL DE ALTA DENSIDAD[^\n]*?\s+([\d,\.]+)\s+([^\s]+)',
            'COLESTEROL LDL': r'COLESTEROL DE BAJA DENSIDAD[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'TRIGLICERIDOS': r'TRIGLIC[EÉ]RIDOS\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'TESTOSTERONA': r'TESTOSTERONA TOTAL\s+([\d,\.]+)\s+([^\s]+)',
            'SHBG': r'GLOBULINA TRANSPORTADORA[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
            'PSA': r'ANTIGENO PROSTATICO ESPECIFICO[^\n]*?\s+([\d,\.]+)\s+([^\s]+)\s+([^\n]+)',
        }
        
        # Buscar cada test conocido
        for test_name, pattern in known_tests.items():
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Verificar si ya existe este test en los resultados
                existing = any(
                    test_name.lower() in r.get('test_name', '').lower() 
                    for r in self.test_results
                )
                if not existing:
                    value = match.group(1).replace(',', '.')
                    units = match.group(2).strip()
                    reference = match.group(3).strip() if len(match.groups()) > 2 else ''
                    
                    try:
                        numeric_value = float(value)
                    except ValueError:
                        numeric_value = None
                    
                    test_result = {
                        'test_name': test_name,
                        'value': value,
                        'numeric_value': numeric_value,
                        'units': units,
                        'reference_range': self._parse_reference_range(reference) if reference else {},
                        'reference_text': reference
                    }
                    
                    self.test_results.append(test_result)
    
    def _parse_reference_range(self, reference_text: str) -> Dict[str, Any]:
        """Parsea el texto de rango de referencia en un diccionario estructurado"""
        if not reference_text:
            return {}
        
        reference_text = reference_text.strip()
        
        # Patrón: "3,7 a 13,9" o "Hasta 6,0" o "2,4 a 10,8"
        range_match = re.search(r'([\d,\.]+)\s+a\s+([\d,\.]+)', reference_text)
        if range_match:
            try:
                min_val = float(range_match.group(1).replace(',', '.'))
                max_val = float(range_match.group(2).replace(',', '.'))
                return {
                    'min': min_val,
                    'max': max_val,
                    'type': 'range'
                }
            except ValueError:
                pass
        
        # Patrón: "Hasta X" o "Más de X"
        hasta_match = re.search(r'Hasta\s+([\d,\.]+)', reference_text, re.IGNORECASE)
        if hasta_match:
            try:
                max_val = float(hasta_match.group(1).replace(',', '.'))
                return {
                    'max': max_val,
                    'type': 'max_only'
                }
            except ValueError:
                pass
        
        # Patrón: "Más de X"
        mas_match = re.search(r'M[áa]s de\s+([\d,\.]+)', reference_text, re.IGNORECASE)
        if mas_match:
            try:
                min_val = float(mas_match.group(1).replace(',', '.'))
                return {
                    'min': min_val,
                    'type': 'min_only'
                }
            except ValueError:
                pass
        
        # Si no se puede parsear, devolver el texto original
        return {
            'text': reference_text,
            'type': 'text'
        }
    
    def save_to_json(self, output_path: str, data: Dict[str, Any]):
        """Guarda los resultados parseados en un archivo JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Resultados guardados en: {output_path}")
        except Exception as e:
            print(f"[ERROR] Error guardando JSON: {e}")


def parse_blood_test(pdf_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Función de conveniencia para parsear un examen de sangre
    
    Args:
        pdf_path: Ruta al PDF del examen
        output_path: Ruta opcional para guardar el JSON (si no se proporciona, 
                     se genera automáticamente)
    
    Returns:
        Diccionario con los datos parseados
    """
    parser = BloodTestParser()
    data = parser.parse_pdf(pdf_path)
    
    if output_path is None:
        # Generar nombre de archivo automáticamente
        pdf_file = Path(pdf_path)
        output_path = pdf_file.parent / f"{pdf_file.stem}_parsed.json"
    
    if data:
        parser.save_to_json(output_path, data)
    
    return data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python blood_test_parser.py <ruta_al_pdf> [ruta_salida.json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    data = parse_blood_test(pdf_path, output_path)
    
    if data:
        print(f"\n[OK] Parseo completado:")
        print(f"   - Paciente: {data.get('patient', {}).get('name', 'N/A')}")
        print(f"   - Total de exámenes: {data.get('metadata', {}).get('total_tests', 0)}")
        print(f"   - Archivo guardado: {output_path or 'N/A'}")

