from typing import Dict, List, Optional
import os
import json
from src.dna_analyzer.blood_test_parser import BloodTestParser
from .state import AgentState

class BiomarkerAgent:
    """
    Agente especializado en análisis de biomarcadores de sangre.
    Identifica desviaciones de rangos óptimos funcionales y metabólicos.
    """
    
    def analyze(self, state: AgentState) -> Dict:
        print("[BiomarkerAgent] Analizando biomarcadores de sangre...")
        
        blood_data = state.get("blood_test_data")
        
        # Si no hay datos directos, intentar cargar de archivos conocidos
        if not blood_data:
            blood_pdf_path = state.get("blood_pdf_path") # Podríamos añadir este campo al estado
            if blood_pdf_path and os.path.exists(blood_pdf_path):
                parser = BloodTestParser()
                parsed_results = parser.parse_pdf(blood_pdf_path)
                blood_data = parsed_results.get("test_results", [])
            else:
                # Intentar buscar en la carpeta data/raw/examenes_sangre
                blood_dir = "data/raw/examenes_sangre"
                if os.path.exists(blood_dir):
                    pdfs = [f for f in os.listdir(blood_dir) if f.endswith(".pdf")]
                    if pdfs:
                        parser = BloodTestParser()
                        parsed_results = parser.parse_pdf(os.path.join(blood_dir, pdfs[0]))
                        blood_data = parsed_results.get("test_results", [])
        
        if not blood_data:
            return {"errors": ["No se encontraron datos de exámenes de sangre"]}
        
        # Lógica de análisis funcional (Longevidad/Optimización)
        # Esto podría expandirse con una base de datos de rangos óptimos
        analyzed_findings = []
        for test in blood_data:
            marker = test.get("test_name")
            value = test.get("numeric_value")
            units = test.get("units")
            ref_range = test.get("reference_range", {})
            
            status = "normal"
            note = ""
            
            if value is not None:
                # Ejemplo de lógica funcional para marcadores críticos
                if "HOMOCISTEINA" in marker.upper():
                    if value > 10:
                        status = "elevado"
                        note = "Nivel óptimo funcional es < 7-8 μmol/L. Elevación sugiere problemas de metilación."
                elif "VITAMINA B12" in marker.upper() or "B-12" in marker.upper():
                    if value < 500:
                        status = "bajo"
                        note = "Nivel óptimo para longevidad es > 800 pg/mL."
                elif "VITAMINA D" in marker.upper():
                    if value < 40:
                        status = "bajo"
                        note = "Nivel óptimo es entre 50-80 ng/mL para salud ósea e inmune."
                
                # Fallback a rangos de laboratorio si no hay lógica funcional
                elif ref_range.get("type") == "range":
                    if value < ref_range["min"]:
                        status = "bajo"
                    elif value > ref_range["max"]:
                        status = "alto"
            
            analyzed_findings.append({
                "marker": marker,
                "value": value,
                "units": units,
                "status": status,
                "note": note,
                "reference_text": test.get("reference_text")
            })
            
        return {
            "biomarker_findings": analyzed_findings,
            "next_step": "reasoning"
        }
