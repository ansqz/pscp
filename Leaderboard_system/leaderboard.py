import json
import discord
from datetime import datetime

# ไฟล์เก็บคะแนน
SCORES_FILE = "score_manager/scores.json"

async def show_leaderboard(channel, top_n=10):
    """แสดงตารางคะแนน Top 10"""

    # โหลดไฟล์คะแนน
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            scores = json.load(f)
    except:
        await channel.send("❌ ไม่มีข้อมูลคะแนน")
        return

    if not scores:
        await channel.send("❌ ไม่มีข้อมูลคะแนน")
        return

    # เรียงคะแนนจากมากไปน้อย
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    text = "**🏆 Leaderboard 🏆**\n\n"
    for i, (user_id, score) in enumerate(sorted_scores[:top_n], start=1):
        name = f"<@{user_id}>" if user_id.isdigit() else user_id
        text += f"{i}. {name}: {score} คะแนน\n"

    embed = discord.Embed(
        title="📊 Leaderboard",
        description=text,
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await channel.send(embed=embed)


async def reset_scores(channel):
    """รีเซ็ตคะแนนทั้งหมด"""
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
    await channel.send("🔄 คะแนนทั้งหมดถูกรีเซ็ตแล้ว (ทุกวันที่ 1 ของเดือน)")
