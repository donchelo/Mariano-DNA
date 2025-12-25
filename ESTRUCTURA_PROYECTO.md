# Estructura y Naming del Proyecto Mariano DNA

Este documento explica el propósito de cada carpeta y tipo de archivo en el proyecto, así como las reglas de naming que deben seguirse para mantener la consistencia.

---

## 📋 Reglas de Naming

### Principios Generales
1. **Minúsculas**: Todos los nombres de archivos y carpetas deben estar en minúsculas
2. **Sin espacios**: Usar guiones bajos (`_`) o guiones (`-`) en lugar de espacios
3. **Descriptivos**: Los nombres deben ser claros sobre el contenido
4. **Idioma**: 
   - **Código fuente**: Inglés (variables, funciones, clases)
   - **Documentos de usuario**: Español (reportes, protocolos, guías)
   - **Datos raw**: Mantener nombres originales cuando sea necesario para identificación

### Convenciones Específicas
- **Archivos de código**: `snake_case.py` (ej: `genome_parser.py`)
- **Documentos Markdown**: `snake_case.md` o `PascalCase.md` para títulos importantes
- **Archivos de datos**: Mantener nombres originales si son de proveedores externos, o usar `snake_case` para archivos generados
- **Carpetas**: `snake_case` (ej: `data/raw/`, `outputs/analisis/`)

---

## 📁 Estructura de Carpetas

### `data/` - Datos del Proyecto
**Propósito**: Almacenar todos los datos fuente y procesados del proyecto.

#### `data/raw/` - Datos Originales Sin Procesar
**Propósito**: Archivos originales tal como se recibieron de proveedores externos o se descargaron.

- **`data/raw/genome/`**: Archivos de genoma raw (formato 23andMe, AncestryDNA, etc.)
  - Contiene archivos `.txt` con secuencias de SNPs
  - Puede incluir archivos comprimidos (`.tar.gz`, `.zip`)
  - **Naming**: Mantener nombres originales del proveedor para identificación

- **`data/raw/ancestry/`**: Datos de ancestría genética
  - Archivos Excel, CSV o PDF con análisis de composición ancestral
  - **Naming**: `ancestry_[proveedor]_[fecha].xlsx` o mantener nombre original

- **`data/raw/reportes_proveedores/`**: Reportes PDF de proveedores externos
  - Reportes de Genetic Genie, NutraHacker, Promethease, etc.
  - Reportes de tests epigenéticos (TruDiagnostic, Elysium, etc.)
  - **Naming**: `[proveedor]_[tipo]_[nombre]_[fecha].pdf`
  - Ejemplos:
    - `genetic_genie_methylation_profile_mariano_garcia_posada.pdf`
    - `nutrahacker_detox_methylation_report_customer_[id].pdf`
    - `promethease_report_[fecha].pdf`
    - `wellmultid104_report_mariano_garcia_posada.pdf`

- **`data/raw/reportes_proveedores/promethease/`**: Archivos específicos de Promethease
  - HTML, TXT y metadatos de reportes de Promethease
  - **Naming**: Mantener nombres originales o `promethease_[tipo]_[fecha].[ext]`

- **`data/raw/epigenetics/`**: Datos brutos de tests epigenéticos (futuro)
  - Archivos CSV, TXT con datos de metilación
  - Datos de relojes biológicos
  - **Naming**: `epigenetic_[proveedor]_[tipo]_[fecha].[ext]`

#### `data/processed/` - Datos Procesados
**Propósito**: Archivos generados durante el análisis que son intermedios o estructurados.

- **`data/processed/hallazgos_geneticos.json`**: JSON estructurado con hallazgos genéticos
  - Resultado intermedio del análisis
  - **Naming**: `hallazgos_geneticos.json` (singular, descriptivo)

- **`data/processed/epigenetics/`**: Resultados procesados de análisis epigenético (futuro)
  - Datos estructurados derivados de tests epigenéticos
  - **Naming**: `epigenetic_[tipo]_[fecha].json`

---

### `src/` - Código Fuente
**Propósito**: Código Python del sistema de análisis genético.

#### `src/dna_analyzer/` - Módulo Principal
**Propósito**: Módulo Python reutilizable para análisis genético.

