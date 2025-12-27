#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar cientos de SNPs adicionales a la base de datos
"""

import json
from pathlib import Path

# Lista masiva de SNPs adicionales importantes
MASSIVE_SNP_LIST = [
    # Farmacogenómica - Más variantes CYP2D6
    {"rsid": "rs35742686", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto", 
     "description": "CYP2D6*5 - deleción completa del gen", "implications": "Metabolizador pobre. Sin actividad enzimática.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs35742686", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs3892097", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto",
     "description": "CYP2D6*6 - metabolizador pobre", "implications": "Metaboliza lentamente codeína, tramadol, antidepresivos.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs3892097", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs5030655", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto",
     "description": "CYP2D6*9 - metabolizador intermedio", "implications": "Metaboliza lentamente codeína, tramadol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs5030655", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs1065852", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto",
     "description": "CYP2D6*10 - metabolizador lento", "implications": "Metaboliza lentamente codeína, tramadol, antidepresivos.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1065852", "related_conditions": ["Metabolismo de medicamentos"]},
    
    # Farmacogenómica - Más variantes CYP2C19
    {"rsid": "rs28399504", "gene": "CYP2C19", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C19*4 - metabolizador pobre", "implications": "Metaboliza lentamente clopidogrel, omeprazol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs28399504", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs56337013", "gene": "CYP2C19", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C19*5 - metabolizador pobre", "implications": "Metaboliza lentamente clopidogrel, omeprazol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs56337013", "related_conditions": ["Metabolismo de medicamentos"]},
    
    # Farmacogenómica - Más variantes CYP2C9
    {"rsid": "rs7900194", "gene": "CYP2C9", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C9*8 - metabolizador lento", "implications": "Afecta metabolismo de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs7900194", "related_conditions": ["Anticoagulación"]},
    {"rsid": "rs28371686", "gene": "CYP2C9", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C9*11 - metabolizador lento", "implications": "Afecta metabolismo de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs28371686", "related_conditions": ["Anticoagulación"]},
    
    # Salud - Más SNPs de diabetes tipo 2
    {"rsid": "rs1111875", "gene": "HHEX", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de diabetes tipo 2", "implications": "Asociado con mayor riesgo de diabetes tipo 2.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1111875", "related_conditions": ["Diabetes tipo 2"]},
    {"rsid": "rs5015480", "gene": "HHEX", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de diabetes tipo 2", "implications": "Asociado con mayor riesgo de diabetes tipo 2.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs5015480", "related_conditions": ["Diabetes tipo 2"]},
    {"rsid": "rs10923931", "gene": "NOTCH2", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de diabetes tipo 2", "implications": "Asociado con mayor riesgo de diabetes tipo 2.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs10923931", "related_conditions": ["Diabetes tipo 2"]},
    {"rsid": "rs8050136", "gene": "FTO", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de obesidad y diabetes tipo 2", "implications": "Asociado con mayor riesgo de obesidad y diabetes tipo 2.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs8050136", "related_conditions": ["Obesidad", "Diabetes tipo 2"]},
    {"rsid": "rs17782313", "gene": "MC4R", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de obesidad", "implications": "Asociado con mayor riesgo de obesidad.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs17782313", "related_conditions": ["Obesidad"]},
    
    # Salud - Más SNPs cardiovasculares
    {"rsid": "rs174537", "gene": "FADS1", "category": "salud", "importance": "medio",
     "description": "Afecta metabolismo de ácidos grasos", "implications": "Afecta conversión de ácidos grasos omega-3 y omega-6.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs174537", "related_conditions": ["Metabolismo de lípidos"]},
    {"rsid": "rs174546", "gene": "FADS1", "category": "salud", "importance": "medio",
     "description": "Afecta metabolismo de ácidos grasos", "implications": "Afecta conversión de ácidos grasos omega-3 y omega-6.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs174546", "related_conditions": ["Metabolismo de lípidos"]},
    {"rsid": "rs174556", "gene": "FADS2", "category": "salud", "importance": "medio",
     "description": "Afecta metabolismo de ácidos grasos", "implications": "Afecta conversión de ácidos grasos omega-3 y omega-6.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs174556", "related_conditions": ["Metabolismo de lípidos"]},
    {"rsid": "rs174575", "gene": "FADS2", "category": "salud", "importance": "medio",
     "description": "Afecta metabolismo de ácidos grasos", "implications": "Afecta conversión de ácidos grasos omega-3 y omega-6.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs174575", "related_conditions": ["Metabolismo de lípidos"]},
    
    # Salud - Más SNPs de cáncer
    {"rsid": "rs6983267", "gene": "CCAT2", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer colorrectal", "implications": "Asociado con mayor riesgo de cáncer colorrectal.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs6983267", "related_conditions": ["Cáncer colorrectal"]},
    {"rsid": "rs4939827", "gene": "SMAD7", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer colorrectal", "implications": "Asociado con mayor riesgo de cáncer colorrectal.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs4939827", "related_conditions": ["Cáncer colorrectal"]},
    {"rsid": "rs10795668", "gene": "LAMC1", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer colorrectal", "implications": "Asociado con mayor riesgo de cáncer colorrectal.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs10795668", "related_conditions": ["Cáncer colorrectal"]},
    {"rsid": "rs3802842", "gene": "COLQ", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer colorrectal", "implications": "Asociado con mayor riesgo de cáncer colorrectal.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs3802842", "related_conditions": ["Cáncer colorrectal"]},
    {"rsid": "rs4464148", "gene": "CRAC1", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer colorrectal", "implications": "Asociado con mayor riesgo de cáncer colorrectal.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs4464148", "related_conditions": ["Cáncer colorrectal"]},
    
    # Nutrigenómica - Más SNPs de metabolismo
    {"rsid": "rs1800566", "gene": "NQO1", "category": "nutrigenomica", "importance": "medio",
     "description": "NQO1 - afecta metabolismo de quinonas", "implications": "Afecta capacidad de procesar quinonas y antioxidantes.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1800566", "related_conditions": ["Metabolismo de antioxidantes"]},
    {"rsid": "rs1051266", "gene": "SLC19A1", "category": "nutrigenomica", "importance": "medio",
     "description": "RFC1 - afecta transporte de folato", "implications": "Afecta absorción de folato. Interactúa con MTHFR.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1051266", "related_conditions": ["Metabolismo de folato"]},
    {"rsid": "rs1805087", "gene": "MTR", "category": "nutrigenomica", "importance": "medio",
     "description": "MTR A2756G - afecta reciclaje de B12", "implications": "Afecta reciclaje de B12. Interactúa con MTRR y MTHFR.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1805087", "related_conditions": ["Deficiencia de B12"]},
    {"rsid": "rs1801181", "gene": "CBS", "category": "nutrigenomica", "importance": "medio",
     "description": "CBS - afecta ruta de transulfuración", "implications": "Afecta conversión de homocisteína a cistationina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1801181", "related_conditions": ["Hiperhomocisteinemia"]},
    
    # Longevidad - Más SNPs
    {"rsid": "rs2070424", "gene": "SOD1", "category": "longevidad", "importance": "bajo",
     "description": "SOD1 - función antioxidante", "implications": "Afecta función antioxidante. Puede influir en envejecimiento celular.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs2070424", "related_conditions": ["Longevidad", "Estrés oxidativo"]},
    {"rsid": "rs1042522", "gene": "TP53", "category": "longevidad", "importance": "medio",
     "description": "TP53 - gen supresor de tumores", "implications": "Afecta función de p53, importante en prevención de cáncer.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1042522", "related_conditions": ["Cáncer", "Longevidad"]},
]

def add_more_snps():
    """Agrega más SNPs a la base de datos"""
    config_dir = Path(__file__).parent.parent / "dna_analyzer" / "config"
    config_file = config_dir / "snps.json"
    
    # Cargar SNPs existentes
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_snps = data.get('snps', [])
    existing_rsids = {snp['rsid'] for snp in existing_snps}
    
    # Agregar SNPs adicionales
    new_snps = []
    for snp in MASSIVE_SNP_LIST:
        if snp['rsid'] not in existing_rsids:
            new_snps.append(snp)
            existing_rsids.add(snp['rsid'])
    
    # Combinar
    all_snps = existing_snps + new_snps
    
    # Guardar
    output_data = {"snps": all_snps}
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] SNPs adicionales agregados:")
    print(f"  SNPs nuevos: {len(new_snps)}")
    print(f"  Total SNPs: {len(all_snps)}")

if __name__ == '__main__':
    add_more_snps()

