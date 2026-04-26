from fastapi import FastAPI, Request, HTTPException
import requests
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")


def get_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="No token")
    return auth_header.replace("Bearer ", "")


@app.get("/assets/current")
async def get_assets(request: Request):
    token = get_token(request)

    # Viewを取得
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/current_assets",
        headers={
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {token}",
        }
    )
    
    print(res.text)

    data = res.json()[0]  # 1レコードだけ返る想定

    total = data["total_assets"]
    total_prev = data["total_prev"]
    total_jan = data["total_jan"]

    # 差分
    diff_from_last_month = total - total_prev
    diff_from_jan = total - total_jan

    # 割合
    for u in data["users"]:
        user_total = u["total"]

        u["ratio"] = user_total / total if total else 0
        u["cash_ratio"] = u["cash"] / user_total if user_total else 0
        u["investment_ratio"] = u["investment"] / user_total if user_total else 0

    return {
        "counted_at": data["counted_at"],
        "total_assets": total,
        "diff_from_last_month": diff_from_last_month,
        "diff_from_jan": diff_from_jan,
        "users": data["users"]
    }