- **`analyzer.py`**: Motor lógico principal que identifica SNPs críticos
- **`parser.py`**: Procesador de archivos raw de genoma (formato 23andMe)
- **`pdf_extractor.py`**: Extractor de datos desde reportes PDF
- **`promethease_parser.py`**: Parser especializado para Promethease
- **`snp_database.py`**: Base de datos curada de SNPs importantes
- **`report_generator.py`**: Generador de reportes en Markdown
- **`__init__.py`**: Inicialización del módulo

**Naming**: `snake_case.py` (en inglés, siguiendo convenciones Python)

#### `src/scripts/` - Scripts de Ejecución
**Propósito**: Scripts ejecutables que orquestan el análisis.

- **`run_analysis.py`**: Script principal que ejecuta el flujo completo
- **`parse_genetic_data.py`**: Script auxiliar para convertir reportes a JSON

**Naming**: `snake_case.py` (en inglés)

---

### `docs/` - Documentación de Referencia
**Propósito**: Guías estáticas y protocolos de referencia que no cambian frecuentemente.

#### `docs/reference/` - Guías y Protocolos
**Propósito**: Documentos de referencia para implementación del plan de salud.

- **`README_Suplementacion.md`**: Plan maestro de suplementación
  - Resumen ejecutivo de variantes genéticas
  - Guía de inicio y estrategia general
  - **Uso**: Leer primero para entender la estrategia

- **`examenes_sangre_protocolo.md`**: Protocolo de laboratorio
  - Lista de exámenes dividida por prioridades (Tiers)
  - Rangos óptimos funcionales
  - **Uso**: Llevar al médico o laboratorio para seguimiento

- **`Guia_Monitoreo_Resultados.md`**: Bitácora de seguimiento
  - Registro de síntomas (energía, sueño, ánimo)
  - Métricas de éxito
  - **Uso**: Registrar cambios mensualmente para ajustar el plan

- **`Guia_Rapida_Referencia.md`**: Resumen diario
  - Lista rápida de dosis por horario (mañana/tarde/noche)
  - Señales de advertencia
  - **Uso**: Consulta rápida diaria o impresión para tener a mano

**Naming**: `PascalCase.md` o `snake_case.md` (en español, descriptivo)

---

### `outputs/` - Resultados Generados
**Propósito**: Separar resultados generados por el software de documentos de uso diario.

#### `outputs/analisis/` - Análisis Generados por Software
**Propósito**: Reportes técnicos generados automáticamente por el sistema de análisis.

- **`hallazgos_geneticos_completos.md`**: Reporte consolidado de análisis genético
  - Análisis completo de variantes genéticas encontradas
  - Generado por `run_analysis.py`
  - **Uso**: Revisar después de ejecutar el análisis

- **`perfil_ancestria_[nombre].md`**: Perfil de ancestría
  - Análisis de composición genética ancestral
  - **Uso**: Referencia de ancestría

**Naming**: `snake_case.md` (en español, descriptivo)

#### `outputs/protocolos/` - Protocolos de Uso Diario
**Propósito**: Documentos prácticos para implementación del plan de salud.

- **`calendario_suplementacion.md`**: Cronograma de inicio
  - Plan de introducción gradual (Semana 1-8)
  - Para evitar efectos secundarios
  - **Uso**: Seguir día a día durante los primeros dos meses

- **`protocolo_suplementacion_semanal.md`**: Protocolo semanal
  - Plan de suplementación organizado por semanas
  - **Uso**: Seguimiento semanal del plan

- **`lista_compras_suplementos.md`**: Checklist de compras
  - Marcas recomendadas (Thorne, Pure, etc.)
  - Dosis y advertencias de calidad
  - **Uso**: Organizar las compras de los suplementos necesarios

- **`suplementos_disponibles.md`**: Inventario de suplementos
  - Lista de suplementos disponibles y sus características
  - **Uso**: Consulta de disponibilidad y características

**Naming**: `snake_case.md` (en español, descriptivo)

#### `outputs/genetic_genie/` - Reportes Específicos de Genetic Genie
**Propósito**: Reportes técnicos específicos extraídos de Genetic Genie.

