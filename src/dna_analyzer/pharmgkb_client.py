#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente para acceder a datos de PharmGKB y CPIC guidelines
Proporciona información farmacogenómica basada en evidencia clínica
"""

import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class DrugGuideline:
    """Guía clínica para un medicamento específico"""
    drug_name: str
    gene: str
    phenotype: str
    recommendation: str
    strength: str  # 'strong', 'moderate', 'optional'
    cpic_level: Optional[str] = None
    dosing_recommendation: Optional[str] = None
    alternative_drugs: Optional[List[str]] = None


@dataclass
class GenePhenotype:
    """Fenotipo de un gen farmacogenómico"""
    gene: str
    diplotype: Optional[str] = None
    phenotype: str = "Unknown"
    activity_score: Optional[float] = None
    metabolizer_status: Optional[str] = None  # 'poor', 'intermediate', 'normal', 'ultra-rapid'


class PharmGKBClient:
    """Cliente para acceder a datos de PharmGKB"""
    
    BASE_URL = "https://api.pharmgkb.org/v1"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Inicializa el cliente PharmGKB
        
        Args:
            cache_dir: Directorio para cachear respuestas (opcional)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Mariano-DNA-Analyzer/1.0'
        })
    
    def _get_cached_path(self, key: str) -> Optional[Path]:
        """Obtiene la ruta del archivo cacheado"""
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            return self.cache_dir / f"{key}.json"
        return None
    
    def _load_cache(self, key: str) -> Optional[Dict]:
        """Carga datos del cache"""
        cache_path = self._get_cached_path(key)
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    def _save_cache(self, key: str, data: Dict):
        """Guarda datos en el cache"""
        cache_path = self._get_cached_path(key)
        if cache_path:
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
    
    def get_gene_alleles(self, gene: str) -> List[Dict]:
        """
        Obtiene información sobre alelos de un gen
        
        Args:
            gene: Nombre del gen (ej: 'CYP2D6', 'CYP2C19')
            
        Returns:
            Lista de alelos con información
        """
        cache_key = f"gene_alleles_{gene}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Nota: La API de PharmGKB requiere autenticación para algunos endpoints
            # Por ahora, usamos datos estáticos conocidos
            alleles = self._get_static_allele_data(gene)
            self._save_cache(cache_key, alleles)
            return alleles
        except Exception as e:
            print(f"⚠ Error obteniendo alelos para {gene}: {e}")
            return []
    
    def _get_static_allele_data(self, gene: str) -> List[Dict]:
        """Obtiene datos estáticos de alelos conocidos"""
        # Datos estáticos basados en conocimiento conocido de PharmGKB/CPIC
        static_data = {
            'CYP2D6': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*2', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*3', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*4', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*5', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*6', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*9', 'function': 'decreased', 'activity_score': 0.5},
                {'allele': '*10', 'function': 'decreased', 'activity_score': 0.25},
                {'allele': '*17', 'function': 'decreased', 'activity_score': 0.5},
                {'allele': '*41', 'function': 'decreased', 'activity_score': 0.5},
            ],
            'CYP2C19': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*2', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*3', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*4', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*5', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*6', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*17', 'function': 'increased', 'activity_score': 1.5},
            ],
            'CYP2C9': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*2', 'function': 'decreased', 'activity_score': 0.5},
                {'allele': '*3', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*5', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*6', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*8', 'function': 'decreased', 'activity_score': 0.5},
                {'allele': '*11', 'function': 'decreased', 'activity_score': 0.5},
            ],
            'CYP3A5': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*3', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*6', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*7', 'function': 'no_function', 'activity_score': 0.0},
            ],
            'DPYD': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*2A', 'function': 'no_function', 'activity_score': 0.0},
                {'allele': '*13', 'function': 'no_function', 'activity_score': 0.0},
            ],
            'TPMT': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*2', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*3A', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*3B', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*3C', 'function': 'decreased', 'activity_score': 0.0},
            ],
            'NUDT15': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*2', 'function': 'decreased', 'activity_score': 0.0},
                {'allele': '*3', 'function': 'decreased', 'activity_score': 0.0},
            ],
            'UGT1A1': [
                {'allele': '*1', 'function': 'normal', 'activity_score': 1.0},
                {'allele': '*28', 'function': 'decreased', 'activity_score': 0.3},
                {'allele': '*6', 'function': 'decreased', 'activity_score': 0.5},
            ],
        }
        
        return static_data.get(gene, [])
    
    def calculate_diplotype(self, gene: str, genotypes: Dict[str, str]) -> Optional[str]:
        """
        Calcula el diplotipo basado en genotipos de SNPs
        
        Args:
            gene: Nombre del gen
            genotypes: Diccionario de rsid -> genotipo
            
        Returns:
            Diplotipo (ej: '*1/*2') o None si no se puede determinar
        """
        # Mapeo de SNPs a alelos conocidos
        snp_to_allele = {
            'CYP2D6': {
                'rs1065852': {'G': '*4', 'A': '*1'},
                'rs16947': {'C': '*2', 'T': '*1'},
                'rs28371725': {'C': '*10', 'T': '*1'},
                'rs5030865': {'G': '*41', 'A': '*1'},
            },
            'CYP2C19': {
                'rs4244285': {'A': '*2', 'G': '*1'},
                'rs4986893': {'A': '*3', 'G': '*1'},
                'rs12248560': {'C': '*17', 'T': '*1'},
            },
            'CYP2C9': {
                'rs1799853': {'C': '*2', 'T': '*1'},
                'rs1057910': {'A': '*3', 'C': '*1'},
            },
            'CYP3A5': {
                'rs776746': {'A': '*3', 'G': '*1'},
            },
            'DPYD': {
                'rs3918290': {'G': '*2A', 'A': '*1'},
                'rs55886062': {'T': '*13', 'C': '*1'},
            },
            'TPMT': {
                'rs1800462': {'C': '*2', 'T': '*1'},
                'rs1142345': {'G': '*3A', 'A': '*1'},
            },
            'NUDT15': {
                'rs116855232': {'T': '*2', 'C': '*1'},
            },
            'UGT1A1': {
                'rs8175347': {'TA7': '*28', 'TA6': '*1'},
            },
        }
        
        gene_snps = snp_to_allele.get(gene, {})
        alleles = []
        
        for rsid, allele_map in gene_snps.items():
            if rsid in genotypes:
                genotype = genotypes[rsid]
                # Determinar alelo basado en genotipo
                if genotype and len(genotype) >= 2:
                    # Para la mayoría, asumimos que el alelo de riesgo es el menos común
                    # Esto es una simplificación - en la práctica se necesita más lógica
                    for allele_char, allele_name in allele_map.items():
                        if allele_char in genotype:
                            alleles.append(allele_name)
                            break
        
        if len(alleles) >= 2:
            # Ordenar alelos (normalmente *1 primero si está presente)
            alleles_sorted = sorted(set(alleles), key=lambda x: (x != '*1', x))
            return '/'.join(alleles_sorted[:2])
        elif len(alleles) == 1:
            # Asumir homocigoto o heterocigoto con *1
            return f"{alleles[0]}/*1"
        
        return None
    
    def get_phenotype_from_diplotype(self, gene: str, diplotype: str) -> GenePhenotype:
        """
        Determina el fenotipo basado en el diplotipo
        
        Args:
            gene: Nombre del gen
            diplotype: Diplotipo (ej: '*1/*2')
            
        Returns:
            GenePhenotype con información del fenotipo
        """
        alleles = diplotype.split('/')
        alleles_data = self._get_static_allele_data(gene)
        
        # Crear diccionario de alelos
        allele_dict = {a['allele']: a for a in alleles_data}
        
        # Calcular activity score
        activity_score = 0.0
        for allele in alleles:
            if allele in allele_dict:
                activity_score += allele_dict[allele].get('activity_score', 0.0)
        
        # Determinar fenotipo basado en activity score
        if gene in ['CYP2D6', 'CYP2C19', 'CYP2C9']:
            if activity_score == 0:
                phenotype = "Poor Metabolizer"
                metabolizer_status = "poor"
            elif activity_score < 1.0:
                phenotype = "Intermediate Metabolizer"
                metabolizer_status = "intermediate"
            elif activity_score == 1.0:
                phenotype = "Normal Metabolizer"
                metabolizer_status = "normal"
            elif activity_score > 1.0:
                phenotype = "Ultra-rapid Metabolizer"
                metabolizer_status = "ultra-rapid"
            else:
                phenotype = "Unknown"
                metabolizer_status = None
        else:
            # Para otros genes, usar lógica similar
            if activity_score == 0:
                phenotype = "No Function"
                metabolizer_status = "poor"
            elif activity_score < 1.0:
                phenotype = "Decreased Function"
                metabolizer_status = "intermediate"
            else:
                phenotype = "Normal Function"
                metabolizer_status = "normal"
        
        return GenePhenotype(
            gene=gene,
            diplotype=diplotype,
            phenotype=phenotype,
            activity_score=activity_score,
            metabolizer_status=metabolizer_status
        )
    
    def get_drug_guidelines(self, drug_name: str, gene: str, phenotype: str) -> List[DrugGuideline]:
        """
        Obtiene guías clínicas para un medicamento basado en fenotipo
        
        Args:
            drug_name: Nombre del medicamento
            gene: Gen relevante
            phenotype: Fenotipo del gen
            
        Returns:
            Lista de guías clínicas
        """
        # Guías estáticas basadas en CPIC guidelines conocidas
        guidelines = self._get_static_guidelines(drug_name, gene, phenotype)
        return guidelines
    
    def _get_static_guidelines(self, drug_name: str, gene: str, phenotype: str) -> List[DrugGuideline]:
        """Obtiene guías estáticas basadas en CPIC"""
        # Guías conocidas de CPIC
        cpic_guidelines = {
            ('clopidogrel', 'CYP2C19', 'Poor Metabolizer'): DrugGuideline(
                drug_name='clopidogrel',
                gene='CYP2C19',
                phenotype='Poor Metabolizer',
                recommendation='Avoid clopidogrel. Use alternative antiplatelet agent (e.g., prasugrel, ticagrelor).',
                strength='strong',
                cpic_level='A',
                alternative_drugs=['prasugrel', 'ticagrelor']
            ),
            ('clopidogrel', 'CYP2C19', 'Intermediate Metabolizer'): DrugGuideline(
                drug_name='clopidogrel',
                gene='CYP2C19',
                phenotype='Intermediate Metabolizer',
                recommendation='Consider alternative antiplatelet agent or increased dose.',
                strength='moderate',
                cpic_level='B'
            ),
            ('warfarin', 'CYP2C9', 'Poor Metabolizer'): DrugGuideline(
                drug_name='warfarin',
                gene='CYP2C9',
                phenotype='Poor Metabolizer',
                recommendation='Reduce initial dose by 50-75%. Monitor INR closely.',
                strength='strong',
                cpic_level='A',
                dosing_recommendation='Reduce initial dose by 50-75%'
            ),
            ('codeine', 'CYP2D6', 'Poor Metabolizer'): DrugGuideline(
                drug_name='codeine',
                gene='CYP2D6',
                phenotype='Poor Metabolizer',
                recommendation='Avoid codeine. Use alternative analgesic.',
                strength='strong',
                cpic_level='A',
                alternative_drugs=['morphine', 'oxycodone', 'hydrocodone']
            ),
            ('codeine', 'CYP2D6', 'Ultra-rapid Metabolizer'): DrugGuideline(
                drug_name='codeine',
                gene='CYP2D6',
                phenotype='Ultra-rapid Metabolizer',
                recommendation='Avoid codeine. Increased risk of toxicity.',
                strength='strong',
                cpic_level='A',
                alternative_drugs=['morphine', 'oxycodone']
            ),
            ('simvastatin', 'SLCO1B1', 'Poor Function'): DrugGuideline(
                drug_name='simvastatin',
                gene='SLCO1B1',
                phenotype='Poor Function',
                recommendation='Avoid simvastatin >40 mg/day. Use alternative statin.',
                strength='strong',
                cpic_level='A',
                alternative_drugs=['atorvastatin', 'rosuvastatin', 'pravastatin']
            ),
            ('azathioprine', 'TPMT', 'Poor Metabolizer'): DrugGuideline(
                drug_name='azathioprine',
                gene='TPMT',
                phenotype='Poor Metabolizer',
                recommendation='Avoid azathioprine. Use alternative immunosuppressant.',
                strength='strong',
                cpic_level='A',
                alternative_drugs=['mycophenolate', 'methotrexate']
            ),
            ('azathioprine', 'TPMT', 'Intermediate Metabolizer'): DrugGuideline(
                drug_name='azathioprine',
                gene='TPMT',
                phenotype='Intermediate Metabolizer',
                recommendation='Reduce dose by 30-50%. Monitor blood counts closely.',
                strength='strong',
                cpic_level='A',
                dosing_recommendation='Reduce dose by 30-50%'
            ),
            ('5-fluorouracil', 'DPYD', 'Poor Metabolizer'): DrugGuideline(
                drug_name='5-fluorouracil',
                gene='DPYD',
                phenotype='Poor Metabolizer',
                recommendation='Avoid 5-FU. Use alternative chemotherapy.',
                strength='strong',
                cpic_level='A',
                alternative_drugs=['capecitabine alternatives']
            ),
        }
        
        key = (drug_name.lower(), gene, phenotype)
        guideline = cpic_guidelines.get(key)
        
        if guideline:
            return [guideline]
        
        return []


if __name__ == '__main__':
    # Ejemplo de uso
    client = PharmGKBClient()
    
    # Ejemplo: calcular diplotipo
    genotypes = {
        'rs4244285': 'AA',  # CYP2C19*2/*2
        'rs4986893': 'GG',  # CYP2C19*1/*1
    }
    
    diplotype = client.calculate_diplotype('CYP2C19', genotypes)
    print(f"Diplotipo CYP2C19: {diplotype}")
    
    if diplotype:
        phenotype = client.get_phenotype_from_diplotype('CYP2C19', diplotype)
        print(f"Fenotipo: {phenotype.phenotype}")
        print(f"Activity Score: {phenotype.activity_score}")
        
        guidelines = client.get_drug_guidelines('clopidogrel', 'CYP2C19', phenotype.phenotype)
        for guideline in guidelines:
            print(f"\nGuía para {guideline.drug_name}:")
            print(f"  Recomendación: {guideline.recommendation}")
            print(f"  Fuerza: {guideline.strength}")

