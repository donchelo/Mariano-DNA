import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path para que las importaciones funcionen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agents.orchestrator import MarianoDNAOrchestrator, create_initial_state

def main():
    # Cargar variables de entorno (API Keys)
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] No se encontró la OPENAI_API_KEY en las variables de entorno.")
        return

    # 1. Definir datos iniciales
    # En una ejecución real, aquí pondríamos las rutas a los archivos raw
    dna_path = "data/raw/genome/mariano_genome.txt"
    blood_pdf = "data/raw/examenes_sangre/vitalea_mariano_2025.pdf"
    
    # Si los archivos no existen, el sistema usará los datos procesados previos
    # o reportará errores controlados.
    
    notes = "Me siento cansado por las tardes y me cuesta concentrarme. Mi dieta es baja en carne roja."

    # 2. Crear estado inicial
    initial_state = create_initial_state(notes=notes)
    # Podemos pasar las rutas si las tenemos
    if os.path.exists(dna_path):
        initial_state["dna_file_path"] = dna_path
    if os.path.exists(blood_pdf):
        initial_state["blood_pdf_path"] = blood_pdf

    # 3. Inicializar el orquestador
    print("[MAIN] Inicializando orquestador de agentes...")
    orchestrator = MarianoDNAOrchestrator()

    # 4. Ejecutar el flujo
    print("[MAIN] Iniciando flujo de análisis...")
    final_state = orchestrator.run(initial_state)

    # 5. Mostrar resultados
    print("\n" + "="*50)
    print("REPORTE FINAL GENERADO POR AGENTES")
    print("="*50)
    if final_state.get("final_report"):
        print(final_state["final_report"])
    else:
        print("[ERROR] No se pudo generar el reporte.")
        if final_state.get("errors"):
            print("Errores encontrados:", final_state["errors"])

if __name__ == "__main__":
    main()
