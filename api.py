from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from nl2sql import ask_database
import pandas as pd
import json

app = FastAPI(title="Chat with Structured Data API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str | None = None
    data: list[dict] | None = None
    columns: list[str] | None = None
    error: str | None = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required.")
        
    sql, df, error = ask_database(request.question)
    
    if error:
        return QueryResponse(sql=sql, error=error)
        
    if df is not None:
        # Convert DataFrame to list of dicts for JSON serialization
        # handle nan/nat by replacing with None
        df = df.where(pd.notnull(df), None)
        data = df.to_dict(orient="records")
        columns = df.columns.tolist()
        return QueryResponse(sql=sql, data=data, columns=columns)
    
    return QueryResponse(sql=sql)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
