"""
Análisis Sistémico de Examen de Sangre
Genera un análisis completo organizado por sistemas del cuerpo
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Rangos óptimos funcionales basados en medicina funcional
OPTIMAL_RANGES = {
    'HOMOCISTEINA': {'optimal_max': 7.0, 'unit': 'µmol/L', 'critical': True},
    'VITAMINA D': {'optimal_min': 50.0, 'optimal_max': 70.0, 'unit': 'ng/mL', 'critical': True},
    'VITAMINA B-12': {'optimal_min': 500.0, 'optimal_max': 800.0, 'unit': 'pg/mL', 'critical': True},
    'ÁCIDO FÓLICO': {'optimal_min': 15.0, 'unit': 'ng/mL', 'critical': True},
    'TSH': {'optimal_min': 1.0, 'optimal_max': 2.0, 'unit': 'µIU/mL', 'critical': False},
    'T3 LIBRE': {'optimal_position': 'upper_third', 'unit': 'pg/mL', 'critical': False},
    'T4 LIBRE': {'optimal_position': 'upper_half', 'unit': 'ng/dL', 'critical': False},
    'GLICEMIA': {'optimal_max': 85.0, 'unit': 'mg/dL', 'critical': False},
    'HbA1C': {'optimal_max': 5.3, 'unit': '%', 'critical': False},
    'COLESTEROL LDL': {'optimal_max': 100.0, 'unit': 'mg/dL', 'critical': False},
    'COLESTEROL HDL': {'optimal_min': 60.0, 'unit': 'mg/dL', 'critical': False},
    'TRIGLICERIDOS': {'optimal_max': 100.0, 'unit': 'mg/dL', 'critical': False},
}


def find_test(test_results: List[Dict], search_terms: List[str]) -> Optional[Dict]:
    """Busca un test en los resultados usando múltiples términos de búsqueda"""
    for test in test_results:
        test_name_upper = test.get('test_name', '').upper()
        for term in search_terms:
            if term.upper() in test_name_upper:
                return test
    return None


def evaluate_test(test: Dict, optimal_range: Dict) -> Dict[str, Any]:
    """Evalúa un test comparándolo con rangos óptimos"""
    value = test.get('numeric_value')
    if value is None:
        return {'status': 'unknown', 'message': 'Valor no numérico'}
    
    ref_range = test.get('reference_range', {})
    ref_min = ref_range.get('min')
    ref_max = ref_range.get('max')
    
    # Evaluar contra rango normal
    normal_status = 'normal'
    if ref_min is not None and value < ref_min:
        normal_status = 'low'
    elif ref_max is not None and value > ref_max:
        normal_status = 'high'
    
    # Evaluar contra rango óptimo funcional
    optimal_status = 'optimal'
    optimal_message = ''
    
    if 'optimal_max' in optimal_range:
        if value > optimal_range['optimal_max']:
            optimal_status = 'suboptimal'
            optimal_message = f"Por encima del óptimo funcional ({optimal_range['optimal_max']} {optimal_range['unit']})"
    
    if 'optimal_min' in optimal_range:
        if value < optimal_range['optimal_min']:
            optimal_status = 'suboptimal'
            optimal_message = f"Por debajo del óptimo funcional ({optimal_range['optimal_min']} {optimal_range['unit']})"
    
    if 'optimal_position' in optimal_range:
        if ref_min and ref_max:
            range_size = ref_max - ref_min
            if optimal_range['optimal_position'] == 'upper_third':
                target_min = ref_max - (range_size / 3)
                if value < target_min:
                    optimal_status = 'suboptimal'
                    optimal_message = f"No está en el tercio superior del rango"
            elif optimal_range['optimal_position'] == 'upper_half':
                target_min = (ref_min + ref_max) / 2
                if value < target_min:
                    optimal_status = 'suboptimal'
                    optimal_message = f"No está en la mitad superior del rango"
    
    return {
        'normal_status': normal_status,
        'optimal_status': optimal_status,
        'optimal_message': optimal_message,
        'value': value,
        'reference_range': ref_range,
        'reference_text': test.get('reference_text', '')
    }


def analyze_system(system_name: str, tests: List[Dict], test_results: List[Dict]) -> Dict:
    """Analiza un sistema específico del cuerpo"""
    findings = []
    
    for test_info in tests:
        test = find_test(test_results, test_info['search_terms'])
        if not test:
            continue
        
        evaluation = {}
        if 'optimal_range' in test_info:
            evaluation = evaluate_test(test, test_info['optimal_range'])
        
        finding = {
            'test_name': test.get('test_name'),
            'value': test.get('value'),
            'numeric_value': test.get('numeric_value'),
            'units': test.get('units'),
            'reference_text': test.get('reference_text', ''),
            'evaluation': evaluation,
            'genetic_context': test_info.get('genetic_context', ''),
            'importance': test_info.get('importance', 'medium')
        }
        findings.append(finding)
    
    return {
        'system_name': system_name,
        'findings': findings,
        'summary': generate_system_summary(system_name, findings)
    }


def generate_system_summary(system_name: str, findings: List[Dict]) -> str:
    """Genera un resumen del análisis del sistema"""
    critical = [f for f in findings if f.get('evaluation', {}).get('optimal_status') == 'suboptimal' and f.get('importance') == 'critical']
    important = [f for f in findings if f.get('evaluation', {}).get('optimal_status') == 'suboptimal' and f.get('importance') != 'critical']
    normal = [f for f in findings if f.get('evaluation', {}).get('optimal_status') == 'optimal']
    
    summary_parts = []
    if critical:
        summary_parts.append(f"{len(critical)} hallazgo(s) crítico(s) que requieren atención inmediata")
    if important:
        summary_parts.append(f"{len(important)} hallazgo(s) importante(s) que requieren monitoreo")
    if normal:
        summary_parts.append(f"{len(normal)} valor(es) en rango óptimo")
    
    return ". ".join(summary_parts) if summary_parts else "Sin hallazgos significativos"


def generate_report(data: Dict) -> str:
    """Genera el reporte completo de análisis sistémico"""
    
    test_results = data.get('test_results', [])
    patient = data.get('patient', {})
    
    # Definir sistemas y sus tests
    systems = {
        'Sistema de Metilación y Homocisteína': {
            'tests': [
                {
                    'search_terms': ['HOMOCISTEINA'],
                    'optimal_range': OPTIMAL_RANGES['HOMOCISTEINA'],
                    'genetic_context': 'MTHFR C677T (AA/Homocigoto): Reducción ~70% actividad enzimática. CTH rs1021737 (TT): Afecta ruta de transulfuración.',
                    'importance': 'critical'
                },
                {
                    'search_terms': ['VITAMINA B-12', 'B12', 'B-12'],
                    'optimal_range': OPTIMAL_RANGES['VITAMINA B-12'],
                    'genetic_context': 'MTRR A66G (AG): Reduce reciclaje de B12. FUT2 (AA/No-secretor): Absorción intestinal reducida.',
                    'importance': 'critical'
                },
                {
                    'search_terms': ['ÁCIDO FÓLICO', 'FOLATO'],
                    'optimal_range': OPTIMAL_RANGES['ÁCIDO FÓLICO'],
                    'genetic_context': 'MTHFR C677T (AA): No puedes convertir ácido fólico sintético eficientemente. Necesitas metilfolato directamente.',
                    'importance': 'critical'
                }
            ]
        },
        'Sistema Tiroideo': {
            'tests': [
                {
                    'search_terms': ['TSH'],
                    'optimal_range': OPTIMAL_RANGES['TSH'],
                    'genetic_context': 'DIO1 rs2235544 (AA): Conversión T4→T3 reducida. Necesitas TSH más bajo para compensar.',
                    'importance': 'high'
                },
                {
                    'search_terms': ['T3 LIBRE'],
                    'optimal_range': OPTIMAL_RANGES['T3 LIBRE'],
                    'genetic_context': 'DIO1: Debe estar en tercio superior del rango para compensar conversión reducida.',
                    'importance': 'high'
                },
                {
                    'search_terms': ['T4 LIBRE'],
                    'optimal_range': OPTIMAL_RANGES['T4 LIBRE'],
                    'genetic_context': 'DIO1: Debe estar en mitad superior del rango.',
                    'importance': 'medium'
                }
            ]
        },
        'Metabolismo de Glucosa': {
            'tests': [
                {
                    'search_terms': ['GLICEMIA'],
                    'optimal_range': OPTIMAL_RANGES['GLICEMIA'],
                    'genetic_context': 'MTNR1B rs10830963 (GG): Mayor riesgo de diabetes tipo 2. Mayor nivel de glucosa en ayunas.',
                    'importance': 'high'
                },
                {
                    'search_terms': ['HbA1C', 'GLICOSILADA'],
                    'optimal_range': OPTIMAL_RANGES['HbA1C'],
                    'genetic_context': 'MTNR1B: Objetivo <5.3% para óptimo metabólico.',
                    'importance': 'high'
                }
            ]
        },
        'Perfil Lipídico': {
            'tests': [
                {
                    'search_terms': ['COLESTEROL TOTAL'],
                    'genetic_context': 'SLCO1B1: Función disminuida puede afectar metabolismo de estatinas si se requieren.',
                    'importance': 'medium'
                },
                {
                    'search_terms': ['COLESTEROL LDL', 'LDL'],
                    'optimal_range': OPTIMAL_RANGES['COLESTEROL LDL'],
                    'genetic_context': 'Objetivo <100 mg/dL para salud cardiovascular óptima.',
                    'importance': 'high'
                },
                {
                    'search_terms': ['COLESTEROL HDL', 'HDL'],
                    'optimal_range': OPTIMAL_RANGES['COLESTEROL HDL'],
                    'genetic_context': 'Objetivo >60 mg/dL para protección cardiovascular.',
                    'importance': 'high'
                },
                {
                    'search_terms': ['TRIGLICERIDOS'],
                    'optimal_range': OPTIMAL_RANGES['TRIGLICERIDOS'],
                    'genetic_context': 'Objetivo <100 mg/dL para salud metabólica óptima.',
                    'importance': 'medium'
                }
            ]
        },
        'Sistema Hormonal': {
            'tests': [
                {
                    'search_terms': ['TESTOSTERONA'],
                    'genetic_context': 'Evaluación hormonal completa. Rango normal para edad 20-49 años: 2.4-10.8 ng/mL.',
                    'importance': 'medium'
                },
                {
                    'search_terms': ['SHBG'],
                    'genetic_context': 'Contexto para testosterona biodisponible. Valores normales.',
                    'importance': 'low'
                }
            ]
        },
        'Vitamina D y Metabolismo Óseo': {
            'tests': [
                {
                    'search_terms': ['VITAMINA D'],
                    'optimal_range': OPTIMAL_RANGES['VITAMINA D'],
                    'genetic_context': 'VDR Taq (+/+): Receptores de vitamina D menos eficientes. Requieres niveles más altos (50-70 ng/mL) para función óptima.',
                    'importance': 'critical'
                }
            ]
        },
        'Sistema Hematopoyético': {
            'tests': [
                {
                    'search_terms': ['HEMOGLOBINA'],
                    'genetic_context': 'Valores normales. Sin evidencia de anemia.',
                    'importance': 'low'
                },
                {
                    'search_terms': ['HEMATOCRITO'],
                    'genetic_context': 'Valores normales.',
                    'importance': 'low'
                },
                {
                    'search_terms': ['LEUCOCITOS'],
                    'genetic_context': 'Recuento normal. Sin evidencia de infección o inflamación aguda.',
                    'importance': 'low'
                }
            ]
        },
        'Salud Prostática': {
            'tests': [
                {
                    'search_terms': ['PSA', 'PROSTATICO'],
                    'genetic_context': 'Valores excelentes. Ratio PSA Libre/Total >0.15 indica probable hiperplasia benigna, no cáncer.',
                    'importance': 'low'
                }
            ]
        }
    }
    
    # Analizar cada sistema
    system_analyses = []
    for system_name, system_data in systems.items():
        analysis = analyze_system(system_name, system_data['tests'], test_results)
        system_analyses.append(analysis)
    
    # Generar reporte en Markdown
    report = f"""# Análisis Sistémico de Examen de Sangre
