"""
Generador de reportes en Markdown
"""

from typing import List
from datetime import datetime
from .analyzer import Finding


class ReportGenerator:
    """Genera reportes en formato Markdown"""
    
    def __init__(self, findings: List[Finding], statistics: dict, epigenetic_data: List[dict] = None):
        """
        Inicializa el generador
        
        Args:
            findings: Lista de hallazgos genéticos
            statistics: Estadísticas del análisis
            epigenetic_data: Lista de datos epigenéticos encontrados (opcional)
        """
        self.findings = findings
        self.statistics = statistics
        self.epigenetic_data = epigenetic_data or []
    
    def generate(self) -> str:
        """
        Genera el reporte completo en Markdown
        
        Returns:
            Contenido del reporte en Markdown
        """
        lines = []
        
        # Encabezado
        lines.append("# Reporte de Hallazgos Genéticos Completos")
        lines.append(f"**Generado el:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Advertencia importante
        lines.append("## ⚠️ ADVERTENCIA IMPORTANTE")
        lines.append("")
        lines.append("Este reporte es **solo para fines informativos y educativos**.")
        lines.append("**NO reemplaza el consejo médico profesional.**")
        lines.append("")
        lines.append("Si encuentras hallazgos preocupantes, consulta con un:")
        lines.append("- Médico genetista")
        lines.append("- Asesor genético")
        lines.append("- Profesional de salud calificado")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Resumen ejecutivo
        lines.append("## 📊 Resumen Ejecutivo")
        lines.append("")
        lines.append(f"- **Total de hallazgos importantes:** {self.statistics['total_findings']}")
        lines.append(f"- **Hallazgos encontrados en genoma:** {self.statistics['found_in_genome']}")
        lines.append(f"- **Hallazgos solo en reportes:** {self.statistics['found_in_reports_only']}")
        if self.epigenetic_data:
            lines.append(f"- **Reportes epigenéticos procesados:** {len(self.epigenetic_data)}")
        lines.append("")
        
        # Estadísticas por categoría
        lines.append("### Hallazgos por Categoría")
        lines.append("")
        for category, count in sorted(self.statistics['by_category'].items()):
            category_name = {
                'salud': 'Riesgos de Salud',
                'farmacogenetica': 'Farmacogenética',
                'nutrigenomica': 'Nutrigenómica',
                'longevidad': 'Longevidad',
                'rasgos': 'Rasgos Heredados'
            }.get(category, category.title())
            lines.append(f"- **{category_name}:** {count}")
        lines.append("")
        
        # Estadísticas por importancia
        lines.append("### Hallazgos por Importancia")
        lines.append("")
        for importance, count in sorted(self.statistics['by_importance'].items(), 
                                      key=lambda x: {'alto': 0, 'medio': 1, 'bajo': 2}.get(x[0], 3)):
            importance_name = {
                'alto': '🔴 Alta',
                'medio': '🟡 Media',
                'bajo': '🟢 Baja'
            }.get(importance, importance.title())
            lines.append(f"- **{importance_name}:** {count}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Hallazgos por categoría
        categories = ['salud', 'farmacogenetica', 'nutrigenomica', 'longevidad', 'rasgos']
        category_names = {
            'salud': 'Riesgos de Salud',
            'farmacogenetica': 'Farmacogenética',
            'nutrigenomica': 'Nutrigenómica',
            'longevidad': 'Longevidad y Envejecimiento',
            'rasgos': 'Rasgos Heredados'
        }
        
        for category in categories:
            category_findings = [f for f in self.findings if f.category == category]
            if not category_findings:
                continue
            
            lines.append(f"## {category_names[category]}")
            lines.append("")
            
            # Ordenar por importancia (alto -> medio -> bajo)
            category_findings.sort(key=lambda x: {'alto': 0, 'medio': 1, 'bajo': 2}.get(x.importance, 3))
            
            for finding in category_findings:
                self._add_finding(lines, finding)
            
            lines.append("---")
            lines.append("")
        
        # Sección de Epigenética
        if self.epigenetic_data:
            lines.append("## 🧬 Datos Epigenéticos")
            lines.append("")
            lines.append("Los datos epigenéticos muestran modificaciones químicas del ADN que pueden cambiar con el tiempo y están influenciadas por factores ambientales, dieta, ejercicio y estilo de vida.")
            lines.append("")
            lines.append("### Comparación: Genética vs Epigenética")
            lines.append("")
            lines.append("- **Genética (SNPs):** Variantes permanentes heredadas que no cambian")
            lines.append("- **Epigenética (Metilación):** Modificaciones modificables que reflejan el estado actual")
            lines.append("")
            
            for epi_data in self.epigenetic_data:
                lines.append(f"### 📄 {epi_data.get('file_name', 'Reporte Epigenético')}")
                lines.append("")
                
                if epi_data.get('biological_age'):
                    lines.append(f"- **Edad Biológica (Epigenética):** {epi_data['biological_age']} años")
                    lines.append("")
                
                if epi_data.get('methylation_level'):
                    lines.append(f"- **Nivel de Metilación Global:** {epi_data['methylation_level']}%")
                    lines.append("")
                
                if epi_data.get('related_snps'):
                    lines.append(f"- **SNPs relacionados encontrados:** {len(epi_data['related_snps'])}")
                    if len(epi_data['related_snps']) <= 10:
                        snps_str = ', '.join(epi_data['related_snps'])
                        lines.append(f"  - {snps_str}")
                    else:
                        snps_str = ', '.join(epi_data['related_snps'][:10])
                        lines.append(f"  - {snps_str}... (y {len(epi_data['related_snps']) - 10} más)")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # Referencias y recursos
        lines.append("## 📚 Recursos Adicionales")
        lines.append("")
        lines.append("- **SNPedia:** https://www.snpedia.com/")
        lines.append("- **Genetic Genie:** https://geneticgenie.org/")
        lines.append("- **NutraHacker:** https://nutrahacker.com/")
        lines.append("- **Promethease:** https://promethease.com/")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📝 Notas Finales")
        lines.append("")
        lines.append("- Este reporte se basa en análisis genético y literatura científica disponible.")
        lines.append("- La genética es solo una pieza del rompecabezas de la salud.")
        lines.append("- Factores ambientales, dieta, ejercicio y estilo de vida también son cruciales.")
        lines.append("- Siempre consulta con profesionales de salud antes de tomar decisiones médicas.")
        lines.append("")
        
        return "\n".join(lines)
    
    def _add_finding(self, lines: List[str], finding: Finding):
        """Añade un hallazgo al reporte"""
        # Encabezado del hallazgo
        importance_emoji = {
            'alto': '🔴',
            'medio': '🟡',
            'bajo': '🟢'
        }.get(finding.importance, '⚪')
        
        lines.append(f"### {importance_emoji} {finding.rsid} - {finding.snp_info.gene if finding.snp_info else 'N/A'}")
        lines.append("")
        
        # Información básica
        if finding.genotype:
            lines.append(f"- **Genotipo:** `{finding.genotype}`")
        else:
            lines.append("- **Genotipo:** No encontrado en genoma raw")
        
        if finding.found_in_reports:
            sources = ', '.join(finding.report_sources)
            lines.append(f"- **Encontrado en reportes:** {sources}")
        
        # Información adicional de Promethease
        if finding.magnitude is not None:
            lines.append(f"- **Magnitud:** {finding.magnitude}")
            if finding.max_magnitude and finding.max_magnitude != finding.magnitude:
                lines.append(f"- **Magnitud máxima:** {finding.max_magnitude}")
        
        if finding.repute:
            repute_emoji = {'Good': '✅', 'Bad': '⚠️', 'Not Set': '⚪'}.get(finding.repute, '')
            lines.append(f"- **Reputación:** {repute_emoji} {finding.repute}")
        
        if finding.frequency:
            lines.append(f"- **Frecuencia poblacional:** {finding.frequency}")
        
        if finding.chromosome and finding.position:
            lines.append(f"- **Ubicación:** Cromosoma {finding.chromosome}, posición {finding.position}")
        
        if finding.genes:
            genes_str = ', '.join(finding.genes)
            lines.append(f"- **Genes:** {genes_str}")
        
        if finding.publications:
            lines.append(f"- **Publicaciones:** {finding.publications}")
        
        lines.append("")
        
        # Resumen de Promethease si está disponible
        if finding.summary:
            lines.append(f"**Resumen:** {finding.summary}")
            lines.append("")
        
        # Descripción
        if finding.description:
            lines.append(f"**Descripción:** {finding.description}")
            lines.append("")
        
        # Implicaciones
        lines.append(f"**Implicaciones:** {finding.implications}")
        lines.append("")
        
        # Condiciones relacionadas
        all_conditions = set(finding.related_conditions)
        if finding.medical_conditions_from_reports:
            all_conditions.update(finding.medical_conditions_from_reports)
        
        if all_conditions:
            lines.append("**Condiciones relacionadas:**")
            for condition in sorted(all_conditions):
                lines.append(f"- {condition}")
            lines.append("")
        
        # Topics de Promethease si están disponibles
        if finding.topics:
            lines.append("**Temas relacionados:**")
            topics_str = ', '.join(finding.topics[:10])  # Limitar a 10 topics
            lines.append(topics_str)
            lines.append("")
        
        # Enlace a SNPedia
        lines.append(f"**Más información:** [{finding.rsid} en SNPedia]({finding.snpedia_url})")
        lines.append("")
        
        # Separador
        lines.append("---")
        lines.append("")

