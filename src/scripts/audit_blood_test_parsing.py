"""
Auditoría del parsing de exámenes de sangre
Compara el JSON parseado con el PDF original para verificar exactitud
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pdfplumber

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def extract_pdf_text(pdf_path: str) -> str:
    """Extrae todo el texto del PDF"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] Error extrayendo PDF: {e}")
    return text


def find_test_in_pdf(test_name: str, pdf_text: str) -> Optional[Dict]:
    """Busca un test específico en el texto del PDF y extrae su valor"""
    # Normalizar nombre del test para búsqueda
    search_terms = []
    test_name_upper = test_name.upper()
    
    # Crear términos de búsqueda basados en el nombre
    if 'HOMOCISTEINA' in test_name_upper:
        search_terms = ['HOMOCISTEINA', 'HOMOCISTE']
    elif 'VITAMINA B-12' in test_name_upper or 'B12' in test_name_upper:
        search_terms = ['VITAMINA B-12', 'VITAMINA B12', 'B-12']
    elif 'VITAMINA D' in test_name_upper:
        search_terms = ['VITAMINA D', '25-HIDROXI']
    elif 'ÁCIDO FÓLICO' in test_name_upper or 'FOLATO' in test_name_upper:
        search_terms = ['ÁCIDO FÓLICO', 'ACIDO FOLICO', 'FÓLICO']
    elif 'TSH' in test_name_upper:
        search_terms = ['TSH', 'Hormona Estimulante de la Tiroides']
    elif 'T3 LIBRE' in test_name_upper:
        search_terms = ['T3 LIBRE', 'Triyodotironina Libre']
    elif 'T4 LIBRE' in test_name_upper:
        search_terms = ['T4 LIBRE', 'Tiroxina Libre']
    elif 'GLICEMIA' in test_name_upper:
        search_terms = ['GLICEMIA', 'GLICEMIA EN AYUNAS']
    elif 'GLICOSILADA' in test_name_upper or 'HbA1C' in test_name_upper:
        search_terms = ['HEMOGLOBINA GLICOSILADA', 'HbA1C', 'HbA1c']
    elif 'COLESTEROL LDL' in test_name_upper or 'LDL' in test_name_upper:
        search_terms = ['COLESTEROL DE BAJA DENSIDAD', 'LDL']
    elif 'COLESTEROL HDL' in test_name_upper or 'HDL' in test_name_upper:
        search_terms = ['COLESTEROL DE ALTA DENSIDAD', 'HDL']
    elif 'COLESTEROL TOTAL' in test_name_upper:
        search_terms = ['COLESTEROL TOTAL']
    elif 'TRIGLICERIDOS' in test_name_upper:
        search_terms = ['TRIGLICERIDOS', 'TRIGLICÉRIDOS']
    elif 'TESTOSTERONA' in test_name_upper:
        search_terms = ['TESTOSTERONA TOTAL', 'TESTOSTERONA']
    elif 'SHBG' in test_name_upper:
        search_terms = ['SHBG', 'GLOBULINA TRANSPORTADORA']
    elif 'PSA' in test_name_upper or 'PROSTATICO' in test_name_upper:
        search_terms = ['ANTIGENO PROSTATICO', 'PSA']
    else:
        # Usar el nombre completo como término de búsqueda
        search_terms = [test_name_upper]
    
    # Buscar en el texto
    for term in search_terms:
        # Buscar el término seguido de un valor numérico
        pattern = rf'{re.escape(term)}[^\n]*?([\d,\.]+)\s+([^\s]+(?:\s+[^\s]+)?)\s+([^\n]+?)(?:\n|Método:|$)'
        match = re.search(pattern, pdf_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        if match:
            value = match.group(1).replace(',', '.')
            units = match.group(2).strip()
            reference = match.group(3).strip()
            
            # Limpiar referencia (puede contener texto adicional)
            reference = re.sub(r'\s+Método:.*$', '', reference).strip()
            
            try:
                numeric_value = float(value)
            except ValueError:
                numeric_value = None
            
            return {
                'test_name': test_name,
                'value': value,
                'numeric_value': numeric_value,
                'units': units,
                'reference_text': reference
            }
    
    return None


def compare_values(parsed: Dict, pdf_extracted: Optional[Dict]) -> Dict:
    """Compara valores parseados con valores extraídos del PDF"""
    result = {
        'test_name': parsed.get('test_name'),
        'match': False,
        'discrepancies': [],
        'parsed_value': parsed.get('value'),
        'parsed_numeric': parsed.get('numeric_value'),
        'pdf_value': None,
        'pdf_numeric': None,
        'parsed_units': parsed.get('units'),
        'pdf_units': None,
        'parsed_reference': parsed.get('reference_text'),
        'pdf_reference': None
    }
    
    if pdf_extracted is None:
        result['discrepancies'].append('Test no encontrado en PDF')
        return result
    
    result['pdf_value'] = pdf_extracted.get('value')
    result['pdf_numeric'] = pdf_extracted.get('numeric_value')
    result['pdf_units'] = pdf_extracted.get('units')
    result['pdf_reference'] = pdf_extracted.get('reference_text')
    
    # Comparar valores numéricos (con tolerancia para redondeo)
    parsed_num = parsed.get('numeric_value')
    pdf_num = pdf_extracted.get('numeric_value')
    
    if parsed_num is not None and pdf_num is not None:
        # Tolerancia de 0.1 para diferencias de redondeo
        if abs(parsed_num - pdf_num) > 0.1:
            result['discrepancies'].append(f'Valor numérico diferente: parseado={parsed_num}, PDF={pdf_num}')
        else:
            result['match'] = True
    elif parsed_num is None and pdf_num is None:
        result['match'] = True
    else:
        result['discrepancies'].append(f'Uno de los valores es None: parseado={parsed_num}, PDF={pdf_num}')
    
    # Comparar unidades (normalizar espacios y mayúsculas)
    parsed_units = parsed.get('units', '').strip().upper()
    pdf_units = pdf_extracted.get('units', '').strip().upper()
    
    if parsed_units != pdf_units:
        # Algunas diferencias son aceptables (ej: "µmol/L" vs "μmol/L")
        if not (parsed_units.replace(' ', '') == pdf_units.replace(' ', '') or
                parsed_units in pdf_units or pdf_units in parsed_units):
            result['discrepancies'].append(f'Unidades diferentes: parseado="{parsed.get("units")}", PDF="{pdf_extracted.get("units")}"')
    
    return result


def audit_parsing(json_path: str, pdf_path: str) -> Dict:
    """Realiza auditoría completa del parsing"""
    print(f"Auditando parsing de: {json_path}")
    print(f"Comparando con PDF: {pdf_path}\n")
    
    # Cargar JSON parseado
    with open(json_path, 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)
    
    # Extraer texto del PDF
    pdf_text = extract_pdf_text(pdf_path)
    
    # Obtener lista de tests parseados (excluir artefactos como "Preliminar Página")
    parsed_tests = [
        test for test in parsed_data.get('test_results', [])
        if not test.get('test_name', '').startswith('Preliminar')
    ]
    
    print(f"Total de tests parseados (excluyendo artefactos): {len(parsed_tests)}\n")
    
    # Comparar cada test
    comparisons = []
    not_found = []
    matches = 0
    discrepancies = 0
    
    for parsed_test in parsed_tests:
        test_name = parsed_test.get('test_name')
        pdf_extracted = find_test_in_pdf(test_name, pdf_text)
        
        comparison = compare_values(parsed_test, pdf_extracted)
        comparisons.append(comparison)
        
        if pdf_extracted is None:
            not_found.append(test_name)
        elif comparison['match'] and not comparison['discrepancies']:
            matches += 1
        else:
            discrepancies += 1
    
    # Generar reporte
    report = {
        'total_tests': len(parsed_tests),
        'matches': matches,
        'discrepancies': discrepancies,
        'not_found': len(not_found),
        'comparisons': comparisons,
        'not_found_tests': not_found,
        'discrepancy_details': [c for c in comparisons if c['discrepancies']]
    }
    
    return report


def generate_audit_report(audit_result: Dict) -> str:
    """Genera reporte de auditoría en formato legible"""
    report = f"""# Auditoría de Parsing - Examen de Sangre
## Resultados de Verificación

### Resumen General
- **Total de tests parseados**: {audit_result['total_tests']}
- **Tests que coinciden**: {audit_result['matches']} ({audit_result['matches']/audit_result['total_tests']*100:.1f}%)
- **Tests con discrepancias**: {audit_result['discrepancies']} ({audit_result['discrepancies']/audit_result['total_tests']*100:.1f}%)
- **Tests no encontrados en PDF**: {audit_result['not_found']} ({audit_result['not_found']/audit_result['total_tests']*100:.1f}%)

---

"""
    
    if audit_result['discrepancy_details']:
        report += "## ⚠️ DISCREPANCIAS ENCONTRADAS\n\n"
        for comp in audit_result['discrepancy_details']:
            report += f"### {comp['test_name']}\n\n"
            report += f"- **Valor parseado**: {comp['parsed_value']} {comp['parsed_units']}\n"
            report += f"- **Valor en PDF**: {comp['pdf_value']} {comp['pdf_units']}\n"
            report += f"- **Referencia parseada**: {comp['parsed_reference']}\n"
            report += f"- **Referencia en PDF**: {comp['pdf_reference']}\n"
            report += f"- **Discrepancias**:\n"
            for disc in comp['discrepancies']:
                report += f"  - {disc}\n"
            report += "\n---\n\n"
    
    if audit_result['not_found_tests']:
        report += "## ⚠️ TESTS NO ENCONTRADOS EN PDF\n\n"
        report += "Los siguientes tests fueron parseados pero no se encontraron en el PDF:\n\n"
        for test_name in audit_result['not_found_tests']:
            report += f"- {test_name}\n"
        report += "\n---\n\n"
    
    # Tests que coinciden perfectamente
    perfect_matches = [c for c in audit_result['comparisons'] 
                      if c['match'] and not c['discrepancies'] and c['pdf_value'] is not None]
    
    if perfect_matches:
        report += f"## ✅ TESTS VERIFICADOS CORRECTAMENTE ({len(perfect_matches)})\n\n"
        for comp in perfect_matches[:10]:  # Mostrar primeros 10
            report += f"- **{comp['test_name']}**: {comp['parsed_value']} {comp['parsed_units']} ✓\n"
        if len(perfect_matches) > 10:
            report += f"\n... y {len(perfect_matches) - 10} más\n"
        report += "\n---\n\n"
    
    report += f"""
## 📊 CONCLUSIÓN

"""
    
    accuracy = (audit_result['matches'] / audit_result['total_tests']) * 100 if audit_result['total_tests'] > 0 else 0
    
    if accuracy >= 95:
        report += "✅ **Parsing EXCELENTE**: Más del 95% de los tests coinciden perfectamente.\n"
    elif accuracy >= 85:
        report += "✅ **Parsing BUENO**: Más del 85% de los tests coinciden. Revisar discrepancias menores.\n"
    elif accuracy >= 70:
        report += "⚠️ **Parsing ACEPTABLE**: Más del 70% de los tests coinciden. Hay discrepancias que requieren atención.\n"
    else:
        report += "❌ **Parsing REQUIERE REVISIÓN**: Menos del 70% de coincidencia. Revisar lógica de parsing.\n"
    
    report += f"\n**Precisión general**: {accuracy:.1f}%\n"
    
    return report


def main():
    if len(sys.argv) < 3:
        print("Uso: python audit_blood_test_parsing.py <ruta_json_parseado> <ruta_pdf_original> [ruta_reporte_salida]")
        sys.exit(1)
    
    json_path = sys.argv[1]
    pdf_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Realizar auditoría
    audit_result = audit_parsing(json_path, pdf_path)
    
    # Generar reporte
    report = generate_audit_report(audit_result)
    
    # Guardar reporte
    if output_path is None:
        json_file = Path(json_path)
        output_path = json_file.parent / f"auditoria_{json_file.stem}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] Reporte de auditoría generado: {output_path}")
    print(f"\nResumen:")
    print(f"  - Tests verificados: {audit_result['total_tests']}")
    print(f"  - Coincidencias: {audit_result['matches']} ({audit_result['matches']/audit_result['total_tests']*100:.1f}%)")
    print(f"  - Discrepancias: {audit_result['discrepancies']}")
    print(f"  - No encontrados: {audit_result['not_found']}")


if __name__ == "__main__":
    main()

