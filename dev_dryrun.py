# dev_dryrun.py — Offline integration test (no real Discord connection)
# ใช้ทดสอบร่วม: ques_choices.question_manager + score_manager + leaderboard

import asyncio
import json
import random
from typing import List, Tuple

from ques_choices.question_manager import get_question, load_questions
from score_manager.score_manager import add_score, read_file, save
from Leaderboard_system.leaderboard import show_leaderboard


# ---------- Fake Discord TextChannel ----------
class FakeChannel:
    async def send(self, content=None, embed=None):
        if embed:
            print("\n[EMBED]")
            print("title:", embed.title)
            print("desc:\n", embed.description)
        elif content is not None:
            print("\n[MSG]", content)


# ---------- Helpers ----------
def validate_questions():
    """ตรวจโครง questions.json แบบเบา ๆ"""
    data = load_questions()
    if not isinstance(data, dict) or not data:
        raise ValueError("questions.json ต้องเป็น dict และไม่ว่าง")
    uniq = len(set(map(str.strip, data.values())))
    if uniq < 4:
        raise ValueError(
            f"คำแปลไม่ซ้ำมี {uniq} รายการ (< 4) อาจสุ่มช้อยส์ 4 ตัวไม่ได้ทุกข้อ"
        )
    return data


def evaluate_and_award(correct_index: int, answers: List[Tuple[int, int]]):
    """นับเฉพาะคำตอบแรกของแต่ละ user; ให้คะแนน 5,4,3 แล้วที่เหลือ 1"""
    seen = set()
    correct_order = []
    for uid, choice in answers:
        if uid in seen:
            continue
        seen.add(uid)
        if choice == correct_index:
            correct_order.append(uid)

    if not correct_order:
        return []

    plan = [5, 4, 3] + [1] * max(0, len(correct_order) - 3)
    awarded = list(zip(correct_order, plan))
    for uid, pts in awarded:
        add_score(uid, pts)
    return awarded


# ---------- One offline round (5 questions) ----------
async def run_offline_round():
    ch = FakeChannel()

    # เริ่มเทสต์: เคลียร์คะแนนให้สะอาดตา
    save({})

    # ตรวจโครงคำถาม
    validate_questions()

    print("=== OFFLINE ROUND START (5 คำ) ===")
    # จำลอง user id 5 คน
    users = [1111, 2222, 3333, 4444, 5555]

    for i in range(5):
        word, answer, choices = get_question()

        try:
            correct_index = choices.index(answer) + 1
        except ValueError:
            print(f"[WARN] ข้อ {i+1}: answer ไม่อยู่ใน choices — ข้าม")
            continue

        print(f"\nQ{i+1}: What is '{word}' in Thai?")
        for n, c in enumerate(choices, 1):
            print(f"  {n}. {c}")
        print(f"(correct #{correct_index}: {answer})")

        # จำลองลำดับการตอบ: สุ่มผู้ใช้/สุ่มตัวเลือก (แต่ให้บางคนตอบถูกแน่ ๆ)
        random.shuffle(users)
        script: List[Tuple[int, int]] = []

        # ให้ 3 คนแรกตอบถูกตามลำดับ (ทดสอบการให้ 5,4,3 คะแนน)
        for uid in users[:3]:
            script.append((uid, correct_index))

        # คนที่เหลือสุ่มตอบ อาจถูก/ผิดก็ได้
        for uid in users[3:]:
            choice = random.randint(1, 4)
            script.append((uid, choice))

        # ใส่คำตอบซ้ำของคนแรก (ต้องไม่นับ)
        script.append((users[0], correct_index))

        awarded = evaluate_and_award(correct_index, script)
        if awarded:
            print("Awarded:", ", ".join([f"{uid}+{pts}" for uid, pts in awarded]))
        else:
            print("No one correct.")

    print("\n=== SCORES AFTER ROUND ===")
    print(json.dumps(read_file(), ensure_ascii=False, indent=2))

    # แสดง Leaderboard ผ่าน FakeChannel (ใช้โค้ดจริง)
    await show_leaderboard(ch, top_n=10)
    print("\n=== OFFLINE ROUND END ===")


if __name__ == "__main__":
    asyncio.run(run_offline_round())
