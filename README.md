# MS Asilbek Bot — Referal tizimi

Majburiy obuna + referal tizimi (5 ta taklifdan keyin maxsus guruh havolasi).

## ⚠️ MUHIM: Tokenni almashtiring

Ushbu suhbatda bot tokeni ochiq ko'rinib qoldi. GitHub'ga yuklashdan oldin:

1. Telegram'da **@BotFather** ga o'ting
2. `/mybots` → botingizni tanlang → **API Token** → **Revoke current token**
3. Yangi tokenni oling va pastdagi qadamlarda ishlating

## 1-qadam: GitHub'ga yuklash

```bash
cd ms-asilbek-bot
git init
git add .
git commit -m "Initial commit: MS Asilbek referal bot"
git branch -M main
git remote add origin https://github.com/FOYDALANUVCHI_NOMI/ms-asilbek-bot.git
git push -u origin main
```

`.env` yoki tokenni o'z ichiga olgan fayllar `.gitignore` orqali yuklanmaydi — bu xavfsiz.

## 2-qadam: Render'da deploy qilish

1. [render.com](https://render.com) ga kiring, **New +** → **Background Worker** ni tanlang
   (bu bot `polling` rejimida ishlaydi, shuning uchun "Web Service" emas, **Worker** kerak)
2. GitHub repongizni ulang
3. Sozlamalar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. **Environment** bo'limida quyidagi o'zgaruvchilarni qo'shing:
   - `BOT_TOKEN` = yangi tokeningiz
   - `ADMIN_CHAT_ID` = `7924605766`
   - `GROUP_CHAT_ID` = (hozircha bo'sh qoldiring, pastga qarang)
   - `STATIC_GROUP_LINK` = maxsus guruhingiz havolasi (masalan `https://t.me/+AbCdEfGh`)
5. **Deploy** tugmasini bosing

## 3-qadam: Botni kanallarga admin qilib qo'shish

Majburiy obunani tekshirish ishlashi uchun bot ikkala kanalga ham **admin** sifatida qo'shilishi shart:
- `@Matematika_milliysertifikatim`
- `@talimtalaba`

## 4-qadam (ixtiyoriy): Har bir foydalanuvchiga ALOHIDA guruh havolasi

Siz "guruh havolasini har xil qilsa bo'ladi" dedingiz — bu ikki xil bo'lishi mumkin:

**A) Oddiy variant (hozir shunday sozlangan):** Hamma 5 ta referalga yetganda bitta statik havolani oladi (`STATIC_GROUP_LINK`).

**B) Har kimga bitta martalik, alohida havola:** Bot guruhga **admin** qilib qo'shilsa va Render'da `GROUP_CHAT_ID` o'zgaruvchisiga guruh ID'si yozilsa (masalan `-1001234567890`), bot avtomatik ravishda har bir foydalanuvchi uchun faqat 1 marta ishlaydigan (`member_limit=1`) shaxsiy havola yaratadi. Guruh ID'sini olish uchun botni guruhga qo'shib, `@userinfobot` yoki shunga o'xshash yordamchi bot orqali ID'ni aniqlang, keyin ayting — men sozlab beraman.

## Fayllar tuzilishi

```
ms-asilbek-bot/
├── bot.py              # Asosiy bot logikasi
├── config.py           # Barcha sozlamalar (kanal, emoji ID, referal soni)
├── storage.py           # SQLite orqali foydalanuvchi/referal hisobi
├── requirements.txt     # aiogram kutubxonasi
├── render.yaml          # Render deploy konfiguratsiyasi
├── .env.example          # Environment o'zgaruvchilar namunasi
└── .gitignore
```

## Nima ishlaydi

- ✅ `/start` bosilganda 2 ta kanalga majburiy obuna talab qilinadi
- ✅ Kanal nomlari oldida siz bergan custom emoji (🔵/🟢 fallback bilan)
- ✅ "Tasdiqlash" tugmasi oldida custom emoji, tugma matnida 🔴 belgisi
- ✅ Referal havola: `https://t.me/BOT_USERNAME?start=ref_USER_ID`
- ✅ 5 ta referalga yetganda avtomatik guruh havolasi yuboriladi
- ✅ Referrer'ga har safar "yangi odam qo'shildi" haqida xabar

## Bilib qo'yish kerak bo'lgan cheklovlar

- Telegram Bot API tugmalarning fon rangini o'zgartirishga ruxsat bermaydi (ko'k/yashil/qizil rang — bu Telegram klientining o'zi tomonidan belgilanadi, hech bir bot buni o'zgartira olmaydi). Shu sabab men rangli doira emojilardan (🔵🟢🔴) foydalandim.
- SQLite fayl asosli baza — Render'ning **bepul** tarifida disk har deploy/restart'da tozalanishi mumkin. Agar foydalanuvchilar sonini doimiy saqlashni istasangiz, keyinchalik PostgreSQL (Render'da bepul beriladi) ga o'tkazib beraman — hozircha demo/kichik loyiha uchun SQLite yetarli.
