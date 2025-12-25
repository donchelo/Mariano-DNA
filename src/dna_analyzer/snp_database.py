"""
Base de datos curada de SNPs importantes por categoría
"""

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


class SNPDatabase:
    """Base de datos de SNPs importantes para análisis genético"""
    
    def __init__(self):
        self.snps: Dict[str, SNPInfo] = {}
        self._load_database()
    
    def _load_database(self):
        """Carga la base de datos de SNPs importantes"""
        
        # ===== SALUD - RIESGOS DE ENFERMEDADES =====
        
        # APOE - Alzheimer y colesterol
        self.snps['rs429358'] = SNPInfo(
            rsid='rs429358',
            gene='APOE',
            category='salud',
            importance='alto',
            description='Variante ε4 del gen APOE asociada con mayor riesgo de Alzheimer',
            implications='Portadores de ε4 tienen mayor riesgo de Alzheimer. También afecta metabolismo del colesterol.',
            snpedia_url='https://www.snpedia.com/index.php/Rs429358',
            related_conditions=['Alzheimer', 'Hipercolesterolemia']
        )
        
        self.snps['rs7412'] = SNPInfo(
            rsid='rs7412',
            gene='APOE',
            category='salud',
            importance='alto',
            description='Variante ε2 del gen APOE (protección contra Alzheimer)',
            implications='La combinación con rs429358 determina el haplotipo APOE (ε2/ε3/ε4)',
            snpedia_url='https://www.snpedia.com/index.php/Rs7412',
            related_conditions=['Alzheimer']
        )
        
        # BRCA - Cáncer de mama/ovario
        self.snps['rs80357373'] = SNPInfo(
            rsid='rs80357373',
            gene='BRCA1',
            category='salud',
            importance='alto',
            description='Variantes en BRCA1 asociadas con cáncer de mama y ovario',
            implications='Portadores tienen mayor riesgo de cáncer de mama y ovario hereditario',
            snpedia_url='https://www.snpedia.com/index.php/Brca1',
            related_conditions=['Cáncer de mama', 'Cáncer de ovario']
        )
        
        # FTO - Obesidad y diabetes
        self.snps['rs9939609'] = SNPInfo(
            rsid='rs9939609',
            gene='FTO',
            category='salud',
            importance='medio',
            description='Variante asociada con mayor riesgo de obesidad y diabetes tipo 2',
            implications='Mayor predisposición a obesidad y resistencia a la insulina',
            snpedia_url='https://www.snpedia.com/index.php/Rs9939609',
            related_conditions=['Obesidad', 'Diabetes tipo 2']
        )
        
        # TCF7L2 - Diabetes tipo 2
        self.snps['rs7903146'] = SNPInfo(
            rsid='rs7903146',
            gene='TCF7L2',
            category='salud',
            importance='medio',
            description='Variante asociada con mayor riesgo de diabetes tipo 2',
            implications='Mayor riesgo de desarrollar diabetes tipo 2',
            snpedia_url='https://www.snpedia.com/index.php/Rs7903146',
            related_conditions=['Diabetes tipo 2']
        )
        
        # Factor V Leiden - Trombosis
        self.snps['rs6025'] = SNPInfo(
            rsid='rs6025',
            gene='F5',
            category='salud',
            importance='alto',
            description='Factor V Leiden - mayor riesgo de trombosis venosa',
            implications='Mayor riesgo de coágulos sanguíneos, especialmente en combinación con anticonceptivos orales',
            snpedia_url='https://www.snpedia.com/index.php/Rs6025',
            related_conditions=['Trombosis venosa', 'Embolia pulmonar']
        )
        
        # ===== FARMACOGENÉTICA =====
        
        # CYP2C19 - Metabolismo de medicamentos
        self.snps['rs4244285'] = SNPInfo(
            rsid='rs4244285',
            gene='CYP2C19',
            category='farmacogenetica',
            importance='alto',
            description='CYP2C19*2 - metabolizador lento',
            implications='Metaboliza lentamente clopidogrel, omeprazol, antidepresivos. Puede necesitar dosis ajustadas.',
            snpedia_url='https://www.snpedia.com/index.php/Rs4244285',
            related_conditions=['Metabolismo de medicamentos']
        )
        
        self.snps['rs4986893'] = SNPInfo(
            rsid='rs4986893',
            gene='CYP2C19',
            category='farmacogenetica',
            importance='alto',
            description='CYP2C19*3 - metabolizador lento',
            implications='Similar a *2, afecta metabolismo de múltiples medicamentos',
            snpedia_url='https://www.snpedia.com/index.php/Rs4986893',
            related_conditions=['Metabolismo de medicamentos']
        )
        
        # CYP2D6 - Metabolismo de medicamentos
        self.snps['rs1065852'] = SNPInfo(
            rsid='rs1065852',
            gene='CYP2D6',
            category='farmacogenetica',
            importance='alto',
            description='CYP2D6*4 - metabolizador lento',
            implications='Afecta metabolismo de codeína, tramadol, antidepresivos, betabloqueadores',
            snpedia_url='https://www.snpedia.com/index.php/Rs1065852',
            related_conditions=['Metabolismo de medicamentos']
        )
        
        # SLCO1B1 - Estatinas
        self.snps['rs4149056'] = SNPInfo(
            rsid='rs4149056',
            gene='SLCO1B1',
            category='farmacogenetica',
            importance='alto',
            description='Mayor riesgo de miopatía con estatinas',
            implications='Portadores tienen mayor riesgo de efectos secundarios musculares con simvastatina',
            snpedia_url='https://www.snpedia.com/index.php/Rs4149056',
            related_conditions=['Miopatía por estatinas']
        )
        
        # VKORC1 - Warfarina
        self.snps['rs9923231'] = SNPInfo(
            rsid='rs9923231',
            gene='VKORC1',
            category='farmacogenetica',
            importance='alto',
            description='Afecta dosis requerida de warfarina',
            implications='Portadores requieren dosis más bajas de warfarina para anticoagulación',
            snpedia_url='https://www.snpedia.com/index.php/Rs9923231',
            related_conditions=['Anticoagulación']
        )
        
        # ===== NUTRIGENÓMICA =====
        
        # MTHFR - Metilación
        self.snps['rs1801133'] = SNPInfo(
            rsid='rs1801133',
            gene='MTHFR',
            category='nutrigenomica',
            importance='alto',
            description='MTHFR C677T - reduce conversión de folato',
            implications='Homocigoto (TT) reduce actividad enzimática ~70%. Necesita metilfolato, no ácido fólico sintético.',
            snpedia_url='https://www.snpedia.com/index.php/Rs1801133',
            related_conditions=['Hiperhomocisteinemia', 'Defectos del tubo neural']
        )
        
        self.snps['rs1801131'] = SNPInfo(
            rsid='rs1801131',
            gene='MTHFR',
            category='nutrigenomica',
            importance='medio',
            description='MTHFR A1298C - reduce conversión de folato',
            implications='Reduce actividad enzimática. Efecto sinérgico con C677T.',
            snpedia_url='https://www.snpedia.com/index.php/Rs1801131',
            related_conditions=['Hiperhomocisteinemia']
        )
        
        # MTRR - B12
        self.snps['rs1801394'] = SNPInfo(
            rsid='rs1801394',
            gene='MTRR',
            category='nutrigenomica',
            importance='alto',
            description='MTRR A66G - reduce reciclaje de B12',
            implications='Necesita B12 activa (metilcobalamina) y dosis más altas',
            snpedia_url='https://www.snpedia.com/index.php/Rs1801394',
            related_conditions=['Deficiencia de B12']
        )
        
        # VDR - Vitamina D
        self.snps['rs1544410'] = SNPInfo(
            rsid='rs1544410',
            gene='VDR',
            category='nutrigenomica',
            importance='medio',
            description='VDR BsmI - afecta receptores de vitamina D',
            implications='Puede requerir niveles más altos de vitamina D para función óptima',
            snpedia_url='https://www.snpedia.com/index.php/Rs1544410',
            related_conditions=['Deficiencia de vitamina D']
        )
        
        self.snps['rs7975232'] = SNPInfo(
            rsid='rs7975232',
            gene='VDR',
            category='nutrigenomica',
            importance='medio',
            description='VDR ApaI - afecta receptores de vitamina D',
            implications='Similar a BsmI, afecta absorción y utilización de vitamina D',
            snpedia_url='https://www.snpedia.com/index.php/Rs7975232',
            related_conditions=['Deficiencia de vitamina D']
        )
        
        self.snps['rs731236'] = SNPInfo(
            rsid='rs731236',
            gene='VDR',
            category='nutrigenomica',
            importance='medio',
            description='VDR TaqI - afecta receptores de vitamina D',
            implications='Afecta función de receptores de vitamina D',
            snpedia_url='https://www.snpedia.com/index.php/Rs731236',
            related_conditions=['Deficiencia de vitamina D']
        )
        
        # BCMO1 - Conversión beta-caroteno
        self.snps['rs12934922'] = SNPInfo(
            rsid='rs12934922',
            gene='BCMO1',
            category='nutrigenomica',
            importance='medio',
            description='Reduce conversión de beta-caroteno a vitamina A',
            implications='Mejor obtener vitamina A directamente de fuentes animales o suplementos',
            snpedia_url='https://www.snpedia.com/index.php/Rs12934922',
            related_conditions=['Deficiencia de vitamina A']
        )
        
        # FUT2 - Vitamina B12 y secreción
        self.snps['rs601338'] = SNPInfo(
            rsid='rs601338',
            gene='FUT2',
            category='nutrigenomica',
            importance='medio',
            description='No-secretor - afecta absorción de B12',
            implications='Mayor riesgo de deficiencia de B12, especialmente en vegetarianos',
            snpedia_url='https://www.snpedia.com/index.php/Rs601338',
            related_conditions=['Deficiencia de B12']
        )
        
        # LCT - Intolerancia a lactosa
        self.snps['rs4988235'] = SNPInfo(
            rsid='rs4988235',
            gene='LCT',
            category='nutrigenomica',
            importance='medio',
            description='Intolerancia a lactosa en adultos',
            implications='Portadores pierden capacidad de digerir lactosa en la edad adulta',
            snpedia_url='https://www.snpedia.com/index.php/Rs4988235',
            related_conditions=['Intolerancia a lactosa']
        )
        
        # COMT - Metabolismo de dopamina
        self.snps['rs4680'] = SNPInfo(
            rsid='rs4680',
            gene='COMT',
            category='nutrigenomica',
            importance='medio',
            description='COMT Val158Met - velocidad de metabolismo de dopamina',
            implications='GG = metabolismo rápido (mayor tolerancia al estrés, menor sensibilidad a dolor). AG/AA = metabolismo lento (mayor sensibilidad, cuidado con sobre-metilación)',
            snpedia_url='https://www.snpedia.com/index.php/Rs4680',
            related_conditions=['Sensibilidad al estrés', 'Dolor crónico']
        )
        
        # SOD2 - Antioxidantes
        self.snps['rs4880'] = SNPInfo(
            rsid='rs4880',
            gene='SOD2',
            category='nutrigenomica',
            importance='medio',
            description='SOD2 Ala16Val - función antioxidante mitocondrial',
            implications='GG = menor actividad antioxidante, mayor necesidad de antioxidantes',
            snpedia_url='https://www.snpedia.com/index.php/Rs4880',
            related_conditions=['Estrés oxidativo']
        )
        
        # ===== LONGEVIDAD =====
        
        # FOXO3 - Longevidad
        self.snps['rs2802292'] = SNPInfo(
            rsid='rs2802292',
            gene='FOXO3',
            category='longevidad',
            importance='medio',
            description='Asociado con longevidad y envejecimiento saludable',
            implications='Portadores de GG tienen mayor probabilidad de longevidad',
            snpedia_url='https://www.snpedia.com/index.php/Rs2802292',
            related_conditions=['Longevidad']
        )
        
        # CETP - Colesterol y longevidad
        self.snps['rs5882'] = SNPInfo(
            rsid='rs5882',
            gene='CETP',
            category='longevidad',
            importance='medio',
            description='Asociado con longevidad y perfil de colesterol',
            implications='GG = mayor longevidad, mejor perfil de colesterol',
            snpedia_url='https://www.snpedia.com/index.php/Rs5882',
            related_conditions=['Longevidad', 'Colesterol']
        )
        
        # ===== RASGOS =====
        
        # MC1R - Piel y cabello
        self.snps['rs1805007'] = SNPInfo(
            rsid='rs1805007',
            gene='MC1R',
            category='rasgos',
            importance='bajo',
            description='Asociado con piel clara y cabello rojo',
            implications='Mayor sensibilidad al sol, mayor riesgo de quemaduras',
            snpedia_url='https://www.snpedia.com/index.php/Rs1805007',
            related_conditions=['Sensibilidad al sol']
        )
        
        # HERC2 - Color de ojos
        self.snps['rs12913832'] = SNPInfo(
            rsid='rs12913832',
            gene='HERC2',
            category='rasgos',
            importance='bajo',
            description='Asociado con color de ojos',
            implications='GG = ojos marrones, AG = ojos verdes/avellana, AA = ojos azules',
            snpedia_url='https://www.snpedia.com/index.php/Rs12913832',
            related_conditions=[]
        )
        
        # TAS2R38 - Sensibilidad al sabor amargo
        self.snps['rs713598'] = SNPInfo(
            rsid='rs713598',
            gene='TAS2R38',
            category='rasgos',
            importance='bajo',
            description='Sensibilidad al sabor amargo (PROP)',
            implications='GG = no siente amargo, AG = siente moderadamente, AA = siente muy amargo',
            snpedia_url='https://www.snpedia.com/index.php/Rs713598',
            related_conditions=[]
        )
        
        print(f"[OK] Base de datos cargada: {len(self.snps)} SNPs importantes")
    
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