## Mariano García Posada - {patient.get('sample_date', 'N/A')}
### Laboratorio: {data.get('laboratory', {}).get('name', 'N/A')[:50]}...

---

## 📋 INFORMACIÓN DEL PACIENTE

- **Nombre**: {patient.get('name', 'N/A')}
- **Edad**: {patient.get('age', {}).get('years', 'N/A')} años, {patient.get('age', {}).get('months', 'N/A')} meses, {patient.get('age', {}).get('days', 'N/A')} días
- **Fecha de nacimiento**: {patient.get('birth_date', 'N/A')}
- **Sexo**: {patient.get('sex', 'N/A')}
- **Fecha de muestra**: {patient.get('sample_date', 'N/A')}
- **Total de exámenes**: {data.get('metadata', {}).get('total_tests', 0)}

---

"""
    
    # Agregar análisis por sistema
    for system_analysis in system_analyses:
        report += f"## 🔬 {system_analysis['system_name']}\n\n"
        report += f"**Resumen**: {system_analysis['summary']}\n\n"
        
        for finding in system_analysis['findings']:
            eval_data = finding.get('evaluation', {})
            optimal_status = eval_data.get('optimal_status', 'unknown')
            
            # Determinar emoji y estado
            if optimal_status == 'optimal':
                status_emoji = "✅"
                status_text = "ÓPTIMO"
            elif optimal_status == 'suboptimal' and finding.get('importance') == 'critical':
                status_emoji = "🔴"
                status_text = "CRÍTICO"
            elif optimal_status == 'suboptimal':
                status_emoji = "🟡"
                status_text = "SUBÓPTIMO"
            else:
                status_emoji = "⚪"
                status_text = "NORMAL"
            
            report += f"### {status_emoji} {finding['test_name']} - {status_text}\n\n"
            report += f"| Métrica | Valor | Rango Normal | Rango Óptimo Funcional | Estado |\n"
            report += f"|---------|-------|--------------|------------------------|--------|\n"
            
            value_str = f"{finding.get('value', 'N/A')} {finding.get('units', '')}"
            ref_text = finding.get('reference_text', 'N/A')
            
            # Determinar rango óptimo
            optimal_range_text = "N/A"
            if finding.get('test_name', '').upper() in ['HOMOCISTEINA']:
                optimal_range_text = "< 7 µmol/L"
            elif finding.get('test_name', '').upper() in ['VITAMINA D']:
                optimal_range_text = "50-70 ng/mL"
            elif finding.get('test_name', '').upper() in ['VITAMINA B-12', 'B12']:
                optimal_range_text = "> 500 pg/mL (óptimo >800)"
            elif finding.get('test_name', '').upper() in ['ÁCIDO FÓLICO', 'FOLATO']:
                optimal_range_text = "> 15 ng/mL"
            elif finding.get('test_name', '').upper() in ['TSH']:
                optimal_range_text = "1.0 - 2.0 µIU/mL"
            elif finding.get('test_name', '').upper() in ['T3 LIBRE']:
                optimal_range_text = "Tercio superior del rango"
            elif finding.get('test_name', '').upper() in ['T4 LIBRE']:
                optimal_range_text = "Mitad superior del rango"
            elif finding.get('test_name', '').upper() in ['GLICEMIA']:
                optimal_range_text = "< 85 mg/dL"
            elif finding.get('test_name', '').upper() in ['HbA1C', 'GLICOSILADA']:
                optimal_range_text = "< 5.3%"
            elif finding.get('test_name', '').upper() in ['COLESTEROL LDL', 'LDL']:
                optimal_range_text = "< 100 mg/dL"
            elif finding.get('test_name', '').upper() in ['COLESTEROL HDL', 'HDL']:
                optimal_range_text = "> 60 mg/dL"
            elif finding.get('test_name', '').upper() in ['TRIGLICERIDOS']:
                optimal_range_text = "< 100 mg/dL"
            
            report += f"| **{finding['test_name']}** | **{value_str}** | {ref_text} | {optimal_range_text} | {status_emoji} **{status_text}** |\n\n"
            
            # Análisis
            if optimal_status == 'suboptimal':
                report += f"**Análisis:**\n"
                if eval_data.get('optimal_message'):
                    report += f"- {eval_data['optimal_message']}\n"
                
                if finding.get('genetic_context'):
                    report += f"\n**Justificación Genética:**\n"
                    report += f"- {finding['genetic_context']}\n"
                
                # Riesgos asociados
                test_name_upper = finding.get('test_name', '').upper()
                if 'HOMOCISTEINA' in test_name_upper:
                    report += f"\n**Riesgos Asociados:**\n"
                    report += f"- Mayor riesgo cardiovascular (infarto, trombosis)\n"
                    report += f"- Daño endotelial\n"
                    report += f"- Estrés oxidativo aumentado\n"
                    report += f"- Problemas neurológicos a largo plazo\n"
                elif 'VITAMINA D' in test_name_upper:
                    report += f"\n**Riesgos Asociados:**\n"
                    report += f"- Absorción de calcio reducida\n"
                    report += f"- Función inmunológica comprometida\n"
                    report += f"- Mayor riesgo de enfermedades autoinmunes\n"
                    report += f"- Fatiga y debilidad muscular\n"
                elif 'B12' in test_name_upper or 'B-12' in test_name_upper:
                    report += f"\n**Riesgos Asociados:**\n"
                    report += f"- Anemia megaloblástica\n"
                    report += f"- Neuropatía periférica\n"
                    report += f"- Deterioro cognitivo\n"
                    report += f"- Fatiga crónica\n"
                elif 'FÓLICO' in test_name_upper or 'FOLATO' in test_name_upper:
                    report += f"\n**Riesgos Asociados:**\n"
                    report += f"- Anemia megaloblástica\n"
                    report += f"- Defectos del tubo neural (si planeas descendencia)\n"
                    report += f"- Mayor riesgo de homocisteína elevada\n"
                elif 'TSH' in test_name_upper:
                    report += f"\n**Riesgos Asociados:**\n"
                    report += f"- Función tiroidea subóptima\n"
                    report += f"- Metabolismo lento\n"
                    report += f"- Fatiga\n"
                elif 'GLICEMIA' in test_name_upper or 'HbA1C' in test_name_upper:
                    report += f"\n**Riesgos Asociados:**\n"
                    report += f"- Mayor riesgo de diabetes tipo 2\n"
                    report += f"- Resistencia a la insulina\n"
                    report += f"- Complicaciones metabólicas a largo plazo\n"
                
                # Acción requerida
                report += f"\n**Acción Requerida:**\n"
                if 'HOMOCISTEINA' in test_name_upper:
                    report += f"1. **Iniciar protocolo de metilación INMEDIATAMENTE**\n"
                    report += f"2. **Metilfolato (L-5-MTHF)**: 800-1000 mcg/día\n"
                    report += f"3. **Metilcobalamina (B12)**: 2000-2500 mcg/día sublingual\n"
                    report += f"4. **P5P (B6 activa)**: 100 mg/día\n"
                    report += f"5. **TMG (Trimetilglicina)**: 1000 mg/día\n"
                    report += f"6. **Riboflavina (B2)**: 50-100 mg/día (cofactor MTHFR)\n"
                    report += f"7. **Repetir examen en 3 meses** para verificar reducción\n"
                elif 'VITAMINA D' in test_name_upper:
                    report += f"1. **Aumentar dosis de D3+K2** (ya tienes 10,000 IU)\n"
                    report += f"2. **Asegurar absorción**: Tomar con grasa, considerar magnesio\n"
                    report += f"3. **Monitorear cada 3 meses** hasta alcanzar 50-70 ng/mL\n"
                    report += f"4. **Objetivo**: 50-70 ng/mL (no solo \"normal\")\n"
                elif 'B12' in test_name_upper or 'B-12' in test_name_upper:
                    report += f"1. **Aumentar dosis de metilcobalamina** a 2000-2500 mcg/día\n"
                    report += f"2. **Asegurar que sea sublingual** (bypassa problemas de absorción)\n"
                    report += f"3. **Repetir en 3 meses** para verificar mejoría\n"
                elif 'FÓLICO' in test_name_upper or 'FOLATO' in test_name_upper:
                    report += f"1. **NO usar ácido fólico sintético**\n"
                    report += f"2. **Usar metilfolato (L-5-MTHF)**: 800-1000 mcg/día\n"
                    report += f"3. **Repetir en 3 meses** para verificar mejoría\n"
                elif 'TSH' in test_name_upper:
                    report += f"1. **Asegurar cofactores**: Selenio (200 mcg), Zinc (15-30 mg), Yodo\n"
                    report += f"2. **Monitorear en 6 meses** para ver si mejora con suplementación\n"
                    report += f"3. **Considerar T3 reversa** si TSH no mejora\n"
                elif 'GLICEMIA' in test_name_upper or 'HbA1C' in test_name_upper:
                    report += f"1. **Monitorear glicemia en ayunas** regularmente\n"
                    report += f"2. **Considerar suplementos**: Cromo, Magnesio, Ácido alfa-lipoico\n"
                    report += f"3. **Dieta**: Reducir carbohidratos refinados, aumentar fibra\n"
                    report += f"4. **Repetir en 6 meses** para seguimiento\n"
            else:
                if finding.get('genetic_context'):
                    report += f"**Nota Genética:** {finding['genetic_context']}\n\n"
            
            report += "\n---\n\n"
    
    # Resumen ejecutivo
    critical_findings = []
    important_findings = []
    
    for system_analysis in system_analyses:
        for finding in system_analysis['findings']:
            eval_data = finding.get('evaluation', {})
            if eval_data.get('optimal_status') == 'suboptimal':
                if finding.get('importance') == 'critical':
                    critical_findings.append(finding)
                else:
                    important_findings.append(finding)
    
    report += f"""## 📊 RESUMEN EJECUTIVO

