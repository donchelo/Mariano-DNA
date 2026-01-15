from typing import Annotated, Dict, List, Optional, TypedDict
import operator

class AgentState(TypedDict):
    # Entradas
    dna_data: Optional[Dict]
    dna_file_path: Optional[str]
    blood_test_data: Optional[List[Dict]]
    blood_pdf_path: Optional[str]
    patient_notes: Optional[str]
    
    # Resultados intermedios de agentes
    genomic_findings: Annotated[List[Dict], operator.add]
    biomarker_findings: Annotated[List[Dict], operator.add]
    clinical_reasoning: Annotated[List[str], operator.add]
    literature_evidence: Annotated[List[Dict], operator.add]
    
    # Resultados finales
    final_report: Optional[str]
    next_step: Optional[str]
    errors: Annotated[List[str], operator.add]
