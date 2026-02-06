# 🔍 Autonomous KYT Auditor

## Overview
An AI-powered compliance tool that identifies suspicious patterns in real-time transactions using a multi-agent architecture.

## Features
- **Multi-Agent Architecture**: Three specialized AI agents (Forensic, Legal, Report)
- **Real-time Analysis**: Analyze transactions for suspicious patterns
- **Sanctions Screening**: Check entities against OFAC and other sanctions lists
- **Responsible AI**: Built-in bias detection using Azure Content Safety
- **Audit Trail**: Complete documentation for regulatory compliance

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Streamlit Web App                          │
├─────────────────────────────────────────────────────────────────────┤
│                      LangChain Orchestrator                         │
├──────────────────┬──────────────────┬──────────────────────────────┤
│  Forensic Agent  │   Legal Agent    │       Report Agent           │
│  (Pattern Det.)  │  (Compliance)    │    (Audit Trails)            │
├──────────────────┴──────────────────┴──────────────────────────────┤
│                    Azure OpenAI Service                             │
├─────────────────────────────────────────────────────────────────────┤
│  Azure AI Search  │  Azure Content Safety  │  Azure Blob Storage    │
│  (Sanctions/Docs) │  (Bias Detection)      │  (Audit Logs)          │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.9+
- Azure subscription with:
  - Azure OpenAI Service (GPT-4 deployment)
  - Azure AI Search
  - Azure Content Safety
  - Azure Blob Storage (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kyt-auditor
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

5. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
kyt-auditor/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # This file
│
├── agents/                   # AI Agents
│   ├── __init__.py
│   ├── base_agent.py         # Base agent configuration
│   ├── forensic_agent.py     # Pattern detection agent
│   ├── legal_agent.py        # Compliance evaluation agent
│   └── report_agent.py       # Audit report generation agent
│
├── services/                 # Azure Services Integration
│   ├── __init__.py
│   ├── search_service.py     # Azure AI Search integration
│   └── content_safety.py     # Azure Content Safety integration
│
├── orchestrator/             # Agent Orchestration
│   ├── __init__.py
│   └── kyt_orchestrator.py   # Main orchestrator
│
├── data/                     # Sample Data
│   ├── sample_sanctions.py   # Sample sanctions list
│   ├── sample_policies.py    # Sample compliance policies
│   └── sample_transactions.csv
│
├── tests/                    # Unit Tests
│   ├── test_agents.py
│   └── test_integration.py
│
└── docs/                     # Documentation
    └── demo_script.md
```

## Usage

### 1. Load Transactions
Upload a CSV file or use the sample data provided.

### 2. Run Analysis
Click "Run KYT Analysis" to start the multi-agent analysis.

### 3. Review Results
- **Forensic Analysis**: View detected patterns and high-risk transactions
- **Compliance**: Check sanctions matches and regulatory requirements
- **Responsible AI**: Review bias assessment results
- **Audit Report**: Download the complete audit trail

## API Reference

### KYTOrchestrator

```python
from orchestrator.kyt_orchestrator import KYTOrchestrator

orchestrator = KYTOrchestrator()
results = orchestrator.analyze_transactions(transactions)
```

### Agents

```python
from agents import ForensicAgent, LegalAgent, ReportAgent

# Forensic Agent
forensic = ForensicAgent()
forensic_results = forensic.analyze(transactions)

# Legal Agent  
legal = LegalAgent()
compliance_results = legal.evaluate(transactions, entities)

# Report Agent
report = ReportAgent()
audit_report = report.generate_report(forensic_results, compliance_results, transactions)
```

## License
MIT License

## Acknowledgments
- Azure OpenAI Service
- LangChain Framework
- Streamlit