### Prioridad CRÍTICA (Acción Inmediata)
"""
    if critical_findings:
        for i, finding in enumerate(critical_findings, 1):
            report += f"{i}. **{finding['test_name']}**: {finding.get('value', 'N/A')} {finding.get('units', '')} - {finding.get('evaluation', {}).get('optimal_message', 'Requiere atención')}\n"
    else:
        report += "Ninguno\n"
    
    report += f"\n### Prioridad ALTA (Próximos 3 meses)\n"
    if important_findings:
        for i, finding in enumerate(important_findings, 1):
            report += f"{i}. **{finding['test_name']}**: {finding.get('value', 'N/A')} {finding.get('units', '')} - {finding.get('evaluation', {}).get('optimal_message', 'Requiere monitoreo')}\n"
    else:
        report += "Ninguno\n"
    
    report += f"""
---

## 🎯 PLAN DE ACCIÓN PRIORIZADO

### Semana 1-2: Protocolo de Metilación Intensivo
- **Metilfolato (L-5-MTHF)**: 800-1000 mcg/día
- **Metilcobalamina (B12)**: 2000-2500 mcg/día sublingual
- **P5P (B6 activa)**: 100 mg/día
- **TMG (Trimetilglicina)**: 1000 mg/día
- **Riboflavina (B2)**: 50-100 mg/día

