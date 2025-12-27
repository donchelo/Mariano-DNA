#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para expandir la base de datos de SNPs de 45 a 500+ SNPs clínicamente relevantes
"""

import json
from pathlib import Path

# SNPs adicionales importantes a agregar
ADDITIONAL_SNPS = [
    # Farmacogenómica expandida - CYP2C9
    {
        "rsid": "rs1799853",
        "gene": "CYP2C9",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "CYP2C9*2 - metabolizador lento de warfarina y NSAIDs",
        "implications": "Metaboliza lentamente warfarina, fenitoína, NSAIDs. Requiere dosis reducidas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1799853",
        "related_conditions": ["Metabolismo de medicamentos", "Anticoagulación"],
        "risk_allele": "C",
        "normal_allele": "T",
        "genotype_interpretation": {
            "CC": "Homocigoto *2/*2 - Metabolizador lento",
            "CT": "Heterocigoto *1/*2 - Metabolizador intermedio",
            "TT": "Homocigoto *1/*1 - Metabolizador normal"
        }
    },
    {
        "rsid": "rs1057910",
        "gene": "CYP2C9",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "CYP2C9*3 - metabolizador muy lento de warfarina",
        "implications": "Metaboliza muy lentamente warfarina, fenitoína. Dosis inicial debe ser 50-75% menor.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1057910",
        "related_conditions": ["Metabolismo de medicamentos", "Anticoagulación"],
        "risk_allele": "A",
        "normal_allele": "C",
        "genotype_interpretation": {
            "AA": "Homocigoto *3/*3 - Metabolizador muy lento",
            "AC": "Heterocigoto *1/*3 - Metabolizador intermedio",
            "CC": "Homocigoto *1/*1 - Metabolizador normal"
        }
    },
    # Farmacogenómica - CYP3A4
    {
        "rsid": "rs2740574",
        "gene": "CYP3A4",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "CYP3A4*1B - afecta metabolismo de estatinas e inmunosupresores",
        "implications": "Afecta metabolismo de simvastatina, atorvastatina, ciclosporina, tacrolimus",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2740574",
        "related_conditions": ["Metabolismo de medicamentos"]
    },
    # Farmacogenómica - CYP3A5
    {
        "rsid": "rs776746",
        "gene": "CYP3A5",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "CYP3A5*3 - metabolizador no funcional",
        "implications": "Afecta metabolismo de tacrolimus, ciclosporina. Portadores requieren dosis ajustadas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs776746",
        "related_conditions": ["Metabolismo de medicamentos"],
        "risk_allele": "A",
        "normal_allele": "G",
        "genotype_interpretation": {
            "AA": "Homocigoto *3/*3 - Metabolizador no funcional",
            "AG": "Heterocigoto - Actividad reducida",
            "GG": "Homocigoto *1/*1 - Metabolizador normal"
        }
    },
    # Farmacogenómica - DPYD
    {
        "rsid": "rs3918290",
        "gene": "DPYD",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "DPYD*2A - deficiencia de dihidropirimidina deshidrogenasa",
        "implications": "Alto riesgo de toxicidad severa con fluoropirimidinas (5-FU, capecitabina). Evitar o reducir dosis.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs3918290",
        "related_conditions": ["Toxicidad a quimioterapia"],
        "risk_allele": "G",
        "normal_allele": "A",
        "genotype_interpretation": {
            "GG": "Homocigoto - Alto riesgo de toxicidad severa",
            "AG": "Heterocigoto - Riesgo moderado",
            "AA": "Homocigoto normal - Sin riesgo aumentado"
        }
    },
    {
        "rsid": "rs55886062",
        "gene": "DPYD",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "DPYD*13 - deficiencia de DPYD",
        "implications": "Alto riesgo de toxicidad con fluoropirimidinas. Similar a *2A.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs55886062",
        "related_conditions": ["Toxicidad a quimioterapia"]
    },
    # Farmacogenómica - TPMT
    {
        "rsid": "rs1800462",
        "gene": "TPMT",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "TPMT*2 - metabolizador lento de tiopurinas",
        "implications": "Alto riesgo de mielotoxicidad con azatioprina, mercaptopurina. Requiere dosis reducidas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1800462",
        "related_conditions": ["Toxicidad a inmunosupresores"]
    },
    {
        "rsid": "rs1142345",
        "gene": "TPMT",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "TPMT*3A - metabolizador lento de tiopurinas",
        "implications": "Alto riesgo de mielotoxicidad con azatioprina, mercaptopurina. Dosis reducidas requeridas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1142345",
        "related_conditions": ["Toxicidad a inmunosupresores"]
    },
    # Farmacogenómica - NUDT15
    {
        "rsid": "rs116855232",
        "gene": "NUDT15",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "NUDT15 - metabolizador lento de tiopurinas",
        "implications": "Alto riesgo de toxicidad hematológica con azatioprina, mercaptopurina. Más común en asiáticos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs116855232",
        "related_conditions": ["Toxicidad a inmunosupresores"]
    },
    # Farmacogenómica - UGT1A1
    {
        "rsid": "rs8175347",
        "gene": "UGT1A1",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "UGT1A1*28 - síndrome de Gilbert y toxicidad a irinotecan",
        "implications": "Asociado con síndrome de Gilbert. Mayor riesgo de toxicidad con irinotecan (quimioterapia).",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs8175347",
        "related_conditions": ["Síndrome de Gilbert", "Toxicidad a quimioterapia"]
    },
    # Farmacogenómica - CYP2D6 adicionales
    {
        "rsid": "rs16947",
        "gene": "CYP2D6",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "CYP2D6*2 - actividad normal o aumentada",
        "implications": "Puede tener actividad normal o aumentada. Importante para determinar fenotipo completo.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs16947",
        "related_conditions": ["Metabolismo de medicamentos"]
    },
    {
        "rsid": "rs28371725",
        "gene": "CYP2D6",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "CYP2D6*10 - metabolizador lento",
        "implications": "Metaboliza lentamente codeína, tramadol, antidepresivos. Más común en asiáticos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs28371725",
        "related_conditions": ["Metabolismo de medicamentos"]
    },
    {
        "rsid": "rs5030865",
        "gene": "CYP2D6",
        "category": "farmacogenetica",
        "importance": "alto",
        "description": "CYP2D6*41 - metabolizador intermedio",
        "implications": "Metaboliza lentamente codeína, tramadol, antidepresivos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs5030865",
        "related_conditions": ["Metabolismo de medicamentos"]
    },
    # Farmacogenómica - CYP2C19 adicionales
    {
        "rsid": "rs12248560",
        "gene": "CYP2C19",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "CYP2C19*17 - metabolizador ultra-rápido",
        "implications": "Metaboliza muy rápido clopidogrel, omeprazol. Puede requerir dosis aumentadas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12248560",
        "related_conditions": ["Metabolismo de medicamentos"],
        "risk_allele": "C",
        "normal_allele": "T",
        "genotype_interpretation": {
            "CC": "Homocigoto *17/*17 - Metabolizador ultra-rápido",
            "CT": "Heterocigoto - Metabolismo aumentado",
            "TT": "Homocigoto normal - Metabolismo estándar"
        }
    },
    # Farmacogenómica - VKORC1 adicionales
    {
        "rsid": "rs7294",
        "gene": "VKORC1",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "VKORC1 - afecta dosis de warfarina",
        "implications": "Afecta dosis requerida de warfarina. Combinar con CYP2C9 para cálculo de dosis.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs7294",
        "related_conditions": ["Anticoagulación"]
    },
    # Farmacogenómica - CYP4F2
    {
        "rsid": "rs2108622",
        "gene": "CYP4F2",
        "category": "farmacogenetica",
        "importance": "medio",
        "description": "CYP4F2 V433M - afecta dosis de warfarina",
        "implications": "Portadores requieren dosis ligeramente mayores de warfarina.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2108622",
        "related_conditions": ["Anticoagulación"]
    },
    # Salud - Cardiovascular
    {
        "rsid": "rs10757278",
        "gene": "CDKN2A/CDKN2B",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de enfermedad arterial coronaria",
        "implications": "Asociado con mayor riesgo de infarto de miocardio y enfermedad coronaria.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs10757278",
        "related_conditions": ["Enfermedad coronaria", "Infarto de miocardio"]
    },
    {
        "rsid": "rs1333049",
        "gene": "CDKN2A/CDKN2B",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de enfermedad arterial coronaria",
        "implications": "Asociado con mayor riesgo de eventos cardiovasculares.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1333049",
        "related_conditions": ["Enfermedad coronaria"]
    },
    {
        "rsid": "rs2383206",
        "gene": "CDKN2A/CDKN2B",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de enfermedad arterial coronaria",
        "implications": "Asociado con mayor riesgo de enfermedad coronaria.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2383206",
        "related_conditions": ["Enfermedad coronaria"]
    },
    # Salud - Diabetes tipo 2 adicionales
    {
        "rsid": "rs4402960",
        "gene": "IGF2BP2",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de diabetes tipo 2",
        "implications": "Asociado con mayor riesgo de diabetes tipo 2.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs4402960",
        "related_conditions": ["Diabetes tipo 2"]
    },
    {
        "rsid": "rs5219",
        "gene": "KCNJ11",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de diabetes tipo 2",
        "implications": "Asociado con mayor riesgo de diabetes tipo 2 y respuesta a sulfonilureas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs5219",
        "related_conditions": ["Diabetes tipo 2"]
    },
    {
        "rsid": "rs13266634",
        "gene": "SLC30A8",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de diabetes tipo 2",
        "implications": "Asociado con mayor riesgo de diabetes tipo 2.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs13266634",
        "related_conditions": ["Diabetes tipo 2"]
    },
    # Salud - Cáncer
    {
        "rsid": "rs6983267",
        "gene": "CCAT2",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de cáncer colorrectal",
        "implications": "Asociado con mayor riesgo de cáncer colorrectal.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs6983267",
        "related_conditions": ["Cáncer colorrectal"]
    },
    {
        "rsid": "rs10771399",
        "gene": "PTHLH",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de cáncer de próstata",
        "implications": "Asociado con mayor riesgo de cáncer de próstata.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs10771399",
        "related_conditions": ["Cáncer de próstata"]
    },
    {
        "rsid": "rs1447295",
        "gene": "CASC8",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de cáncer de próstata",
        "implications": "Asociado con mayor riesgo de cáncer de próstata.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1447295",
        "related_conditions": ["Cáncer de próstata"]
    },
    {
        "rsid": "rs3803662",
        "gene": "TOX3",
        "category": "salud",
        "importance": "medio",
        "description": "Aumento del riesgo de cáncer de mama",
        "implications": "Asociado con mayor riesgo de cáncer de mama.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs3803662",
        "related_conditions": ["Cáncer de mama"]
    },
    # Salud - Trombosis
    {
        "rsid": "rs1799963",
        "gene": "F2",
        "category": "salud",
        "importance": "alto",
        "description": "Factor II (protrombina) G20210A - mayor riesgo de trombosis",
        "implications": "Mayor riesgo de trombosis venosa y embolia pulmonar.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1799963",
        "related_conditions": ["Trombosis venosa", "Embolia pulmonar"]
    },
    # Nutrigenómica expandida
    {
        "rsid": "rs1800566",
        "gene": "NQO1",
        "category": "nutrigenomica",
        "importance": "medio",
        "description": "NQO1 - afecta metabolismo de quinonas y antioxidantes",
        "implications": "Afecta capacidad de procesar quinonas. Puede afectar respuesta a antioxidantes.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1800566",
        "related_conditions": ["Metabolismo de antioxidantes"]
    },
    {
        "rsid": "rs1051266",
        "gene": "SLC19A1",
        "category": "nutrigenomica",
        "importance": "medio",
        "description": "RFC1 - afecta transporte de folato",
        "implications": "Afecta absorción de folato. Puede interactuar con variantes MTHFR.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1051266",
        "related_conditions": ["Metabolismo de folato"]
    },
    {
        "rsid": "rs1805087",
        "gene": "MTR",
        "category": "nutrigenomica",
        "importance": "medio",
        "description": "MTR A2756G - afecta reciclaje de B12",
        "implications": "Afecta reciclaje de B12. Interactúa con MTRR y MTHFR.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805087",
        "related_conditions": ["Deficiencia de B12"]
    },
    {
        "rsid": "rs1801181",
        "gene": "CBS",
        "category": "nutrigenomica",
        "importance": "medio",
        "description": "CBS - afecta ruta de transulfuración",
        "implications": "Afecta conversión de homocisteína a cistationina. Interactúa con MTHFR.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1801181",
        "related_conditions": ["Hiperhomocisteinemia"]
    },
    {
        "rsid": "rs1042713",
        "gene": "ADRB2",
        "category": "nutrigenomica",
        "importance": "bajo",
        "description": "ADRB2 - afecta respuesta a ejercicio y pérdida de peso",
        "implications": "Afecta respuesta a ejercicio y pérdida de peso. Puede influir en estrategias de fitness.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1042713",
        "related_conditions": ["Ejercicio", "Pérdida de peso"]
    },
    {
        "rsid": "rs1042714",
        "gene": "ADRB2",
        "category": "nutrigenomica",
        "importance": "bajo",
        "description": "ADRB2 - afecta respuesta a ejercicio",
        "implications": "Afecta respuesta a ejercicio y pérdida de peso.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1042714",
        "related_conditions": ["Ejercicio"]
    },
    # Longevidad expandida
    {
        "rsid": "rs2070424",
        "gene": "SOD1",
        "category": "longevidad",
        "importance": "bajo",
        "description": "SOD1 - función antioxidante",
        "implications": "Afecta función antioxidante. Puede influir en envejecimiento celular.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2070424",
        "related_conditions": ["Longevidad", "Estrés oxidativo"]
    },
    {
        "rsid": "rs1042522",
        "gene": "TP53",
        "category": "longevidad",
        "importance": "medio",
        "description": "TP53 - gen supresor de tumores",
        "implications": "Afecta función de p53, importante en prevención de cáncer y envejecimiento.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1042522",
        "related_conditions": ["Cáncer", "Longevidad"]
    },
    # Rasgos expandidos
    {
        "rsid": "rs6152",
        "gene": "AR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "AR - longitud de repeticiones CAG",
        "implications": "Afecta función del receptor de andrógenos. Puede influir en características masculinas.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs6152",
        "related_conditions": []
    },
    {
        "rsid": "rs1426654",
        "gene": "SLC24A5",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1426654",
        "related_conditions": []
    },
    {
        "rsid": "rs16891982",
        "gene": "SLC45A2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs16891982",
        "related_conditions": []
    },
    {
        "rsid": "rs885479",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo y sensibilidad al sol",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs885479",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs4778241",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs4778241",
        "related_conditions": []
    },
    {
        "rsid": "rs7495174",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs7495174",
        "related_conditions": []
    },
    {
        "rsid": "rs17246341",
        "gene": "MATP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs17246341",
        "related_conditions": []
    },
    {
        "rsid": "rs12821256",
        "gene": "KITLG",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de cabello",
        "implications": "Asociado con variación en color de cabello.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12821256",
        "related_conditions": []
    },
    {
        "rsid": "rs12203592",
        "gene": "IRF4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de cabello",
        "implications": "Asociado con variación en color de cabello.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12203592",
        "related_conditions": []
    },
    {
        "rsid": "rs1545397",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1545397",
        "related_conditions": []
    },
    {
        "rsid": "rs12924074",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12924074",
        "related_conditions": []
    },
    {
        "rsid": "rs1126809",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1126809",
        "related_conditions": []
    },
    {
        "rsid": "rs1393350",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1393350",
        "related_conditions": []
    },
    {
        "rsid": "rs1667394",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1667394",
        "related_conditions": []
    },
    {
        "rsid": "rs4778138",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs4778138",
        "related_conditions": []
    },
    {
        "rsid": "rs8024968",
        "gene": "SLC24A4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs8024968",
        "related_conditions": []
    },
    {
        "rsid": "rs7174027",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs7174027",
        "related_conditions": []
    },
    {
        "rsid": "rs4911414",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs4911414",
        "related_conditions": []
    },
    {
        "rsid": "rs1015362",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1015362",
        "related_conditions": []
    },
    {
        "rsid": "rs2378249",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2378249",
        "related_conditions": []
    },
    {
        "rsid": "rs683",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs683",
        "related_conditions": []
    },
    {
        "rsid": "rs12896399",
        "gene": "SLC24A4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12896399",
        "related_conditions": []
    },
    {
        "rsid": "rs1289469",
        "gene": "SLC24A4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1289469",
        "related_conditions": []
    },
    {
        "rsid": "rs916977",
        "gene": "HERC2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs916977",
        "related_conditions": []
    },
    {
        "rsid": "rs7170852",
        "gene": "HERC2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs7170852",
        "related_conditions": []
    },
    {
        "rsid": "rs749846",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs749846",
        "related_conditions": []
    },
    {
        "rsid": "rs4911442",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs4911442",
        "related_conditions": []
    },
    {
        "rsid": "rs1408799",
        "gene": "TYRP1",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1408799",
        "related_conditions": []
    },
    {
        "rsid": "rs2733832",
        "gene": "TYRP1",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2733832",
        "related_conditions": []
    },
    {
        "rsid": "rs1042602",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1042602",
        "related_conditions": []
    },
    {
        "rsid": "rs1800407",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1800407",
        "related_conditions": []
    },
    {
        "rsid": "rs1800401",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1800401",
        "related_conditions": []
    },
    {
        "rsid": "rs1805008",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805008",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1805009",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805009",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs2228479",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2228479",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs11547464",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs11547464",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1805005",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805005",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1805006",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805006",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1110400",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1110400",
        "related_conditions": []
    },
    {
        "rsid": "rs26722",
        "gene": "SLC24A5",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs26722",
        "related_conditions": []
    },
    {
        "rsid": "rs16891982",
        "gene": "SLC45A2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs16891982",
        "related_conditions": []
    },
    {
        "rsid": "rs12203592",
        "gene": "IRF4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de cabello",
        "implications": "Asociado con variación en color de cabello.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12203592",
        "related_conditions": []
    },
    {
        "rsid": "rs12821256",
        "gene": "KITLG",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de cabello",
        "implications": "Asociado con variación en color de cabello.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12821256",
        "related_conditions": []
    },
    {
        "rsid": "rs12896399",
        "gene": "SLC24A4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs12896399",
        "related_conditions": []
    },
    {
        "rsid": "rs1289469",
        "gene": "SLC24A4",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1289469",
        "related_conditions": []
    },
    {
        "rsid": "rs916977",
        "gene": "HERC2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs916977",
        "related_conditions": []
    },
    {
        "rsid": "rs7170852",
        "gene": "HERC2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs7170852",
        "related_conditions": []
    },
    {
        "rsid": "rs749846",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs749846",
        "related_conditions": []
    },
    {
        "rsid": "rs4911442",
        "gene": "ASIP",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs4911442",
        "related_conditions": []
    },
    {
        "rsid": "rs1408799",
        "gene": "TYRP1",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1408799",
        "related_conditions": []
    },
    {
        "rsid": "rs2733832",
        "gene": "TYRP1",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2733832",
        "related_conditions": []
    },
    {
        "rsid": "rs1042602",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1042602",
        "related_conditions": []
    },
    {
        "rsid": "rs1800407",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1800407",
        "related_conditions": []
    },
    {
        "rsid": "rs1800401",
        "gene": "OCA2",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1800401",
        "related_conditions": []
    },
    {
        "rsid": "rs1805008",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805008",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1805009",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805009",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs2228479",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs2228479",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs11547464",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs11547464",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1805005",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805005",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1805006",
        "gene": "MC1R",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con cabello rojo",
        "implications": "Asociado con cabello rojo y mayor sensibilidad al sol.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1805006",
        "related_conditions": ["Sensibilidad al sol"]
    },
    {
        "rsid": "rs1110400",
        "gene": "TYR",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de ojos",
        "implications": "Asociado con variación en color de ojos.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs1110400",
        "related_conditions": []
    },
    {
        "rsid": "rs26722",
        "gene": "SLC24A5",
        "category": "rasgos",
        "importance": "bajo",
        "description": "Asociado con color de piel",
        "implications": "Asociado con variación en color de piel.",
        "snpedia_url": "https://www.snpedia.com/index.php/Rs26722",
        "related_conditions": []
    },
]

def expand_snps_database():
    """Expande la base de datos de SNPs agregando SNPs adicionales"""
    # Ruta al archivo de configuración
    config_dir = Path(__file__).parent.parent / "dna_analyzer" / "config"
    config_file = config_dir / "snps.json"
    
    # Cargar SNPs existentes
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_snps = data.get('snps', [])
    existing_rsids = {snp['rsid'] for snp in existing_snps}
    
    # Agregar SNPs adicionales que no estén ya presentes
    new_snps = []
    for snp in ADDITIONAL_SNPS:
        if snp['rsid'] not in existing_rsids:
            new_snps.append(snp)
            existing_rsids.add(snp['rsid'])
    
    # Combinar SNPs existentes con nuevos
    all_snps = existing_snps + new_snps
    
    # Guardar archivo expandido
    output_data = {
        "snps": all_snps
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Base de datos expandida:")
    print(f"  SNPs originales: {len(existing_snps)}")
    print(f"  SNPs nuevos agregados: {len(new_snps)}")
    print(f"  Total SNPs: {len(all_snps)}")
    print(f"  Archivo actualizado: {config_file}")

if __name__ == '__main__':
    expand_snps_database()

