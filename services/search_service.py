from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
import os
from typing import List, Dict
import json


class SanctionsSearcher:
    """
    Azure AI Search integration for sanctions list searching.
    Provides fuzzy matching against OFAC SDN and other sanctions lists.
    """
    
    INDEX_NAME = "sanctions-index"
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.credential = AzureKeyCredential(self.key) if self.key else None
        
        if self.endpoint and self.credential:
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.INDEX_NAME,
                credential=self.credential
            )
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=self.credential
            )
        else:
            self.search_client = None
            self.index_client = None
    
    def create_index(self):
        """Create the sanctions search index if it doesn't exist."""
        if not self.index_client:
            return {"error": "Search client not initialized"}
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="name", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="aliases", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            SimpleField(name="entity_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="sanctions_list", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="country", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="date_added", type=SearchFieldDataType.DateTimeOffset),
            SearchableField(name="details", type=SearchFieldDataType.String),
        ]
        
        index = SearchIndex(name=self.INDEX_NAME, fields=fields)
        
        try:
            self.index_client.create_or_update_index(index)
            return {"status": "success", "message": f"Index '{self.INDEX_NAME}' created/updated"}
        except Exception as e:
            return {"error": str(e)}
    
    def upload_sanctions_data(self, sanctions_data: List[Dict]):
        """Upload sanctions data to the search index."""
        if not self.search_client:
            return {"error": "Search client not initialized"}
        
        try:
            result = self.search_client.upload_documents(documents=sanctions_data)
            return {"status": "success", "uploaded": len(sanctions_data)}
        except Exception as e:
            return {"error": str(e)}
    
    def search(self, query: str, top: int = 5) -> List[Dict]:
        """Search sanctions list for matching entities."""
        if not self.search_client:
            # Return mock data for demo if not connected
            return self._mock_search(query)
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True,
                query_type="full",
                search_mode="any"
            )
            
            matches = []
            for result in results:
                matches.append({
                    "id": result.get("id"),
                    "name": result.get("name"),
                    "aliases": result.get("aliases", []),
                    "sanctions_list": result.get("sanctions_list"),
                    "country": result.get("country"),
                    "score": result.get("@search.score", 0),
                    "match_type": "EXACT" if result.get("@search.score", 0) > 10 else "FUZZY"
                })
            
            return matches
        except Exception as e:
            print(f"Sanctions search error for '{query}': {e}")
            return []
    
    def _mock_search(self, query: str) -> List[Dict]:
        """Mock search for demo purposes."""
        # Sample sanctions entries for demo
        mock_sanctions = [
            {
                "id": "SDN-001",
                "name": "ACME Shell Corporation",
                "aliases": ["ACME Holdings", "ACME LLC"],
                "sanctions_list": "OFAC SDN",
                "country": "Unknown",
                "score": 0.95
            },
            {
                "id": "SDN-002",
                "name": "Offshore Trust Ltd",
                "aliases": ["OT Limited", "Offshore Holdings"],
                "sanctions_list": "OFAC SDN",
                "country": "Cayman Islands",
                "score": 0.88
            }
        ]
        
        query_lower = query.lower()
        matches = [s for s in mock_sanctions if query_lower in s["name"].lower() or 
                   any(query_lower in a.lower() for a in s.get("aliases", []))]
        
        return matches


class PolicySearcher:
    """
    Azure AI Search integration for compliance policy document searching.
    Enables retrieval of relevant policies based on transaction context.
    """
    
    INDEX_NAME = "policies-index"
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.credential = AzureKeyCredential(self.key) if self.key else None
        
        if self.endpoint and self.credential:
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.INDEX_NAME,
                credential=self.credential
            )
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=self.credential
            )
        else:
            self.search_client = None
            self.index_client = None
    
    def create_index(self):
        """Create the policy search index if it doesn't exist."""
        if not self.index_client:
            return {"error": "Search client not initialized"}
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="regulation", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="effective_date", type=SearchFieldDataType.DateTimeOffset),
            SearchableField(name="keywords", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
        ]
        
        index = SearchIndex(name=self.INDEX_NAME, fields=fields)
        
        try:
            self.index_client.create_or_update_index(index)
            return {"status": "success", "message": f"Index '{self.INDEX_NAME}' created/updated"}
        except Exception as e:
            return {"error": str(e)}
    
    def search(self, query: str, category: str = None, top: int = 5) -> List[Dict]:
        """Search for relevant compliance policies."""
        if not self.search_client:
            return self._mock_search(query)
        
        try:
            filter_expr = f"category eq '{category}'" if category else None
            
            results = self.search_client.search(
                search_text=query,
                filter=filter_expr,
                top=top,
                include_total_count=True
            )
            
            policies = []
            for result in results:
                policies.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "content": result.get("content"),
                    "category": result.get("category"),
                    "regulation": result.get("regulation"),
                    "relevance_score": result.get("@search.score", 0)
                })
            
            return policies
        except Exception as e:
            return [{"error": str(e)}]
    
    def _mock_search(self, query: str) -> List[Dict]:
        """Mock search for demo purposes."""
        mock_policies = [
            {
                "id": "POL-001",
                "title": "Currency Transaction Report (CTR) Requirements",
                "content": "Financial institutions must file a CTR for each deposit, withdrawal, exchange of currency, or other payment or transfer that involves a transaction in currency of more than $10,000.",
                "category": "BSA",
                "regulation": "31 CFR 1010.311",
                "relevance_score": 0.95
            },
            {
                "id": "POL-002",
                "title": "Suspicious Activity Report (SAR) Requirements",
                "content": "Banks must report any suspicious transaction relevant to a possible violation of law or regulation. This includes any transaction conducted or attempted that involves funds derived from illegal activities.",
                "category": "BSA",
                "regulation": "31 CFR 1020.320",
                "relevance_score": 0.90
            },
            {
                "id": "POL-003",
                "title": "Enhanced Due Diligence (EDD) Requirements",
                "content": "Enhanced due diligence is required for high-risk customers, including PEPs, customers from high-risk jurisdictions, and those with complex ownership structures.",
                "category": "AML",
                "regulation": "31 CFR 1010.610",
                "relevance_score": 0.85
            }
        ]
        
        query_lower = query.lower()
        matches = [p for p in mock_policies if query_lower in p["title"].lower() or 
                   query_lower in p["content"].lower()]
        
        return matches if matches else mock_policies[:2]
