import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import config
import storage

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ms_asilbek_bot")

router = Router()


# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------

def build_subscribe_keyboard() -> InlineKeyboardMarkup:
    """Kanallarga obuna bo'lish + tasdiqlash tugmalari (haqiqiy rang va custom emoji bilan)"""
    buttons = []
    styles = ["primary", "success"]  # 1-kanal ko'k, 2-kanal yashil
    for i, ch in enumerate(config.CHANNELS):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{i + 1}-kanalga obuna bo'lish",
                    url=ch["url"],
                    icon_custom_emoji_id=ch["emoji_id"],
                    style=styles[i],
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Tasdiqlash",
                callback_data="check_subscription",
                icon_custom_emoji_id=config.CONFIRM_EMOJI_ID,
                style="danger",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_subscribe_text() -> str:
    lines = ["<b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n"]
    for i, ch in enumerate(config.CHANNELS, start=1):
        lines.append(f"{i}. {ch['title']}")
    lines.append("\nObuna bo'lgach, pastdagi <b>Tasdiqlash</b> tugmasini bosing.")
    return "\n".join(lines)


async def check_user_subscribed(bot: Bot, user_id: int) -> bool:
    for ch in config.CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{ch['username']}", user_id=user_id)
            if member.status in (
                ChatMemberStatus.LEFT,
                ChatMemberStatus.KICKED,
            ):
                return False
        except TelegramBadRequest as e:
            log.warning("Obunani tekshirishda xato (%s): %s", ch["username"], e)
            return False
    return True


async def get_group_invite_link(bot: Bot, user_id: int) -> str:
    """
    Agar GROUP_CHAT_ID sozlangan va bot o'sha guruhda admin bo'lsa -
    har bir foydalanuvchi uchun bir martalik (member_limit=1) alohida
    havola yaratadi. Aks holda statik havola qaytaradi.
    """
    if not config.GROUP_CHAT_ID:
        return config.STATIC_GROUP_LINK
    try:
        invite = await bot.create_chat_invite_link(
            chat_id=config.GROUP_CHAT_ID,
            member_limit=1,
            name=f"ref_{user_id}",
        )
        return invite.invite_link
    except Exception as e:
        log.warning("Guruh havolasini yaratib bo'lmadi, statik havola ishlatiladi: %s", e)
        return config.STATIC_GROUP_LINK


async def send_group_link_if_needed(bot: Bot, referrer_id: int, new_count: int | None):
    if new_count is None:
        return
    if new_count >= config.REFERRAL_TARGET:
        user = storage.get_user(referrer_id)
        if user and user["group_link_sent"]:
            return
        link = await get_group_invite_link(bot, referrer_id)
        storage.mark_group_link_sent(referrer_id)
        try:
            await bot.send_message(
                referrer_id,
                "🎉 Tabriklaymiz! Siz <b>{}</b> ta do'stingizni taklif qildingiz "
                "va maxsus yopiq guruhga kirish huquqiga ega bo'ldingiz:\n\n{}".format(
                    config.REFERRAL_TARGET, link
                ),
            )
        except Exception as e:
            log.warning("Foydalanuvchiga (%s) xabar yuborib bo'lmadi: %s", referrer_id, e)


def build_premium_menu_text(user_row) -> str:
    count = user_row["referral_count"] if user_row else 0
    remaining = max(config.REFERRAL_TARGET - count, 0)
    text = (
        "✅ <b>Obuna tasdiqlandi!</b>\n\n"
        "Endi botning premium tizimidan foydalanishingiz mumkin.\n\n"
        f"👥 Sizning taklif qilganlaringiz: <b>{count}</b>\n"
    )
    if remaining > 0:
        text += f"🎯 Maxsus guruhga kirish uchun yana <b>{remaining}</b> ta do'st taklif qiling."
    else:
        text += "🎉 Siz maxsus guruhga kirish huquqiga ega bo'lgansiz!"
    return text


def build_referral_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


def build_premium_menu_keyboard(bot_username: str, user_id: int) -> InlineKeyboardMarkup:
    ref_link = build_referral_link(bot_username, user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Mening referal havolam", callback_data="my_ref_link")],
            [InlineKeyboardButton(text="📊 Statistikam", callback_data="my_stats")],
        ]
    )


# ---------------------------------------------------------------------------
# Handlerlar
# ---------------------------------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    payload = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    referrer_id = None
    if payload and payload.startswith("ref_"):
        try:
            candidate = int(payload.replace("ref_", ""))
            if candidate != user.id:
                referrer_id = candidate
        except ValueError:
            pass

    storage.add_user_if_not_exists(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or "",
        referrer_id=referrer_id,
    )

    if storage.is_verified(user.id):
        row = storage.get_user(user.id)
        me = await bot.get_me()
        await message.answer(
            build_premium_menu_text(row),
            reply_markup=build_premium_menu_keyboard(me.username, user.id),
        )
        return

    await message.answer(
        build_subscribe_text(),
        reply_markup=build_subscribe_keyboard(),
    )


@router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    subscribed = await check_user_subscribed(bot, user_id)

    if not subscribed:
        await callback.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz. Obuna bo'lib, qayta urinib ko'ring.",
            show_alert=True,
        )
        return

    was_already_verified = storage.is_verified(user_id)
    storage.mark_verified(user_id)

    if not was_already_verified:
        referrer_id, new_count = storage.count_referral_once(user_id)
        if referrer_id:
            await send_group_link_if_needed(bot, referrer_id, new_count)
            try:
                await bot.send_message(
                    referrer_id,
                    f"✅ Sizning referal havolangiz orqali yangi foydalanuvchi qo'shildi!\n"
                    f"👥 Jami taklif qilganlaringiz: <b>{new_count}</b>/{config.REFERRAL_TARGET}",
                )
            except Exception as e:
                log.warning("Referrerga xabar yuborilmadi: %s", e)

    row = storage.get_user(user_id)
    me = await bot.get_me()
    await callback.message.edit_text(
        build_premium_menu_text(row),
        reply_markup=build_premium_menu_keyboard(me.username, user_id),
    )
    await callback.answer("✅ Tasdiqlandi!")


@router.callback_query(F.data == "my_ref_link")
async def cb_my_ref_link(callback: CallbackQuery, bot: Bot):
    me = await bot.get_me()
    link = build_referral_link(me.username, callback.from_user.id)
    await callback.answer()
    await callback.message.answer(
        "🔗 <b>Sizning shaxsiy referal havolangiz:</b>\n\n"
        f"<code>{link}</code>\n\n"
        "Do'stlaringizni shu havola orqali taklif qiling. "
        f"{config.REFERRAL_TARGET} ta do'st qo'shsangiz, maxsus guruh havolasini olasiz!"
    )


@router.callback_query(F.data == "my_stats")
async def cb_my_stats(callback: CallbackQuery):
    row = storage.get_user(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(build_premium_menu_text(row))


# ---------------------------------------------------------------------------
# Ishga tushirish
# ---------------------------------------------------------------------------

async def handle_health(request: web.Request):
    """Render (yoki UptimeRobot) shu manzilga so'rov yuborib, botni 'uyg'oq' saqlaydi."""
    return web.Response(text="MS Asilbek bot ishlayapti ✅")


async def start_web_server():
    """Render Web Service $PORT talab qiladi - shuning uchun kichik HTTP server ochamiz."""
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    log.info("Health-check server %s portda ishga tushdi", port)


async def main():
    storage.init_db()
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    log.info("Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)

    # HTTP server (Render uchun) va Telegram polling'ni PARALLEL ishga tushiramiz
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
