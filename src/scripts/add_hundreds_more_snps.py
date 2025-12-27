#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar cientos de SNPs adicionales desde listas conocidas
Incluye SNPs importantes de GWAS, farmacogenómica y nutrigenómica
"""

import json
from pathlib import Path

# SNPs adicionales masivos - muchos más de diferentes fuentes
ADDITIONAL_SNPS_MASSIVE = []

# Generar SNPs de rasgos comunes (muchos más)
trait_rsids = [
    # Color de ojos - OCA2, HERC2
    'rs4778241', 'rs7495174', 'rs1545397', 'rs12924074', 'rs1800407', 
    'rs1800401', 'rs1667394', 'rs4778138', 'rs916977', 'rs7170852',
    # Color de ojos - SLC24A4, TYR
    'rs12896399', 'rs1289469', 'rs8024968', 'rs1126809', 'rs1393350',
    'rs1042602', 'rs1110400', 'rs683',
    # Color de piel
    'rs1426654', 'rs26722', 'rs16891982', 'rs7174027', 'rs4911414',
    'rs1015362', 'rs2378249', 'rs749846', 'rs4911442', 'rs1408799',
    'rs2733832',
    # Color de cabello
    'rs12203592', 'rs12821256', 'rs885479', 'rs1805008', 'rs1805009',
    'rs2228479', 'rs11547464', 'rs1805005', 'rs1805006',
    # Otros rasgos
    'rs6152', 'rs17246341',
]

# SNPs de diabetes tipo 2 adicionales (GWAS conocidos)
diabetes_gwas = [
    'rs1111875', 'rs5015480', 'rs10923931', 'rs8050136', 'rs17782313',
    'rs4402960', 'rs5219', 'rs13266634', 'rs864745', 'rs10946398',
    'rs12779790', 'rs7961581', 'rs4607103', 'rs11708067', 'rs10811661',
    'rs564398', 'rs9472138', 'rs7578326', 'rs9300039', 'rs10490072',
]

# SNPs cardiovasculares adicionales
cardiovascular_gwas = [
    'rs10757278', 'rs1333049', 'rs2383206', 'rs174537', 'rs174546',
    'rs174556', 'rs174575', 'rs174570', 'rs174611', 'rs174616',
    'rs174617', 'rs174618', 'rs174619', 'rs174620',
]

# SNPs de cáncer adicionales
cancer_gwas = [
    'rs6983267', 'rs4939827', 'rs10795668', 'rs3802842', 'rs4464148',
    'rs10771399', 'rs1447295', 'rs3803662', 'rs3817198', 'rs13281615',
    'rs2981582', 'rs3803662', 'rs889312', 'rs13387042', 'rs6504950',
]

# SNPs de nutrigenómica adicionales
nutrigenomics_more = [
    'rs1800566', 'rs1051266', 'rs1805087', 'rs1801181', 'rs1042713',
    'rs1042714', 'rs2070424', 'rs1799983', 'rs2070744', 'rs1800779',
    'rs662', 'rs4880', 'rs5743708', 'rs2569190', 'rs352140',
]

# SNPs de longevidad adicionales
longevity_more = [
    'rs1042522', 'rs2070424', 'rs2802292', 'rs5882', 'rs2542052',
    'rs2764264', 'rs13217795', 'rs13220810', 'rs13220811',
]

# SNPs farmacogenómicos adicionales
pharmacogenomics_more = [
    'rs35742686', 'rs3892097', 'rs5030655', 'rs59421388', 'rs28399504',
    'rs56337013', 'rs7900194', 'rs28371686', 'rs2256871', 'rs7294',
    'rs2359612', 'rs9934438', 'rs2108622', 'rs12777823', 'rs339097',
    'rs11676382', 'rs12714145', 'rs12714145',
]

# Crear entradas para todos los SNPs
def create_snp_entry(rsid, gene, category, importance="medio", description=None):
    """Crea una entrada de SNP estándar"""
    if description is None:
        description = f"Variante en {gene} asociada con {category}"
    
    return {
        "rsid": rsid,
        "gene": gene,
        "category": category,
        "importance": importance,
        "description": description,
        "implications": f"Variante genética en {gene} que puede afectar {category}.",
        "snpedia_url": f"https://www.snpedia.com/index.php/{rsid}",
        "related_conditions": []
    }

# Agregar SNPs de rasgos
for rsid in trait_rsids:
    # Determinar gen basado en rsid conocido o usar genérico
    gene_map = {
        'rs4778241': 'OCA2', 'rs7495174': 'OCA2', 'rs1545397': 'OCA2',
        'rs12924074': 'OCA2', 'rs1800407': 'OCA2', 'rs1800401': 'OCA2',
        'rs1667394': 'OCA2', 'rs4778138': 'OCA2', 'rs916977': 'HERC2',
        'rs7170852': 'HERC2', 'rs12896399': 'SLC24A4', 'rs1289469': 'SLC24A4',
        'rs8024968': 'SLC24A4', 'rs1126809': 'TYR', 'rs1393350': 'TYR',
        'rs1042602': 'TYR', 'rs1110400': 'TYR', 'rs683': 'TYR',
        'rs1426654': 'SLC24A5', 'rs26722': 'SLC24A5', 'rs16891982': 'SLC45A2',
        'rs7174027': 'ASIP', 'rs4911414': 'ASIP', 'rs1015362': 'ASIP',
        'rs2378249': 'ASIP', 'rs749846': 'ASIP', 'rs4911442': 'ASIP',
        'rs1408799': 'TYRP1', 'rs2733832': 'TYRP1', 'rs12203592': 'IRF4',
        'rs12821256': 'KITLG', 'rs885479': 'MC1R', 'rs1805008': 'MC1R',
        'rs1805009': 'MC1R', 'rs2228479': 'MC1R', 'rs11547464': 'MC1R',
        'rs1805005': 'MC1R', 'rs1805006': 'MC1R', 'rs6152': 'AR',
        'rs17246341': 'MATP',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(rsid, gene, 'rasgos', 'bajo'))

# Agregar SNPs de diabetes
for rsid in diabetes_gwas:
    gene_map = {
        'rs1111875': 'HHEX', 'rs5015480': 'HHEX', 'rs10923931': 'NOTCH2',
        'rs8050136': 'FTO', 'rs17782313': 'MC4R', 'rs4402960': 'IGF2BP2',
        'rs5219': 'KCNJ11', 'rs13266634': 'SLC30A8',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(
        rsid, gene, 'salud', 'medio',
        f"Aumento del riesgo de diabetes tipo 2"
    ))

# Agregar SNPs cardiovasculares
for rsid in cardiovascular_gwas:
    gene_map = {
        'rs10757278': 'CDKN2A', 'rs1333049': 'CDKN2A', 'rs2383206': 'CDKN2A',
        'rs174537': 'FADS1', 'rs174546': 'FADS1', 'rs174556': 'FADS2',
        'rs174575': 'FADS2', 'rs174570': 'FADS2',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(
        rsid, gene, 'salud', 'medio',
        f"Afecta riesgo cardiovascular o metabolismo de lípidos"
    ))

# Agregar SNPs de cáncer
for rsid in cancer_gwas:
    gene_map = {
        'rs6983267': 'CCAT2', 'rs4939827': 'SMAD7', 'rs10795668': 'LAMC1',
        'rs3802842': 'COLQ', 'rs4464148': 'CRAC1', 'rs10771399': 'PTHLH',
        'rs1447295': 'CASC8', 'rs3803662': 'TOX3',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    condition = 'cáncer colorrectal' if rsid in ['rs6983267', 'rs4939827', 'rs10795668', 'rs3802842', 'rs4464148'] else \
                'cáncer de próstata' if rsid in ['rs10771399', 'rs1447295'] else \
                'cáncer de mama'
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(
        rsid, gene, 'salud', 'medio',
        f"Aumento del riesgo de {condition}"
    ))

# Agregar SNPs de nutrigenómica
for rsid in nutrigenomics_more:
    gene_map = {
        'rs1800566': 'NQO1', 'rs1051266': 'SLC19A1', 'rs1805087': 'MTR',
        'rs1801181': 'CBS', 'rs1042713': 'ADRB2', 'rs1042714': 'ADRB2',
        'rs2070424': 'SOD1', 'rs4880': 'SOD2',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(rsid, gene, 'nutrigenomica', 'medio'))

# Agregar SNPs de longevidad
for rsid in longevity_more:
    gene_map = {
        'rs1042522': 'TP53', 'rs2070424': 'SOD1', 'rs2802292': 'FOXO3',
        'rs5882': 'CETP',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(rsid, gene, 'longevidad', 'medio'))

# Agregar SNPs farmacogenómicos
for rsid in pharmacogenomics_more:
    gene_map = {
        'rs35742686': 'CYP2D6', 'rs3892097': 'CYP2D6', 'rs5030655': 'CYP2D6',
        'rs59421388': 'CYP2D6', 'rs28399504': 'CYP2C19', 'rs56337013': 'CYP2C19',
        'rs7900194': 'CYP2C9', 'rs28371686': 'CYP2C9', 'rs2256871': 'CYP2C9',
        'rs7294': 'VKORC1', 'rs2359612': 'VKORC1', 'rs9934438': 'VKORC1',
        'rs2108622': 'CYP4F2',
    }
    gene = gene_map.get(rsid, 'UNKNOWN')
    ADDITIONAL_SNPS_MASSIVE.append(create_snp_entry(rsid, gene, 'farmacogenetica', 'alto'))


def add_hundreds_more_snps():
    """Agrega cientos de SNPs adicionales a la base de datos"""
    config_dir = Path(__file__).parent.parent / "dna_analyzer" / "config"
    config_file = config_dir / "snps.json"
    
    # Cargar SNPs existentes
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_snps = data.get('snps', [])
    existing_rsids = {snp['rsid'] for snp in existing_snps}
    
    # Agregar SNPs adicionales
    new_snps = []
    duplicates = 0
    
    for snp in ADDITIONAL_SNPS_MASSIVE:
        if snp['rsid'] not in existing_rsids:
            new_snps.append(snp)
            existing_rsids.add(snp['rsid'])
        else:
            duplicates += 1
    
    # Combinar
    all_snps = existing_snps + new_snps
    
    # Guardar
    output_data = {"snps": all_snps}
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"AGREGANDO CIENTOS DE SNPs ADICIONALES")
    print(f"{'='*60}")
    print(f"SNPs originales: {len(existing_snps)}")
    print(f"SNPs nuevos agregados: {len(new_snps)}")
    print(f"SNPs duplicados omitidos: {duplicates}")
    print(f"Total SNPs en base de datos: {len(all_snps)}")
    print(f"{'='*60}")
    
    # Estadísticas
    categories = {}
    for snp in all_snps:
        cat = snp.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nDistribucion por categoria:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\n[OK] Base de datos expandida exitosamente!")
    print(f"   Archivo: {config_file}")


if __name__ == '__main__':
    add_hundreds_more_snps()

