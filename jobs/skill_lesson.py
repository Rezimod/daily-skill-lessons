import os
import asyncio
from datetime import datetime
from telegram import Bot
import pytz

from daily_skill.generator import generate_daily_lesson_text
from daily_skill.utils import parse_iso_date

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Tbilisi timezone
TBILISI_TZ = pytz.timezone('Asia/Tbilisi')

def generate_daily_lesson() -> str:
    """Generate a single daily skill lesson in Georgian (content system only)."""
    try:
        slot_raw = os.getenv("DAILY_LESSON_SLOT", "0").strip()
        slot = int(slot_raw) if slot_raw else 0

        date_override = os.getenv("DAILY_LESSON_DATE", "").strip()
        on_date = parse_iso_date(date_override) if date_override else None

        return generate_daily_lesson_text(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4o",
            slot=slot,
            on_date=on_date,
        )
    except Exception as e:
        return f"შეცდომა გაკვეთილის გენერირებისას: {str(e)}"

async def send_lesson():
    """Send the daily micro-lesson"""
    try:
        print("Generating daily skill lesson...")
        lesson = generate_daily_lesson()
        
        # Initialize bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        print(f"Sending lesson to chat {CHAT_ID}...")
        await bot.send_message(
            chat_id=CHAT_ID,
            text=lesson,
            parse_mode=None
        )
        
        print("✅ Daily lesson sent successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def main():
    """Main function"""
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY or not CHAT_ID:
        print("❌ Missing required environment variables!")
        print("Please set: TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, TELEGRAM_CHAT_ID")
        return
    
    print("📚 Starting Daily Skill Lesson Bot...")
    print(f"📅 Current time (Tbilisi): {datetime.now(TBILISI_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run the async function
    asyncio.run(send_lesson())

if __name__ == '__main__':
    main()
