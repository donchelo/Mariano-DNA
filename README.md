# Proyecto Mariano DNA - Optimización de Salud Basada en Genética y Epigenética

Este proyecto contiene un ecosistema completo para el análisis de datos genéticos (genoma raw) y epigenéticos, junto con la implementación de un plan de salud personalizado basado en variantes genéticas específicas (SNPs) y marcadores epigenéticos. El objetivo es optimizar la suplementación, la dieta y el monitoreo de salud para Mariano García Posada.

## 📁 Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas:

```
Mariano DNA/
├── data/                    # Datos del proyecto
│   ├── raw/                 # Archivos originales sin procesar
│   │   ├── genome/          # Archivos de genoma raw (23andMe, AncestryDNA, etc.)
│   │   ├── epigenetics/     # Datos brutos de tests epigenéticos (CSV, TXT)
│   │   │                    #   - Relojes biológicos (edad epigenética)
│   │   │                    #   - Niveles de metilación del ADN
│   │   │                    #   - Perfiles de metilación por gen
│   │   ├── reportes_proveedores/  # Reportes PDF de proveedores externos
│   │   │   ├── promethease/ # Archivos HTML y TXT de Promethease
│   │   │   └── epigenetic/  # Reportes PDF de tests epigenéticos
│   │   │                    #   (TruDiagnostic, Elysium, etc.)
│   │   └── ancestry/        # Datos de ancestría
│   └── processed/           # Archivos generados durante el análisis
│       ├── hallazgos_geneticos.json  # JSON intermedio de análisis genético
│       └── epigenetics/     # Resultados procesados de análisis epigenético
├── docs/                    # Documentación de referencia
│   └── reference/           # Guías y protocolos de referencia
├── outputs/                 # Resultados generados
│   ├── analisis/            # Reportes técnicos generados por software
│   ├── protocolos/          # Protocolos de uso diario
│   └── genetic_genie/       # Reportes específicos de Genetic Genie
├── src/                     # Código fuente
│   ├── dna_analyzer/        # Módulo principal de análisis genético
│   └── scripts/             # Scripts de ejecución
├── ESTRUCTURA_PROYECTO.md   # Documento de estructura y naming
└── README.md                # Este archivo
```

## 🧬 Componentes del Proyecto

El proyecto se divide en tres áreas principales:

1.  **Software de Análisis (`src/dna_analyzer/`)**: Un motor de análisis desarrollado en Python que procesa archivos de genoma raw (23andMe) y extrae información de reportes externos para consolidar hallazgos importantes. El sistema cruza datos genéticos con bases de conocimiento curadas para identificar variantes críticas.
2.  **Documentación de Protocolos**: Guías detalladas para la implementación diaria del plan de suplementación y salud, incluyendo protocolos de laboratorio y monitoreo.
3.  **Reportes y Datos**: Archivos fuente del genoma, datos epigenéticos y reportes de plataformas como Promethease, Genetic Genie, NutraHacker, y proveedores de tests epigenéticos.

### 🔬 Diferencia entre Genética y Epigenética

- **Genética**: Analiza las variantes genéticas (SNPs) que son permanentes y heredadas. Estos son los "planos" de tu ADN que no cambian a lo largo de la vida. Ejemplos: variantes MTHFR, COMT, VDR.

- **Epigenética**: Analiza modificaciones químicas (principalmente metilación del ADN) que pueden cambiar con el tiempo y están influenciadas por factores ambientales, dieta, ejercicio y estilo de vida. Ejemplos: edad epigenética, niveles de metilación global, patrones de metilación por gen.

Ambos tipos de datos son complementarios: la genética te dice tu predisposición, mientras que la epigenética te muestra el estado actual y cómo está respondiendo tu cuerpo a las intervenciones.

---

## 📂 Descripción de Documentos

### 📋 Protocolos y Guías

#### Documentación de Referencia (`docs/reference/`)

| Archivo | Descripción | Uso |
| :--- | :--- | :--- |
| `README_Suplementacion.md` | **Plan Maestro**. Resumen ejecutivo de variantes genéticas y guía de inicio. | Leer primero para entender la estrategia general. |
| `examenes_sangre_protocolo.md` | **Protocolo de Laboratorio**. Lista de exámenes dividida por prioridades (Tiers) y rangos óptimos funcionales. | Llevar al médico o laboratorio para seguimiento. |
| `Guia_Monitoreo_Resultados.md` | **Bitácora de Seguimiento**. Registro de síntomas (energía, sueño, ánimo) y métricas de éxito. | Registrar cambios mensualmente para ajustar el plan. |
| `Guia_Rapida_Referencia.md` | **Resumen Diario**. Lista rápida de dosis por horario (mañana/tarde/noche) y señales de advertencia. | Consulta rápida diaria o impresión para tener a mano. |

