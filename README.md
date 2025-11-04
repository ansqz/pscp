# PSCP Project | LinguaQuest Bot
LinguaQuest Bot เป็นบอทในโปรแกรม ดิสคอร์ด ส่งเสริมการเรียนรู้ภาษาอังกฤษของคนไทย โดยบอทที่พัฒนาขึ้นนี้มีฟังก์ชันการทำงานหลักคือ เกมทายคำศัพท์ 

## Feature
- สร้างเกมแข่งทายคำศัพท์ได้ในช่องแชท
- ระบบเก็บเต้มและ leaderboard
- ระบบรีเซ็ทคะแนนสำหรับผู้ดูแล

## Library
<ul>
    <li>discord.py 2.4.0</li>
    <li>APScheduler 3.10.4</li>
    <li>python-dotenv 1.0.1</li>
    <li>json 2.0.9</li>
    <li>asyncio</li>
    <li>random</li>
    <li>datetime</li>
</ul>

## General Setup
1. Clone the repo on your local machine
2. Install all of the library
3. Create `.env` file and put your discord token in `DISCORD_TOKEN = ''`
4. Change to your server ID in `bot_main.py`
5. Invite the bot into your server 
6. Run `bot_main.py`


