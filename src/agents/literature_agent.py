from typing import Dict, List
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from .state import AgentState

class LiteratureAgent:
    """
    Agente de Literatura Médica (Agentic RAG).
    Valida el razonamiento clínico con evidencia científica real usando Tavily Search.
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.search = TavilySearchResults(max_results=3)
        
    def analyze(self, state: AgentState) -> Dict:
        print("[LiteratureAgent] Buscando evidencia científica real...")
        
        reasoning = state.get("clinical_reasoning", [])
        last_reasoning = reasoning[-1] if reasoning else "No hay razonamiento disponible"
        
        # 1. Generar queries de búsqueda basadas en el razonamiento
        query_prompt = f"""
        Basado en el siguiente razonamiento clínico, genera 2 queries de búsqueda precisas en INGLÉS para encontrar evidencia científica en PubMed o Google Scholar.
        
        RAZONAMIENTO:
        {last_reasoning}
        
        Responde SOLO con un JSON array de strings: ["query1", "query2"]
        """
        
        query_messages = [
            SystemMessage(content="Eres un experto en investigación médica bibliográfica."),
            HumanMessage(content=query_prompt)
        ]
        
        query_response = self.llm.invoke(query_messages)
        try:
            queries = json.loads(query_response.content)
        except:
            queries = ["impact of MTHFR on homocysteine levels", "functional vitamin B12 optimization longevity"]

        # 2. Ejecutar búsquedas
        all_results = []
        for q in queries:
            print(f"  Buscando: {q}")
            results = self.search.invoke(q)
            all_results.extend(results)

        # 3. Sintetizar la evidencia
        synthesis_prompt = f"""
        Basado en los resultados de búsqueda y el razonamiento clínico, extrae y sintetiza la evidencia científica más relevante.
        
        RAZONAMIENTO ORIGINAL:
        {last_reasoning}
        
        RESULTADOS DE BÚSQUEDA:
        {json.dumps(all_results, indent=2)}
        
        FORMATO DE SALIDA (JSON):
        [
            {{
                "topic": "Título del tema",
                "evidence": "Resumen de la evidencia encontrada",
                "mechanism": "Mecanismo biológico validado",
                "source_url": "URL de la fuente",
                "relevance": "Alta/Media/Baja"
            }}
        ]
        """
        
        synthesis_messages = [
            SystemMessage(content="Eres un investigador médico experto en síntesis de evidencia científica."),
            HumanMessage(content=synthesis_prompt)
        ]
        
        final_response = self.llm.invoke(synthesis_messages)
        
        try:
            content = final_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            evidence = json.loads(content)
        except:
            evidence = [{"topic": "Validación General", "evidence": final_response.content, "mechanism": "N/A", "relevance": "Media"}]
        
        return {
            "literature_evidence": evidence,
            "next_step": "protocol"
        }