#### Análisis Generados (`outputs/analisis/`)

| Archivo | Descripción | Uso |
| :--- | :--- | :--- |
| `hallazgos_geneticos_completos.md` | **Reporte Consolidado**. Análisis completo de variantes genéticas encontradas. | Revisar después de ejecutar el análisis. |
| `perfil_ancestria_mariano_garcia_posada.md` | **Perfil de Ancestría**. Análisis de composición genética ancestral. | Referencia de ancestría. |

#### Protocolos de Uso Diario (`outputs/protocolos/`)

| Archivo | Descripción | Uso |
| :--- | :--- | :--- |
| `calendario_suplementacion.md` | **Cronograma de Inicio**. Plan de introducción gradual (Semana 1-8) para evitar efectos secundarios. | Seguir día a día durante los primeros dos meses. |
| `protocolo_suplementacion_semanal.md` | **Protocolo Semanal**. Plan de suplementación organizado por semanas. | Seguimiento semanal del plan. |
| `lista_compras_suplementos.md` | **Checklist de Compras**. Marcas recomendadas (Thorne, Pure, etc.), dosis y advertencias de calidad. | Organizar las compras de los suplementos necesarios. |
| `suplementos_disponibles.md` | **Inventario de Suplementos**. Lista de suplementos disponibles y sus características. | Consulta de disponibilidad y características. |

#### Reportes de Genetic Genie (`outputs/genetic_genie/`)

| Archivo | Descripción | Uso |
| :--- | :--- | :--- |
| `farmacogenetica.md` | Informe técnico de farmacogenética. Variantes relacionadas con respuesta a fármacos. | Referencia para decisiones médicas. |
| `variantes_significativas.md` | Variantes clínicamente significativas con impacto clínico potencial. | Referencia clínica. |
| `variantes_geneticas.md` | Variantes genéticas generales. | Referencia técnica. |
| `mutaciones_raras.md` | Mutaciones raras encontradas. | Referencia técnica. |
| `mutaciones_no_comunes.md` | Mutaciones no comunes. | Referencia técnica. |
| `tarjeta_alerta_medica.md` | Tarjeta de alerta médica con información crítica para emergencias. | Llevar en billetera o tener a mano. |

### 💻 Software de Análisis (`src/`)

Este módulo permite automatizar el cruce de información genética y la generación de reportes consolidados:

#### Scripts de Ejecución (`src/scripts/`)

*   **`run_analysis.py`**: Script principal que ejecuta el flujo completo de análisis genético:
    - Parsea el archivo de genoma raw (formato 23andMe)
    - Extrae información de reportes PDF existentes (Genetic Genie, NutraHacker)
    - Carga datos estructurados de Promethease (JSON o HTML)
    - Cruza información con la base de datos de SNPs importantes
    - Genera reporte consolidado en Markdown

*   **`parse_genetic_data.py`**: Script auxiliar para convertir reportes de texto de Promethease a JSON estructurado, facilitando el procesamiento posterior.

#### Módulo de Análisis (`src/dna_analyzer/`)

*   **`analyzer.py`**: Motor lógico principal que identifica SNPs críticos (MTHFR, COMT, VDR, APOE, etc.) y genera hallazgos estructurados. Integra datos del genoma raw con información de reportes externos, priorizando fuentes más completas como Promethease.

*   **`parser.py`**: Procesador de archivos raw de genoma (formato 23andMe estándar). Extrae genotipos por rsID y permite búsquedas eficientes en el genoma completo.

*   **`pdf_extractor.py`**: Extractor de datos desde reportes PDF de Genetic Genie y NutraHacker. También procesa reportes HTML de Promethease y archivos JSON estructurados con metadatos completos (magnitude, repute, genes, condiciones médicas).

*   **`snp_database.py`**: Base de datos curada de SNPs importantes organizados por categorías (salud, farmacogenética, nutrigenómica, longevidad, rasgos). Cada SNP incluye descripción, implicaciones, condiciones relacionadas y enlaces a SNPedia.

