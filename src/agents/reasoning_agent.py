from typing import Dict, List
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import AgentState

class ReasoningAgent:
    """
    Agente de Razonamiento Clínico.
    Realiza la fusión multimodal entre genómica y biomarcadores.
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        
    def analyze(self, state: AgentState) -> Dict:
        print("[ReasoningAgent] Realizando fusión multimodal...")
        
        genomics = state.get("genomic_findings", [])
        biomarkers = state.get("biomarker_findings", [])
        notes = state.get("patient_notes", "")
        
        # Filtrar solo hallazgos de genómica importantes (alto/medio riesgo)
        critical_genomics = [f for f in genomics if f.get("importance") in ["alto", "medio"]]
        
        # Filtrar biomarcadores alterados
        altered_biomarkers = [b for b in biomarkers if b.get("status") != "normal"]
        
        prompt = f"""
        Como experto en medicina de precisión, tu objetivo es cruzar la predisposición genética con el estado actual del paciente.
        
        HALLAZGOS GENÉTICOS CRÍTICOS:
        {json.dumps(critical_genomics, indent=2)}
        
        BIOMARKERS ALTERADOS EN SANGRE:
        {json.dumps(altered_biomarkers, indent=2)}
        
        CONTEXTO ADICIONAL:
        {notes}
        
        TAREAS:
        1. Identifica "Coincidencias Críticas": Casos donde un riesgo genético coincide con un biomarcador alterado (ej: riesgo en MTHFR + homocisteína alta).
        2. Identifica "Riesgos Silenciosos": Riesgos genéticos donde el biomarcador aún es normal (prevención).
        3. Identifica "Alteraciones Epigenéticas/Estilo de Vida": Biomarcadores alterados sin una predisposición genética clara (causa externa).
        4. Elabora un razonamiento clínico detallado para cada categoría.
        
        Usa Chain-of-Thought para explicar tus conclusiones.
        """
        
        messages = [
            SystemMessage(content="Eres un motor de razonamiento clínico experto en bioinformática y medicina funcional."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "clinical_reasoning": [response.content],
            "next_step": "literature"
        }
