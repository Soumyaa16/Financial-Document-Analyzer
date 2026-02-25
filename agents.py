## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()


from crewai import Agent, LLM

from tools import search_tool, read_data_tool

### Loading LLM
llm = LLM(
    model="groq/llama-3.1-8b-instant",   # or gemini if you use it
    temperature=0.1,
    api_key=os.getenv("GROQ_API_KEY")
)

# Creating an Experienced Financial Analyst agent
financial_analyst=Agent(
    role="Senior Financial Analyst Who Knows Everything About Markets",
    goal="Analyze the provided financial document and extract accurate financial insights for the query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced financial analyst with deep expertise in financial statements, "
        "ratio analysis, and corporate performance evaluation. "
        "You always rely strictly on the provided documents and avoid speculation."
    ),
    tools=[read_data_tool],
    llm=llm,
    max_iter=3,
    max_rpm=1,
    allow_delegation=True  # Allow delegation to other specialists
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify whether the uploaded file is a valid financial document and ensure extracted data is accurate.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a financial compliance expert responsible for validating financial documents "
        "and ensuring accuracy before analysis."
    ),
    llm=llm,
    max_iter=2,
    max_rpm=1,
    allow_delegation=True
)


investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide investment recommendations based strictly on analyzed financial data and risk profile.",
    verbose=True,
    backstory=(
        "You are a certified investment advisor who provides responsible and data-driven recommendations "
        "based on financial analysis and market fundamentals."
    ),
    llm=llm,
    max_iter=2,
    max_rpm=1,
    allow_delegation=False
)


risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Evaluate financial risks present in the document and provide realistic risk insights.",
    verbose=True,
    backstory=(
        "You specialize in financial risk analysis including liquidity risk, credit risk, "
        "market volatility, and operational risk."
    ),
    llm=llm,
    max_iter=2,
    max_rpm=1,
    allow_delegation=False
)
