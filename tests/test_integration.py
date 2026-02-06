import pytest
from unittest.mock import Mock, patch
import json


class TestKYTOrchestrator:
    """Integration tests for the KYT Orchestrator."""
    
    @patch('orchestrator.kyt_orchestrator.ForensicAgent')
    @patch('orchestrator.kyt_orchestrator.LegalAgent')
    @patch('orchestrator.kyt_orchestrator.ReportAgent')
    def test_orchestrator_initialization(self, mock_report, mock_legal, mock_forensic):
        """Test orchestrator initializes all agents."""
        from orchestrator.kyt_orchestrator import KYTOrchestrator
        
        orchestrator = KYTOrchestrator()
        
        assert orchestrator.forensic_agent is not None
        assert orchestrator.legal_agent is not None
        assert orchestrator.report_agent is not None
    
    @patch('orchestrator.kyt_orchestrator.ForensicAgent')
    @patch('orchestrator.kyt_orchestrator.LegalAgent')
    @patch('orchestrator.kyt_orchestrator.ReportAgent')
    def test_extract_entities(self, mock_report, mock_legal, mock_forensic):
        """Test entity extraction from transactions."""
        from orchestrator.kyt_orchestrator import KYTOrchestrator
        
        orchestrator = KYTOrchestrator()
        
        transactions = [
            {"sender_name": "John Doe", "receiver_name": "ACME Corp"},
            {"sender_name": "Jane Smith", "counterparty": "XYZ Ltd"},
        ]
        
        entities = orchestrator._extract_entities(transactions)
        
        assert "John Doe" in entities
        assert "ACME Corp" in entities
        assert "Jane Smith" in entities
        assert "XYZ Ltd" in entities
    
    @patch('orchestrator.kyt_orchestrator.ForensicAgent')
    @patch('orchestrator.kyt_orchestrator.LegalAgent')
    @patch('orchestrator.kyt_orchestrator.ReportAgent')
    def test_extract_high_risk(self, mock_report, mock_legal, mock_forensic):
        """Test high-risk transaction extraction."""
        from orchestrator.kyt_orchestrator import KYTOrchestrator
        
        orchestrator = KYTOrchestrator()
        
        transactions = [
            {"id": "TXN001", "amount": 9500, "country": "US"},
            {"id": "TXN002", "amount": 5000, "country": "US"},
            {"id": "TXN003", "amount": 50000, "country": "Iran"},
        ]
        
        high_risk = orchestrator._extract_high_risk(transactions)
        
        # TXN001 should be flagged for being near threshold
        # TXN003 should be flagged for high-risk jurisdiction
        assert len(high_risk) >= 2
    
    @patch('orchestrator.kyt_orchestrator.ForensicAgent')
    @patch('orchestrator.kyt_orchestrator.LegalAgent')
    @patch('orchestrator.kyt_orchestrator.ReportAgent')
    def test_detect_patterns_structuring(self, mock_report, mock_legal, mock_forensic):
        """Test structuring pattern detection."""
        from orchestrator.kyt_orchestrator import KYTOrchestrator
        
        orchestrator = KYTOrchestrator()
        
        # Structuring pattern: multiple transactions under $10k totaling over $10k
        transactions = [
            {"id": "TXN001", "account_id": "ACC001", "amount": 9000},
            {"id": "TXN002", "account_id": "ACC001", "amount": 8500},
            {"id": "TXN003", "account_id": "ACC001", "amount": 9500},
        ]
        
        patterns = orchestrator._detect_patterns(transactions)
        
        assert len(patterns) > 0
        assert patterns[0]["type"] == "POTENTIAL_STRUCTURING"


class TestContentSafetyService:
    """Tests for the Content Safety Service."""
    
    def test_mock_analyze(self):
        """Test mock analysis when Azure not configured."""
        from services.content_safety import ContentSafetyService
        
        service = ContentSafetyService()
        result = service._mock_analyze("Test text for analysis")
        
        assert result["is_safe"] == True
        assert "categories" in result
    
    def test_check_decision_bias_clean(self):
        """Test bias check with clean decision."""
        from services.content_safety import ContentSafetyService
        
        service = ContentSafetyService()
        
        decision = {
            "decision_type": "RISK_ASSESSMENT",
            "risk_score": 5,
            "reasoning": "Multiple transactions below threshold detected"
        }
        
        result = service.check_decision_bias(decision)
        
        assert result["overall_assessment"]["status"] == "PASSED"
    
    def test_check_decision_bias_demographic(self):
        """Test bias check with demographic indicators."""
        from services.content_safety import ContentSafetyService
        
        service = ContentSafetyService()
        
        decision = {
            "decision_type": "RISK_ASSESSMENT",
            "risk_score": 8,
            "reasoning": "Flagged due to nationality and country of origin"
        }
        
        result = service.check_decision_bias(decision)
        
        assert len(result["bias_indicators"]) > 0


class TestSearchService:
    """Tests for the Search Services."""
    
    def test_sanctions_mock_search(self):
        """Test sanctions mock search."""
        from services.search_service import SanctionsSearcher
        
        searcher = SanctionsSearcher()
        results = searcher._mock_search("ACME")
        
        assert len(results) > 0
        assert results[0]["name"] == "ACME Shell Corporation"
    
    def test_policy_mock_search(self):
        """Test policy mock search."""
        from services.search_service import PolicySearcher
        
        searcher = PolicySearcher()
        results = searcher._mock_search("CTR")
        
        assert len(results) > 0
        assert "CTR" in results[0]["title"]


class TestEndToEnd:
    """End-to-end integration tests."""
    
    @patch('agents.base_agent.get_llm')
    def test_full_analysis_flow(self, mock_llm):
        """Test complete analysis flow with mocked LLM."""
        # Mock the LLM to return a simple response
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = Mock(content="Analysis complete")
        mock_llm.return_value = mock_llm_instance
        
        from orchestrator.kyt_orchestrator import KYTOrchestrator
        
        orchestrator = KYTOrchestrator()
        
        transactions = [
            {
                "id": "TXN001",
                "account_id": "ACC001",
                "amount": 9500,
                "sender_name": "Test User",
                "receiver_name": "Test Corp",
                "country": "US"
            }
        ]
        
        # The actual test would run the full flow
        # For unit testing, we test individual components
        entities = orchestrator._extract_entities(transactions)
        assert "Test User" in entities
        assert "Test Corp" in entities
        
        high_risk = orchestrator._extract_high_risk(transactions)
        assert len(high_risk) > 0  # Should flag near-threshold amount


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
