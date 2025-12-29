"""
Script para parsear exámenes de sangre y extraer resultados en formato JSON organizado

Uso:
    python src/scripts/parse_blood_test.py <ruta_al_pdf> [ruta_salida.json]
    
Ejemplo:
    python src/scripts/parse_blood_test.py data/raw/examenes_sangre/examen_sangre_vitalea_2025-12-26.pdf
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.dna_analyzer.blood_test_parser import parse_blood_test


def main():
    if len(sys.argv) < 2:
        print("Uso: python parse_blood_test.py <ruta_al_pdf> [ruta_salida.json]")
        print("\nEjemplo:")
        print("  python parse_blood_test.py data/raw/examenes_sangre/examen_sangre_vitalea_2025-12-26.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Verificar que el archivo existe
    if not Path(pdf_path).exists():
        print(f"[ERROR] El archivo no existe: {pdf_path}")
        sys.exit(1)
    
    print(f"Parseando examen de sangre: {pdf_path}")
    data = parse_blood_test(pdf_path, output_path)
    
    if data:
        print(f"\n[OK] Parseo completado:")
        print(f"   - Paciente: {data.get('patient', {}).get('name', 'N/A')}")
        print(f"   - Fecha de muestra: {data.get('patient', {}).get('sample_date', 'N/A')}")
        print(f"   - Laboratorio: {data.get('laboratory', {}).get('name', 'N/A')[:50]}...")
        print(f"   - Total de exámenes: {data.get('metadata', {}).get('total_tests', 0)}")
        print(f"   - Archivo guardado: {output_path or 'N/A'}")
        
        # Mostrar algunos tests importantes
        important_tests = ['HOMOCISTEINA', 'VITAMINA D', 'VITAMINA B-12', 'TSH', 'GLICEMIA']
        print(f"\nTests importantes encontrados:")
        for test_name in important_tests:
            for result in data.get('test_results', []):
                if test_name in result.get('test_name', '').upper():
                    ref_text = result.get('reference_text', '')
                    if ref_text:
                        print(f"   - {result['test_name']}: {result['value']} {result['units']} (Ref: {ref_text})")
                    else:
                        print(f"   - {result['test_name']}: {result['value']} {result['units']}")
                    break
    else:
        print("[ERROR] No se pudo parsear el archivo")
        sys.exit(1)


if __name__ == "__main__":
    main()

