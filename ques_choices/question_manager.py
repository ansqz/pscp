# ques_choices/question_manager.py
from pathlib import Path
import json, random
from typing import Tuple, List

# รากโปรเจกต์
ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = ROOT / "ques_choices" / "questions.json"

def load_questions() -> dict:
    """โหลดไฟล์ questions.json (รูปแบบคีย์=คำอังกฤษ, ค่า=คำแปลไทย)"""
    return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))

def get_question() -> Tuple[str, str, List[str]]:
    """
    สุ่มคำถาม 1 ข้อ
    return: (word, answer, choices[4])
    """
    questions = load_questions()
    word, answer = random.choice(list(questions.items()))

    # ตัวเลือกอื่น ๆ ที่ไม่ใช่คำตอบ
    other_choices = [val for val in questions.values() if val != answer]
    # กรณีคลังคำไม่พอ 3 ตัวเลือก ให้สุ่มจากที่มี (กันพัง)
    pick = min(3, len(other_choices))
    choices = random.sample(other_choices, pick)
    while len(choices) < 3:
        choices.append(answer)  # ถ้าคำไม่พอ เติมด้วยคำตอบเพื่อกัน error (จะถูก shuffle)

    choices.append(answer)
    random.shuffle(choices)
    return word, answer, choices
