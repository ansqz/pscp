# Leaderboard_system/scheduler.py
import os
import asyncio
from typing import List, Tuple

import discord
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# โมดูลในโปรเจกต์
from ques_choices.question_manager import get_question
from score_manager.score_manager import add_score
from Leaderboard_system.leaderboard import show_leaderboard, reset_scores

# โหลด .env (เผื่อ main ยังไม่ได้โหลด)
load_dotenv()
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# ---------- แกนเล่น 1 รอบ (5 คำ) ----------
async def _play_round(bot: discord.Client) -> None:
    """
    เล่น 1 รอบ (5 คำ)
    - โพสต์คำถามละ 1 ข้อ: คำอังกฤษ + ตัวเลือก 4 ตัว
    - เก็บคำตอบภายใน 5 วินาที (ผู้ใช้พิมพ์เลข 1-4)
    - ให้คะแนนตามลำดับผู้ตอบถูก: 5,4,3 และคนถัดไปได้ 1
    - คูลดาวน์ 2 วินาที ระหว่างข้อ
    - จบครบ 5 ข้อ โพสต์ Leaderboard รอบนี้
    """
    ch = bot.get_channel(CHANNEL_ID)
    if ch is None or not isinstance(ch, discord.TextChannel):
        return  # ช่องไม่พร้อมก็จบเงียบ ๆ

    for i in range(5):  # รอบละ 5 ข้อ
        # ใช้ฟังก์ชันของคุณ: ได้ (word, answer, choices[4])
        word, answer, choices = get_question()
        # หา index คำตอบที่ถูก (1-4)
        try:
            correct_index = choices.index(answer) + 1
        except ValueError:
            # ถ้าข้อมูลผิดรูป (answer ไม่อยู่ใน choices) ให้ข้ามข้อ
            await ch.send("⚠️ ข้อมูลคำถามผิดรูปแบบ ข้ามข้อนี้")
            await asyncio.sleep(1)
            continue

        header = f"**คำที่ {i+1}/5**  What is '{word}' in Thai?"
        body = "\n".join(f"{n}. {txt}" for n, txt in enumerate(choices, start=1))
        await ch.send(f"{header}\n{body}\nพิมพ์เลขคำตอบ (1-4) ภายใน **5 วินาที** !")

        # เก็บคำตอบ (user_id, ตัวเลือก)
        answers: List[Tuple[int, int]] = []

        def check(msg: discord.Message) -> bool:
            return (
                msg.channel.id == ch.id
                and msg.content.isdigit()
                and 1 <= int(msg.content) <= 4
            )

        try:
            while True:
                msg = await bot.wait_for("message", check=check, timeout=5)
                answers.append((msg.author.id, int(msg.content)))
        except asyncio.TimeoutError:
            pass  # หมดเวลา

        # นับเฉพาะคำตอบแรกของแต่ละคน แล้วคัดเฉพาะที่ตอบถูก
        seen = set()
        correct_order: List[int] = []
        for uid, choice in answers:
            if uid in seen:
                continue
            seen.add(uid)
            if choice == correct_index:
                correct_order.append(uid)

        # ให้คะแนน: 5,4,3, แล้วที่เหลือได้ 1
        if correct_order:
            plan = [5, 4, 3]
            if len(correct_order) > 3:
                plan += [1] * (len(correct_order) - 3)
            for uid, pts in zip(correct_order, plan):
                add_score(uid, pts)

        await ch.send(f"✅ เฉลย: **{answer}**")
        await asyncio.sleep(2)  # คูลดาวน์ก่อนข้อถัดไป

    # จบรอบ → โชว์ Leaderboard รอบนี้ (Top 10)
    await show_leaderboard(ch, top_n=10)

# ---------- โพสต์ Top10 รายสัปดาห์ ----------
async def _post_weekly(bot: discord.Client) -> None:
    ch = bot.get_channel(CHANNEL_ID)
    if ch and isinstance(ch, discord.TextChannel):
        await ch.send("🗓️ **Top 10 ประจำสัปดาห์**")
        await show_leaderboard(ch, top_n=10)

# ---------- รีเซ็ตคะแนนรายเดือน ----------
async def _post_monthly_reset(bot: discord.Client) -> None:
    ch = bot.get_channel(CHANNEL_ID)
    if ch and isinstance(ch, discord.TextChannel):
        await reset_scores(ch)

# ---------- จุดเริ่ม Scheduler ----------
def schedule_tasks(
    bot: discord.Client,
    timezone_str: str = "Asia/Bangkok",
    debug: bool = False,
) -> AsyncIOScheduler:
    """
    ตั้งตารางอัตโนมัติ:
      - เริ่มเกมทุก 20 นาที (ถ้า debug=True จะเหลือทุก 1 นาที)
      - โพสต์ Top10 ทุกวันอาทิตย์ 12:00
      - รีเซ็ตคะแนนทุกวันที่ 1 เวลา 00:05
    """
    interval_min = 1 if debug else 20

    sch = AsyncIOScheduler(timezone=timezone_str)
    # กันงานทับกัน: max_instances=1 และ coalesce=True
    sch.add_job(
        lambda: asyncio.create_task(_play_round(bot)),
        IntervalTrigger(minutes=interval_min),
        id="round_every_interval",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    sch.add_job(
        lambda: asyncio.create_task(_post_weekly(bot)),
        CronTrigger(day_of_week="sun", hour=12, minute=0),
        id="weekly_top10",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    sch.add_job(
        lambda: asyncio.create_task(_post_monthly_reset(bot)),
        CronTrigger(day="1", hour=0, minute=5),
        id="monthly_reset",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    sch.start()
    return sch
