from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from celery.result import AsyncResult
from tasks_queue import analyze_document_task

app = FastAPI(title="Financial Document Analyzer", debug=True)

# Allow the HTML page to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
    )


@app.get("/")
async def root():
    """Serve the UI"""
    return FileResponse("index.html")


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
):
    if not query or not query.strip():
        query = "Analyze this financial document for investment insights"

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    os.makedirs("data", exist_ok=True)

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        with open(file_path, "wb") as f:
            f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    task = analyze_document_task.delay(query=query.strip(), file_path=file_path)

    return {
        "job_id": task.id,
        "status": "QUEUED",
        "message": "Document queued for analysis.",
        "file_received": file.filename,
    }


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    result = AsyncResult(job_id)
    state = result.state

    if state == "PENDING":
        return {"job_id": job_id, "status": "PENDING", "message": "Waiting in queue..."}
    if state == "STARTED":
        return {"job_id": job_id, "status": "STARTED", "message": "Analysis in progress...", "meta": result.info}
    if state == "SUCCESS":
        return {"job_id": job_id, "status": "SUCCESS", "result": result.get()}
    if state == "FAILURE":
        return {"job_id": job_id, "status": "FAILURE", "error": str(result.info)}

    return {"job_id": job_id, "status": state, "meta": str(result.info)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)