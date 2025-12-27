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

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dna_analyzer.parser import GenomeParser
from dna_analyzer.analyzer import GeneticAnalyzer
from dna_analyzer.snp_database import SNPDatabase
from dna_analyzer.pdf_extractor import ReportExtractor
from dna_analyzer.pharmacogenomics import PharmacogenomicsAnalyzer
from dna_analyzer.prs_calculator import PRSCalculator
from dna_analyzer.clinvar_client import ClinVarClient


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


def main():
    """Función principal del dashboard"""
    st.set_page_config(
        page_title="Análisis Genético - Mariano DNA",
        page_icon="🧬",
        layout="wide"
    )
    
    st.title("🧬 Dashboard de Análisis Genético")
    st.markdown("---")
    
    # Sidebar para configuración
    st.sidebar.header("Configuración")
    
    # Buscar archivo de genoma
    genome_file = find_genome_file()
    if genome_file:
        st.sidebar.success(f"Genoma encontrado: {genome_file.name}")
    else:
        st.sidebar.error("No se encontró archivo de genoma")
        st.stop()
    
    # Inicializar componentes
    try:
        parser = GenomeParser(str(genome_file))
        snp_db = SNPDatabase()
        report_extractor = ReportExtractor()
        analyzer = GeneticAnalyzer(parser, snp_db, report_extractor)
        
        # Ejecutar análisis
        with st.spinner("Ejecutando análisis genético..."):
            findings = analyzer.analyze()
            stats = analyzer.get_statistics()
        
        # Tabs principales
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Resumen", 
            "🔍 Hallazgos", 
            "💊 Farmacogenómica",
            "📈 PRS",
            "📋 Reportes"
        ])
        
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
                category_data = stats['by_category']
                if category_data:
                    fig = px.pie(
                        values=list(category_data.values()),
                        names=list(category_data.keys()),
                        title="Distribución por Categoría"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Hallazgos por Importancia")
                importance_data = stats['by_importance']
                if importance_data:
                    colors = {'alto': 'red', 'medio': 'orange', 'bajo': 'green'}
                    fig = px.bar(
                        x=list(importance_data.keys()),
                        y=list(importance_data.values()),
                        title="Distribución por Importancia",
                        color=list(importance_data.keys()),
                        color_discrete_map=colors
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
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
        
        # Tab 5: Reportes
        with tab5:
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


if __name__ == '__main__':
    main()

