from pydantic import BaseModel, Field
from typing import Literal

class ErrorLogCreate(BaseModel):
    part: Literal["Part 1", "Part 2", "Part 3", "Part 4"] = Field(..., description="多益聽力題型")
    context_info: str = Field(..., min_length=1, max_length=100, description="題號與情境描述（上限100字）")
    error_type: Literal["A", "B", "C"] = Field(..., description="錯誤類型：A 聲音盲點 / B 轉譯延遲 / C 節奏失誤")
    obstacle_point: str = Field(..., min_length=1, max_length=300, description="聽力阻礙點（上限300字）")
    correction_fix: str = Field(..., min_length=1, max_length=300, description="正確替換字詞（上限300字）")

class ErrorLogResponse(ErrorLogCreate):
    id: int
    created_at: str