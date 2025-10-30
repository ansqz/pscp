'''discord bot'''
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# our function
from ques_choices.question_manager import get_question
from score_manager.score_manager import add_score
from Leaderboard_system.leaderboard import show_leaderboard, reset_scores

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True          # Required to see members in a server
intents.message_content = True  # Required to read message content
bot = commands.Bot(command_prefix='!', intents=intents) # Set prefix to '!' to run commands

@bot.event
async def on_ready():
    '''check if bot online'''
    print('Bot Online!')

@bot.event
async def on_message(message):
    '''This function runs every time a message is sent'''
    # don't answer itself
    if message.author == bot.user:
        return

    mes = message.content
    if mes == 'ping':
        await message.channel.send('Pong!')

    await bot.process_commands(message) # check if all condition is not met

@bot.command()
async def hello(ctx):
    '''test discord command'''
    await ctx.send(f"hello {ctx.author.name}!")

@bot.command()
async def quiz(ctx):
    """
    เล่น 1 รอบ (5 คำ)
    - โพสต์คำถามละ 1 ข้อ: คำอังกฤษ + ตัวเลือก 4 ตัว
    - เก็บคำตอบภายใน 5 วินาที (ผู้ใช้พิมพ์เลข 1-4)
    - ให้คะแนนตามลำดับผู้ตอบถูก: 5,4,3 และคนถัดไปได้ 1
    - คูลดาวน์ 2 วินาที ระหว่างข้อ
    - จบครบ 5 ข้อ โพสต์ Leaderboard รอบนี้
    """
    ch = ctx.channel
    for i in range(5):  # รอบละ 5 ข้อ
        word, answer, choices = get_question()
        # หา index คำตอบที่ถูก (1-4)
        try:
            correct_index = choices.index(answer) + 1
        except ValueError:
            # ถ้าข้อมูลผิดรูป (answer ไม่อยู่ใน choices) ให้ข้ามข้อ
            await ctx.send("⚠️ ข้อมูลผิด! ข้ามข้อนี้")
            await asyncio.sleep(1)
            continue

        question = f'What is {word} in Thai?'
        str_choices = '\n'.join([f'{i+1}. {choices[i]}' for i in range(4)])
        await ch.send(f'**{question}**\n{str_choices}')

        # เก็บข้อมูลคำตอบของผู้เล่น
        answers = []
        def check(msg: discord.Message) -> bool:
            return (
                msg.channel.id == ch.id
                and msg.content.isdigit()
                and 1 <= int(msg.content) <= 4
            )

        try:
            while True:
                msg = await bot.wait_for("message", check=check, timeout=5.0)
                answers.append((msg.author.id, int(msg.content)))
        except asyncio.TimeoutError:
            pass  # หมดเวลา

        # นับเฉพาะคำตอบแรกของแต่ละคน แล้วคัดเฉพาะที่ตอบถูก
        seen = set()
        correct_user = []
        for uid, choice in answers:
            if uid in seen:
                continue
            seen.add(uid)
            if choice == correct_index:
                correct_user.append(uid)

        # ให้คะแนน: 5,4,3, แล้วที่เหลือได้ 1
        if not correct_user:
            await ch.send(f"❎ หมดเวลา! คำตอบคือ **{answer}** ไม่มีใครตอบถูก")
            await asyncio.sleep(2)
            continue
        points = [5, 4, 3]
        if len(correct_user) > 3:
            points += [1] * (len(correct_user) - 3)
        for uid, pts in zip(correct_user, points):
            add_score(uid, pts)

        await ch.send(f"✅ เฉลย: **{answer}**")
        await asyncio.sleep(2)  # คูลดาวน์ก่อนข้อถัดไป

    # จบรอบ → โชว์ Leaderboard รอบนี้ (Top 10)
    await show_leaderboard(ch, top_n=10)

@bot.command()
async def reset(ctx):
    '''รีเซ็ตคะแนน'''
    await reset_scores(ctx.channel)
@bot.command()
async def leaderboard(ctx):
    '''ดู leader board'''
    await show_leaderboard(ctx.channel, top_n=10)


bot.run(token)
