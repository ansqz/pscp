# dev_dryrun_simple.py
# ใช้ทดสอบเกมแบบออฟไลน์ (ไม่ต้องเชื่อม Discord จริง)
# โปรแกรมนี้จำลองการเล่น 1 รอบ (5 คำ) พร้อมระบบให้คะแนนและแสดงอันดับ

import asyncio
import json
import random

# นำเข้าฟังก์ชันที่ใช้จากไฟล์อื่น
from ques_choices.question_manager import get_question, load_questions
from score_manager.score_manager import add_score, read_file, save
from Leaderboard_system.leaderboard import show_leaderboard


# ------------------------------
# สร้างช่องปลอมไว้ใช้ทดสอบแทน Discord
# ------------------------------
class FakeChannel:
    async def send(self, content=None, embed=None):
        """จำลองการส่งข้อความ"""
        if embed:  # ถ้าเป็น embed (ตารางคะแนน)
            print("\n===== LEADERBOARD =====")
            print(embed.description)
        elif content:
            print("\n[MSG]", content)


# ------------------------------
# ฟังก์ชันช่วยตรวจคำถาม
# ------------------------------
def check_questions():
    """ตรวจว่ามีคำถามในไฟล์ questions.json หรือไม่"""
    data = load_questions()
    if not data or not isinstance(data, dict):
        print("❌ ไม่มีข้อมูลคำถาม หรือรูปแบบไม่ถูกต้อง")
        exit()
    print(f"✅ Loaded {len(data)} questions.")
    return data


# ------------------------------
# ฟังก์ชันให้คะแนน
# ------------------------------
def give_points(correct_choice, answers):
    """
    ให้คะแนนกับคนที่ตอบถูก
    - คนที่ตอบถูก 3 คนแรกได้ 5, 4, 3 คะแนน
    - คนอื่นที่ตอบถูกได้ 1 คะแนน
    - คนตอบซ้ำไม่นับ
    """
    seen = set()
    correct_users = []

    for uid, choice in answers:
        if uid in seen:
            continue
        seen.add(uid)
        if choice == correct_choice:
            correct_users.append(uid)

    if not correct_users:
        return []

    scores = [5, 4, 3] + [1] * (len(correct_users) - 3)
    result = list(zip(correct_users, scores))

    for uid, s in result:
        add_score(uid, s)

    return result


# ------------------------------
# ฟังก์ชันทดสอบเล่น 1 รอบ (5 คำ)
# ------------------------------
async def run_offline_test():
    """จำลองการเล่น 1 รอบแบบออฟไลน์"""
    ch = FakeChannel()
    save({})  # ล้างคะแนนเก่า
    check_questions()  # ตรวจคำถาม

    print("=== เริ่มเกมรอบออฟไลน์ ===")
    users = [1111, 2222, 3333, 4444, 5555]

    for i in range(5):
        word, answer, choices = get_question()
        print(f"\nคำที่ {i+1}: '{word}' แปลว่าอะไร?")
        for n, c in enumerate(choices, start=1):
            print(f"  {n}. {c}")

        # คำตอบที่ถูกคือหมายเลขไหน
        try:
            correct = choices.index(answer) + 1
        except ValueError:
            print("⚠️ ข้อมูลผิดข้ามข้อนี้")
            continue

        print(f"(เฉลยคือ {correct}: {answer})")

        # จำลองผู้เล่นตอบ
        random.shuffle(users)
        answers = []

        # 3 คนแรกตอบถูก
        for uid in users[:3]:
            answers.append((uid, correct))
        # 2 คนหลังสุ่มตอบ
        for uid in users[3:]:
            answers.append((uid, random.randint(1, 4)))

        # ใส่คำตอบซ้ำของคนแรก (ไม่นับ)
        answers.append((users[0], correct))

        # ให้คะแนน
        result = give_points(correct, answers)
        if result:
            print("ให้คะแนน:", ", ".join([f"{uid}+{pts}" for uid, pts in result]))
        else:
            print("ไม่มีใครตอบถูก")

    # แสดงคะแนนทั้งหมด
    print("\n=== คะแนนทั้งหมด ===")
    print(json.dumps(read_file(), ensure_ascii=False, indent=2))

    # แสดง leaderboard จำลอง
    await show_leaderboard(ch, top_n=10)
    print("\n=== จบรอบออฟไลน์ ===")


# ------------------------------
# เริ่มโปรแกรม
# ------------------------------
if __name__ == "__main__":
    asyncio.run(run_offline_test())
