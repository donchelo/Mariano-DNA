"""
Base de datos curada de SNPs importantes por categoría
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SNPInfo:
    """Información sobre un SNP importante"""
    rsid: str
    gene: str
    category: str
    importance: str  # 'alto', 'medio', 'bajo'
    description: str
    implications: str
    snpedia_url: str
    related_conditions: List[str]
    # Campos opcionales para validación de genotipos
    risk_allele: Optional[str] = None
    normal_allele: Optional[str] = None
    genotype_interpretation: Optional[Dict[str, str]] = None
    requires_combination: bool = False
    combination_snp: Optional[str] = None


class SNPDatabase:
    """Base de datos de SNPs importantes para análisis genético"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa la base de datos de SNPs
        
        Args:
            config_file: Ruta al archivo JSON de configuración. Si es None, usa el archivo por defecto.
        """
        self.snps: Dict[str, SNPInfo] = {}
        if config_file is None:
            # Usar archivo por defecto relativo a este módulo
            config_dir = Path(__file__).parent / "config"
            config_file = str(config_dir / "snps.json")
        self.config_file = config_file
        self._load_database()
    
    def _load_database(self):
        """Carga la base de datos de SNPs importantes desde archivo JSON"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            print(f"⚠ Advertencia: Archivo de configuración no encontrado: {self.config_file}")
            print("  Usando base de datos vacía. Crea el archivo JSON para cargar SNPs.")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar SNPs desde el JSON
            snps_list = data.get('snps', [])
            
            for snp_data in snps_list:
                snp_info = SNPInfo(
                    rsid=snp_data['rsid'],
                    gene=snp_data['gene'],
                    category=snp_data['category'],
                    importance=snp_data['importance'],
                    description=snp_data['description'],
                    implications=snp_data['implications'],
                    snpedia_url=snp_data['snpedia_url'],
                    related_conditions=snp_data.get('related_conditions', []),
                    risk_allele=snp_data.get('risk_allele'),
                    normal_allele=snp_data.get('normal_allele'),
                    genotype_interpretation=snp_data.get('genotype_interpretation'),
                    requires_combination=snp_data.get('requires_combination', False),
                    combination_snp=snp_data.get('combination_snp')
                )
                self.snps[snp_info.rsid] = snp_info
            
            print(f"[OK] Base de datos cargada: {len(self.snps)} SNPs importantes desde {self.config_file}")
            
        except json.JSONDecodeError as e:
            print(f"⚠ Error decodificando JSON: {e}")
            print(f"  Archivo: {self.config_file}")
        except KeyError as e:
            print(f"⚠ Error en estructura del JSON: falta campo {e}")
            print(f"  Archivo: {self.config_file}")
        except Exception as e:
            print(f"⚠ Error cargando base de datos: {e}")
            import traceback
            traceback.print_exc()
    
    def get_snp(self, rsid: str) -> Optional[SNPInfo]:
        """Obtiene información de un SNP"""
        return self.snps.get(rsid)
    
    def get_by_category(self, category: str) -> List[SNPInfo]:
        """Obtiene todos los SNPs de una categoría"""
        return [snp for snp in self.snps.values() if snp.category == category]
    
    def get_all_rsids(self) -> List[str]:
        """Retorna lista de todos los rsIDs en la base de datos"""
        return list(self.snps.keys())
    
    def get_by_importance(self, importance: str) -> List[SNPInfo]:
        """Obtiene SNPs por nivel de importancia"""
        return [snp for snp in self.snps.values() if snp.importance == importance]

