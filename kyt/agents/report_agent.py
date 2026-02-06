from langchain_core.tools import Tool
from .base_agent import get_llm, create_base_agent
from datetime import datetime
from typing import Dict, List
import json
import hashlib


class ReportAgent:
    """
    Report Agent for generating audit trails and compliance reports.
    Creates comprehensive, auditable documentation of analysis results.
    """
    
    SYSTEM_PROMPT = """You are a compliance report generation AI agent specialized in 
    creating audit-ready documentation. Your role is to:
    
    1. Generate comprehensive audit reports
    2. Create clear, timestamped audit trails
    3. Document all decision rationale
    4. Produce executive summaries
    5. Format reports for regulatory submission
    
    Always ensure reports are:
    - Complete and accurate
    - Properly timestamped
    - Include all evidence and reasoning
    - Follow regulatory formatting requirements
    - Ready for examiner review"""
    
    def __init__(self, blob_storage_client=None):
        self.llm = get_llm()
        self.blob_storage_client = blob_storage_client
        self.tools = self._create_tools()
        self.agent = create_base_agent(self.llm, self.tools, self.SYSTEM_PROMPT)
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the report agent."""
        return [
            Tool(
                name="generate_audit_trail",
                func=self._generate_audit_trail,
                description="Generate a timestamped audit trail entry. Input: JSON with event details."
            ),
            Tool(
                name="create_risk_summary",
                func=self._create_risk_summary,
                description="Create a risk summary from analysis results. Input: JSON with findings."
            ),
            Tool(
                name="format_regulatory_report",
                func=self._format_regulatory_report,
                description="Format findings into a regulatory-compliant report. Input: JSON with all findings."
            ),
            Tool(
                name="generate_report_hash",
                func=self._generate_report_hash,
                description="Generate a tamper-evident hash for the report. Input: report content string."
            ),
        ]
    
    def _generate_audit_trail(self, event_json: str) -> str:
        """Generate a timestamped audit trail entry."""
        try:
            event = json.loads(event_json)
            
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event.get("type", "ANALYSIS"),
                "event_id": event.get("id", f"EVT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
                "actor": event.get("actor", "KYT_SYSTEM"),
                "action": event.get("action", ""),
                "details": event.get("details", {}),
                "result": event.get("result", ""),
                "evidence": event.get("evidence", [])
            }
            
            return json.dumps(audit_entry, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _create_risk_summary(self, findings_json: str) -> str:
        """Create a risk summary from analysis results."""
        try:
            findings = json.loads(findings_json)
            
            # Calculate aggregate risk metrics
            risk_scores = findings.get("risk_scores", [])
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            summary = {
                "summary_date": datetime.utcnow().isoformat() + "Z",
                "total_transactions_analyzed": findings.get("transaction_count", 0),
                "high_risk_count": findings.get("high_risk_count", 0),
                "medium_risk_count": findings.get("medium_risk_count", 0),
                "low_risk_count": findings.get("low_risk_count", 0),
                "average_risk_score": round(avg_risk, 2),
                "overall_risk_level": self._determine_overall_risk(avg_risk),
                "key_findings": findings.get("key_findings", []),
                "recommended_actions": findings.get("recommended_actions", []),
                "sanctions_matches": findings.get("sanctions_matches", 0),
                "reporting_required": findings.get("reporting_required", False)
            }
            
            return json.dumps(summary, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _determine_overall_risk(self, avg_risk: float) -> str:
        """Determine overall risk level from average score."""
        if avg_risk >= 7:
            return "HIGH"
        elif avg_risk >= 4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _format_regulatory_report(self, findings_json: str) -> str:
        """Format findings into a regulatory-compliant report."""
        try:
            findings = json.loads(findings_json)
            
            report = {
                "report_metadata": {
                    "report_id": f"KYT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "report_type": "KYT_AUDIT_REPORT",
                    "version": "1.0"
                },
                "executive_summary": {
                    "period_covered": findings.get("period", "N/A"),
                    "total_transactions": findings.get("transaction_count", 0),
                    "alerts_generated": findings.get("alert_count", 0),
                    "escalations_required": findings.get("escalations", 0)
                },
                "forensic_analysis": findings.get("forensic_results", {}),
                "compliance_evaluation": findings.get("compliance_results", {}),
                "risk_assessment": {
                    "overall_risk": findings.get("overall_risk", "PENDING"),
                    "risk_factors": findings.get("risk_factors", [])
                },
                "recommendations": findings.get("recommendations", []),
                "appendix": {
                    "audit_trail": findings.get("audit_trail", []),
                    "evidence_references": findings.get("evidence", [])
                }
            }
            
            return json.dumps(report, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _generate_report_hash(self, content: str) -> str:
        """Generate a tamper-evident hash for the report."""
        report_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return json.dumps({
            "hash_algorithm": "SHA-256",
            "hash_value": report_hash,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "purpose": "Tamper-evident verification"
        })
    
    def generate_report(self, forensic_results: Dict, compliance_results: Dict, 
                       transactions: List[Dict]) -> Dict:
        """Generate a comprehensive audit report."""
        input_text = f"""Generate a comprehensive KYT audit report based on:
        
        Forensic Analysis Results:
        {json.dumps(forensic_results, indent=2)}
        
        Compliance Evaluation Results:
        {json.dumps(compliance_results, indent=2)}
        
        Transactions Analyzed:
        {json.dumps(transactions, indent=2)}
        
        Create a complete audit report including:
        1. Executive summary
        2. Detailed findings
        3. Risk assessment
        4. Regulatory compliance status
        5. Recommended actions
        6. Full audit trail
        7. Report hash for verification"""
        
        result = self.agent.invoke({"input": input_text})
        return result
