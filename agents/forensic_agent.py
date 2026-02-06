from langchain_core.tools import Tool
from .base_agent import get_llm, create_base_agent
from typing import Dict, List
import json


class ForensicAgent:
    """
    Forensic Agent for pattern detection in transactions.
    Analyzes transactions for suspicious patterns and anomalies.
    """
    
    SYSTEM_PROMPT = """You are a forensic financial analyst AI agent specialized in 
    detecting suspicious transaction patterns. Your role is to:
    
    1. Analyze transaction data for anomalies
    2. Identify potential structuring (smurfing) patterns
    3. Detect unusual transaction velocities
    4. Flag transactions with high-risk jurisdictions
    5. Identify round-number transactions that may indicate laundering
    
    Always provide detailed reasoning for your findings and assign risk scores (1-10).
    Be thorough but avoid false positives by considering legitimate business patterns."""
    
    def __init__(self):
        self.llm = get_llm()
        self.tools = self._create_tools()
        self.agent = create_base_agent(self.llm, self.tools, self.SYSTEM_PROMPT)
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the forensic agent."""
        return [
            Tool(
                name="analyze_transaction_pattern",
                func=self._analyze_transaction_pattern,
                description="Analyze a single transaction for suspicious patterns. Input: JSON string of transaction data."
            ),
            Tool(
                name="detect_structuring",
                func=self._detect_structuring,
                description="Detect potential structuring/smurfing patterns across multiple transactions. Input: JSON array of transactions."
            ),
            Tool(
                name="check_velocity",
                func=self._check_velocity,
                description="Check transaction velocity for a given account. Input: JSON with account_id and transactions."
            ),
        ]
    
    def _analyze_transaction_pattern(self, transaction_json: str) -> str:
        """Analyze a single transaction for suspicious patterns."""
        try:
            transaction = json.loads(transaction_json)
            findings = []
            risk_score = 0
            
            amount = transaction.get("amount", 0)
            
            # Check for round numbers (potential structuring indicator)
            if amount > 1000 and amount % 1000 == 0:
                findings.append(f"Round number transaction: ${amount}")
                risk_score += 2
            
            # Check for amounts just below reporting thresholds
            if 9000 <= amount < 10000:
                findings.append(f"Amount just below $10,000 reporting threshold: ${amount}")
                risk_score += 4
            
            # Check for high-value transactions
            if amount > 50000:
                findings.append(f"High-value transaction: ${amount}")
                risk_score += 3
            
            return json.dumps({
                "transaction_id": transaction.get("id"),
                "findings": findings,
                "risk_score": min(risk_score, 10),
                "requires_review": risk_score >= 5
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _detect_structuring(self, transactions_json: str) -> str:
        """Detect potential structuring patterns."""
        try:
            transactions = json.loads(transactions_json)
            findings = []
            
            # Group transactions by account
            account_totals = {}
            for txn in transactions:
                account = txn.get("account_id")
                amount = txn.get("amount", 0)
                if account not in account_totals:
                    account_totals[account] = []
                account_totals[account].append(amount)
            
            # Check for structuring patterns
            for account, amounts in account_totals.items():
                if len(amounts) >= 3:
                    # Multiple transactions that together exceed threshold
                    total = sum(amounts)
                    if total > 10000 and all(a < 10000 for a in amounts):
                        findings.append({
                            "account": account,
                            "pattern": "Potential structuring",
                            "total": total,
                            "transaction_count": len(amounts),
                            "risk_score": 8
                        })
            
            return json.dumps({"structuring_findings": findings})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _check_velocity(self, input_json: str) -> str:
        """Check transaction velocity for suspicious activity."""
        try:
            data = json.loads(input_json)
            account_id = data.get("account_id")
            transactions = data.get("transactions", [])
            
            # Calculate velocity metrics
            total_transactions = len(transactions)
            total_amount = sum(t.get("amount", 0) for t in transactions)
            
            findings = {
                "account_id": account_id,
                "transaction_count": total_transactions,
                "total_amount": total_amount,
                "velocity_risk": "HIGH" if total_transactions > 10 else "NORMAL"
            }
            
            return json.dumps(findings)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def analyze(self, transactions: List[Dict]) -> Dict:
        """Run forensic analysis on transactions."""
        input_text = f"""Analyze these transactions for suspicious patterns:
        {json.dumps(transactions, indent=2)}
        
        Provide a comprehensive forensic analysis including:
        1. Individual transaction risk assessment
        2. Structuring pattern detection
        3. Velocity analysis
        4. Overall risk summary"""
        
        result = self.agent.invoke({"input": input_text})
        return result
