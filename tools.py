import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from crewai.tools import tool
from langchain_community.document_loaders import PyPDFLoader

## Creating search tool
search_tool = SerperDevTool()


# =========================
# Financial Document Reader
# =========================

@tool("Read Financial Document")
def read_data_tool(path: str = "data/sample.pdf") -> str:
    """
    Reads a financial PDF document and returns cleaned text.
    """

    loader = PyPDFLoader(file_path=path)
    docs = loader.load()

    full_report = []
    char_count = 0
    max_chars = 8000

    for doc in docs:
        content = doc.page_content
        content = " ".join(content.split())

        if char_count + len(content) > max_chars:
            remaining = max_chars - char_count
            full_report.append(content[:remaining])
            break

        full_report.append(content)
        char_count += len(content)

    return "\n".join(full_report)


# =========================
# Investment Analysis Tool
# =========================

class InvestmentTool:

    @tool("Investment Analysis")
    def analyze_investment_tool(financial_document_data: str) -> str:
        """
        Analyze financial data and provide investment insights.
        """

        cleaned_data = " ".join(financial_document_data.split())

        # Placeholder logic
        return f"Investment analysis based on provided document:\n{cleaned_data[:1000]}"


# =========================
# Risk Assessment Tool
# =========================

class RiskTool:

    @tool("Risk Assessment")
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        """
        Analyze financial risks from document.
        """

        return "Risk assessment functionality to be implemented based on financial indicators."