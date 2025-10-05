"""Leaderboard"""

import os
import json
import discord
from datetime import datetime

#Find (leaderboard.py) fix path scores.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(BASE_DIR, "scores.json")

async def show_leaderboard(channel, top_n=10):
    """
    Show leaderboard on Discord

    Parameters:
        channel (discord.TextChannel): Channel to send leaderboard
        top_n (int): TOP10 (default=10)
    """

    # open scores file
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            scores = json.load(f)
        print("DEBUG scores:", scores)
    except FileNotFoundError:
        await channel.send("❌ ไม่มีข้อมูลคะแนน")
        return

    if not scores:
        await channel.send("❌ ไม่มีข้อมูลคะแนน")
        return

    # sort scores high to low
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # top N
    top_scores = sorted_scores[:top_n]

    # text leaderboard
    leaderboard_text = "**🏆 Leaderboard 🏆**\n\n"
    for i, (username, score) in enumerate(top_scores, start=1):
        leaderboard_text += f"{i}. {username}: {score} คะแนน\n"

    # send embed
    embed = discord.Embed(
        title="📊 Leaderboard",
        description=leaderboard_text,
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    await channel.send(embed=embed)


async def reset_scores(channel):
    """
    Reset all scores and send notice on Discord

    Parameters:
        channel (discord.TextChannel): Channel notice will be sent to
    """

    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)  # reset scores

    await channel.send("🔄 คะแนนทั้งหมดถูกรีเซ็ตแล้ว (ทุกวันที่ 1 ของเดือน)")
