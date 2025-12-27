#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de análisis farmacogenómico completo
Integra diplotipos, fenotipos y guías clínicas CPIC
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .pharmgkb_client import PharmGKBClient, GenePhenotype, DrugGuideline
from .parser import GenomeParser


@dataclass
class PharmacogenomicProfile:
    """Perfil farmacogenómico completo de un individuo"""
    gene: str
    diplotype: Optional[str]
    phenotype: str
    activity_score: Optional[float]
    metabolizer_status: Optional[str]
    relevant_drugs: List[str]
    guidelines: List[DrugGuideline]


class PharmacogenomicsAnalyzer:
    """Analizador farmacogenómico completo"""
    
    # Genes farmacogenómicos importantes
    PHARMACOGENOMIC_GENES = [
        'CYP2D6', 'CYP2C19', 'CYP2C9', 'CYP3A4', 'CYP3A5',
        'DPYD', 'TPMT', 'NUDT15', 'UGT1A1', 'SLCO1B1', 'VKORC1'
    ]
    
    # SNPs clave para cada gen
    GENE_SNPS = {
        'CYP2D6': ['rs1065852', 'rs16947', 'rs28371725', 'rs5030865', 'rs35742686', 'rs3892097'],
        'CYP2C19': ['rs4244285', 'rs4986893', 'rs12248560', 'rs28399504'],
        'CYP2C9': ['rs1799853', 'rs1057910', 'rs7900194', 'rs28371686'],
        'CYP3A4': ['rs2740574'],
        'CYP3A5': ['rs776746'],
        'DPYD': ['rs3918290', 'rs55886062'],
        'TPMT': ['rs1800462', 'rs1142345'],
        'NUDT15': ['rs116855232'],
        'UGT1A1': ['rs8175347'],
        'SLCO1B1': ['rs4149056'],
        'VKORC1': ['rs9923231', 'rs7294'],
    }
    
    def __init__(self, genome_parser: GenomeParser, pharmgkb_client: Optional[PharmGKBClient] = None):
        """
        Inicializa el analizador farmacogenómico
        
        Args:
            genome_parser: Parser del genoma
            pharmgkb_client: Cliente PharmGKB (opcional, se crea uno si no se proporciona)
        """
        self.genome_parser = genome_parser
        self.pharmgkb_client = pharmgkb_client or PharmGKBClient()
        self.profiles: Dict[str, PharmacogenomicProfile] = {}
    
    def analyze_all_genes(self) -> Dict[str, PharmacogenomicProfile]:
        """
        Analiza todos los genes farmacogenómicos
        
        Returns:
            Diccionario de gen -> perfil farmacogenómico
        """
        print("\n[FARMACOGENOMICA] Analizando genes farmacogenómicos...")
        
        for gene in self.PHARMACOGENOMIC_GENES:
            profile = self.analyze_gene(gene)
            if profile:
                self.profiles[gene] = profile
        
        print(f"[OK] Analizados {len(self.profiles)} genes farmacogenómicos")
        return self.profiles
    
    def analyze_gene(self, gene: str) -> Optional[PharmacogenomicProfile]:
        """
        Analiza un gen farmacogenómico específico
        
        Args:
            gene: Nombre del gen
            
        Returns:
            Perfil farmacogenómico o None si no se puede determinar
        """
        # Obtener SNPs relevantes para este gen
        snps = self.GENE_SNPS.get(gene, [])
        if not snps:
            return None
        
        # Obtener genotipos del genoma
        genotypes = {}
        for rsid in snps:
            genotype = self.genome_parser.get_snp(rsid)
            if genotype:
                genotypes[rsid] = genotype
        
        if not genotypes:
            return None
        
        # Calcular diplotipo
        diplotype = self.pharmgkb_client.calculate_diplotype(gene, genotypes)
        if not diplotype:
            # Si no se puede calcular diplotipo, intentar con fenotipo basado en SNPs individuales
            return self._analyze_from_snps(gene, genotypes)
        
        # Obtener fenotipo
        phenotype_info = self.pharmgkb_client.get_phenotype_from_diplotype(gene, diplotype)
        
        # Obtener medicamentos relevantes y guías
        relevant_drugs = self._get_relevant_drugs(gene)
        guidelines = []
        for drug in relevant_drugs:
            drug_guidelines = self.pharmgkb_client.get_drug_guidelines(
                drug, gene, phenotype_info.phenotype
            )
            guidelines.extend(drug_guidelines)
        
        profile = PharmacogenomicProfile(
            gene=gene,
            diplotype=diplotype,
            phenotype=phenotype_info.phenotype,
            activity_score=phenotype_info.activity_score,
            metabolizer_status=phenotype_info.metabolizer_status,
            relevant_drugs=relevant_drugs,
            guidelines=guidelines
        )
        
        return profile
    
    def _analyze_from_snps(self, gene: str, genotypes: Dict[str, str]) -> Optional[PharmacogenomicProfile]:
        """Analiza gen basado en SNPs individuales cuando no se puede calcular diplotipo"""
        # Lógica simplificada basada en SNPs conocidos
        if gene == 'CYP2D6' and 'rs1065852' in genotypes:
            genotype = genotypes['rs1065852']
            if genotype == 'AA':
                phenotype = "Poor Metabolizer"
                metabolizer_status = "poor"
            elif 'A' in genotype:
                phenotype = "Intermediate Metabolizer"
                metabolizer_status = "intermediate"
            else:
                phenotype = "Normal Metabolizer"
                metabolizer_status = "normal"
        elif gene == 'CYP2C19' and 'rs4244285' in genotypes:
            genotype = genotypes['rs4244285']
            if genotype == 'AA':
                phenotype = "Poor Metabolizer"
                metabolizer_status = "poor"
            elif 'A' in genotype:
                phenotype = "Intermediate Metabolizer"
                metabolizer_status = "intermediate"
            else:
                phenotype = "Normal Metabolizer"
                metabolizer_status = "normal"
        elif gene == 'CYP2C9' and 'rs1057910' in genotypes:
            genotype = genotypes['rs1057910']
            if genotype == 'AA':
                phenotype = "Poor Metabolizer"
                metabolizer_status = "poor"
            elif 'A' in genotype:
                phenotype = "Intermediate Metabolizer"
                metabolizer_status = "intermediate"
            else:
                phenotype = "Normal Metabolizer"
                metabolizer_status = "normal"
        else:
            return None
        
        relevant_drugs = self._get_relevant_drugs(gene)
        guidelines = []
        for drug in relevant_drugs:
            drug_guidelines = self.pharmgkb_client.get_drug_guidelines(drug, gene, phenotype)
            guidelines.extend(drug_guidelines)
        
        return PharmacogenomicProfile(
            gene=gene,
            diplotype=None,
            phenotype=phenotype,
            activity_score=None,
            metabolizer_status=metabolizer_status,
            relevant_drugs=relevant_drugs,
            guidelines=guidelines
        )
    
    def _get_relevant_drugs(self, gene: str) -> List[str]:
        """Obtiene lista de medicamentos relevantes para un gen"""
        drug_map = {
            'CYP2D6': ['codeine', 'tramadol', 'metoprolol', 'propranolol', 'amitriptyline', 'paroxetine', 'fluoxetine'],
            'CYP2C19': ['clopidogrel', 'omeprazole', 'citalopram', 'escitalopram', 'sertraline'],
            'CYP2C9': ['warfarin', 'phenytoin', 'celecoxib', 'diclofenac', 'tolbutamide'],
            'CYP3A4': ['simvastatin', 'atorvastatin', 'cyclosporine', 'tacrolimus'],
            'CYP3A5': ['tacrolimus', 'cyclosporine'],
            'DPYD': ['5-fluorouracil', 'capecitabine'],
            'TPMT': ['azathioprine', 'mercaptopurine', 'thioguanine'],
            'NUDT15': ['azathioprine', 'mercaptopurine'],
            'UGT1A1': ['irinotecan'],
            'SLCO1B1': ['simvastatin', 'atorvastatin', 'pravastatin'],
            'VKORC1': ['warfarin', 'acenocoumarol'],
        }
        return drug_map.get(gene, [])
    
    def generate_pharmacogenomic_card(self) -> str:
        """
        Genera una tarjeta farmacogenómica en formato texto
        
        Returns:
            Tarjeta farmacogenómica formateada
        """
        card = []
        card.append("=" * 80)
        card.append("TARJETA FARMACOGENÓMICA")
        card.append("=" * 80)
        card.append("")
        card.append("⚠️ IMPORTANTE: Esta información debe ser compartida con todos los profesionales de salud")
        card.append("")
        
        for gene, profile in self.profiles.items():
            card.append(f"\n{'=' * 80}")
            card.append(f"GEN: {gene}")
            card.append(f"{'=' * 80}")
            
            if profile.diplotype:
                card.append(f"Diplotipo: {profile.diplotype}")
            card.append(f"Fenotipo: {profile.phenotype}")
            if profile.activity_score is not None:
                card.append(f"Activity Score: {profile.activity_score}")
            if profile.metabolizer_status:
                card.append(f"Estado: {profile.metabolizer_status}")
            
            if profile.guidelines:
                card.append("\nRecomendaciones Clínicas:")
                for guideline in profile.guidelines:
                    card.append(f"\n  Medicamento: {guideline.drug_name.upper()}")
                    card.append(f"  Recomendación: {guideline.recommendation}")
                    card.append(f"  Fuerza: {guideline.strength.upper()}")
                    if guideline.dosing_recommendation:
                        card.append(f"  Dosificación: {guideline.dosing_recommendation}")
                    if guideline.alternative_drugs:
                        card.append(f"  Alternativas: {', '.join(guideline.alternative_drugs)}")
            else:
                card.append(f"\nMedicamentos relevantes: {', '.join(profile.relevant_drugs)}")
                card.append("(No hay guías específicas disponibles para este fenotipo)")
        
        card.append("\n" + "=" * 80)
        card.append("Fuente: CPIC Guidelines, PharmGKB")
        card.append("=" * 80)
        
        return "\n".join(card)
    
    def get_critical_alerts(self) -> List[Dict]:
        """
        Obtiene alertas críticas basadas en perfiles farmacogenómicos
        
        Returns:
            Lista de alertas críticas
        """
        alerts = []
        
        for gene, profile in self.profiles.items():
            # Alertas para metabolizadores pobres o ultra-rápidos
            if profile.metabolizer_status in ['poor', 'ultra-rapid']:
                for guideline in profile.guidelines:
                    if guideline.strength == 'strong':
                        alerts.append({
                            'gene': gene,
                            'drug': guideline.drug_name,
                            'severity': 'high',
                            'message': f"⚠️ ALERTA CRÍTICA: {gene} {profile.phenotype} - {guideline.recommendation}",
                            'guideline': guideline
                        })
        
        return alerts


if __name__ == '__main__':
    # Ejemplo de uso
    from .parser import GenomeParser
    
    # Esto requeriría un archivo de genoma real
    # parser = GenomeParser("path/to/genome.txt")
    # analyzer = PharmacogenomicsAnalyzer(parser)
    # profiles = analyzer.analyze_all_genes()
    # card = analyzer.generate_pharmacogenomic_card()
    # print(card)
    pass

