"""
Parser para archivos de genoma raw de 23andMe
"""

import re
from typing import Dict, Optional
from pathlib import Path


class GenomeParser:
    """Parser para archivos de genoma raw de 23andMe"""
    
    def __init__(self, genome_file: str):
        """
        Inicializa el parser con un archivo de genoma
        
        Args:
            genome_file: Ruta al archivo de genoma raw de 23andMe
        """
        self.genome_file = Path(genome_file)
        self.genome_index: Dict[str, str] = {}
        self.metadata: Dict[str, str] = {}
        
    def parse(self) -> Dict[str, str]:
        """
        Parsea el archivo de genoma y crea un índice de SNPs
        
        Returns:
            Diccionario con rsID -> genotipo
        """
        print(f"Leyendo archivo de genoma: {self.genome_file}")
        
        with open(self.genome_file, 'r', encoding='utf-8') as f:
            header_found = False
            count = 0
            
            for line in f:
                line_stripped = line.strip()
                
                # Saltar líneas vacías
                if not line_stripped:
                    continue
                
                # Procesar líneas de metadata (comentarios)
                if line_stripped.startswith('#'):
                    # Extraer metadata
                    if ':' in line_stripped:
                        try:
                            key, value = line_stripped[1:].split(':', 1)
                            self.metadata[key.strip()] = value.strip()
                        except:
                            pass
                    continue
                
                # Detectar encabezado (línea que contiene "rsid" y "chromosome")
                if 'rsid' in line_stripped.lower() and ('chromosome' in line_stripped.lower() or 'chrom' in line_stripped.lower()):
                    header_found = True
                    continue
                
                # Procesar líneas de datos (SNPs)
                # Una línea de datos tiene al menos 4 columnas separadas por tabs
                # y la primera columna empieza con "rs"
                parts = line_stripped.split('\t')
                if len(parts) >= 4:
                    rsid = parts[0].strip()
                    
                    # Verificar que es un rsID válido
                    if rsid.startswith('rs'):
                        chromosome = parts[1].strip()
                        position = parts[2].strip()
                        genotype = parts[3].strip()
                        
                        # Solo incluir SNPs válidos (no --)
                        if genotype and genotype != '--':
                            self.genome_index[rsid] = {
                                'genotype': genotype,
                                'chromosome': chromosome,
                                'position': position
                            }
                            count += 1
                            
                            if count % 100000 == 0:
                                print(f"  Procesados {count:,} SNPs...")
        
        print(f"[OK] Total de SNPs indexados: {len(self.genome_index):,}")
        return self.genome_index
    
    def get_genotype(self, rsid: str) -> Optional[str]:
        """
        Obtiene el genotipo para un rsID específico
        
        Args:
            rsid: ID del SNP (ej: 'rs1801133')
            
        Returns:
            Genotipo (ej: 'AA', 'AG', 'GG') o None si no se encuentra
        """
        if rsid in self.genome_index:
            if isinstance(self.genome_index[rsid], dict):
                return self.genome_index[rsid].get('genotype')
            return self.genome_index[rsid]
        return None
    
    def get_snps(self, rsids: list) -> Dict[str, Optional[str]]:
        """
        Obtiene genotipos para múltiples rsIDs
        
        Args:
            rsids: Lista de rsIDs
            
        Returns:
            Diccionario con rsID -> genotipo
        """
        results = {}
        for rsid in rsids:
            results[rsid] = self.get_genotype(rsid)
        return results
    
    def has_snp(self, rsid: str) -> bool:
        """Verifica si un SNP está presente en el genoma"""
        return rsid in self.genome_index
    
    def get_total_snps(self) -> int:
        """Retorna el total de SNPs indexados"""
        return len(self.genome_index)

