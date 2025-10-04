import asyncio

async def countdown(seconds: int):
    print("Start countdown")  # แนะนำให้เพิ่มบรรทัดนี้ไว้เช็ค
    for i in range(seconds, 0, -1):
        print(f"⏳ เหลือ {i} วินาที")
        await asyncio.sleep(1)
    print("⏰ หมดเวลา!")

if __name__ == "__main__":
    asyncio.run(countdown(5))
