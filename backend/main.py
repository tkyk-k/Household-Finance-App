from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

class Expense(BaseModel):
    amount: int
    memo: str
    date: str


# トークン取得
def get_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="No token")
    return auth_header.replace("Bearer ", "")


@app.post("/expenses")
async def create_expense(expense: Expense, request: Request):
    token = get_token(request)

    data = expense.dict()

    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/expenses",
        json=data,
        headers={
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    return {
        "status_code": res.status_code,
        "text": res.text
    }