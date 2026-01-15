from typing import Dict, List, Literal
from langgraph.graph import StateGraph, END
from .state import AgentState
from .genomics_agent import GenomicsAgent
from .biomarker_agent import BiomarkerAgent
from .reasoning_agent import ReasoningAgent
from .literature_agent import LiteratureAgent
from .protocol_agent import ProtocolAgent

class MarianoDNAOrchestrator:
    """
    Orquestador principal del sistema Multi-Agente Mariano DNA.
    Define el flujo de trabajo y la comunicación entre agentes.
    """
    
    def __init__(self):
        # Inicializar agentes
        self.genomics_agent = GenomicsAgent()
        self.biomarker_agent = BiomarkerAgent()
        self.reasoning_agent = ReasoningAgent()
        self.literature_agent = LiteratureAgent()
        self.protocol_agent = ProtocolAgent()
        
        # Construir el grafo
        workflow = StateGraph(AgentState)
        
        # Añadir nodos (agentes)
        workflow.add_node("genomics", self.genomics_agent.analyze)
        workflow.add_node("biomarkers", self.biomarker_agent.analyze)
        workflow.add_node("reasoning", self.reasoning_agent.analyze)
        workflow.add_node("literature", self.literature_agent.analyze)
        workflow.add_node("protocol", self.protocol_agent.analyze)
        
        # Definir los bordes (flujo)
        workflow.set_entry_point("genomics")
        
        workflow.add_edge("genomics", "biomarkers")
        workflow.add_edge("biomarkers", "reasoning")
        workflow.add_edge("reasoning", "literature")
        workflow.add_edge("literature", "protocol")
        workflow.add_edge("protocol", END)
        
        # Compilar el grafo
        self.app = workflow.compile()
        
    def run(self, initial_state: AgentState) -> AgentState:
        """Ejecuta el flujo completo de agentes"""
        return self.app.invoke(initial_state)

def create_initial_state(dna_data=None, blood_data=None, notes=None) -> AgentState:
    """Crea el estado inicial para el orquestador"""
    return {
        "dna_data": dna_data,
        "blood_test_data": blood_data,
        "patient_notes": notes,
        "genomic_findings": [],
        "biomarker_findings": [],
        "clinical_reasoning": [],
        "literature_evidence": [],
        "final_report": None,
        "next_step": None,
        "errors": []
    }