- **`farmacogenetica.md`**: Informe técnico de farmacogenética
  - Variantes relacionadas con respuesta a fármacos
  - **Uso**: Referencia para decisiones médicas

- **`variantes_significativas.md`**: Variantes clínicamente significativas
  - Variantes con impacto clínico potencial
  - **Uso**: Referencia clínica

- **`variantes_geneticas.md`**: Variantes genéticas generales
- **`mutaciones_raras.md`**: Mutaciones raras encontradas
- **`mutaciones_no_comunes.md`**: Mutaciones no comunes
- **`tarjeta_alerta_medica.md`**: Tarjeta de alerta médica
  - Información crítica para emergencias médicas
  - **Uso**: Llevar en billetera o tener a mano

**Naming**: `snake_case.md` (en español, descriptivo)

---

## 📄 Tipos de Archivos y su Propósito

### Archivos de Código Python (`.py`)
- **Ubicación**: `src/`
- **Propósito**: Lógica de análisis, procesamiento y generación de reportes
- **Naming**: `snake_case.py`
- **Idioma**: Inglés (código, comentarios, docstrings)

### Archivos Markdown (`.md`)
- **Ubicación**: `docs/`, `outputs/`
- **Propósito**: Documentación, reportes, protocolos
- **Naming**: `snake_case.md` o `PascalCase.md` para títulos importantes
- **Idioma**: Español (contenido de usuario), Inglés (documentación técnica si aplica)

### Archivos JSON (`.json`)
- **Ubicación**: `data/processed/`
- **Propósito**: Datos estructurados intermedios
- **Naming**: `snake_case.json`
- **Formato**: JSON válido, UTF-8

### Archivos PDF (`.pdf`)
- **Ubicación**: `data/raw/reportes_proveedores/`
- **Propósito**: Reportes originales de proveedores externos
- **Naming**: `[proveedor]_[tipo]_[nombre]_[fecha].pdf` o mantener nombre original si es crítico para identificación

### Archivos de Genoma Raw (`.txt`, `.tar.gz`, `.zip`)
- **Ubicación**: `data/raw/genome/`
- **Propósito**: Archivos de genoma sin procesar
- **Naming**: Mantener nombres originales del proveedor para identificación

### Archivos Excel/CSV (`.xlsx`, `.csv`)
- **Ubicación**: `data/raw/ancestry/`, `data/raw/epigenetics/`
- **Propósito**: Datos tabulares de ancestría o epigenética
- **Naming**: `[tipo]_[proveedor]_[fecha].[ext]` o mantener nombre original

---

## 🔄 Flujo de Datos

```
data/raw/
  ├── genome/                    → Parser → data/processed/hallazgos_geneticos.json
  ├── reportes_proveedores/      → Extractor → data/processed/hallazgos_geneticos.json
  └── ancestry/                  → (procesamiento manual o futuro)

data/processed/
  └── hallazgos_geneticos.json   → Analyzer → outputs/analisis/hallazgos_geneticos_completos.md
```

---

## 📝 Ejemplos de Naming Correcto

### ✅ Correcto
- `hallazgos_geneticos_completos.md`
- `calendario_suplementacion.md`
- `genetic_genie_methylation_profile.pdf`
- `genome_parser.py`
- `run_analysis.py`

### ❌ Incorrecto
- `Hallazgos Geneticos Completos.md` (espacios, mayúsculas)
- `calendario-suplementacion.md` (guiones en lugar de guiones bajos para archivos)
- `Genetic Genie Methylation Profile.pdf` (espacios)
- `GenomeParser.py` (PascalCase para archivos Python)
- `runAnalysis.py` (camelCase)

---

## 🎯 Resumen de Principios

1. **Separación clara**: Datos raw vs procesados, código vs documentación, análisis vs protocolos
2. **Naming consistente**: snake_case para archivos, descriptivo y claro
3. **Idioma apropiado**: Español para documentos de usuario, Inglés para código
4. **Mantenibilidad**: Estructura que facilita encontrar y actualizar archivos
5. **Escalabilidad**: Estructura que permite agregar nuevos tipos de datos sin reorganización mayor

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0

