#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard interactivo para análisis genético
Usa Streamlit para visualización web
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
import re
from typing import Optional, Dict, List, Any
from datetime import datetime

# Agregar el directorio src al path para imports
try:
    project_root = Path(__file__).parent.parent.parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except Exception:
    pass

import dna_analyzer
from dna_analyzer.parser import GenomeParser
from dna_analyzer.analyzer import GeneticAnalyzer
from dna_analyzer.snp_database import SNPDatabase
from dna_analyzer.pdf_extractor import ReportExtractor
from dna_analyzer.pharmacogenomics import PharmacogenomicsAnalyzer
from dna_analyzer.prs_calculator import PRSCalculator
from dna_analyzer.clinvar_client import ClinVarClient
from dna_analyzer.system_mapper import SystemMapper

# Importar agentes para el Chat
try:
    from agents.orchestrator import MarianoDNAOrchestrator, create_initial_state
    HAS_AGENTS = True
except ImportError:
    HAS_AGENTS = False


def find_genome_file() -> Optional[Path]:
    """Encuentra el archivo de genoma más reciente"""
    genome_dir = Path("data/raw/genome")
    if not genome_dir.exists():
        return None
    
    # Buscar archivos .txt en subdirectorios
    txt_files = list(genome_dir.rglob("*.txt"))
    if not txt_files:
        return None
    
    # Retornar el más reciente
    return max(txt_files, key=lambda p: p.stat().st_mtime)


