import pytest
from unittest.mock import Mock, patch
import json


class TestForensicAgent:
    """Tests for the Forensic Agent."""
    
    @patch('agents.forensic_agent.get_llm')
    def test_analyze_transaction_pattern_round_number(self, mock_llm):
        """Test detection of round number transactions."""
        from agents.forensic_agent import ForensicAgent
        
        mock_llm.return_value = Mock()
        agent = ForensicAgent()
        
        transaction = {"id": "TXN001", "amount": 10000}
        result = json.loads(agent._analyze_transaction_pattern(json.dumps(transaction)))
        
        assert result["risk_score"] > 0
        assert "round number" in str(result["findings"]).lower() or result["risk_score"] >= 2
    
    @patch('agents.forensic_agent.get_llm')
    def test_analyze_transaction_pattern_threshold(self, mock_llm):
        """Test detection of amounts near reporting threshold."""
        from agents.forensic_agent import ForensicAgent
        
        mock_llm.return_value = Mock()
        agent = ForensicAgent()
        
        transaction = {"id": "TXN001", "amount": 9500}
        result = json.loads(agent._analyze_transaction_pattern(json.dumps(transaction)))
        
        assert result["risk_score"] >= 4
        assert result["requires_review"] == True
    
    @patch('agents.forensic_agent.get_llm')
    def test_detect_structuring(self, mock_llm):
        """Test detection of structuring patterns."""
        from agents.forensic_agent import ForensicAgent
        
        mock_llm.return_value = Mock()
        agent = ForensicAgent()
        
        transactions = [
            {"account_id": "ACC001", "amount": 9000},
            {"account_id": "ACC001", "amount": 8500},
            {"account_id": "ACC001", "amount": 9500},
        ]
        
        result = json.loads(agent._detect_structuring(json.dumps(transactions)))
        
        assert "structuring_findings" in result
        assert len(result["structuring_findings"]) > 0


class TestLegalAgent:
    """Tests for the Legal Agent."""
    
    @patch('agents.legal_agent.get_llm')
    def test_check_sanctions_match(self, mock_llm):
        """Test sanctions checking with known entity."""
        from agents.legal_agent import LegalAgent
        
        mock_llm.return_value = Mock()
        agent = LegalAgent()
        
        result = json.loads(agent._check_sanctions("ACME Shell Corporation"))
        
        assert result["match_found"] == True
        assert result["list"] == "OFAC SDN"
    
    @patch('agents.legal_agent.get_llm')
    def test_check_sanctions_no_match(self, mock_llm):
        """Test sanctions checking with clean entity."""
        from agents.legal_agent import LegalAgent
        
        mock_llm.return_value = Mock()
        agent = LegalAgent()
        
        result = json.loads(agent._check_sanctions("Legitimate Business Inc"))
        
        assert result["match_found"] == False
    
    @patch('agents.legal_agent.get_llm')
    def test_check_jurisdiction_risk_high(self, mock_llm):
        """Test high-risk jurisdiction detection."""
        from agents.legal_agent import LegalAgent
        
        mock_llm.return_value = Mock()
        agent = LegalAgent()
        
        result = json.loads(agent._check_jurisdiction_risk("Iran"))
        
        assert result["risk_level"] == "HIGH"
    
    @patch('agents.legal_agent.get_llm')
    def test_check_jurisdiction_risk_low(self, mock_llm):
        """Test low-risk jurisdiction detection."""
        from agents.legal_agent import LegalAgent
        
        mock_llm.return_value = Mock()
        agent = LegalAgent()
        
        result = json.loads(agent._check_jurisdiction_risk("United States"))
        
        assert result["risk_level"] == "LOW"
    
    @patch('agents.legal_agent.get_llm')
    def test_determine_reporting_requirements_ctr(self, mock_llm):
        """Test CTR requirement determination."""
        from agents.legal_agent import LegalAgent
        
        mock_llm.return_value = Mock()
        agent = LegalAgent()
        
        transaction = {"id": "TXN001", "amount": 15000, "type": "cash_deposit"}
        result = json.loads(agent._determine_reporting_requirements(json.dumps(transaction)))
        
        assert result["requires_action"] == True
        assert any(r["report_type"] == "CTR" for r in result["reporting_requirements"])


class TestReportAgent:
    """Tests for the Report Agent."""
    
    @patch('agents.report_agent.get_llm')
    def test_generate_audit_trail(self, mock_llm):
        """Test audit trail generation."""
        from agents.report_agent import ReportAgent
        
        mock_llm.return_value = Mock()
        agent = ReportAgent()
        
        event = {
            "type": "ANALYSIS",
            "action": "Transaction analyzed",
            "result": "HIGH_RISK"
        }
        
        result = json.loads(agent._generate_audit_trail(json.dumps(event)))
        
        assert "timestamp" in result
        assert result["event_type"] == "ANALYSIS"
    
    @patch('agents.report_agent.get_llm')
    def test_create_risk_summary(self, mock_llm):
        """Test risk summary creation."""
        from agents.report_agent import ReportAgent
        
        mock_llm.return_value = Mock()
        agent = ReportAgent()
        
        findings = {
            "transaction_count": 10,
            "high_risk_count": 2,
            "medium_risk_count": 3,
            "low_risk_count": 5,
            "risk_scores": [8, 7, 5, 4, 3, 2, 2, 1, 1, 1]
        }
        
        result = json.loads(agent._create_risk_summary(json.dumps(findings)))
        
        assert result["total_transactions_analyzed"] == 10
        assert result["high_risk_count"] == 2
        assert "overall_risk_level" in result
    
    @patch('agents.report_agent.get_llm')
    def test_generate_report_hash(self, mock_llm):
        """Test report hash generation."""
        from agents.report_agent import ReportAgent
        
        mock_llm.return_value = Mock()
        agent = ReportAgent()
        
        content = "Test report content"
        result = json.loads(agent._generate_report_hash(content))
        
        assert result["hash_algorithm"] == "SHA-256"
        assert len(result["hash_value"]) == 64  # SHA-256 produces 64 hex characters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
