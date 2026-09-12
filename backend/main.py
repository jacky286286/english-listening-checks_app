from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List

from .database import get_db_connection, init_db
from .models import ErrorLogCreate, ErrorLogResponse

# 初始化資料庫
init_db()

app = FastAPI(title="TOEIC Listening Review System")

# 跨域請求支援（允許前端獨立啟動）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/logs", response_model=ErrorLogResponse, status_code=201)
def create_error_log(payload: ErrorLogCreate):
    """新增單筆錯題檢討紀錄"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO toeic_error_logs (part, context_info, error_type, obstacle_point, correction_fix)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.part, payload.context_info, payload.error_type, payload.obstacle_point, payload.correction_fix)
        )
        conn.commit()
        log_id = cursor.lastrowid

        row = cursor.execute("SELECT * FROM toeic_error_logs WHERE id = ?", (log_id,)).fetchone()
        return dict(row)

@app.get("/api/logs", response_model=List[ErrorLogResponse])
def get_all_error_logs():
    """取得所有檢討紀錄（以最新時間降冪排列）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM toeic_error_logs ORDER BY id DESC").fetchall()
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

# 掛載前端靜態檔案目錄
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")