import os
import asyncio
from datetime import datetime
from telegram import Bot
from openai import OpenAI
import pytz

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

client = OpenAI(api_key=OPENAI_API_KEY)
TBILISI_TZ = pytz.timezone('Asia/Tbilisi')

# 18 weekly groups x 3 topics = 54 unique financial skills
# Each group covers Mon / Wed / Fri of the same week
WEEKLY_TOPICS = [
    ("50/30/20 ბიუჯეტის წესი",          "სასწრაფო ფონდი",                  "შემადგენელი პროცენტი"),
    ("საფონდო ბირჟა — საფუძვლები",      "ინდექს-ფონდები და ETF",            "ვალის მართვა"),
    ("პასიური შემოსავალი",               "უძრავი ქონება",                    "ოქრო და საქონელი"),
    ("კრიპტოვალუტა — საფუძვლები",       "DeFi და Web3",                     "NFT და ციფრული აქტივები"),
    ("საგადასახადო ოპტიმიზაცია",         "საპენსიო გეგმა",                   "სადაზღვევო სტრატეგია"),
    ("დივიდენდური ინვესტიცია",           "ობლიგაციები",                      "ურთიერთი ფონდები"),
    ("ფინანსური მიზნების დასახვა",       "ხარჯების თვალყური",                "FIRE — ფინანსური თავისუფლება"),
    ("ბიზნეს დაფინანსება",              "სტარტაფის შეფასება",               "ვენჩური კაპიტალი"),
    ("ვალუტის ვაჭრობა — Forex",         "ოფციონები და ფიუჩერსები",          "ტექნიკური ანალიზი"),
    ("ქცევითი ეკონომიკა",               "ფსიქოლოგია ინვესტიციებში",         "რისკის მართვა"),
    ("ეკონომიკური ციკლები",             "ინფლაცია",                         "ცენტრალური ბანკი და განაკვეთები"),
    ("ESG ინვესტიცია",                  "მწვანე ენერგია",                   "სოციალური ინვესტიცია"),
    ("მიკრო-ინვესტიცია",               "Robo-Advisors",                     "ავტომატური ინვესტიცია"),
    ("კრედიტის ქულა",                  "იპოთეკა",                          "ლიზინგი vs ყიდვა"),
    ("ფრილანს ფინანსები",              "მეწარმის ბუღალტერია",              "ონლაინ შემოსავლის წყაროები"),
    ("საერთაშორისო ინვესტიცია",        "განვითარებადი ბაზრები",            "გლობალური დივერსიფიკაცია"),
    ("ნეტ-ვორთის გაზომვა",            "პირადი ბალანსური ფურცელი",         "ფინანსური ჯანმრთელობა"),
    ("მემკვიდრეობის დაგეგმვა",         "ტრასტი და ანდერძი",               "ქველმოქმედება და სიმდიდრე"),
]

# Day-of-week to slot index: 0=Mon, 2=Wed, 4=Fri
WEEKDAY_SLOT = {0: 0, 2: 1, 4: 2}


def get_topic_for_today():
    """Pick topic based on ISO week number and weekday."""
    now = datetime.now(TBILISI_TZ)
    week_num = now.isocalendar()[1]
    weekday = now.weekday()

    group = WEEKLY_TOPICS[week_num % len(WEEKLY_TOPICS)]
    slot = WEEKDAY_SLOT.get(weekday, weekday % 3)  # fallback for manual runs
    topic = group[slot]
    label = f"კვირის შეტყობინება {slot + 1}/3"
    return topic, label


def generate_lesson(topic: str) -> str:
    """Generate a focused financial lesson using gpt-4o-mini."""
    prompt = (
        f"თემა: {topic}\n\n"
        "დაწერე ფინანსური გაკვეთილი ამ თემაზე ქართულად:\n"
        "- რა არის და რატომ მნიშვნელოვანია (2-3 წინადადება)\n"
        "- 3 მთავარი პრინციპი ან ნაბიჯი (emoji-ებით)\n"
        "- 1 რეალური მაგალითი ან სტატისტიკა\n"
        "- 1 პრაქტიკული დავალება დღეს გასაკეთებლად\n"
        "- მოტივაციური დასკვნა (1 წინადადება)\n\n"
        "სტილი: მარტივი, ენერგიული, პრაქტიკული. გამოიყენე emoji-ები."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "ფინანსური მასწავლებელი ქართულად. მოკლედ, ნათლად, პრაქტიკულად.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1200,
    )
    return response.choices[0].message.content


def split_message(text: str, max_len: int = 3900) -> list:
    """Split text at paragraph boundaries to stay within Telegram's limit."""
    if len(text) <= max_len:
        return [text]

    parts = []
    while len(text) > max_len:
        split_at = text.rfind("\n\n", 0, max_len)
        if split_at == -1:
            split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        parts.append(text[:split_at].strip())
        text = text[split_at:].strip()

    if text:
        parts.append(text)
    return parts


async def send_message():
    topic, label = get_topic_for_today()
    now = datetime.now(TBILISI_TZ)
    print(f"Topic: {topic} | {label} | {now.strftime('%Y-%m-%d %H:%M')}")

    lesson = generate_lesson(topic)

    header = f"📚 {topic}\n{label}\n{'—' * 30}\n\n"
    full_text = header + lesson

    parts = split_message(full_text)
    total = len(parts)

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for i, part in enumerate(parts, 1):
        if total > 1:
            part = f"[{i}/{total}]\n\n{part}"
        await bot.send_message(chat_id=CHAT_ID, text=part, parse_mode=None)
        if i < total:
            await asyncio.sleep(1)

    print(f"✅ Sent {total} part(s) for: {topic}")


def main():
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY or not CHAT_ID:
        print("Missing: TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, TELEGRAM_CHAT_ID")
        return

    print(f"Financial Teacher Bot — {datetime.now(TBILISI_TZ).strftime('%Y-%m-%d %H:%M')} Tbilisi")
    asyncio.run(send_message())


if __name__ == "__main__":
    main()
