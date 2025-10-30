# score_manager/score_manager.py
from pathlib import Path
import json
from typing import Dict

SCORES_FILE = Path(__file__).resolve().parent / "scores.json"

def read_file() -> Dict[str, int]:
    """อ่านคะแนนทั้งหมดจาก scores.json"""
    if not SCORES_FILE.exists():
        return {}
    try:
        return json.loads(SCORES_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}

def save(scores: Dict[str, int]) -> None:
    """บันทึกคะแนนกลับไปที่ไฟล์"""
    SCORES_FILE.write_text(
        json.dumps(scores, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def add_score(user, score: int) -> int:
    """
    บวกคะแนนให้ผู้ใช้ (user ควรเป็น user_id จาก Discord)
    คืนค่าคะแนนรวมของผู้ใช้นั้นหลังอัปเดต
    """
    scores = read_file()
    key = str(user)
    scores[key] = scores.get(key, 0) + int(score)
    save(scores)
    return scores[key]
