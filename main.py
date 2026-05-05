

from fastapi import FastAPI, UploadFile, File , Request 

@app.post("/upload")
async def upload_files(files: List[UploadFile]):
    try:
        ingestion = DataIngestion()
        ingestion.run_pipeline(files)
    except Exception as e:
        return ""