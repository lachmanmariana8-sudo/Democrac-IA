"""DEMOCRAC.IA / PEIRS — Instrumentos legales y regiones"""

REGION_AMERICAS = "americas"
REGION_EUROPE = "europe"
REGION_AFRICA = "africa"
REGION_ASIA_PACIFIC = "asia_pacific"
REGION_ARAB = "arab_states"

COUNTRY_REGIONS = {
    "VEN": REGION_AMERICAS, "NIC": REGION_AMERICAS, "GTM": REGION_AMERICAS,
    "URY": REGION_AMERICAS, "COL": REGION_AMERICAS, "BRA": REGION_AMERICAS,
    "MEX": REGION_AMERICAS, "ARG": REGION_AMERICAS, "CHL": REGION_AMERICAS,
    "BOL": REGION_AMERICAS, "ECU": REGION_AMERICAS, "PER": REGION_AMERICAS,
    "HND": REGION_AMERICAS, "SLV": REGION_AMERICAS, "PAN": REGION_AMERICAS,
    "CRI": REGION_AMERICAS, "DOM": REGION_AMERICAS, "PRY": REGION_AMERICAS, "CUB": REGION_AMERICAS,
    "DEU": REGION_EUROPE, "FRA": REGION_EUROPE, "HUN": REGION_EUROPE, "POL": REGION_EUROPE,
    "TUR": REGION_EUROPE, "RUS": REGION_EUROPE, "BLR": REGION_EUROPE, "UKR": REGION_EUROPE, "GEO": REGION_EUROPE,
    "ZAF": REGION_AFRICA, "NGA": REGION_AFRICA, "KEN": REGION_AFRICA, "ZWE": REGION_AFRICA, "GHA": REGION_AFRICA,
    "IND": REGION_ASIA_PACIFIC, "PHL": REGION_ASIA_PACIFIC, "IDN": REGION_ASIA_PACIFIC, "THA": REGION_ASIA_PACIFIC,
    "TUN": REGION_ARAB,
}

UNIVERSAL_INSTRUMENTS = [
    {"id": "ICCPR", "name": "Pacto Internacional de Derechos Civiles y Políticos",
     "key_articles": ["Art. 1", "Art. 2", "Art. 3", "Art. 9", "Art. 14", "Art. 19", "Art. 21", "Art. 22", "Art. 25", "Art. 26"]},
    {"id": "CEDAW", "name": "Convención sobre la Eliminación de Todas las Formas de Discriminación contra la Mujer",
     "key_articles": ["Art. 7", "Art. 8"]},
    {"id": "ICERD", "name": "Convención Internacional sobre la Eliminación de Todas las Formas de Discriminación Racial",
     "key_articles": ["Art. 5"]},
    {"id": "CRPD", "name": "Convención sobre los Derechos de las Personas con Discapacidad",
     "key_articles": ["Art. 29"]},
    {"id": "UNDRIP", "name": "Declaración de las Naciones Unidas sobre los Derechos de los Pueblos Indígenas",
     "key_articles": ["Art. 5", "Art. 18"]},
    {"id": "UNCAC", "name": "Convención de las Naciones Unidas contra la Corrupción",
     "key_articles": ["Art. 7", "Art. 12", "Art. 13"]},
]

REGIONAL_INSTRUMENTS = {
    REGION_AMERICAS: [
        {"id": "CADH", "name": "Convención Americana sobre Derechos Humanos",
         "key_articles": ["Art. 23"], "observer": "OEA/DECO, UNIORE, Centro Carter"},
        {"id": "CDI", "name": "Carta Democrática Interamericana",
         "key_articles": ["Art. 3", "Art. 23", "Art. 24"], "observer": "OEA"},
    ],
    REGION_EUROPE: [
        {"id": "ECHR_P1", "name": "Convenio Europeo de Derechos Humanos, Protocolo 1",
         "key_articles": ["Art. 3"], "observer": "OSCE/ODIHR, Comisión de Venecia"},
        {"id": "COPENHAGEN", "name": "Documento de Copenhague OSCE 1990",
         "key_articles": ["Par. 5", "Par. 6", "Par. 7", "Par. 8"], "observer": "OSCE/ODIHR"},
    ],
    REGION_AFRICA: [
        {"id": "ACHPR", "name": "Carta Africana de Derechos Humanos y de los Pueblos",
         "key_articles": ["Art. 13"], "observer": "Unión Africana, ECOWAS, SADC"},
        {"id": "ACDEG", "name": "Carta Africana sobre Democracia, Elecciones y Gobernanza",
         "key_articles": ["Art. 3", "Art. 17", "Art. 22"], "observer": "Unión Africana"},
    ],
    REGION_ASIA_PACIFIC: [
        {"id": "ANFREL_DEC", "name": "Declaración de Bangkok ANFREL",
         "key_articles": [], "observer": "ANFREL, Pacific Islands Forum"},
    ],
    REGION_ARAB: [
        {"id": "ARAB_CHARTER", "name": "Carta Árabe de Derechos Humanos",
         "key_articles": ["Art. 24"], "observer": "Liga Árabe"},
    ],
}

EMB_NAMES = {
    "VEN": "Consejo Nacional Electoral (CNE)", "NIC": "Consejo Supremo Electoral (CSE)",
    "GTM": "Tribunal Supremo Electoral (TSE)", "URY": "Corte Electoral",
    "COL": "Registraduria Nacional del Estado Civil", "BRA": "Tribunal Superior Electoral (TSE)",
    "MEX": "Instituto Nacional Electoral (INE)", "ARG": "Camara Nacional Electoral",
    "CHL": "Servicio Electoral (SERVEL)", "BOL": "Tribunal Supremo Electoral (TSE)",
    "ECU": "Consejo Nacional Electoral (CNE)", "PER": "Jurado Nacional de Elecciones (JNE)",
    "HND": "Consejo Nacional Electoral (CNE)", "SLV": "Tribunal Supremo Electoral (TSE)",
    "PAN": "Tribunal Electoral", "CRI": "Tribunal Supremo de Elecciones (TSE)",
    "DOM": "Junta Central Electoral (JCE)", "PRY": "Tribunal Superior de Justicia Electoral (TSJE)",
    "CUB": "Comision Electoral Nacional", "DEU": "Bundeswahlleiter",
    "FRA": "Conseil Constitutionnel", "HUN": "Nemzeti Valasztasi Bizottsag",
    "POL": "Panstwowa Komisja Wyborcza (PKW)", "TUR": "Yuksek Secim Kurulu (YSK)",
    "RUS": "Tsentralnaya izbiratelnaya komissiya (TsIK)",
    "BLR": "Tsentralnaya komissiya po vyboram",
    "UKR": "Tsentralna vyborcha komisiya (TsVK)",
    "GEO": "Central Election Commission of Georgia",
    "ZAF": "Electoral Commission (IEC)", "NGA": "Independent National Electoral Commission (INEC)",
    "KEN": "Independent Electoral and Boundaries Commission (IEBC)",
    "ZWE": "Zimbabwe Electoral Commission (ZEC)", "GHA": "Electoral Commission of Ghana (EC)",
    "IND": "Election Commission of India (ECI)", "PHL": "Commission on Elections (COMELEC)",
    "IDN": "Komisi Pemilihan Umum (KPU)", "THA": "Election Commission of Thailand",
    "TUN": "Instance Superieure Independante pour les Elections (ISIE)",
}
