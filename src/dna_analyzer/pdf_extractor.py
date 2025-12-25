"""
Extractor de información de reportes PDF y HTML existentes
Refactorizado con patrón Strategy para facilitar extensión
"""

import re
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import pdfplumber


class BaseReportParser(ABC):
    """Clase base abstracta para parsers de reportes"""
    
    def __init__(self, source_name: str):
        """
        Inicializa el parser
        
        Args:
            source_name: Nombre de la fuente (ej: 'promethease', 'genetic_genie')
        """
        self.source_name = source_name
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """
        Verifica si este parser puede procesar el archivo dado
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede procesar el archivo
        """
        pass
    
    @abstractmethod
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parsea el archivo y extrae hallazgos
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de hallazgos encontrados
        """
        pass
    
    def extract_pdf_text(self, pdf_file: str) -> str:
        """
        Extrae texto de un archivo PDF (método auxiliar compartido)
        
        Args:
            pdf_file: Ruta al archivo PDF
            
        Returns:
            Texto extraído del PDF
        """
        text = ""
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"⚠ Error extrayendo PDF {pdf_file}: {e}")
        
        return text


class PrometheaseHTMLParser(BaseReportParser):
    """Parser para reportes HTML de Promethease"""
    
    def __init__(self):
        super().__init__('promethease')
    
    def can_parse(self, file_path: str) -> bool:
        """Verifica si es un archivo HTML de Promethease"""
        path = Path(file_path)
        return path.suffix.lower() == '.html' and 'promethease' in path.name.lower()
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae hallazgos del reporte HTML de Promethease"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar patrones de SNPs en el HTML
            rsid_pattern = r'rs\d+'
            rsids_found = set(re.findall(rsid_pattern, content))
            
            # Buscar secciones con información de genotipos
            geno_pattern = r'(rs\d+)([AGCT]{2})'
            geno_matches = re.findall(geno_pattern, content)
            
            for rsid, genotype in geno_matches:
                findings.append({
                    'rsid': rsid,
                    'genotype': genotype,
                    'source': self.source_name,
                    'raw_text': f'{rsid} {genotype}'
                })
            
            # Buscar texto descriptivo cerca de rsIDs
            soup = BeautifulSoup(content, 'html.parser')
            
            # Buscar enlaces a SNPedia que contienen rsIDs
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'snpedia.com' in href and 'rs' in href:
                    rsid_match = re.search(r'rs\d+', href)
                    if rsid_match:
                        rsid = rsid_match.group()
                        # Buscar texto cercano
                        parent = link.parent
                        if parent:
                            text = parent.get_text(strip=True)
                            if text and len(text) > 10:
                                findings.append({
                                    'rsid': rsid,
                                    'description': text[:200],
                                    'source': self.source_name,
                                    'snpedia_url': href
                                })
            
            print(f"[OK] Promethease HTML: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo Promethease HTML: {e}")
        
        return findings


class PrometheaseJSONParser(BaseReportParser):
    """Parser para reportes JSON de Promethease"""
    
    def __init__(self):
        super().__init__('promethease')
    
    def can_parse(self, file_path: str) -> bool:
        """Verifica si es un archivo JSON de Promethease"""
        path = Path(file_path)
        return path.suffix.lower() == '.json' and ('promethease' in path.name.lower() or 
                                                   'hallazgos_geneticos' in path.name.lower())
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Carga hallazgos desde el archivo JSON estructurado de Promethease"""
        findings = []
        
        try:
            json_path = Path(file_path)
            if not json_path.exists():
                print(f"⚠ Archivo JSON no encontrado: {file_path}")
                return findings
            
            with open(json_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            for entry in entries:
                # Extraer rsID del record_id (puede ser rs123 o gs123)
                record_id = entry.get('record_id', '')
                if not record_id.startswith('rs'):
                    # Saltar genosets (gs) por ahora, solo procesar rsIDs
                    continue
                
                rsid = record_id
                genotype = entry.get('genotype')
                
                # Construir hallazgo con todos los metadatos
                finding = {
                    'rsid': rsid,
                    'genotype': genotype,
                    'source': self.source_name,
                    'magnitude': entry.get('magnitude'),
                    'max_magnitude': entry.get('max_magnitude'),
                    'repute': entry.get('repute'),
                    'summary': entry.get('summary', ''),
                    'description': entry.get('description', ''),
                    'frequency': entry.get('frequency'),
                    'chromosome': entry.get('chromosome'),
                    'position': entry.get('position'),
                    'genes': entry.get('genes', []),
                    'publications': entry.get('publications'),
                    'gmaf': entry.get('gmaf'),
                    'topics': entry.get('topics', []),
                    'medical_conditions': entry.get('medical_conditions', []),
                    'clinvar_significance': entry.get('clinvar_significance'),
                    'snpedia_url': f'https://www.snpedia.com/index.php/{rsid}'
                }
                
                findings.append(finding)
            
            print(f"[OK] Promethease JSON: {len(findings)} hallazgos cargados")
            
        except json.JSONDecodeError as e:
            print(f"⚠ Error decodificando JSON de Promethease: {e}")
        except Exception as e:
            print(f"⚠ Error cargando Promethease JSON: {e}")
            import traceback
            traceback.print_exc()
        
        return findings


class GeneticGenieParser(BaseReportParser):
    """Parser para reportes PDF de Genetic Genie"""
    
    def __init__(self):
        super().__init__('genetic_genie')
    
    def can_parse(self, file_path: str) -> bool:
        """Verifica si es un archivo PDF de Genetic Genie"""
        path = Path(file_path)
        name_lower = path.name.lower()
        return (path.suffix.lower() == '.pdf' and 
                ('genetic_genie' in name_lower or 'geneticgenie' in name_lower))
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae hallazgos del reporte de Genetic Genie"""
        findings = []
        
        try:
            text = self.extract_pdf_text(file_path)
            
            # Buscar rsIDs en el texto
            rsid_pattern = r'rs\d+'
            rsids = set(re.findall(rsid_pattern, text))
            
            # Buscar genotipos asociados
            for rsid in rsids:
                # Buscar contexto alrededor del rsID
                pattern = rf'.{{0,100}}{re.escape(rsid)}.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                for match in matches[:3]:  # Limitar a 3 matches por rsID
                    # Buscar genotipo en el contexto
                    geno_match = re.search(r'([AGCT]{2}|[+-]{2})', match)
                    genotype = geno_match.group(1) if geno_match else None
                    
                    findings.append({
                        'rsid': rsid,
                        'genotype': genotype,
                        'source': self.source_name,
                        'context': match.strip()
                    })
            
            print(f"[OK] Genetic Genie: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo Genetic Genie: {e}")
        
        return findings


class NutraHackerParser(BaseReportParser):
    """Parser para reportes PDF de NutraHacker"""
    
    def __init__(self):
        super().__init__('nutrahacker')
    
    def can_parse(self, file_path: str) -> bool:
        """Verifica si es un archivo PDF de NutraHacker"""
        path = Path(file_path)
        name_lower = path.name.lower()
        return (path.suffix.lower() == '.pdf' and 
                ('nutrahacker' in name_lower or 'nutra_hacker' in name_lower))
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae hallazgos del reporte de NutraHacker"""
        findings = []
        
        try:
            text = self.extract_pdf_text(file_path)
            
            # Buscar rsIDs
            rsid_pattern = r'rs\d+'
            rsids = set(re.findall(rsid_pattern, text))
            
            # Buscar recomendaciones y suplementos mencionados
            supplement_keywords = [
                'methylfolate', 'B12', 'vitamin D', 'magnesium',
                'folate', 'B6', 'B2', 'choline', 'betaine'
            ]
            
            for rsid in rsids:
                # Buscar contexto
                pattern = rf'.{{0,200}}{re.escape(rsid)}.{{0,200}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                context_text = ' '.join(matches[:2])
                
                # Buscar suplementos mencionados
                supplements_mentioned = []
                for keyword in supplement_keywords:
                    if keyword.lower() in context_text.lower():
                        supplements_mentioned.append(keyword)
                
                findings.append({
                    'rsid': rsid,
                    'source': self.source_name,
                    'context': context_text[:300],
                    'supplements': supplements_mentioned
                })
            
            print(f"[OK] NutraHacker: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo NutraHacker: {e}")
        
        return findings


class FoundMyFitnessParser(BaseReportParser):
    """Parser para reportes PDF de FoundMyFitness"""
    
    def __init__(self):
        super().__init__('foundmyfitness')
    
    def can_parse(self, file_path: str) -> bool:
        """Verifica si es un archivo PDF de FoundMyFitness"""
        path = Path(file_path)
        name_lower = path.name.lower()
        return (path.suffix.lower() == '.pdf' and 
                ('foundmyfitness' in name_lower or 'found_my_fitness' in name_lower))
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae hallazgos del reporte de FoundMyFitness"""
        findings = []
        
        try:
            text = self.extract_pdf_text(file_path)
            
            # Buscar rsIDs en el texto
            rsid_pattern = r'rs\d+'
            rsids = set(re.findall(rsid_pattern, text))
            
            for rsid in rsids:
                # Buscar contexto alrededor del rsID
                pattern = rf'.{{0,150}}{re.escape(rsid)}.{{0,150}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                context_text = ' '.join(matches[:2])
                
                findings.append({
                    'rsid': rsid,
                    'source': self.source_name,
                    'context': context_text[:300]
                })
            
            print(f"[OK] FoundMyFitness: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo FoundMyFitness: {e}")
        
        return findings


class EpigeneticParser(BaseReportParser):
    """Parser para reportes PDF de tests epigenéticos (WellMultiD, TruDiagnostic, etc.)"""
    
    def __init__(self):
        super().__init__('epigenetic')
        self.epigenetic_keywords = [
            'epigenetic', 'wellmultid', 'trudiagnostic', 'elysium',
            'methylation', 'biological age', 'epigenetic age', 'dna methylation'
        ]
    
    def can_parse(self, file_path: str) -> bool:
        """Verifica si es un archivo PDF de test epigenético"""
        path = Path(file_path)
        name_lower = path.name.lower()
        
        if path.suffix.lower() != '.pdf':
            return False
        
        # Verificar si contiene palabras clave epigenéticas
        return any(keyword in name_lower for keyword in self.epigenetic_keywords)
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae información epigenética del reporte"""
        findings = []
        
        try:
            text = self.extract_pdf_text(file_path)
            
            # Buscar información de edad epigenética
            age_patterns = [
                r'biological age[:\s]+(\d+\.?\d*)',
                r'epigenetic age[:\s]+(\d+\.?\d*)',
                r'age[:\s]+(\d+\.?\d*)\s*years',
            ]
            
            biological_age = None
            for pattern in age_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        biological_age = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Buscar niveles de metilación
            methylation_patterns = [
                r'methylation[:\s]+([\d.]+)%',
                r'global methylation[:\s]+([\d.]+)',
            ]
            
            methylation_level = None
            for pattern in methylation_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        methylation_level = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Buscar rsIDs relacionados con metilación
            rsid_pattern = r'rs\d+'
            rsids = set(re.findall(rsid_pattern, text))
            
            # Crear hallazgo epigenético general
            if biological_age or methylation_level or rsids:
                finding = {
                    'source': self.source_name,
                    'file_name': Path(file_path).name,
                    'biological_age': biological_age,
                    'methylation_level': methylation_level,
                    'related_snps': list(rsids)[:20] if rsids else [],  # Limitar a 20
                    'type': 'epigenetic_data'
                }
                findings.append(finding)
            
            print(f"[OK] Epigenetic: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo datos epigenéticos: {e}")
        
        return findings


class ReportExtractor:
    """Extrae información de reportes PDF y HTML existentes usando parsers específicos"""
    
    def __init__(self):
        self.extracted_findings: Dict[str, List[Dict]] = {}
        
        # Registrar todos los parsers disponibles
        self.parsers: List[BaseReportParser] = [
            PrometheaseHTMLParser(),
            PrometheaseJSONParser(),
            GeneticGenieParser(),
            NutraHackerParser(),
            FoundMyFitnessParser(),
            EpigeneticParser()
        ]
    
    def _get_parser_for_file(self, file_path: str) -> Optional[BaseReportParser]:
        """
        Encuentra el parser adecuado para un archivo
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Parser que puede procesar el archivo, o None si no hay ninguno
        """
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser
        return None
    
    def extract_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extrae información de un archivo usando el parser apropiado
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de hallazgos encontrados
        """
        parser = self._get_parser_for_file(file_path)
        
        if not parser:
            print(f"⚠ No se encontró parser para: {file_path}")
            return []
        
        findings = parser.parse(file_path)
        
        # Agregar a la colección de hallazgos por fuente
        source = parser.source_name
        if source not in self.extracted_findings:
            self.extracted_findings[source] = []
        
        # Combinar con hallazgos existentes (evitar duplicados)
        existing_rsids = {f.get('rsid') for f in self.extracted_findings[source] if 'rsid' in f}
        for finding in findings:
            # Si es un hallazgo con rsID, verificar si ya existe
            if 'rsid' in finding:
                if finding['rsid'] not in existing_rsids:
                    self.extracted_findings[source].append(finding)
                    existing_rsids.add(finding['rsid'])
            else:
                # Si no tiene rsID (ej: datos epigenéticos), agregar directamente
                self.extracted_findings[source].append(finding)
        
        return findings
    
    # Métodos de compatibilidad hacia atrás
    def extract_promethease_html(self, html_file: str) -> List[Dict]:
        """Método de compatibilidad: extrae Promethease HTML"""
        parser = PrometheaseHTMLParser()
        findings = parser.parse(html_file)
        self.extracted_findings['promethease'] = findings
        return findings
    
    def extract_promethease_json(self, json_file: str) -> List[Dict[str, Any]]:
        """Método de compatibilidad: extrae Promethease JSON"""
        parser = PrometheaseJSONParser()
        findings = parser.parse(json_file)
        # Priorizar JSON sobre HTML si ambos existen
        if 'promethease' in self.extracted_findings:
            self.extracted_findings['promethease'] = findings + self.extracted_findings['promethease']
        else:
            self.extracted_findings['promethease'] = findings
        return findings
    
    def extract_genetic_genie(self, pdf_file: str) -> List[Dict]:
        """Método de compatibilidad: extrae Genetic Genie"""
        parser = GeneticGenieParser()
        findings = parser.parse(pdf_file)
        if 'genetic_genie' not in self.extracted_findings:
            self.extracted_findings['genetic_genie'] = []
        self.extracted_findings['genetic_genie'].extend(findings)
        return findings
    
    def extract_nutrahacker(self, pdf_file: str) -> List[Dict]:
        """Método de compatibilidad: extrae NutraHacker"""
        parser = NutraHackerParser()
        findings = parser.parse(pdf_file)
        self.extracted_findings['nutrahacker'] = findings
        return findings
    
    def get_all_findings(self) -> Dict[str, List[Dict]]:
        """Retorna todos los hallazgos extraídos"""
        return self.extracted_findings
    
    def get_rsids_from_all_sources(self) -> set:
        """Retorna conjunto de todos los rsIDs encontrados en todas las fuentes"""
        rsids = set()
        
        for source, findings in self.extracted_findings.items():
            for finding in findings:
                if 'rsid' in finding:
                    rsids.add(finding['rsid'])
                # También buscar en datos epigenéticos
                if 'related_snps' in finding:
                    rsids.update(finding['related_snps'])
        
        return rsids
