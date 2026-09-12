import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "database.db"

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

        # 自動校準：將資料庫中未標註 (UTC+8) 的舊 UTC 紀錄加上 8 小時並標記，確保歷史資料一致
        cursor.execute("""
            UPDATE toeic_error_logs
            SET created_at = datetime(created_at, '+8 hours') || ' (UTC+8)'
            WHERE created_at NOT LIKE '%(UTC+8)%' AND length(created_at) = 19;
        """)

        conn.commit()