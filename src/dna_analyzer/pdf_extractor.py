"""
Extractor de información de reportes PDF y HTML existentes
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import pdfplumber


class ReportExtractor:
    """Extrae información de reportes PDF y HTML existentes"""
    
    def __init__(self):
        self.extracted_findings: Dict[str, List[Dict]] = {
            'promethease': [],
            'genetic_genie': [],
            'nutrahacker': []
        }
    
    def extract_promethease_html(self, html_file: str) -> List[Dict]:
        """
        Extrae hallazgos del reporte HTML de Promethease
        
        Args:
            html_file: Ruta al archivo promethease.html
            
        Returns:
            Lista de hallazgos encontrados
        """
        findings = []
        
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar patrones de SNPs en el HTML
            # Promethease almacena datos en JavaScript embebido
            # Buscar rsIDs y genotipos
            rsid_pattern = r'rs\d+'
            rsids_found = set(re.findall(rsid_pattern, content))
            
            # Buscar secciones con información de genotipos
            # Patrón común: rsID seguido de genotipo
            geno_pattern = r'(rs\d+)([AGCT]{2})'
            geno_matches = re.findall(geno_pattern, content)
            
            for rsid, genotype in geno_matches:
                findings.append({
                    'rsid': rsid,
                    'genotype': genotype,
                    'source': 'promethease',
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
                                    'source': 'promethease',
                                    'snpedia_url': href
                                })
            
            print(f"[OK] Promethease HTML: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo Promethease HTML: {e}")
        
        self.extracted_findings['promethease'] = findings
        return findings
    
    def extract_promethease_json(self, json_file: str) -> List[Dict[str, Any]]:
        """
        Carga hallazgos desde el archivo JSON estructurado de Promethease.
        
        Este método preserva todos los metadatos importantes como magnitude,
        repute, summary, genes, y condiciones médicas.
        
        Args:
            json_file: Ruta al archivo JSON de hallazgos genéticos
            
        Returns:
            Lista de hallazgos encontrados con metadatos completos
        """
        findings = []
        
        try:
            json_path = Path(json_file)
            if not json_path.exists():
                print(f"⚠ Archivo JSON no encontrado: {json_file}")
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
                    'source': 'promethease',
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
        
        # Combinar con hallazgos existentes si los hay
        if self.extracted_findings.get('promethease'):
            # Si ya hay hallazgos de HTML, los combinamos
            existing = self.extracted_findings['promethease']
            # Priorizar JSON sobre HTML (más completo)
            self.extracted_findings['promethease'] = findings + existing
        else:
            self.extracted_findings['promethease'] = findings
        
        return findings
    
    def extract_pdf_text(self, pdf_file: str) -> str:
        """
        Extrae texto de un archivo PDF
        
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
    
    def extract_genetic_genie(self, pdf_file: str) -> List[Dict]:
        """
        Extrae hallazgos del reporte de Genetic Genie
        
        Args:
            pdf_file: Ruta al archivo PDF de Genetic Genie
            
        Returns:
            Lista de hallazgos encontrados
        """
        findings = []
        
        try:
            text = self.extract_pdf_text(pdf_file)
            
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
                        'source': 'genetic_genie',
                        'context': match.strip()
                    })
            
            print(f"[OK] Genetic Genie: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo Genetic Genie: {e}")
        
        self.extracted_findings['genetic_genie'] = findings
        return findings
    
    def extract_nutrahacker(self, pdf_file: str) -> List[Dict]:
        """
        Extrae hallazgos del reporte de NutraHacker
        
        Args:
            pdf_file: Ruta al archivo PDF de NutraHacker
            
        Returns:
            Lista de hallazgos encontrados
        """
        findings = []
        
        try:
            text = self.extract_pdf_text(pdf_file)
            
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
                    'source': 'nutrahacker',
                    'context': context_text[:300],
                    'supplements': supplements_mentioned
                })
            
            print(f"[OK] NutraHacker: {len(findings)} hallazgos extraidos")
            
        except Exception as e:
            print(f"⚠ Error extrayendo NutraHacker: {e}")
        
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
        
        return rsids

