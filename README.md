# 🧬 Mariano DNA: Optimización de Salud Inteligente

Este ecosistema combina **análisis genómico avanzado**, **inteligencia artificial** y **monitoreo epigenético** para crear un plan de salud ultra-personalizado. El objetivo es optimizar la longevidad, el rendimiento cognitivo y la salud sistémica de Mariano García Posada.

---

## 🚀 Capacidades del Sistema

### 1. 🔍 Análisis Genético de Precisión
Procesa archivos de genoma raw (formato 23andMe) y cruza la información con una base de datos curada de más de **500 SNPs críticos** (MTHFR, COMT, APOE, VDR, etc.).
- Identifica predisposiciones genéticas.
- Calcula puntuaciones de riesgo poligénico (**PRS**).
- Analiza la respuesta a fármacos (**Farmacogenómica**).

### 2. 🤖 Sistema Multi-Agente (AI)
Utiliza agentes inteligentes impulsados por **LangGraph** para realizar razonamiento clínico profundo:
- **Agente Genómico**: Interpreta variantes de ADN.
- **Agente de Biomarcadores**: Analiza exámenes de sangre y su evolución.
- **Agente de Literatura**: Busca evidencia científica actualizada.
- **Agente de Protocolo**: Diseña planes de suplementación basados en los hallazgos.

### 3. 📊 Dashboard Interactivo
Una interfaz visual potente construida con **Streamlit** que permite:
- Visualizar hallazgos por sistemas (Metilación, Detox, Longevidad, etc.).
- Rastrear el historial de biomarcadores en sangre vs. dosis de suplementos.
- Interactuar con el **Agente AI** mediante un chat inteligente.
- Generar tarjetas de alerta médica y reportes técnicos.

---

## 📁 Organización del Proyecto

- **`src/`**: El cerebro del sistema.
  - `dna_analyzer/`: Motor de análisis genético y parsing de datos.
  - `agents/`: Orquestación de agentes de inteligencia artificial.
  - `dashboard/`: Aplicación web interactiva.
- **`data/`**: Repositorio de datos (Genome Raw, Blood Tests, Epigenetics).
- **`docs/`**: Documentación de referencia y guías médicas.
- **`outputs/`**: Reportes generados, protocolos de suplementación y listas de compras.

---

## 🛠️ Cómo Empezar

### Instalación
1. Asegúrate de tener **Python 3.10+** instalado.
2. Instala las dependencias necesarias:
   ```bash
   pip install streamlit pandas plotly langgraph openai
   ```
   *(Nota: Se recomienda usar un entorno virtual)*

### Ejecución
- **Para ver el Dashboard:**
  ```bash
   streamlit run src/dashboard/app.py
  ```
- **Para ejecutar un nuevo análisis genético completo:**
  ```bash
  python src/scripts/run_analysis.py
  ```

---

## 📋 Flujo de Trabajo Recomendado

1. **Carga de Datos**: Coloca tu genoma raw en `data/raw/genome/` y tus exámenes de sangre (JSON) en `data/raw/examenes_sangre/`.
2. **Análisis**: Ejecuta `run_analysis.py` para procesar toda la información.
3. **Visualización**: Abre el **Dashboard** para explorar los resultados y el mapa de calor de riesgo.
4. **Consulta**: Usa el **Chat Agente** para hacer preguntas específicas sobre tus resultados.
5. **Acción**: Revisa `outputs/protocolos/` para ver tu calendario de suplementación actualizado.

---

## ⚠️ Advertencia Médica
Este software es una herramienta de análisis informativo y educativo. **No constituye consejo médico.** Cualquier cambio en la suplementación o medicación debe ser supervisado por un profesional de la salud calificado, especialmente dada la complejidad de las variantes de metilación.

---
**Última actualización:** Enero 2026
**Versión:** 3.0 (AI Agent Enabled)
