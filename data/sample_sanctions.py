# Sample sanctions list structure (use OFAC SDN list format)
SAMPLE_SANCTIONS = [
    {
        "id": "SDN-001",
        "name": "ACME Shell Corporation",
        "aliases": ["ACME Holdings", "ACME LLC"],
        "entity_type": "Entity",
        "sanctions_list": "OFAC SDN",
        "country": "Unknown",
        "date_added": "2023-01-15",
        "details": "Designated for sanctions evasion activities"
    },
    {
        "id": "SDN-002",
        "name": "Offshore Trust Ltd",
        "aliases": ["OT Limited", "Offshore Holdings"],
        "entity_type": "Entity",
        "sanctions_list": "OFAC SDN",
        "country": "Cayman Islands",
        "date_added": "2022-08-20",
        "details": "Designated for money laundering activities"
    },
    {
        "id": "SDN-003",
        "name": "XYZ Holdings International",
        "aliases": ["XYZ Global", "XYZ Finance"],
        "entity_type": "Entity",
        "sanctions_list": "OFAC SDN",
        "country": "Panama",
        "date_added": "2023-06-10",
        "details": "Designated for facilitating sanctions evasion"
    },
    {
        "id": "SDN-004",
        "name": "Suspicious Trading Co",
        "aliases": ["STC Trading", "S.T. Company"],
        "entity_type": "Entity",
        "sanctions_list": "UN Consolidated",
        "country": "Syria",
        "date_added": "2022-03-01",
        "details": "Designated for weapons proliferation"
    },
    {
        "id": "SDN-005",
        "name": "Shadow Finance Group",
        "aliases": ["SFG Ltd", "Shadow Holdings"],
        "entity_type": "Entity",
        "sanctions_list": "EU Sanctions",
        "country": "Russia",
        "date_added": "2022-02-28",
        "details": "Designated in response to geopolitical events"
    }
]

# High-risk jurisdictions
HIGH_RISK_JURISDICTIONS = [
    {"code": "IR", "name": "Iran", "risk_level": "HIGH", "notes": "OFAC comprehensive sanctions"},
    {"code": "KP", "name": "North Korea", "risk_level": "HIGH", "notes": "OFAC comprehensive sanctions"},
    {"code": "SY", "name": "Syria", "risk_level": "HIGH", "notes": "OFAC comprehensive sanctions"},
    {"code": "CU", "name": "Cuba", "risk_level": "HIGH", "notes": "OFAC comprehensive sanctions"},
    {"code": "RU", "name": "Russia", "risk_level": "MEDIUM", "notes": "Sectoral sanctions"},
    {"code": "BY", "name": "Belarus", "risk_level": "MEDIUM", "notes": "Targeted sanctions"},
    {"code": "VE", "name": "Venezuela", "risk_level": "MEDIUM", "notes": "Targeted sanctions"},
    {"code": "KY", "name": "Cayman Islands", "risk_level": "MEDIUM", "notes": "Tax haven - enhanced due diligence"},
    {"code": "PA", "name": "Panama", "risk_level": "MEDIUM", "notes": "Tax haven - enhanced due diligence"},
]