### Semana 3-4: Optimización de Vitamina D
- **D3+K2**: Mantener 10,000 IU/día
- **Asegurar absorción**: Tomar con comida que contenga grasa
- **Magnesio**: Asegurar niveles adecuados (cofactor para D)

### Monitoreo
- **Repetir homocisteína, B12, folato en 3 meses**
- **Repetir vitamina D en 3 meses**
- **Repetir panel completo en 6 meses**

---

## 📈 PROYECCIÓN DE RESULTADOS ESPERADOS

### En 3 Meses (Objetivos)
- **Homocisteína**: Reducir de 31.9 a <15 µmol/L (objetivo final <7)
- **Vitamina D**: Aumentar de 23.1 a 40-50 ng/mL
- **B12**: Aumentar de 486 a >800 pg/mL
- **Folato**: Aumentar de 9.01 a >15 ng/mL

### En 6 Meses (Objetivos)
- **Homocisteína**: <10 µmol/L (ideal <7)
- **Vitamina D**: 50-70 ng/mL
- **B12**: >800 pg/mL
- **Folato**: >15 ng/mL
- **HbA1c**: <5.5%
- **TSH**: 1.5-2.0 µIU/mL

---

## ⚠️ ADVERTENCIAS IMPORTANTES

1. **Homocisteína extremadamente alta**: Requiere intervención médica supervisada
2. **No suspender suplementos antes del próximo examen** (excepto si el médico lo indica)
3. **Consultar con médico** antes de hacer cambios significativos en dosis
4. **Monitorear síntomas** de sobre-metilación (ansiedad, insomnio) con COMT GG

---

*Análisis generado: {datetime.now().strftime('%d de %B, %Y')}*
*Basado en protocolo: `docs/reference/examenes_sangre_protocolo.md`*
*Comparado con perfil genético: MTHFR C677T (AA), CTH (TT), MTRR (AG), VDR (Taq +/+), DIO1 (AA), MTNR1B (GG)*

"""
    
    return report


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_blood_test_systemic.py <ruta_al_json_parseado> [ruta_salida.md]")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Cargar datos
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Generar reporte
    report = generate_report(data)
    
    # Guardar reporte
    if output_path is None:
        json_file = Path(json_path)
        output_path = json_file.parent / f"analisis_sistemico_{json_file.stem.replace('_parsed', '')}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] Análisis sistémico generado: {output_path}")
    print(f"\nResumen:")
    print(f"  - Total de sistemas analizados: 8")
    print(f"  - Total de exámenes evaluados: {len(data.get('test_results', []))}")


if __name__ == "__main__":
    main()

