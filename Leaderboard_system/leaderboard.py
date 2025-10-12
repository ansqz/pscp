"""Leaderboard (safe path version)"""
from pathlib import Path
import json
import discord
from datetime import datetime

# โฟลเดอร์รากโปรเจกต์ (.. จากไฟล์นี้)
ROOT = Path(__file__).resolve().parents[1]
SCORES_FILE = ROOT / "score_manager" / "scores.json"

async def show_leaderboard(channel: discord.TextChannel, top_n: int = 10):
    """
    Show leaderboard to a Discord channel.
    """
    try:
        if not SCORES_FILE.exists():
            await channel.send("❌ ไม่มีข้อมูลคะแนน")
            return
        scores = json.loads(SCORES_FILE.read_text(encoding="utf-8"))
    except Exception:
        await channel.send("❌ ไม่มีข้อมูลคะแนน")
        return

    if not scores:
        await channel.send("❌ ไม่มีข้อมูลคะแนน")
        return

    # sort high->low
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_scores = sorted_scores[:top_n]

    # render: ถ้า key เป็นตัวเลข ให้แสดงเป็น mention <@uid>, ไม่งั้นแสดงชื่อข้อความ
    lines = []
    for i, (user_key, score) in enumerate(top_scores, start=1):
        name = f"<@{user_key}>" if str(user_key).isdigit() else str(user_key)
        lines.append(f"{i}. {name}: {score} คะแนน")

    description = "**🏆 Leaderboard 🏆**\n\n" + "\n".join(lines)

    embed = discord.Embed(
        title="📊 Leaderboard",
        description=description,
        color=discord.Color.gold(),
    )
    embed.set_footer(text=f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await channel.send(embed=embed)

async def reset_scores(channel: discord.TextChannel):
    """
    Reset all scores and notify the channel.
    """
    SCORES_FILE.write_text("{}", encoding="utf-8")
    await channel.send("🔄 คะแนนทั้งหมดถูกรีเซ็ตแล้ว (ทุกวันที่ 1 ของเดือน)")
