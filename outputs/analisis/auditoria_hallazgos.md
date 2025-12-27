# Reporte de Auditoría de Hallazgos Genéticos
**Generado el:** 2025-12-26 19:20:36

---

## Resumen Ejecutivo

- **Total SNPs en genoma raw:** 616,770
- **Total SNPs en Promethease:** 125
- **Total SNPs en base de datos curada:** 37
- **Discrepancias de genotipo:** 0
- **SNPs faltantes en genoma:** 0
- **SNPs faltantes en BD curada:** 63
- **Problemas de validación de riesgo:** 0
- **SNPs de alta magnitud (≥3.5):** 1

---

## Consistencia de Genotipos

Todos los genotipos son consistentes entre fuentes.

---

## SNPs Faltantes en Base de Datos Curada

SNPs de alta importancia que deberían estar en `snps.json`:

### rs7089424
- **Magnitud:** 2.5
- **Repute:** Bad
- **Resumen:** moderately (~4x) increased risk for acute lymphoblastic leukemia see references at rs7089424, including meta-analyses
- **Genes:** ARID5B
- **Condiciones:** Leukemia
- **En genoma:** Sí

### rs664143
- **Magnitud:** 2.5
- **Repute:** Bad
- **Resumen:** Higher risk for number of cancers
- **Genes:** ATM, C11orf65
- **Condiciones:** Cancer, Cancers, Lung, Pancreatic
- **En genoma:** Sí

### rs6441286
- **Magnitud:** 2.5
- **Repute:** Bad
- **Resumen:** 3.08x chance of developing primary biliary cirrhosis
- **Genes:** IL12A-AS1
- **En genoma:** Sí

### rs4143094
- **Magnitud:** 2.5
- **Repute:** Bad
- **Resumen:** slightly (17%) higher risk of colorectal cancer correlated with consumption of processed meats
- **Genes:** GATA3
- **Condiciones:** Cancer, Colorectal
- **En genoma:** Sí

### rs11672691
- **Magnitud:** 2.5
- **Repute:** Bad
- **Resumen:** more info
- **Genes:** PCAT19
- **Condiciones:** Cancer, Prostate, Tumor
- **En genoma:** Sí

### rs1121980
- **Magnitud:** 2.5
- **Repute:** Bad
- **Resumen:** Slight increase (1.67x) in risk for obesity see discussion via main rs-page
- **Genes:** FTO
- **Condiciones:** Diabetes, Obesity
- **En genoma:** Sí

### rs1799990
- **Magnitud:** 2.3
- **Repute:** Bad
- **Resumen:** more info
- **Genes:** PRNP
- **Condiciones:** Alzheimer, Disease, Diseases, Prion
- **En genoma:** Sí

### rs3825942
- **Magnitud:** 2.3
- **Repute:** Bad
- **Resumen:** more info
- **Genes:** LOXL1, LOXL1-AS1
- **Condiciones:** Glaucoma, Syndrome
- **En genoma:** Sí

### rs3114018
- **Magnitud:** 2.3
- **Repute:** Bad
- **Resumen:** Somewhat higher risk for gout among Chinese see text on main rs-page
- **Genes:** ABCG2
- **Condiciones:** Gout
- **En genoma:** Sí

### rs4430796
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** 1.38x increased risk for prostate cancer
- **Genes:** HNF1B
- **Condiciones:** Cancer, Diabetes, Prostate
- **En genoma:** Sí

### rs1050631
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** Mean Survival Time of 17 months for esophageal squamous-cell carcinoma
- **Genes:** SLC39A6
- **Condiciones:** Cancer, Carcinoma
- **En genoma:** Sí

### rs17563
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** Risk for otosclerosis
- **Genes:** BMP4
- **Condiciones:** Otosclerosis
- **En genoma:** Sí

### rs7837688
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** 1.7x increased risk for prostate cancer
- **Condiciones:** Cancer, Prostate
- **En genoma:** Sí

### rs1333048
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** 1.5x increased coronary artery disease risk; 2x increased periodontitis risk 2x increased risk of periodontitis and coronary heart disease as discussed at 23andMe blog
- **Condiciones:** Cardiovascular, Coronary, Disease, Heart
- **En genoma:** Sí

### rs801114
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** 2 SNPs located in different regions of chromosome 1 are likely to be associated with increased risk for basal cell carcinoma (BCC), the most common form of skin cancer.
- **Condiciones:** Cancer, Carcinoma, Tumor, cancer, carcinoma
- **En genoma:** Sí

### rs2383207
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** increased risk for heart disease
- **Genes:** CDKN2B-AS1
- **Condiciones:** Coronary, Disease, Heart, Infarction, Myocardial
- **En genoma:** Sí

### rs560887
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** rs560887, p = 4 x 10(-7))
- **Genes:** G6PC2
- **Condiciones:** Diabetes, Pancreatic
- **En genoma:** Sí

### rs944289
- **Magnitud:** 2.1
- **Repute:** Bad
- **Resumen:** 1.3x increased thyroid cancer risk
- **Condiciones:** Cancer, Thyroid
- **En genoma:** Sí

### rs3129934
- **Magnitud:** 2.0
- **Repute:** Bad
- **Resumen:** Increased risk of Multiple Sclerosis.
- **Genes:** C6orf10, LOC101929163
- **Condiciones:** Diabetes, Diseases, Sclerosis
- **En genoma:** Sí

### rs2305795
- **Magnitud:** 2.0
- **Repute:** Bad
- **Resumen:** 1.64x higher risk of narcolepsy compared to (G;G) genotype
- **Genes:** EIF3G, PPAN-P2RY11, P2RY11
- **Condiciones:** Narcolepsy
- **En genoma:** Sí

*... y 43 más*

---

## SNPs de Alta Magnitud (>=3.5)

SNPs con mayor impacto según Promethease:

### rs17646665
- **Magnitud:** 3.9
- **Repute:** Good
- **Resumen:** Moderately reduced risk for Alzheimer's (~0.6x) see link via main rs-page
- **Genes:** SORT1
- **En BD curada:** Sí
- **En genoma:** Sí

---

## Recomendaciones

2. **Agregar SNPs faltantes:** Considerar agregar los 63 SNPs de alta importancia a `snps.json`.
**Sistema funcionando correctamente:** No se encontraron problemas críticos.

---

**Fin del Reporte de Auditoría**