def find_blood_test_files() -> List[Dict[str, Any]]:
    """Encuentra todos los archivos de exámenes de sangre parseados"""
    blood_test_dir = Path("data/raw/examenes_sangre")
    if not blood_test_dir.exists():
        return []
    
    # Buscar archivos JSON parseados
    json_files = list(blood_test_dir.glob("*_parsed.json"))
    if not json_files:
        return []
    
    blood_tests = []
    for json_file in sorted(json_files, key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extraer fecha del nombre del archivo o de los datos
                sample_date = data.get('patient', {}).get('sample_date', '')
                if not sample_date:
                    # Intentar extraer de nombre de archivo
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', json_file.name)
                    if match:
                        sample_date = match.group(1)
                
                blood_tests.append({
                    'file_path': json_file,
                    'data': data,
                    'sample_date': sample_date,
                    'test_name': json_file.stem
                })
        except Exception as e:
            st.warning(f"Error cargando {json_file.name}: {e}")
    
    return blood_tests


def extract_supplement_data() -> Dict[str, Any]:
    """Extrae datos de suplementos del archivo markdown"""
    supplement_file = Path("outputs/protocolos/stack_suplementos_organizado.md")
    if not supplement_file.exists():
        return {}
    
    try:
        with open(supplement_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        supplements = {}
        
        # Mapeo de suplementos a biomarcadores relacionados
        supplement_biomarker_map = {
            'metilfolato': ['HOMOCISTEINA', 'ÁCIDO FÓLICO', 'FOLATO'],
            'metil b-12': ['VITAMINA B-12', 'HOMOCISTEINA'],
            'p5p': ['HOMOCISTEINA'],
            'tmg': ['HOMOCISTEINA'],
            'vitamina b2': ['HOMOCISTEINA'],
            'nac': ['HOMOCISTEINA'],
            'vitamina d3': ['VITAMINA D'],
            'selenio': ['TSH', 'T3 LIBRE', 'T4 LIBRE'],
            'magnesio': ['VITAMINA D'],
            'omega-3': ['COLESTEROL LDL', 'COLESTEROL HDL', 'TRIGLICERIDOS'],
            'citrus bergamot': ['COLESTEROL LDL', 'GLICEMIA', 'COLESTEROL TOTAL'],
            'berberina': ['GLICEMIA', 'HbA1C', 'COLESTEROL LDL']
        }
        
        # Extraer dosis de suplementos usando regex
        # Buscar patrones como "**Metilfolato** (1000-2000 mcg)"
        dose_pattern = r'\*\*([^*]+)\*\*\s*\(([^)]+)\)'
        matches = re.finditer(dose_pattern, content, re.IGNORECASE)
        
        for match in matches:
            supplement_name = match.group(1).strip().lower()
            dose_info = match.group(2).strip()
            
            # Extraer valores numéricos de la dosis
            dose_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-|a)\s*(\d+(?:\.\d+)?)?\s*(mcg|mg|iu|µg)', dose_info, re.IGNORECASE)
            if dose_match:
                min_dose = float(dose_match.group(1))
                max_dose = float(dose_match.group(2)) if dose_match.group(2) else min_dose
                unit = dose_match.group(3).lower()
                
                # Normalizar unidades
                if unit in ['mcg', 'µg']:
                    unit = 'mcg'
                elif unit == 'iu':
                    unit = 'IU'
                
                # Buscar biomarcadores relacionados
                biomarkers = []
                for supp_key, biomarker_list in supplement_biomarker_map.items():
                    if supp_key in supplement_name:
                        biomarkers = biomarker_list
                        break
                
                supplements[supplement_name] = {
                    'name': match.group(1).strip(),
                    'min_dose': min_dose,
                    'max_dose': max_dose,
                    'unit': unit,
                    'biomarkers': biomarkers
                }
        
        return supplements
    except Exception as e:
        st.warning(f"Error extrayendo datos de suplementos: {e}")
        return {}


def load_biomarker_history() -> pd.DataFrame:
    """Carga el historial de biomarcadores desde exámenes de sangre"""
    blood_tests = find_blood_test_files()
    
    if not blood_tests:
        return pd.DataFrame()
    
    records = []
    for test in blood_tests:
        sample_date = test['sample_date']
        test_results = test['data'].get('test_results', [])
        
        for result in test_results:
            test_name = result.get('test_name', '')
            numeric_value = result.get('numeric_value')
            
            if numeric_value is not None:
                records.append({
                    'date': sample_date,
                    'test_name': test_name.upper(),
                    'value': numeric_value,
                    'units': result.get('units', ''),
                    'reference_min': result.get('reference_range', {}).get('min'),
                    'reference_max': result.get('reference_range', {}).get('max')
                })
    
    if records:
        df = pd.DataFrame(records)
        # Convertir fecha a datetime si es posible
        try:
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
            df = df.sort_values('date')
        except:
            pass
        return df
    
    return pd.DataFrame()


def main():
    """Función principal del dashboard"""
    st.set_page_config(
        page_title="Mariano DNA - Control Center",
        page_icon="🧬",
        layout="wide"
    )
    
    # Navegación en la barra lateral
    st.sidebar.title("🧬 Mariano DNA")
    st.sidebar.markdown("---")
    
    menu_option = st.sidebar.radio(
        "Navegación",
        ["🏠 Inicio", "📊 Panel de Salud", "⚙️ Servicios y Acciones", "📚 Biblioteca", "🤖 Asistente AI"]
    )
    
    # Buscar archivo de genoma (necesario para casi todo)
    genome_file = find_genome_file()
    
    if menu_option == "🏠 Inicio":
        render_home_section()
    elif menu_option == "📊 Panel de Salud":
        render_health_panel(genome_file)
    elif menu_option == "⚙️ Servicios y Acciones":
        render_services_section()
    elif menu_option == "📚 Biblioteca":
        render_library_section()
    elif menu_option == "🤖 Asistente AI":
        render_ai_assistant(genome_file)


def render_home_section():
    """Renderiza la página de inicio con instrucciones"""
    st.title("🧬 Mariano DNA - Centro de Control")
    st.markdown("""
    Bienvenido al ecosistema de optimización de salud de Mariano DNA. Desde este panel puedes gestionar todo tu análisis genético y epigenético.
    
    ### 🧭 Guía de Navegación
    
    1.  **🏠 Inicio**: Estado actual de tus archivos y guía rápida.
    2.  **📊 Panel de Salud**: Visualiza tus hallazgos genéticos, riesgos poligénicos (PRS), farmacogenómica y seguimiento de biomarcadores.
    3.  **⚙️ Servicios y Acciones**: Ejecuta los motores de análisis para actualizar tus resultados cuando añadas nuevos datos de ADN o sangre.
    4.  **📚 Biblioteca**: Consulta tus protocolos de suplementación, listas de compras y guías de referencia rápida.
    5.  **🤖 Asistente AI**: Interactúa con un equipo de agentes inteligentes que razonan sobre tus datos para darte recomendaciones personalizadas.
    
    ---
    ### 📂 Estado de los Datos
    """)
    
    col1, col2 = st.columns(2)
    
    genome_file = find_genome_file()
    blood_tests = find_blood_test_files()
    
    with col1:
        st.subheader("🧬 Genoma")
        if genome_file:
            st.success(f"Detectado: `{genome_file.name}`")
            st.info(f"Última modificación: {datetime.fromtimestamp(genome_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.error("No se detectó archivo de genoma en `data/raw/genome/`.")
            
    with col2:
        st.subheader("🩸 Exámenes de Sangre")
        if blood_tests:
            st.success(f"Detectados {len(blood_tests)} exámenes parseados.")
            latest_test = blood_tests[0]
            st.info(f"Más reciente: `{latest_test['test_name']}` ({latest_test['sample_date']})")
        else:
            st.warning("No se detectaron exámenes de sangre parseados en `data/raw/examenes_sangre/`.")

    st.markdown("---")
    st.info("💡 **Consejo:** Si acabas de añadir nuevos datos, ve a **⚙️ Servicios y Acciones** para actualizar los reportes.")


def render_health_panel(genome_file):
    """Renderiza el panel de salud tradicional"""
    st.title("📊 Panel de Salud")
    st.markdown("---")
    
    # Sidebar para configuración (ahora dentro del panel de salud)
    st.sidebar.header("Configuración Panel")
    
    if genome_file:
        st.sidebar.success(f"Genoma: {genome_file.name}")
    else:
        st.sidebar.error("No se encontró genoma")
        st.stop()
    
    # Inicializar componentes
    try:
        parser = GenomeParser(str(genome_file))
        
        # Parsear el genoma (cargar datos en memoria)
        with st.spinner("Cargando genoma..."):
            parser.parse()
        
        snp_db = SNPDatabase()
        report_extractor = ReportExtractor()
        
        # Cargar datos de Promethease si están disponibles
        promethease_json = Path("data/processed/hallazgos_geneticos.json")
        if promethease_json.exists():
            report_extractor.extract_file(str(promethease_json))
        else:
            # Buscar en reportes_proveedores
            promethease_dir = Path("data/raw/reportes_proveedores/promethease")
            if promethease_dir.exists():
                json_files = list(promethease_dir.glob("*.json"))
                if json_files:
                    report_extractor.extract_file(str(max(json_files, key=lambda p: p.stat().st_mtime)))
        
        analyzer = GeneticAnalyzer(parser, snp_db, report_extractor)
        
        # Ejecutar análisis
        with st.spinner("Ejecutando análisis genético..."):
            findings = analyzer.analyze()
            stats = analyzer.get_statistics()
        
        # Tabs principales
        tab_list = [
            "📊 Resumen", 
            "🔍 Hallazgos", 
            "💊 Farmacogenómica",
            "📈 PRS",
            "🗺️ Mapa de Riesgo",
            "📈 Seguimiento",
            "📋 Reportes"
        ]
        
        tabs = st.tabs(tab_list)
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs
        
        # Tab 1: Resumen
        with tab1:
            st.header("Resumen Ejecutivo")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Hallazgos", stats['total_findings'])
            
            with col2:
                st.metric("En Genoma", stats['found_in_genome'])
            
            with col3:
                st.metric("Solo en Reportes", stats['found_in_reports_only'])
            
            with col4:
                high_importance = stats['by_importance'].get('alto', 0)
                st.metric("Alta Importancia", high_importance, delta=None)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Hallazgos por Categoría")
                category_data = stats.get('by_category', {})
                if category_data and len(category_data) > 0:
                    try:
                        # Filtrar valores None o vacíos
                        filtered_data = {k: int(v) for k, v in category_data.items() if v and v > 0}
                        if filtered_data:
                            # Usar go.Figure directamente para evitar problemas con plotly.express
                            labels = list(filtered_data.keys())
                            values = list(filtered_data.values())
                            
                            fig = go.Figure(data=[go.Pie(
                                labels=labels,
                                values=values,
                                title="Distribución por Categoría"
                            )])
                            fig.update_layout(title="Distribución por Categoría")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No hay hallazgos por categoría para mostrar.")
                    except Exception as e:
                        st.error(f"Error creando gráfico de categorías: {e}")
                        # Mostrar tabla como alternativa
                        if category_data:
                            df_cat = pd.DataFrame(list(category_data.items()), columns=['Categoría', 'Cantidad'])
                            st.dataframe(df_cat, use_container_width=True)
                else:
                    st.info("No hay hallazgos por categoría para mostrar. El análisis genético no encontró SNPs relevantes en el genoma.")
            
            with col2:
                st.subheader("Hallazgos por Importancia")
                importance_data = stats.get('by_importance', {})
                if importance_data and len(importance_data) > 0:
                    try:
                        # Filtrar valores None o vacíos
                        filtered_data = {k: int(v) for k, v in importance_data.items() if v and v > 0}
                        if filtered_data:
                            # Usar go.Figure directamente para evitar problemas con plotly.express
                            x_values = list(filtered_data.keys())
                            y_values = list(filtered_data.values())
                            
                            # Mapear colores
                            colors_map = {'alto': 'red', 'medio': 'orange', 'bajo': 'green'}
                            bar_colors = [colors_map.get(imp, 'blue') for imp in x_values]
                            
                            fig = go.Figure(data=[go.Bar(
                                x=x_values,
                                y=y_values,
                                marker_color=bar_colors,
                                text=y_values,
                                textposition='auto'
                            )])
                            fig.update_layout(
                                title="Distribución por Importancia",
                                xaxis_title="Importancia",
                                yaxis_title="Cantidad"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No hay hallazgos por importancia para mostrar.")
                    except Exception as e:
                        st.error(f"Error creando gráfico de importancia: {e}")
                        # Mostrar tabla como alternativa
                        if importance_data:
                            df_imp = pd.DataFrame(list(importance_data.items()), columns=['Importancia', 'Cantidad'])
                            st.dataframe(df_imp, use_container_width=True)
                else:
                    st.info("No hay hallazgos por importancia para mostrar.")
            
            # Mensaje informativo si no hay hallazgos
            if stats['total_findings'] == 0:
                st.warning("""
                **⚠️ No se encontraron hallazgos genéticos**
                
                Esto puede deberse a:
                - El genoma no contiene los SNPs buscados en la base de datos
                - El formato del archivo de genoma no es compatible
                - Los SNPs están presentes pero no se identificaron como de riesgo
                
                **Sugerencias:**
                - Verifica que el archivo de genoma esté en formato 23andMe
                - Revisa la pestaña de "Hallazgos" para ver si hay información en reportes externos
                - El análisis puede estar funcionando correctamente si no hay variantes de riesgo significativas
                """)
        
        # Tab 2: Hallazgos
        with tab2:
            st.header("Hallazgos Genéticos Detallados")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                selected_category = st.selectbox(
                    "Filtrar por Categoría",
                    options=['Todas'] + list(stats['by_category'].keys())
                )
            with col2:
                selected_importance = st.selectbox(
                    "Filtrar por Importancia",
                    options=['Todas', 'alto', 'medio', 'bajo']
                )
            
            # Filtrar hallazgos
            filtered_findings = findings
            if selected_category != 'Todas':
                filtered_findings = [f for f in filtered_findings if f.category == selected_category]
            if selected_importance != 'Todas':
                filtered_findings = [f for f in filtered_findings if f.importance == selected_importance]
            
            # Mostrar hallazgos
            for finding in filtered_findings:
                with st.expander(f"{finding.rsid} - {finding.snp_info.gene if finding.snp_info else 'N/A'}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Genotipo:** {finding.genotype or 'No encontrado'}")
                        st.write(f"**Categoría:** {finding.category}")
                        st.write(f"**Importancia:** {finding.importance}")
                        if finding.magnitude:
                            st.write(f"**Magnitud:** {finding.magnitude}")
                        # Mostrar repute con iconos y colores
                        if finding.repute:
                            repute_emoji = {'Good': '✅', 'Bad': '⚠️', 'Not Set': '⚪'}.get(finding.repute, '')
                            if finding.repute == 'Good':
                                st.markdown(f"**Reputación:** <span style='color:green'>{repute_emoji} {finding.repute} (Protector)</span>", unsafe_allow_html=True)
                            elif finding.repute == 'Bad':
                                st.markdown(f"**Reputación:** <span style='color:red'>{repute_emoji} {finding.repute} (De Riesgo)</span>", unsafe_allow_html=True)
                            else:
                                st.write(f"**Reputación:** {repute_emoji} {finding.repute}")
                    
                    with col2:
                        st.write(f"**Descripción:** {finding.description}")
                        st.write(f"**Implicaciones:** {finding.implications}")
                    
                    if finding.related_conditions:
                        st.write(f"**Condiciones relacionadas:** {', '.join(finding.related_conditions)}")
                    
                    if finding.snpedia_url:
                        st.markdown(f"[Más información en SNPedia]({finding.snpedia_url})")
        
        # Tab 3: Farmacogenómica
        with tab3:
            st.header("Análisis Farmacogenómico")
            
            try:
                pharmgkb_client = None  # Se inicializaría con PharmGKBClient()
                pharm_analyzer = PharmacogenomicsAnalyzer(parser, pharmgkb_client)
                profiles = pharm_analyzer.analyze_all_genes()
                
                if profiles:
                    for gene, profile in profiles.items():
                        with st.expander(f"{gene} - {profile.phenotype}"):
                            st.write(f"**Diplotipo:** {profile.diplotype or 'No determinado'}")
                            st.write(f"**Fenotipo:** {profile.phenotype}")
                            if profile.activity_score is not None:
                                st.write(f"**Activity Score:** {profile.activity_score}")
                            
                            if profile.guidelines:
                                st.subheader("Guías Clínicas")
                                for guideline in profile.guidelines:
                                    st.write(f"**{guideline.drug_name.upper()}**")
                                    st.write(f"Recomendación: {guideline.recommendation}")
                                    st.write(f"Fuerza: {guideline.strength}")
                    else:
                        st.info("No se encontraron perfiles farmacogenómicos")
                else:
                    st.info("No se encontraron perfiles farmacogenómicos")
            except Exception as e:
                st.error(f"Error en análisis farmacogenómico: {e}")
        
        # Tab 4: PRS
        with tab4:
            st.header("Polygenic Risk Scores (PRS)")
            
            try:
                prs_calculator = PRSCalculator(parser)
                prs_results = prs_calculator.calculate_all_prs()
                
                if prs_results:
                    # Crear DataFrame para visualización
                    prs_data = []
                    for condition, result in prs_results.items():
                        prs_data.append({
                            'Condición': condition.replace('_', ' ').title(),
                            'PRS Score': result.prs_score,
                            'Percentil': result.percentile,
                            'Categoría': result.risk_category,
                            'SNPs Usados': f"{result.snps_used}/{result.total_snps}"
                        })
                    
                    df_prs = pd.DataFrame(prs_data)
                    
                    # Gráfico de barras
                    fig = px.bar(
                        df_prs,
                        x='Condición',
                        y='Percentil',
                        color='Categoría',
                        title="PRS por Condición",
                        color_discrete_map={
                            'low': 'green',
                            'moderate': 'yellow',
                            'high': 'orange',
                            'very_high': 'red'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabla detallada
                    st.subheader("Detalles de PRS")
                    st.dataframe(df_prs, use_container_width=True)
                    
                    # Interpretaciones
                    st.subheader("Interpretaciones")
                    for condition, result in prs_results.items():
                        st.write(f"**{condition.replace('_', ' ').title()}:**")
                        st.write(result.interpretation)
                        st.write("")
                else:
                    st.info("No se pudieron calcular PRS")
            except Exception as e:
                st.error(f"Error calculando PRS: {e}")
        
        # Tab 5: Mapa de Calor de Riesgo
        with tab5:
            st.header("🗺️ Mapa de Calor de Riesgo por Sistemas")
            st.markdown("Visualización de la densidad de riesgo genético agrupado por sistemas biológicos")
            
            try:
                # Mapear hallazgos a sistemas
                system_mapper = SystemMapper()
                system_risks = system_mapper.map_findings_to_systems(findings)
                
                # Crear DataFrame para visualización
                df_systems = system_mapper.get_system_risk_dataframe()
                
                if not df_systems.empty:
                    # Gráfico de mapa de calor
                    st.subheader("Mapa de Calor de Riesgo")
                    
                    # Preparar datos para el mapa de calor
                    heatmap_data = df_systems.set_index('Sistema')[['Score de Riesgo', 'Alto Riesgo', 'Riesgo Medio', 'Riesgo Bajo']]
                    
                    fig = px.imshow(
                        heatmap_data.T,
                        labels=dict(x="Sistema", y="Métrica", color="Valor"),
                        color_continuous_scale="RdYlGn_r",  # Rojo-Amarillo-Verde invertido (rojo = alto riesgo)
                        aspect="auto",
                        title="Densidad de Riesgo Genético por Sistema"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Gráfico de barras de score de riesgo
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Score de Riesgo por Sistema")
                        fig_bar = px.bar(
                            df_systems,
                            x='Sistema',
                            y='Score de Riesgo',
                            color='Score de Riesgo',
                            color_continuous_scale="RdYlGn_r",
                            title="Score Normalizado de Riesgo"
                        )
                        fig_bar.update_layout(showlegend=False, height=400)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        st.subheader("Distribución de SNPs por Nivel de Riesgo")
                        # Crear datos apilados
                        risk_data = []
                        for _, row in df_systems.iterrows():
                            risk_data.append({'Sistema': row['Sistema'], 'Nivel': 'Alto Riesgo', 'Cantidad': row['Alto Riesgo']})
                            risk_data.append({'Sistema': row['Sistema'], 'Nivel': 'Riesgo Medio', 'Cantidad': row['Riesgo Medio']})
                            risk_data.append({'Sistema': row['Sistema'], 'Nivel': 'Riesgo Bajo', 'Cantidad': row['Riesgo Bajo']})
                        
                        df_risk_dist = pd.DataFrame(risk_data)
                        fig_stack = px.bar(
                            df_risk_dist,
                            x='Sistema',
                            y='Cantidad',
                            color='Nivel',
                            color_discrete_map={
                                'Alto Riesgo': 'red',
                                'Riesgo Medio': 'orange',
                                'Riesgo Bajo': 'yellow'
                            },
                            title="SNPs por Nivel de Riesgo",
                            barmode='stack'
                        )
                        fig_stack.update_layout(height=400)
                        st.plotly_chart(fig_stack, use_container_width=True)
                    
                    # Tabla detallada
                    st.subheader("Detalles por Sistema")
                    st.dataframe(df_systems, use_container_width=True)
                    
                    # Detalles de hallazgos por sistema
                    st.subheader("Hallazgos Detallados por Sistema")
                    selected_system = st.selectbox(
                        "Seleccionar sistema para ver detalles",
                        options=list(system_risks.keys()),
                        format_func=lambda x: f"{x} ({system_risks[x].total_snps} SNPs)"
                    )
                    
                    if selected_system and system_risks[selected_system].findings:
                        st.write(f"**Total de SNPs en {selected_system}:** {system_risks[selected_system].total_snps}")
                        st.write(f"**Score de Riesgo:** {system_risks[selected_system].risk_score:.3f}")
                        
                        for finding in system_risks[selected_system].findings:
                            with st.expander(f"{finding.rsid} - {finding.snp_info.gene if finding.snp_info else 'N/A'} ({finding.importance})"):
                                st.write(f"**Genotipo:** {finding.genotype or 'No encontrado'}")
                                st.write(f"**Descripción:** {finding.description}")
                                st.write(f"**Implicaciones:** {finding.implications}")
                else:
                    st.info("No se encontraron sistemas con SNPs para visualizar")
            except Exception as e:
                st.error(f"Error generando mapa de calor: {e}")
                st.exception(e)
        
        # Tab 6: Seguimiento de Biomarcadores
        with tab6:
            st.header("📈 Seguimiento de Biomarcadores y Suplementación")
            st.markdown("Relación entre dosis de suplementos y niveles en sangre")
            
            try:
                # Cargar datos
                biomarker_df = load_biomarker_history()
                supplement_data = extract_supplement_data()
                
                if biomarker_df.empty:
                    st.warning("No se encontraron exámenes de sangre. Agrega archivos JSON parseados en `data/raw/examenes_sangre/`")
                else:
                    # Seleccionar biomarcador
                    available_biomarkers = sorted(biomarker_df['test_name'].unique())
                    selected_biomarker = st.selectbox(
                        "Seleccionar biomarcador para visualizar",
                        options=available_biomarkers
                    )
                    
                    if selected_biomarker:
                        # Filtrar datos del biomarcador seleccionado
                        biomarker_data = biomarker_df[biomarker_df['test_name'] == selected_biomarker].copy()
                        
                        if not biomarker_data.empty:
                            # Gráfico de evolución temporal
                            st.subheader(f"Evolución de {selected_biomarker}")
                            
                            # Preparar datos: convertir fechas y filtrar valores inválidos
                            plot_data = biomarker_data.copy()
                            
                            # Convertir fechas de forma segura
                            try:
                                # Intentar convertir a datetime
                                if not pd.api.types.is_datetime64_any_dtype(plot_data['date']):
                                    plot_data['date'] = pd.to_datetime(plot_data['date'], errors='coerce')
                                
                                # Si hay NaT, usar índice como fallback
                                if plot_data['date'].isna().any():
                                    plot_data['date'] = plot_data.index.astype(str)
                                else:
                                    # Convertir datetime a string para Plotly
                                    plot_data['date'] = plot_data['date'].astype(str)
                            except Exception as date_error:
                                # Si falla la conversión, usar índice
                                plot_data['date'] = plot_data.index.astype(str)
                            
                            # Convertir a lista para evitar problemas con Plotly
                            x_values = plot_data['date'].tolist()
                            y_values = plot_data['value'].tolist()
                            
                            # Validar que tenemos datos válidos
                            if not x_values or not y_values:
                                st.warning("No hay datos válidos para graficar")
                            else:
                                # Crear gráfico de línea con rangos de referencia
                                fig = go.Figure()
                                
                                # Agregar línea de valores
                                fig.add_trace(go.Scatter(
                                    x=x_values,
                                    y=y_values,
                                    mode='lines+markers',
                                    name='Valor Medido',
                                    line=dict(color='blue', width=2),
                                    marker=dict(size=10)
                                ))
                                
                                # Agregar rangos de referencia si están disponibles
                                if plot_data['reference_min'].notna().any():
                                    ref_min = plot_data['reference_min'].dropna().iloc[0]
                                    if pd.notna(ref_min):
                                        fig.add_trace(go.Scatter(
                                            x=x_values,
                                            y=[ref_min] * len(plot_data),
                                            mode='lines',
                                            name='Límite Mínimo',
                                            line=dict(color='green', width=1, dash='dash'),
                                            showlegend=True
                                        ))
                                
                                if plot_data['reference_max'].notna().any():
                                    ref_max = plot_data['reference_max'].dropna().iloc[0]
                                    if pd.notna(ref_max):
                                        fig.add_trace(go.Scatter(
                                            x=x_values,
                                            y=[ref_max] * len(plot_data),
                                            mode='lines',
                                            name='Límite Máximo',
                                            line=dict(color='red', width=1, dash='dash'),
                                            showlegend=True
                                        ))
                                
                                # Agregar zona óptima (si hay información)
                                # Por ejemplo, para homocisteína, el óptimo es <7 µmol/L
                                optimal_ranges = {
                                    'HOMOCISTEINA': (0, 7),
                                    'VITAMINA D': (50, 70),
                                    'VITAMINA B-12': (800, 2000),
                                    'ÁCIDO FÓLICO': (15, 20),
                                    'GLICEMIA': (70, 85),
                                    'COLESTEROL LDL': (0, 100),
                                    'COLESTEROL HDL': (50, 100)
                                }
                                
                                biomarker_key = selected_biomarker.upper()
                                if biomarker_key in optimal_ranges:
                                    opt_min, opt_max = optimal_ranges[biomarker_key]
                                    fig.add_trace(go.Scatter(
                                        x=x_values,
                                        y=[opt_max] * len(plot_data),
                                        mode='lines',
                                        name='Óptimo Superior',
                                        line=dict(color='lightgreen', width=1, dash='dot'),
                                        fillcolor='rgba(144, 238, 144, 0.2)',
                                        fill='tonexty' if plot_data['reference_min'].notna().any() else None,
                                        showlegend=True
                                    ))
                                
                                units_str = plot_data['units'].iloc[0] if plot_data['units'].notna().any() else ''
                                fig.update_layout(
                                    title=f"Evolución de {selected_biomarker}",
                                    xaxis_title="Fecha",
                                    yaxis_title=f"Valor ({units_str})",
                                    height=500,
                                    hovermode='x unified'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Mostrar tabla de datos
                            st.subheader("Datos Históricos")
                            display_df = biomarker_data[['date', 'value', 'units', 'reference_min', 'reference_max']].copy()
                            display_df.columns = ['Fecha', 'Valor', 'Unidades', 'Ref. Mín', 'Ref. Máx']
                            st.dataframe(display_df, use_container_width=True)
                            
                            # Información de suplementos relacionados
                            st.subheader("Suplementos Relacionados")
                            related_supplements = []
                            for supp_name, supp_info in supplement_data.items():
                                if selected_biomarker.upper() in [b.upper() for b in supp_info.get('biomarkers', [])]:
                                    related_supplements.append({
                                        'Suplemento': supp_info['name'],
                                        'Dosis': f"{supp_info['min_dose']}-{supp_info['max_dose']} {supp_info['unit']}",
                                        'Biomarcadores': ', '.join(supp_info.get('biomarkers', []))
                                    })
                            
                            if related_supplements:
                                st.dataframe(pd.DataFrame(related_supplements), use_container_width=True)
                            else:
                                st.info("No se encontraron suplementos relacionados con este biomarcador en el stack actual")
                            
                            # Gráfico de dispersión: Dosis vs Nivel (cuando haya múltiples exámenes)
                            if len(biomarker_data) >= 2:
                                st.subheader("Análisis de Correlación")
                                st.info("Cuando tengas un segundo examen de sangre después de iniciar la suplementación, aquí se mostrará la relación entre dosis y niveles.")
                                
                                # Preparar datos para cuando haya información de dosis
                                # Por ahora, mostrar mensaje informativo
                                st.markdown("""
                                **Nota:** Para visualizar la relación dosis vs nivel, necesitas:
                                1. Al menos 2 exámenes de sangre (antes y después de suplementación)
                                2. Registrar las dosis diarias de suplementos tomadas
                                3. El sistema calculará automáticamente la correlación
                                """)
            except Exception as e:
                st.error(f"Error en la pestaña de Seguimiento: {e}")
                st.exception(e)
        
        # Tab 7: Reportes
        with tab7:
            st.header("Reportes Generados")
            
            st.subheader("Tarjeta Farmacogenómica")
            try:
                pharmgkb_client = None
                pharm_analyzer = PharmacogenomicsAnalyzer(parser, pharmgkb_client)
                card = pharm_analyzer.generate_pharmacogenomic_card()
                st.text_area("Tarjeta Farmacogenómica", card, height=400)
            except Exception as e:
                st.error(f"Error generando tarjeta: {e}")
            
            st.subheader("Reporte de PRS")
            try:
                prs_calculator = PRSCalculator(parser)
                prs_report = prs_calculator.generate_prs_report()
                st.text_area("Reporte PRS", prs_report, height=400)
            except Exception as e:
                st.error(f"Error generando reporte PRS: {e}")
    
    except Exception as e:
        st.error(f"Error inicializando análisis: {e}")
        st.exception(e)


def render_services_section():
    """Renderiza la sección de acciones y servicios"""
    st.title("⚙️ Servicios y Acciones")
    st.markdown("Ejecuta procesos de análisis en segundo plano.")
    
    import subprocess
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧬 Análisis Genómico")
        if st.button("Ejecutar run_analysis.py"):
            with st.spinner("Ejecutando análisis genético..."):
                try:
                    result = subprocess.run(["python", "src/scripts/run_analysis.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Análisis completado exitosamente.")
                    else:
                        st.error(f"Error en la ejecución:\n{result.stderr}")
                except Exception as e:
                    st.error(f"Error al intentar ejecutar el script: {e}")
        
        st.subheader("🩸 Análisis Sistémico")
        if st.button("Ejecutar analyze_blood_test_systemic.py"):
            with st.spinner("Ejecutando análisis sistémico..."):
                try:
                    result = subprocess.run(["python", "src/scripts/analyze_blood_test_systemic.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Análisis sistémico completado exitosamente.")
                    else:
                        st.error(f"Error en la ejecución:\n{result.stderr}")
                except Exception as e:
                    st.error(f"Error al intentar ejecutar el script: {e}")

    with col2:
        st.subheader("🔍 Auditoría y Control")
        if st.button("Auditar Hallazgos del Dashboard"):
            with st.spinner("Auditando hallazgos..."):
                try:
                    result = subprocess.run(["python", "src/scripts/audit_dashboard_findings.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Auditoría completada exitosamente.")
                    else:
                        st.error(f"Error en la ejecución:\n{result.stderr}")
                except Exception as e:
                    st.error(f"Error al intentar ejecutar el script: {e}")
        
        st.subheader("🤖 Análisis Pro de Agentes")
        if st.button("Ejecutar run_agent_analysis.py"):
            with st.spinner("Ejecutando agentes en modo batch..."):
                try:
                    result = subprocess.run(["python", "src/scripts/run_agent_analysis.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Análisis de agentes completado exitosamente.")
                    else:
                        st.error(f"Error en la ejecución:\n{result.stderr}")
                except Exception as e:
                    st.error(f"Error al intentar ejecutar el script: {e}")


def render_library_section():
    """Renderiza el explorador de documentos y biblioteca"""
    st.title("📚 Biblioteca y Protocolos")
    
    docs_path = Path("docs/reference")
    outputs_path = Path("outputs")
    
    # Combinar archivos md de ambas rutas
    files = []
    if docs_path.exists():
        files.extend([f for f in docs_path.rglob("*.md")])
    if outputs_path.exists():
        files.extend([f for f in outputs_path.rglob("*.md")])
    
    if not files:
        st.info("No se encontraron documentos Markdown.")
        return
    
    # Crear diccionario de nombres para mostrar
    file_dict = {f.name: f for f in sorted(files, key=lambda p: p.name)}
    
    selected_file_name = st.selectbox("Selecciona un documento para visualizar", options=list(file_dict.keys()))
    
    if selected_file_name:
        selected_file_path = file_dict[selected_file_name]
        st.markdown("---")
        try:
            with open(selected_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.markdown(content)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")


def render_ai_assistant(genome_file):
    """Renderiza el asistente AI"""
    st.title("🤖 Asistente AI")
    
    if not HAS_AGENTS:
        st.error("Los componentes de IA no están cargados correctamente.")
        return

    st.markdown("Interactúa con el sistema multi-agente para obtener razonamiento clínico profundo.")
    
    # Inicializar historial de chat si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if prompt := st.chat_input("¿Qué quieres saber sobre tus resultados?"):
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Procesar con el orquestador
        with st.chat_message("assistant"):
            with st.spinner("Los agentes están analizando tus datos..."):
                try:
                    # Re-analizar rápido para el agente
                    parser = GenomeParser(str(genome_file))
                    parser.parse()
                    snp_db = SNPDatabase()
                    report_extractor = ReportExtractor()
                    analyzer = GeneticAnalyzer(parser, snp_db, report_extractor)
                    findings = analyzer.analyze()
                    
                    orchestrator = MarianoDNAOrchestrator()
                    
                    serialized_findings = []
                    for f in findings:
                        serialized_findings.append({
                            "rsid": f.rsid,
                            "genotype": f.genotype,
                            "category": f.category,
                            "importance": f.importance,
                            "description": f.description,
                            "implications": f.implications,
                            "magnitude": f.magnitude,
                            "repute": f.repute
                        })
                    
                    blood_history = load_biomarker_history()
                    blood_list = []
                    if not blood_history.empty:
                        latest_date = blood_history['date'].max()
                        latest_blood = blood_history[blood_history['date'] == latest_date]
                        for _, row in latest_blood.iterrows():
                            blood_list.append({
                                "test_name": row['test_name'],
                                "numeric_value": row['value'],
                                "units": row['units'],
                                "reference_range": {"min": row['reference_min'], "max": row['reference_max']}
                            })
                    
                    initial_state = create_initial_state(
                        dna_data={"findings": serialized_findings},
                        blood_data=blood_list,
                        notes=prompt
                    )
                    
                    final_state = orchestrator.run(initial_state)
                    response = final_state.get("final_report", "Lo siento, no pude generar una respuesta.")
                    
                    with st.expander("Ver razonamiento clínico de los agentes"):
                        for r in final_state.get("clinical_reasoning", []):
                            st.markdown(r)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as agent_error:
                    st.error(f"Error en el sistema de agentes: {agent_error}")


if __name__ == "__main__":
    main()
