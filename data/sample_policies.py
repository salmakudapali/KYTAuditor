# Sample compliance policies
SAMPLE_POLICIES = [
    {
        "id": "POL-001",
        "title": "Currency Transaction Report (CTR) Requirements",
        "category": "BSA",
        "regulation": "31 CFR 1010.311",
        "effective_date": "2023-01-01",
        "content": """
        Financial institutions must file a Currency Transaction Report (CTR) for each deposit, 
        withdrawal, exchange of currency, or other payment or transfer, by, through, or to the 
        financial institution, which involves a transaction in currency of more than $10,000.
        
        Key Requirements:
        - File within 15 days of the transaction
        - Include all required customer identification information
        - Aggregate multiple transactions if they exceed $10,000 in a single business day
        - Maintain records for 5 years
        """,
        "keywords": ["CTR", "currency", "10000", "cash", "reporting"]
    },
    {
        "id": "POL-002",
        "title": "Suspicious Activity Report (SAR) Requirements",
        "category": "BSA",
        "regulation": "31 CFR 1020.320",
        "effective_date": "2023-01-01",
        "content": """
        Banks must file a Suspicious Activity Report (SAR) for any suspicious transaction 
        relevant to a possible violation of law or regulation. This includes transactions 
        that involve funds derived from illegal activities or are designed to evade 
        reporting requirements.
        
        Key Thresholds:
        - $5,000 or more involving a suspect identified by the bank
        - $25,000 or more regardless of potential suspects
        
        Filing Requirements:
        - File within 30 days of initial detection
        - May extend to 60 days if no suspect is identified
        - Maintain supporting documentation for 5 years
        """,
        "keywords": ["SAR", "suspicious", "activity", "report", "fraud", "money laundering"]
    },
    {
        "id": "POL-003",
        "title": "Enhanced Due Diligence (EDD) Requirements",
        "category": "AML",
        "regulation": "31 CFR 1010.610",
        "effective_date": "2023-01-01",
        "content": """
        Enhanced due diligence is required for accounts that pose higher risks of money 
        laundering or terrorist financing.
        
        EDD Required For:
        - Private banking accounts
        - Correspondent accounts for foreign financial institutions
        - Politically Exposed Persons (PEPs)
        - Customers from high-risk jurisdictions
        - Complex ownership structures
        
        EDD Measures:
        - Obtain senior management approval for new relationships
        - Take reasonable measures to establish source of wealth/funds
        - Conduct enhanced ongoing monitoring
        - Document risk assessment and mitigation measures
        """,
        "keywords": ["EDD", "enhanced", "due diligence", "PEP", "high risk"]
    },
    {
        "id": "POL-004",
        "title": "Know Your Customer (KYC) Requirements",
        "category": "CIP",
        "regulation": "31 CFR 1020.220",
        "effective_date": "2023-01-01",
        "content": """
        Customer Identification Program (CIP) requirements mandate that financial 
        institutions verify the identity of customers opening accounts.
        
        Required Information:
        - Name
        - Date of birth (for individuals)
        - Address
        - Identification number (SSN, TIN, or passport)
        
        Verification Methods:
        - Documentary verification (ID documents)
        - Non-documentary verification (credit reports, databases)
        - Combination of both for higher-risk customers
        
        Record Retention:
        - Maintain records for 5 years after account closure
        """,
        "keywords": ["KYC", "CIP", "customer", "identification", "verification"]
    },
    {
        "id": "POL-005",
        "title": "Beneficial Ownership Requirements",
        "category": "CDD",
        "regulation": "31 CFR 1010.230",
        "effective_date": "2023-01-01",
        "content": """
        Financial institutions must identify and verify the beneficial owners of 
        legal entity customers.
        
        Beneficial Owner Defined:
        - Each individual who owns 25% or more of the equity interests
        - One individual with significant responsibility for the entity
        
        Required Information:
        - Name
        - Date of birth
        - Address
        - Identification number
        
        Verification:
        - Risk-based verification procedures
        - Update information when triggered by events
        """,
        "keywords": ["beneficial", "ownership", "CDD", "entity", "verification"]
    }
]

# Risk scoring matrix
RISK_SCORING_MATRIX = {
    "transaction_amount": {
        "low": {"min": 0, "max": 5000, "score": 1},
        "medium": {"min": 5000, "max": 10000, "score": 3},
        "high": {"min": 10000, "max": float("inf"), "score": 5}
    },
    "jurisdiction_risk": {
        "low": 1,
        "medium": 3,
        "high": 5
    },
    "structuring_indicator": {
        "none": 0,
        "possible": 3,
        "likely": 5
    },
    "sanctions_match": {
        "no_match": 0,
        "possible_match": 4,
        "confirmed_match": 10
    }
}
