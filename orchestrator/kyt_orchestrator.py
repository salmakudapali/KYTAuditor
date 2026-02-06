from agents.forensic_agent import ForensicAgent
from agents.legal_agent import LegalAgent
from agents.report_agent import ReportAgent
from services.search_service import SanctionsSearcher, PolicySearcher
from services.content_safety import ContentSafetyService
from typing import Dict, List
from datetime import datetime
import json


class KYTOrchestrator:
    """
    Main orchestrator for the KYT Auditor system.
    Coordinates the three specialized agents and services.
    """
    
    def __init__(self):
        # Initialize services
        self.sanctions_searcher = SanctionsSearcher()
        self.policy_searcher = PolicySearcher()
        self.content_safety = ContentSafetyService()
        
        # Initialize agents
        self.forensic_agent = ForensicAgent()
        self.legal_agent = LegalAgent(
            sanctions_searcher=self.sanctions_searcher,
            policy_searcher=self.policy_searcher
        )
        self.report_agent = ReportAgent()
        
        # Analysis state
        self.current_analysis = None
        self.analysis_history = []
    
    def analyze_transactions(self, transactions: List[Dict], 
                            callback=None) -> Dict:
        """
        Main entry point for transaction analysis.
        Orchestrates all three agents in sequence.
        
        Args:
            transactions: List of transaction dictionaries to analyze
            callback: Optional callback function for progress updates
            
        Returns:
            Complete analysis results including all agent outputs
        """
        analysis_id = f"KYT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        self.current_analysis = {
            "id": analysis_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "IN_PROGRESS",
            "transactions_count": len(transactions),
            "stages": {}
        }
        
        try:
            # Stage 1: Forensic Analysis
            if callback:
                callback("Starting forensic analysis...", 0.1)
            
            forensic_results = self._run_forensic_analysis(transactions)
            self.current_analysis["stages"]["forensic"] = {
                "status": "COMPLETED",
                "results": forensic_results
            }
            
            if callback:
                callback("Forensic analysis complete", 0.35)
            
            # Stage 2: Legal/Compliance Evaluation
            if callback:
                callback("Starting compliance evaluation...", 0.4)
            
            # Extract entities for sanctions checking
            entities = self._extract_entities(transactions)
            compliance_results = self._run_compliance_evaluation(transactions, entities)
            self.current_analysis["stages"]["compliance"] = {
                "status": "COMPLETED",
                "results": compliance_results
            }
            
            if callback:
                callback("Compliance evaluation complete", 0.65)
            
            # Stage 3: Content Safety / Bias Check
            if callback:
                callback("Running responsible AI checks...", 0.7)
            
            decisions = self._prepare_decisions_for_bias_check(
                forensic_results, compliance_results
            )
            bias_check_results = self.content_safety.generate_responsible_ai_report(decisions)
            self.current_analysis["stages"]["bias_check"] = {
                "status": "COMPLETED",
                "results": bias_check_results
            }
            
            if callback:
                callback("Responsible AI checks complete", 0.8)
            
            # Stage 4: Report Generation
            if callback:
                callback("Generating audit report...", 0.85)
            
            report_results = self._generate_report(
                forensic_results, compliance_results, transactions
            )
            self.current_analysis["stages"]["report"] = {
                "status": "COMPLETED",
                "results": report_results
            }
            
            if callback:
                callback("Report generation complete", 0.95)
            
            # Finalize analysis
            self.current_analysis["status"] = "COMPLETED"
            self.current_analysis["completed_at"] = datetime.utcnow().isoformat()
            
            # Store in history
            self.analysis_history.append(self.current_analysis.copy())
            
            if callback:
                callback("Analysis complete!", 1.0)
            
            return self._compile_final_results()
            
        except Exception as e:
            self.current_analysis["status"] = "FAILED"
            self.current_analysis["error"] = str(e)
            raise
    
    def _run_forensic_analysis(self, transactions: List[Dict]) -> Dict:
        """Run the forensic agent analysis."""
        try:
            result = self.forensic_agent.analyze(transactions)
            return {
                "raw_output": result.get("output", ""),
                "high_risk_transactions": self._extract_high_risk(transactions),
                "patterns_detected": self._detect_patterns(transactions)
            }
        except Exception as e:
            return {"error": str(e), "high_risk_transactions": [], "patterns_detected": []}
    
    def _run_compliance_evaluation(self, transactions: List[Dict], 
                                   entities: List[str]) -> Dict:
        """Run the legal/compliance agent evaluation."""
        try:
            result = self.legal_agent.evaluate(transactions, entities)
            
            # Run sanctions checks
            sanctions_matches = []
            for entity in entities:
                matches = self.sanctions_searcher.search(entity)
                if matches:
                    # Filter out error entries and results without a name
                    valid_matches = [m for m in matches if "error" not in m and m.get("name")]
                    sanctions_matches.extend(valid_matches)
            
            return {
                "raw_output": result.get("output", ""),
                "sanctions_matches": sanctions_matches,
                "compliance_status": "REVIEW_NEEDED" if sanctions_matches else "PASSED"
            }
        except Exception as e:
            return {"error": str(e), "sanctions_matches": [], "compliance_status": "ERROR"}
    
    def _generate_report(self, forensic_results: Dict, 
                        compliance_results: Dict,
                        transactions: List[Dict]) -> Dict:
        """Generate the final audit report."""
        try:
            result = self.report_agent.generate_report(
                forensic_results, compliance_results, transactions
            )
            return {
                "raw_output": result.get("output", ""),
                "report_id": self.current_analysis["id"]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_entities(self, transactions: List[Dict]) -> List[str]:
        """Extract entity names from transactions for sanctions checking."""
        entities = set()
        for txn in transactions:
            if "sender_name" in txn:
                entities.add(txn["sender_name"])
            if "receiver_name" in txn:
                entities.add(txn["receiver_name"])
            if "counterparty" in txn:
                entities.add(txn["counterparty"])
            if "beneficiary" in txn:
                entities.add(txn["beneficiary"])
        return list(entities)
    
    def _extract_high_risk(self, transactions: List[Dict]) -> List[Dict]:
        """Extract high-risk transactions based on simple heuristics."""
        high_risk = []
        for txn in transactions:
            risk_score = 0
            reasons = []
            
            amount = txn.get("amount", 0)
            
            # Check amount thresholds
            if amount >= 10000:
                risk_score += 3
                reasons.append("Amount >= $10,000")
            elif 9000 <= amount < 10000:
                risk_score += 5
                reasons.append("Amount just below $10,000 threshold")
            
            # Check for round numbers
            if amount > 1000 and amount % 1000 == 0:
                risk_score += 2
                reasons.append("Round number amount")
            
            # Check jurisdiction
            country = txn.get("country", "").lower()
            high_risk_countries = ["iran", "north korea", "syria", "russia"]
            if any(c in country for c in high_risk_countries):
                risk_score += 5
                reasons.append(f"High-risk jurisdiction: {country}")
            
            if risk_score >= 5:
                high_risk.append({
                    **txn,
                    "risk_score": min(risk_score, 10),
                    "risk_reasons": reasons
                })
        
        return high_risk
    
    def _detect_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """Detect suspicious patterns across transactions."""
        patterns = []
        
        # Group by account
        account_transactions = {}
        for txn in transactions:
            account = txn.get("account_id", "unknown")
            if account not in account_transactions:
                account_transactions[account] = []
            account_transactions[account].append(txn)
        
        # Check for structuring
        for account, txns in account_transactions.items():
            if len(txns) >= 3:
                amounts = [t.get("amount", 0) for t in txns]
                total = sum(amounts)
                if total > 10000 and all(a < 10000 for a in amounts):
                    patterns.append({
                        "type": "POTENTIAL_STRUCTURING",
                        "account": account,
                        "transaction_count": len(txns),
                        "total_amount": total,
                        "severity": "HIGH"
                    })
        
        return patterns
    
    def _prepare_decisions_for_bias_check(self, forensic_results: Dict,
                                          compliance_results: Dict) -> List[Dict]:
        """Prepare decision data for bias checking."""
        decisions = []
        
        # Add forensic decisions
        for txn in forensic_results.get("high_risk_transactions", []):
            decisions.append({
                "decision_type": "RISK_ASSESSMENT",
                "transaction_id": txn.get("id"),
                "risk_score": txn.get("risk_score", 0),
                "reasoning": ", ".join(txn.get("risk_reasons", [])),
                "sanctions_match": False
            })
        
        # Add compliance decisions
        for match in compliance_results.get("sanctions_matches", []):
            decisions.append({
                "decision_type": "SANCTIONS_MATCH",
                "entity": match.get("name"),
                "match_score": match.get("score", 0),
                "reasoning": f"Matched against {match.get('sanctions_list', 'unknown list')}",
                "sanctions_match": True
            })
        
        return decisions if decisions else [{"decision_type": "NO_ALERTS", "reasoning": "No suspicious activity detected"}]
    
    def _compile_final_results(self) -> Dict:
        """Compile all results into a final output structure."""
        return {
            "analysis_id": self.current_analysis["id"],
            "status": self.current_analysis["status"],
            "started_at": self.current_analysis["started_at"],
            "completed_at": self.current_analysis.get("completed_at"),
            "transactions_analyzed": self.current_analysis["transactions_count"],
            "forensic_analysis": self.current_analysis["stages"].get("forensic", {}).get("results", {}),
            "compliance_evaluation": self.current_analysis["stages"].get("compliance", {}).get("results", {}),
            "responsible_ai": self.current_analysis["stages"].get("bias_check", {}).get("results", {}),
            "audit_report": self.current_analysis["stages"].get("report", {}).get("results", {}),
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict:
        """Generate an executive summary of the analysis."""
        forensic = self.current_analysis["stages"].get("forensic", {}).get("results", {})
        compliance = self.current_analysis["stages"].get("compliance", {}).get("results", {})
        bias = self.current_analysis["stages"].get("bias_check", {}).get("results", {})
        
        high_risk_count = len(forensic.get("high_risk_transactions", []))
        sanctions_count = len(compliance.get("sanctions_matches", []))
        patterns_count = len(forensic.get("patterns_detected", []))
        
        overall_risk = "HIGH" if (sanctions_count > 0 or patterns_count > 0) else \
                       "MEDIUM" if high_risk_count > 0 else "LOW"
        
        return {
            "overall_risk_level": overall_risk,
            "high_risk_transactions": high_risk_count,
            "sanctions_matches": sanctions_count,
            "suspicious_patterns": patterns_count,
            "compliance_status": compliance.get("compliance_status", "UNKNOWN"),
            "responsible_ai_status": bias.get("summary", {}).get("pass_rate", 0),
            "requires_manual_review": overall_risk in ["HIGH", "MEDIUM"]
        }
    
    def get_analysis_history(self) -> List[Dict]:
        """Get the history of all analyses."""
        return self.analysis_history
