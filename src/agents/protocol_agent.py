from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import AgentState

class ProtocolAgent:
    """
    Agente de Protocolos y Estilo de Vida.
    Genera el reporte final y las recomendaciones de suplementación.
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.2)
        
    def analyze(self, state: AgentState) -> Dict:
        print("[ProtocolAgent] Generando protocolo final de salud...")
        
        reasoning = state.get("clinical_reasoning", [])
        evidence = state.get("literature_evidence", [])
        
        prompt = f"""
        Basado en el siguiente razonamiento clínico y evidencia científica, genera un plan de acción personalizado.
        
        RAZONAMIENTO CLÍNICO:
        {reasoning}
        
        EVIDENCIA CIENTÍFICA:
        {evidence}
        
        EL PLAN DEBE INCLUIR:
        1. Resumen Ejecutivo (Qué está pasando y por qué es importante).
        2. Plan de Suplementación (Dosis, forma del suplemento y justificación).
        3. Recomendaciones de Estilo de Vida (Dieta, ejercicio, sueño).
        4. Próximos Pasos y Monitoreo.
        
        Responde en ESPAÑOL y usa un tono profesional pero accesible.
        """
        
        messages = [
            SystemMessage(content="Eres un experto en diseño de protocolos de longevidad y medicina personalizada."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "final_report": response.content,
            "next_step": "end"
        }
