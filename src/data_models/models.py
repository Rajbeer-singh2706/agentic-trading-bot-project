
from pydantic import BaseModel


class RagToolSchema(BaseModel):
    queston: str 

class QuestionRequest(BaseModel):
    question: str