import os

# Bot tokeni - Render'da Environment Variable sifatida beriladi
BOT_TOKEN = os.getenv("BOT_TOKEN", "8622464674:AAHhMWetz7ZUFNjTEJw9khK7JGjElSRwdGQ")

# Adminlar (siz va boshqa xodimlar)ning chat ID'lari - vergul bilan ajratib bir nechtasini yozish mumkin
# Masalan Render'da: ADMIN_CHAT_IDS = 7924605766,123456789,987654321
ADMIN_CHAT_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_CHAT_IDS", "7924605766").split(",")
    if x.strip()
]

# Majburiy obuna kanallari: (username, custom_emoji_id, ko'rinadigan nom)
CHANNELS = [
    {
        "username": "Matematika_milliysertifikatim",
        "url": "https://t.me/Matematika_milliysertifikatim",
        "emoji_id": "5424998072323185646",
        "title": "1-kanal: Matematika Milliy Sertifikatim",
    },
    {
        "username": "talimtalaba",
        "url": "https://t.me/talimtalaba",
        "emoji_id": "5451880684945708278",
        "title": "2-kanal: Talim Talaba",
    },
]

# Tasdiqlash oldidagi custom emoji
CONFIRM_EMOJI_ID = "5273805757396031980"

# Nechta referaldan keyin maxsus guruh havolasi yuborilsin
REFERRAL_TARGET = 5

# Maxsus guruh (ixtiyoriy). Agar bot shu guruhga ADMIN qilib qo'shilsa va
# GROUP_CHAT_ID to'ldirilsa - bot HAR BIR foydalanuvchi uchun ALOHIDA
# (bir martalik, member_limit=1) taklif havolasini avtomatik yaratadi.
# Agar bo'sh qoldirilsa - pastdagi STATIC_GROUP_LINK ishlatiladi.
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "")  # masalan: -1001234567890

# Agar GROUP_CHAT_ID berilmasa, hammaga shu statik havola yuboriladi
STATIC_GROUP_LINK = os.getenv("STATIC_GROUP_LINK", "https://t.me/+SIZNING_GURUH_HAVOLANGIZ")

# Ma'lumotlar saqlanadigan joy - Supabase (PostgreSQL) ulanish manzili
# Render'da Environment Variable sifatida beriladi (Supabase'dan olinadi)
DATABASE_URL = os.getenv("DATABASE_URL", "")
