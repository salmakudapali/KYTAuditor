from langchain_core.tools import Tool
from .base_agent import get_llm, create_base_agent
from typing import Dict, List
import json


class LegalAgent:
    """
    Legal/Compliance Agent for regulatory compliance checking.
    Evaluates transactions against sanctions lists and compliance policies.
    """
    
    SYSTEM_PROMPT = """You are a legal compliance AI agent specialized in 
    Know Your Transaction (KYT) and Anti-Money Laundering (AML) regulations. Your role is to:
    
    1. Check transactions against sanctions lists (OFAC, UN, EU)
    2. Evaluate compliance with BSA/AML regulations
    3. Identify PEP (Politically Exposed Persons) involvement
    4. Assess jurisdiction risks
    5. Determine regulatory reporting requirements
    
    Always cite specific regulations when flagging issues. Be precise and avoid
    over-flagging to prevent alert fatigue. Provide clear, actionable recommendations."""
    
    def __init__(self, sanctions_searcher=None, policy_searcher=None):
        self.llm = get_llm()
        self.sanctions_searcher = sanctions_searcher
        self.policy_searcher = policy_searcher
        self.tools = self._create_tools()
        self.agent = create_base_agent(self.llm, self.tools, self.SYSTEM_PROMPT)
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the legal agent."""
        return [
            Tool(
                name="check_sanctions",
                func=self._check_sanctions,
                description="Check if an entity is on sanctions lists. Input: entity name or identifier."
            ),
            Tool(
                name="check_jurisdiction_risk",
                func=self._check_jurisdiction_risk,
                description="Check the risk level of a jurisdiction/country. Input: country code or name."
            ),
            Tool(
                name="get_compliance_policy",
                func=self._get_compliance_policy,
                description="Retrieve relevant compliance policies. Input: policy topic or regulation name."
            ),
            Tool(
                name="determine_reporting_requirements",
                func=self._determine_reporting_requirements,
                description="Determine if a transaction requires regulatory reporting. Input: JSON with transaction details."
            ),
        ]
    
    def _check_sanctions(self, entity: str) -> str:
        """Check if an entity is on sanctions lists."""
        if self.sanctions_searcher:
            results = self.sanctions_searcher.search(entity)
            return json.dumps(results)
        
        # Mock response for demo
        high_risk_entities = ["acme shell corporation", "xyz holdings", "offshore trust ltd"]
        entity_lower = entity.lower()
        
        if any(risk in entity_lower for risk in high_risk_entities):
            return json.dumps({
                "match_found": True,
                "entity": entity,
                "list": "OFAC SDN",
                "match_score": 0.95,
                "details": "Potential sanctions list match - requires manual review"
            })
        
        return json.dumps({
            "match_found": False,
            "entity": entity,
            "message": "No sanctions match found"
        })
    
    def _check_jurisdiction_risk(self, jurisdiction: str) -> str:
        """Check the risk level of a jurisdiction."""
        high_risk = ["ir", "kp", "sy", "iran", "north korea", "syria"]
        medium_risk = ["ru", "by", "russia", "belarus", "cayman islands", "panama"]
        
        jurisdiction_lower = jurisdiction.lower()
        
        if any(hr in jurisdiction_lower for hr in high_risk):
            risk_level = "HIGH"
            details = "FATF blacklisted or heavily sanctioned jurisdiction"
        elif any(mr in jurisdiction_lower for mr in medium_risk):
            risk_level = "MEDIUM"
            details = "Enhanced due diligence required"
        else:
            risk_level = "LOW"
            details = "Standard due diligence applies"
        
        return json.dumps({
            "jurisdiction": jurisdiction,
            "risk_level": risk_level,
            "details": details
        })
    
    def _get_compliance_policy(self, topic: str) -> str:
        """Retrieve relevant compliance policies."""
        if self.policy_searcher:
            results = self.policy_searcher.search(topic)
            return json.dumps(results)
        
        # Mock policies for demo
        policies = {
            "ctr": "Currency Transaction Report (CTR) required for cash transactions over $10,000",
            "sar": "Suspicious Activity Report (SAR) required when suspicious activity is detected regardless of amount",
            "kyc": "Know Your Customer (KYC) verification required for all new accounts and high-risk transactions",
            "aml": "Anti-Money Laundering (AML) procedures must be followed per BSA requirements"
        }
        
        topic_lower = topic.lower()
        relevant_policies = [v for k, v in policies.items() if k in topic_lower or topic_lower in k]
        
        return json.dumps({
            "topic": topic,
            "policies": relevant_policies if relevant_policies else ["General AML/BSA compliance required"]
        })
    
    def _determine_reporting_requirements(self, transaction_json: str) -> str:
        """Determine regulatory reporting requirements."""
        try:
            transaction = json.loads(transaction_json)
            requirements = []
            
            amount = transaction.get("amount", 0)
            transaction_type = transaction.get("type", "").lower()
            
            # CTR requirement
            if amount >= 10000 and "cash" in transaction_type:
                requirements.append({
                    "report_type": "CTR",
                    "regulation": "31 CFR 1010.311",
                    "deadline": "15 days",
                    "reason": "Cash transaction exceeds $10,000 threshold"
                })
            
            # SAR consideration
            if transaction.get("suspicious", False) or amount >= 5000:
                requirements.append({
                    "report_type": "SAR",
                    "regulation": "31 CFR 1020.320",
                    "deadline": "30 days",
                    "reason": "Transaction flagged for suspicious activity review"
                })
            
            return json.dumps({
                "transaction_id": transaction.get("id"),
                "reporting_requirements": requirements,
                "requires_action": len(requirements) > 0
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def evaluate(self, transactions: List[Dict], entities: List[str] = None) -> Dict:
        """Run compliance evaluation on transactions."""
        input_text = f"""Evaluate these transactions for compliance:
        {json.dumps(transactions, indent=2)}
        
        Entities to check: {entities or 'Extract from transactions'}
        
        Provide a comprehensive compliance evaluation including:
        1. Sanctions screening results
        2. Jurisdiction risk assessment
        3. Regulatory reporting requirements
        4. Policy compliance status
        5. Recommended actions"""
        
        result = self.agent.invoke({"input": input_text})
        return result
