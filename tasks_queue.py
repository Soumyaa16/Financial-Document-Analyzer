import os
from dotenv import load_dotenv
load_dotenv()

from celery_worker import celery_app
from crewai import Crew, Process


@celery_app.task(
    bind=True,
    name="tasks_queue.analyze_document_task",
    max_retries=2,
    default_retry_delay=15,
)
def analyze_document_task(self, query: str, file_path: str) -> dict:
    """
    Runs the CrewAI financial analysis pipeline in a background worker.
    Imported here (not at module level) to avoid circular imports and
    so each worker process loads agents fresh with its own LLM client.
    """
    try:
        # Import here so agents/tasks are loaded inside the worker process
        from agents import financial_analyst
        from task import analyze_financial_document as financial_analysis_task

        self.update_state(
            state="STARTED",
            meta={"message": "CrewAI pipeline started", "file": os.path.basename(file_path)},
        )

        financial_crew = Crew(
            agents=[financial_analyst],
            tasks=[financial_analysis_task],
            process=Process.sequential,
        )

        result = financial_crew.kickoff({"query": query, "file_path": file_path})

        return {
            "status": "success",
            "query": query,
            "analysis": str(result),
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=15)

    finally:
        # Clean up uploaded file after worker is done
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
