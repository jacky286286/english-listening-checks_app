from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from .database import get_db_connection, init_db
from .models import ErrorLogCreate, ErrorLogResponse

# 初始化資料庫與執行舊時區資料校準
init_db()

app = FastAPI(title="TOEIC Listening Review System")

# 定義台灣時區 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/logs", response_model=ErrorLogResponse, status_code=201)
def create_error_log(payload: ErrorLogCreate):
    """新增單筆錯題紀錄（強制以台灣時間 UTC+8 生成時間字串）"""
    taiwan_now = datetime.now(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO toeic_error_logs (created_at, part, context_info, error_type, obstacle_point, correction_fix)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (taiwan_now, payload.part, payload.context_info, payload.error_type, payload.obstacle_point, payload.correction_fix)
        )
        conn.commit()
        log_id = cursor.lastrowid
        row = cursor.execute("SELECT * FROM toeic_error_logs WHERE id = ?", (log_id,)).fetchone()
        return dict(row)

@app.get("/api/logs", response_model=List[ErrorLogResponse])
def get_all_error_logs(
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)")
):
    """取得檢討紀錄，以台灣日期的前 10 碼字串比對範圍，預設依 ID 降冪排列"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        sql = "SELECT * FROM toeic_error_logs WHERE 1=1"
        params = []

        if start_date:
            sql += " AND substr(created_at, 1, 10) >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND substr(created_at, 1, 10) <= ?"
            params.append(end_date)

        sql += " ORDER BY id DESC"
        rows = cursor.execute(sql, tuple(params)).fetchall()
        return [dict(row) for row in rows]

@app.delete("/api/logs/{log_id}", status_code=200)
def delete_error_log(log_id: int):
    """刪除指定 ID 的檢討紀錄"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM toeic_error_logs WHERE id = ?", (log_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="紀錄不存在")
        return {"status": "success", "deleted_id": log_id}

# 掛載前端靜態目錄
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")