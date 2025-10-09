import json, random

def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_question():
    questions = load_questions()
    word, answer = random.choice(list(questions.items()))

    # เอาตัวเลือกอื่นที่ไม่ใช่คำตอบ
    other_choices = [val for val in questions.values() if val != answer]

    # สุ่มตัวเลือก 3 ตัวจากตัวเลือกอื่น
    choices = random.sample(other_choices, 3)

    # ใส่คำตอบลงไป
    choices.append(answer)

    # สุ่มตำแหน่งคำตอบ
    random.shuffle(choices)

    return word, answer, choices

# ตัวอย่างใช้งาน
if __name__ == "__main__":
    word, answer, choices = get_question()
    print("Question:", word)
    print("Choices:", choices)
    print("Answer:", answer)
