#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae SNPs del reporte de Promethease y los agrega a la base de datos
"""

import json
import re
from pathlib import Path

def extract_rsids_from_promethease(file_path: str) -> set:
    """Extrae todos los rsIDs únicos del archivo de Promethease"""
    rsids = set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todos los rsIDs (patrón: rs seguido de números)
    pattern = r'\brs\d+\b'
    matches = re.findall(pattern, content)
    rsids.update(matches)
    
    return rsids

def create_snp_from_rsid(rsid: str) -> dict:
    """Crea una entrada básica de SNP desde un rsID"""
    # Mapeo conocido de algunos rsIDs a genes (se puede expandir)
    known_genes = {
        'rs17646665': 'SORT1',
        'rs10830963': 'MTNR1B',
        'rs1021737': 'CTH',
        'rs7192': 'HLA-DRA',
        'rs1800098': 'CFTR',
        'rs2235544': 'DIO1',
        'rs7754840': 'CDKAL1',
        'rs3815148': 'COG5',
        'rs17089782': 'PIBF1',
        'rs2180439': 'EDA2R',
        'rs1801133': 'MTHFR',
        'rs1426654': 'SLC24A5',
        'rs7089424': 'UNKNOWN',
        'rs601338': 'FUT2',
        'rs664143': 'UNKNOWN',
        'rs2802292': 'FOXO3',
        'rs53576': 'OXTR',
        'rs6441286': 'UNKNOWN',
        'rs4143094': 'GATA3',
        'rs11672691': 'CEACAM21',
        'rs1121980': 'FTO',
        'rs3758391': 'SIRT1',
        'rs1799990': 'PRNP',
        'rs3825942': 'LOXL1',
        'rs3114018': 'ABCG2',
        'rs1837253': 'UNKNOWN',
    }
    
    gene = known_genes.get(rsid, 'UNKNOWN')
    
    # Determinar categoría basada en gen conocido o usar 'salud' por defecto
    category = 'salud'
    if gene in ['MTHFR', 'CTH', 'FUT2', 'DIO1', 'SLC24A5', 'VDR', 'BCMO1', 'LCT', 'COMT', 'SOD2']:
        category = 'nutrigenomica'
    elif gene in ['CYP2D6', 'CYP2C19', 'CYP2C9', 'CYP3A4', 'CYP3A5', 'DPYD', 'TPMT', 'NUDT15', 'UGT1A1', 'SLCO1B1', 'VKORC1']:
        category = 'farmacogenetica'
    elif gene in ['FOXO3', 'SIRT1', 'TP53', 'CETP']:
        category = 'longevidad'
    elif gene in ['OCA2', 'HERC2', 'TYR', 'MC1R', 'IRF4', 'KITLG', 'EDA2R']:
        category = 'rasgos'
    
    return {
        "rsid": rsid,
        "gene": gene,
        "category": category,
        "importance": "bajo" if category == 'rasgos' else "medio",
        "description": f"Variante genética {rsid} en {gene}" if gene != 'UNKNOWN' else f"Variante genética {rsid}",
        "implications": f"Variante en {gene} que puede tener implicaciones clínicas." if gene != 'UNKNOWN' else f"Variante genética {rsid} con posibles implicaciones clínicas.",
        "snpedia_url": f"https://www.snpedia.com/index.php/{rsid}",
        "related_conditions": []
    }

def extract_and_add_promethease_snps():
    """Extrae SNPs de Promethease y los agrega a la base de datos"""
    # Rutas
    promethease_file = Path("data/raw/reportes_proveedores/promethease/prometheus txt.txt")
    config_dir = Path(__file__).parent.parent / "dna_analyzer" / "config"
    config_file = config_dir / "snps.json"
    
    if not promethease_file.exists():
        print(f"Error: No se encontró el archivo de Promethease: {promethease_file}")
        return
    
    # Extraer rsIDs de Promethease
    print("Extrayendo rsIDs del archivo de Promethease...")
    promethease_rsids = extract_rsids_from_promethease(str(promethease_file))
    print(f"Encontrados {len(promethease_rsids)} rsIDs únicos en Promethease")
    
    # Cargar SNPs existentes
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_snps = data.get('snps', [])
    existing_rsids = {snp['rsid'] for snp in existing_snps}
    
    # Crear entradas para rsIDs nuevos
    new_snps = []
    duplicates = 0
    
    for rsid in promethease_rsids:
        if rsid not in existing_rsids:
            snp_entry = create_snp_from_rsid(rsid)
            new_snps.append(snp_entry)
            existing_rsids.add(rsid)
        else:
            duplicates += 1
    
    # Combinar
    all_snps = existing_snps + new_snps
    
    # Guardar
    output_data = {"snps": all_snps}
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"EXTRACCION DE SNPs DE PROMETHEASE")
    print(f"{'='*60}")
    print(f"rsIDs encontrados en Promethease: {len(promethease_rsids)}")
    print(f"SNPs originales en BD: {len(existing_snps)}")
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
    
    print(f"\n[OK] SNPs de Promethease agregados exitosamente!")
    print(f"   Archivo: {config_file}")


if __name__ == '__main__':
    extract_and_add_promethease_snps()

