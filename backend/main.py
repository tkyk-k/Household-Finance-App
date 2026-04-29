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

    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/current_assets",
        headers={
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {token}",
        }
    )

    data_json = res.json()

    if not data_json:
        raise HTTPException(status_code=404, detail="No data")

    data = data_json[0]

    total_assets = data["total_assets"]
    total_prev = data["total_prev"]
    total_jan = data["total_jan"]

    # 差分
    diff_from_last_month = total_assets - total_prev
    diff_from_jan = total_assets - total_jan

    # 全体割合
    total_cash = data["total_cash"]
    total_investment = data["total_investment"]

    cash_ratio = total_cash / total_assets if total_assets else 0
    investment_ratio = total_investment / total_assets if total_assets else 0

    # ユーザー割合
    users = data["users"]
    for u in users:
        user_total = u["total"]
        u["ratio"] = user_total / total_assets if total_assets else 0

    return {
        "counted_at": data["counted_at"],
        "total_assets": total_assets,

        # 差分
        "diff_from_last_month": diff_from_last_month,
        "diff_from_jan": diff_from_jan,

        # 内訳
        "total_cash": total_cash,
        "total_investment": total_investment,

        # 割合
        "cash_ratio": cash_ratio,
        "investment_ratio": investment_ratio,

        # ユーザー
        "users": users
    }