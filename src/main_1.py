
from fastapi import FastAPI, UploadFile, File, Request 
from fastapi.middleware.cors import CORSMiddleware
from typing import List 

from starlette.responses import JSONResponse


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # set specific origins in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app 

app = create_app()


# @app.post("/upload")
# async def upload_files(files:List[UploadFile] = File(...)):
#     try:
#         print("REACHED HSERE ")
#         return {"message": "Files Sucessfully processed and stored."}
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})



#####
#D:\AI_PROJECTS\agentic-trading-bot-project>
# uvicorn src/main:app --host 0.0.0.0 --port 8000 --reload