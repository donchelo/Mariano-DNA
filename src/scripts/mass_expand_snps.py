#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script masivo para expandir la base de datos de SNPs a 500+
Agrega cientos de SNPs clínicamente relevantes de forma sistemática
"""

import json
from pathlib import Path

# Lista masiva de SNPs adicionales organizados por categoría
MASSIVE_SNP_LIST = []

# === FARMACOGENÓMICA ADICIONAL ===
pharmacogenomics_snps = [
    # CYP2D6 adicionales
    {"rsid": "rs35742686", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto",
     "description": "CYP2D6*5 - deleción completa del gen", "implications": "Metabolizador pobre. Sin actividad enzimática.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs35742686", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs3892097", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto",
     "description": "CYP2D6*6 - metabolizador pobre", "implications": "Metaboliza lentamente codeína, tramadol, antidepresivos.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs3892097", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs5030655", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "alto",
     "description": "CYP2D6*9 - metabolizador intermedio", "implications": "Metaboliza lentamente codeína, tramadol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs5030655", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs59421388", "gene": "CYP2D6", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2D6*17 - metabolizador intermedio", "implications": "Metaboliza lentamente codeína, tramadol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs59421388", "related_conditions": ["Metabolismo de medicamentos"]},
    
    # CYP2C19 adicionales
    {"rsid": "rs28399504", "gene": "CYP2C19", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C19*4 - metabolizador pobre", "implications": "Metaboliza lentamente clopidogrel, omeprazol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs28399504", "related_conditions": ["Metabolismo de medicamentos"]},
    {"rsid": "rs56337013", "gene": "CYP2C19", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C19*5 - metabolizador pobre", "implications": "Metaboliza lentamente clopidogrel, omeprazol.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs56337013", "related_conditions": ["Metabolismo de medicamentos"]},
    
    # CYP2C9 adicionales
    {"rsid": "rs7900194", "gene": "CYP2C9", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C9*8 - metabolizador lento", "implications": "Afecta metabolismo de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs7900194", "related_conditions": ["Anticoagulación"]},
    {"rsid": "rs28371686", "gene": "CYP2C9", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C9*11 - metabolizador lento", "implications": "Afecta metabolismo de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs28371686", "related_conditions": ["Anticoagulación"]},
    {"rsid": "rs2256871", "gene": "CYP2C9", "category": "farmacogenetica", "importance": "medio",
     "description": "CYP2C9*6 - metabolizador lento", "implications": "Afecta metabolismo de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs2256871", "related_conditions": ["Anticoagulación"]},
    
    # VKORC1 adicionales
    {"rsid": "rs7294", "gene": "VKORC1", "category": "farmacogenetica", "importance": "medio",
     "description": "VKORC1 - afecta dosis de warfarina", "implications": "Afecta dosis requerida de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs7294", "related_conditions": ["Anticoagulación"]},
    {"rsid": "rs2359612", "gene": "VKORC1", "category": "farmacogenetica", "importance": "medio",
     "description": "VKORC1 - afecta dosis de warfarina", "implications": "Afecta dosis requerida de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs2359612", "related_conditions": ["Anticoagulación"]},
    {"rsid": "rs9934438", "gene": "VKORC1", "category": "farmacogenetica", "importance": "medio",
     "description": "VKORC1 - afecta dosis de warfarina", "implications": "Afecta dosis requerida de warfarina.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs9934438", "related_conditions": ["Anticoagulación"]},
]

# === SALUD - DIABETES TIPO 2 ADICIONALES ===
diabetes_snps = [
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
    {"rsid": "rs8050136", "gene": "FTO", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de obesidad", "implications": "Asociado con mayor riesgo de obesidad.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs8050136", "related_conditions": ["Obesidad"]},
]

# === SALUD - CARDIOVASCULAR ADICIONALES ===
cardiovascular_snps = [
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
    {"rsid": "rs174570", "gene": "FADS2", "category": "salud", "importance": "medio",
     "description": "Afecta metabolismo de ácidos grasos", "implications": "Afecta conversión de ácidos grasos omega-3 y omega-6.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs174570", "related_conditions": ["Metabolismo de lípidos"]},
]

# === SALUD - CÁNCER ADICIONALES ===
cancer_snps = [
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
    {"rsid": "rs10771399", "gene": "PTHLH", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer de próstata", "implications": "Asociado con mayor riesgo de cáncer de próstata.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs10771399", "related_conditions": ["Cáncer de próstata"]},
    {"rsid": "rs1447295", "gene": "CASC8", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer de próstata", "implications": "Asociado con mayor riesgo de cáncer de próstata.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1447295", "related_conditions": ["Cáncer de próstata"]},
    {"rsid": "rs3803662", "gene": "TOX3", "category": "salud", "importance": "medio",
     "description": "Aumento del riesgo de cáncer de mama", "implications": "Asociado con mayor riesgo de cáncer de mama.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs3803662", "related_conditions": ["Cáncer de mama"]},
]

# === NUTRIGENÓMICA ADICIONALES ===
nutrigenomics_snps = [
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
    {"rsid": "rs1042713", "gene": "ADRB2", "category": "nutrigenomica", "importance": "bajo",
     "description": "ADRB2 - afecta respuesta a ejercicio", "implications": "Afecta respuesta a ejercicio y pérdida de peso.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1042713", "related_conditions": ["Ejercicio", "Pérdida de peso"]},
    {"rsid": "rs1042714", "gene": "ADRB2", "category": "nutrigenomica", "importance": "bajo",
     "description": "ADRB2 - afecta respuesta a ejercicio", "implications": "Afecta respuesta a ejercicio y pérdida de peso.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1042714", "related_conditions": ["Ejercicio"]},
    {"rsid": "rs2070424", "gene": "SOD1", "category": "nutrigenomica", "importance": "bajo",
     "description": "SOD1 - función antioxidante", "implications": "Afecta función antioxidante. Puede influir en envejecimiento celular.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs2070424", "related_conditions": ["Estrés oxidativo"]},
]

# === LONGEVIDAD ADICIONALES ===
longevity_snps = [
    {"rsid": "rs1042522", "gene": "TP53", "category": "longevidad", "importance": "medio",
     "description": "TP53 - gen supresor de tumores", "implications": "Afecta función de p53, importante en prevención de cáncer.",
     "snpedia_url": "https://www.snpedia.com/index.php/Rs1042522", "related_conditions": ["Cáncer", "Longevidad"]},
]

# === RASGOS ADICIONALES (muchos más) ===
# Generar SNPs de rasgos comunes de 23andMe
trait_snps = []
trait_genes = {
    'OCA2': ['rs4778241', 'rs7495174', 'rs1545397', 'rs12924074', 'rs1800407', 'rs1800401', 'rs1667394', 'rs4778138'],
    'HERC2': ['rs916977', 'rs7170852'],
    'SLC24A4': ['rs12896399', 'rs1289469', 'rs8024968'],
    'TYR': ['rs1126809', 'rs1393350', 'rs1042602', 'rs1110400', 'rs683'],
    'SLC24A5': ['rs1426654', 'rs26722'],
    'SLC45A2': ['rs16891982'],
    'ASIP': ['rs7174027', 'rs4911414', 'rs1015362', 'rs2378249', 'rs749846', 'rs4911442'],
    'TYRP1': ['rs1408799', 'rs2733832'],
    'MC1R': ['rs885479', 'rs1805008', 'rs1805009', 'rs2228479', 'rs11547464', 'rs1805005', 'rs1805006'],
    'IRF4': ['rs12203592'],
    'KITLG': ['rs12821256'],
}

for gene, rsids in trait_genes.items():
    for rsid in rsids:
        trait_snps.append({
            "rsid": rsid,
            "gene": gene,
            "category": "rasgos",
            "importance": "bajo",
            "description": f"Asociado con variación en características físicas relacionadas con {gene}",
            "implications": f"Variante en {gene} asociada con características físicas.",
            "snpedia_url": f"https://www.snpedia.com/index.php/{rsid}",
            "related_conditions": []
        })

# Combinar todas las listas
MASSIVE_SNP_LIST = (
    pharmacogenomics_snps +
    diabetes_snps +
    cardiovascular_snps +
    cancer_snps +
    nutrigenomics_snps +
    longevity_snps +
    trait_snps
)


def mass_expand_snps():
    """Expande masivamente la base de datos de SNPs"""
    config_dir = Path(__file__).parent.parent / "dna_analyzer" / "config"
    config_file = config_dir / "snps.json"
    
    # Cargar SNPs existentes
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_snps = data.get('snps', [])
    existing_rsids = {snp['rsid'] for snp in existing_snps}
    
    # Agregar SNPs adicionales que no estén ya presentes
    new_snps = []
    duplicates = 0
    
    for snp in MASSIVE_SNP_LIST:
        if snp['rsid'] not in existing_rsids:
            new_snps.append(snp)
            existing_rsids.add(snp['rsid'])
        else:
            duplicates += 1
    
    # Combinar SNPs existentes con nuevos
    all_snps = existing_snps + new_snps
    
    # Guardar archivo expandido
    output_data = {"snps": all_snps}
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"EXPANSIÓN MASIVA DE BASE DE DATOS DE SNPs")
    print(f"{'='*60}")
    print(f"SNPs originales: {len(existing_snps)}")
    print(f"SNPs nuevos agregados: {len(new_snps)}")
    print(f"SNPs duplicados omitidos: {duplicates}")
    print(f"Total SNPs en base de datos: {len(all_snps)}")
    print(f"{'='*60}")
    
    # Estadísticas por categoría
    categories = {}
    for snp in all_snps:
        cat = snp.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nDistribución por categoría:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\n[OK] Base de datos expandida exitosamente!")
    print(f"   Archivo: {config_file}")


if __name__ == '__main__':
    mass_expand_snps()

