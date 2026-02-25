## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier
from tools import search_tool, read_data_tool

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description=(
        "Analyze the financial document located at {file_path} "
        "and answer the user's query: {query}.\n\n"

        "Steps:\n"
        "1. Read the document using the provided tool.\n"
        "2. Extract key financial metrics such as revenue, profit, expenses, growth trends, and risks.\n"
        "3. Provide clear financial insights based only on the document.\n"
        "4. Do NOT make assumptions outside the document.\n"
        "5. Present findings in a structured format."
    ),

    expected_output=(
        "A structured financial analysis including:\n"
        "- Company performance summary\n"
        "- Key financial metrics\n"
        "- Growth trends\n"
        "- Risks identified\n"
        "- Investment insights based on data\n"
    ),

    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description=(
        "Based on the financial document at {file_path}, "
        "provide investment recommendations for the user query: {query}.\n\n"

        "Focus on:\n"
        "- Financial health\n"
        "- Profitability\n"
        "- Risk level\n"
        "- Growth potential\n"
    ),

    expected_output=(
        "Investment recommendations including:\n"
        "- Buy / Hold / Avoid suggestion\n"
        "- Reasoning based on financial metrics\n"
        "- Risk considerations\n"
    ),

    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description=(
        "Evaluate financial risks present in the document located at {file_path}.\n"
        "Answer user query: {query}.\n\n"

        "Identify:\n"
        "- Liquidity risks\n"
        "- Market risks\n"
        "- Operational risks\n"
        "- Financial stability concerns\n"
    ),

    expected_output=(
        "Risk assessment report including:\n"
        "- Key risks identified\n"
        "- Severity level\n"
        "- Potential impact\n"
        "- Mitigation insights\n"
    ),

    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)

    
verification = Task(
    description="""
    Verify whether the provided file at {file_path} is a valid financial document.

    Steps:
    1. Use the read_data_tool to read the file content.
    2. Determine if the document contains financial information such as:
       - Revenue
       - Expenses
       - Profit/Loss
       - Financial statements
       - Company performance metrics
    3. If valid, summarize what type of document it is (earnings report, balance sheet, etc.)
    4. If not valid, clearly state why.
    """,

    expected_output="""
    A structured validation result:
    - Is this a financial document? (Yes/No)
    - Document type
    - Key financial indicators found
    - Short summary
    """,

    agent=verifier,
    tools=[read_data_tool],
    async_execution=False,
)