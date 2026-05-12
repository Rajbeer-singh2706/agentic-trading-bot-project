
from fastapi import FastAPI, UploadFile, File, Request 
from fastapi.middleware.cors import CORSMiddleware
from typing import List 
from starlette.responses import JSONResponse

### 
from ingestion.ingestion_pipeline import DataIngestion

# this should be your graph stream handler
from agents.workflow import GraphBuilder  
from utils.mylogger import setup_logger
from data_models.models import QuestionRequest

logger = setup_logger(__name__)


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

@app.post("/upload")
async def upload_files(files:List[UploadFile] = File(...)):
    try:
        logger.info("REACHED HERE ")
        ingestion = DataIngestion()
        status = ingestion.run_pipeline(files)
        return {"message": status}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/query")
async def query_chatbot(request: QuestionRequest):
    try:
        graph_service = GraphBuilder()
        graph_service.build()
        
        ### Get the trading bot graph
        trading_bot_graph = graph_service.get_graph()

        # Assuming request is a pydantic object like: {"question": "your text"}
        messages={"messages": [request.question]}

        ## Invoke the Agents
        result = trading_bot_graph.invoke(messages)

        # If result is dict with messages:
        if isinstance(result, dict) and "messages" in result:
            final_output = result["messages"][-1].content  # Last AI response
        else:
            final_output = str(result)
        
        return {"answer": final_output}

    except Exception as e:
         return JSONResponse(status_code=500, content={"error": str(e)})