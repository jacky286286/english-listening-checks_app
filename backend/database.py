import os
import sqlite3
from pathlib import Path

# 優先讀取環境變數 DATA_DIR，無設定時預設為 backend 同層目錄（相容本機非容器執行）
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).parent))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "database.db"

def get_db_connection():
    """取得資料庫連線並啟用 Row 字典格式存取"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """建立資料表、索引，並自動校準舊有的 UTC 紀錄為台灣時間 (UTC+8)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS toeic_error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                part TEXT NOT NULL CHECK(part IN ('Part 1', 'Part 2', 'Part 3', 'Part 4')),
                context_info TEXT NOT NULL,
                error_type TEXT NOT NULL CHECK(error_type IN ('A', 'B', 'C')),
                obstacle_point TEXT NOT NULL,
                correction_fix TEXT NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_type ON toeic_error_logs(error_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_part ON toeic_error_logs(part);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON toeic_error_logs(created_at);")

        cursor.execute("""
            UPDATE toeic_error_logs
            SET created_at = datetime(created_at, '+8 hours') || ' (UTC+8)'
            WHERE created_at NOT LIKE '%(UTC+8)%' AND length(created_at) = 19;
        """)

        conn.commit()