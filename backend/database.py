import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "toeic_review.db"

def get_db_connection():
    """取得資料庫連線並啟用 Row 字典格式存取"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """建立多益聽力錯題檢討資料表及查詢索引"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS toeic_error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                part TEXT NOT NULL CHECK(part IN ('Part 1', 'Part 2', 'Part 3', 'Part 4')),
                context_info TEXT NOT NULL,
                error_type TEXT NOT NULL CHECK(error_type IN ('A', 'B', 'C')),
                obstacle_point TEXT NOT NULL,
                correction_fix TEXT NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_type ON toeic_error_logs(error_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_part ON toeic_error_logs(part);")
        conn.commit()