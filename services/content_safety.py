from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from azure.core.credentials import AzureKeyCredential
import os
import json
from typing import Dict, List


class ContentSafetyService:
    """
    Azure Content Safety integration for bias detection in KYT decisions.
    Ensures responsible AI practices by checking for potential biases.
    """
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
        self.key = os.getenv("AZURE_CONTENT_SAFETY_KEY")
        
        if self.endpoint and self.key:
            self.client = ContentSafetyClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.key)
            )
        else:
            self.client = None
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for content safety issues.
        Checks for hate speech, self-harm, sexual content, and violence.
        """
        if not self.client:
            return self._mock_analyze(text)
        
        try:
            request = AnalyzeTextOptions(text=text)
            response = self.client.analyze_text(request)
            
            results = {
                "analyzed_text_length": len(text),
                "categories": {}
            }
            
            for category in response.categories_analysis:
                results["categories"][category.category] = {
                    "severity": category.severity
                }
            
            results["is_safe"] = all(
                cat["severity"] == 0 for cat in results["categories"].values()
            )
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def _mock_analyze(self, text: str) -> Dict:
        """Mock analysis for demo purposes."""
        return {
            "analyzed_text_length": len(text),
            "categories": {
                "Hate": {"severity": 0},
                "SelfHarm": {"severity": 0},
                "Sexual": {"severity": 0},
                "Violence": {"severity": 0}
            },
            "is_safe": True,
            "note": "Mock analysis - Azure Content Safety not configured"
        }
    
    def check_decision_bias(self, decision_data: Dict) -> Dict:
        """
        Check a KYT decision for potential bias indicators.
        Analyzes the decision reasoning for fairness concerns.
        """
        # Extract relevant text from decision
        decision_text = json.dumps(decision_data)
        
        # Analyze the decision text
        safety_result = self.analyze_text(decision_text)
        
        # Additional bias checks specific to KYT
        bias_indicators = self._check_kyt_bias_indicators(decision_data)
        
        return {
            "content_safety": safety_result,
            "bias_indicators": bias_indicators,
            "overall_assessment": self._get_overall_bias_assessment(safety_result, bias_indicators)
        }
    
    def _check_kyt_bias_indicators(self, decision_data: Dict) -> List[Dict]:
        """Check for KYT-specific bias indicators."""
        indicators = []
        
        # Check for over-reliance on demographic factors
        demographic_fields = ["nationality", "country_of_origin", "ethnicity", "religion"]
        reasoning = decision_data.get("reasoning", "").lower()
        
        for field in demographic_fields:
            if field in reasoning:
                indicators.append({
                    "type": "demographic_factor",
                    "field": field,
                    "severity": "medium",
                    "recommendation": f"Review use of {field} in decision reasoning for potential bias"
                })
        
        # Check for name-based bias indicators
        if "name" in reasoning and any(term in reasoning for term in ["foreign", "unusual", "suspicious name"]):
            indicators.append({
                "type": "name_bias",
                "severity": "high",
                "recommendation": "Review name-based reasoning for potential ethnic/cultural bias"
            })
        
        # Check for balanced risk scoring
        risk_score = decision_data.get("risk_score", 0)
        if risk_score > 8 and not decision_data.get("sanctions_match"):
            indicators.append({
                "type": "high_risk_no_match",
                "severity": "low",
                "recommendation": "Verify high risk score is justified by concrete findings, not assumptions"
            })
        
        return indicators
    
    def _get_overall_bias_assessment(self, safety_result: Dict, bias_indicators: List[Dict]) -> Dict:
        """Generate overall bias assessment."""
        high_severity_count = sum(1 for i in bias_indicators if i.get("severity") == "high")
        medium_severity_count = sum(1 for i in bias_indicators if i.get("severity") == "medium")
        
        if high_severity_count > 0:
            status = "REVIEW_REQUIRED"
            message = "High severity bias indicators detected - manual review required"
        elif medium_severity_count > 1:
            status = "CAUTION"
            message = "Multiple medium severity bias indicators - consider review"
        elif not safety_result.get("is_safe", True):
            status = "CONTENT_SAFETY_ISSUE"
            message = "Content safety concerns detected"
        else:
            status = "PASSED"
            message = "No significant bias indicators detected"
        
        return {
            "status": status,
            "message": message,
            "high_severity_count": high_severity_count,
            "medium_severity_count": medium_severity_count,
            "recommendations": [i.get("recommendation") for i in bias_indicators if i.get("recommendation")]
        }
    
    def generate_responsible_ai_report(self, decisions: List[Dict]) -> Dict:
        """
        Generate a Responsible AI report for a batch of decisions.
        Summarizes bias checks and provides recommendations.
        """
        all_checks = []
        
        for decision in decisions:
            check_result = self.check_decision_bias(decision)
            all_checks.append(check_result)
        
        # Aggregate results
        total_reviewed = len(all_checks)
        passed = sum(1 for c in all_checks if c["overall_assessment"]["status"] == "PASSED")
        review_required = sum(1 for c in all_checks if c["overall_assessment"]["status"] == "REVIEW_REQUIRED")
        caution = sum(1 for c in all_checks if c["overall_assessment"]["status"] == "CAUTION")
        
        return {
            "report_type": "Responsible AI Assessment",
            "total_decisions_reviewed": total_reviewed,
            "summary": {
                "passed": passed,
                "review_required": review_required,
                "caution": caution,
                "pass_rate": round(passed / total_reviewed * 100, 2) if total_reviewed > 0 else 0
            },
            "detailed_checks": all_checks,
            "recommendations": self._aggregate_recommendations(all_checks)
        }
    
    def _aggregate_recommendations(self, checks: List[Dict]) -> List[str]:
        """Aggregate unique recommendations from all checks."""
        all_recommendations = set()
        for check in checks:
            for rec in check["overall_assessment"].get("recommendations", []):
                all_recommendations.add(rec)
        return list(all_recommendations)