*   **`report_generator.py`**: Generador de reportes en formato Markdown con estadísticas, hallazgos organizados por categoría e importancia, y referencias a recursos externos.

*   **`promethease_parser.py`**: Parser especializado para procesar reportes de Promethease en formato HTML o texto plano.

---

## 🚀 Cómo Empezar

### Para el Análisis Técnico:

1. **Requisitos previos:**
   - Python 3.10 o superior
   - Archivo de genoma raw en formato 23andMe (ubicado en `data/raw/genome/`)

2. **Instalación:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar análisis genético:**
   ```bash
   python src/scripts/run_analysis.py
   ```
   Este script procesará:
   - El archivo de genoma raw
   - Reportes PDF de Genetic Genie y NutraHacker (si están disponibles)
   - Datos de Promethease (JSON o HTML)
   - Generará un reporte consolidado

4. **Revisar resultados:**
   - El reporte principal se genera en `outputs/analisis/hallazgos_geneticos_completos.md`
   - Incluye hallazgos organizados por categoría e importancia
   - Cada hallazgo incluye genotipo, implicaciones y referencias

### Para el Plan de Salud:

1. **Lectura inicial:**
   - Lee `docs/reference/README_Suplementacion.md` para entender tus variantes clave (MTHFR, COMT, VDR, etc.)
   - Revisa `outputs/analisis/hallazgos_geneticos_completos.md` después de ejecutar el análisis

2. **Consulta profesional:**
   - Consulta con un profesional de la salud antes de iniciar cualquier suplementación
   - Lleva el `docs/reference/examenes_sangre_protocolo.md` para establecer valores basales

3. **Implementación gradual:**
   - Sigue el `outputs/protocolos/calendario_suplementacion.md` para introducir los suplementos de forma segura
   - Usa `docs/reference/Guia_Rapida_Referencia.md` como referencia diaria
   - Registra cambios en `docs/reference/Guia_Monitoreo_Resultados.md`

### Para Tests Epigenéticos:

Los tests epigenéticos (relojes biológicos, niveles de metilación) deben almacenarse en:
- **Datos brutos**: `data/raw/epigenetics/` (archivos CSV, TXT de proveedores)
- **Reportes PDF**: `data/raw/reportes_proveedores/epigenetic/` (reportes finales de TruDiagnostic, Elysium, etc.)
- **Datos procesados**: `data/processed/epigenetics/` (análisis derivados o resultados procesados)

> **Nota**: El software actual se enfoca en análisis genético. Los datos epigenéticos se almacenan para referencia futura y análisis manual comparativo.

---

## ⚠️ Advertencias Importantes

*   Este material tiene fines informativos y educativos únicamente. 
*   **No sustituye el consejo médico profesional.**
*   La suplementación debe ser supervisada por un médico o nutricionista funcional, especialmente considerando las variantes de metilación (MTHFR/COMT).
*   **No usar ácido fólico sintético**; el plan requiere formas metiladas debido a tu perfil genético.
*   Los resultados genéticos representan predisposiciones, no diagnósticos. La epigenética puede cambiar con intervenciones apropiadas.
*   Siempre consulta con profesionales de salud calificados antes de tomar decisiones médicas basadas en análisis genéticos o epigenéticos.

## 📊 Tipos de Datos en el Proyecto

### Datos Genéticos (Permanentes)
- **Genoma raw**: Secuencia completa de SNPs del ADN
- **Variantes genéticas**: SNPs específicos (MTHFR, COMT, VDR, etc.)
- **Ancestría**: Composición genética ancestral
- **Farmacogenética**: Variantes que afectan metabolismo de medicamentos

### Datos Epigenéticos (Modificables)
- **Edad epigenética**: Reloj biológico basado en metilación del ADN
- **Niveles de metilación**: Metilación global y por región genómica
- **Perfiles de metilación**: Patrones específicos por gen o vía metabólica
- **Marcadores de envejecimiento**: Indicadores de salud celular y longevidad

---

---

## 📚 Documentación Adicional

Para más detalles sobre la estructura del proyecto, naming conventions y organización de archivos, consulta:
- **`ESTRUCTURA_PROYECTO.md`**: Documento completo que explica el propósito de cada carpeta y archivo, así como las reglas de naming del proyecto.

---

**Última actualización:** Diciembre 2025  
**Propietario:** Mariano García Posada  
**Versión del proyecto:** 2.0 (Reorganizado)

