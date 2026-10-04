from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from app.api.aggregator import aggregator
from app.bot.formatter import format_telegram_report
from app.bot.keyboards import get_report_keyboard, get_start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "<b>CarCheck KG — Проверка авто по базам данных</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Сервис объединяет 4 официальных источника:\n"
        "• <b>Tolom.kg:</b> Штрафы ГУОБДД, аресты, тонировка\n"
        "• <b>Customs.gov.kg:</b> Статус таможенного оформления КР\n"
        "• <b>Korea-Cars:</b> Дата экспорта и пробег в Южной Корее\n"
        "• <b>AutoPartner / Copart:</b> Аукционная история и фото лота\n\n"
        "📌 <b>Форматы запроса:</b>\n\n"
        "1. <b>Только госномер:</b>\n"
        "   <code>01KG555ADF</code> (или <code>01 555 ADF</code>)\n"
        "   <i>Проверяет штрафы, аресты, тонировку в КР</i>\n\n"
        "2. <b>Только VIN код:</b>\n"
        "   <code>1FTEW1E55KFB29513</code> (17 знаков)\n"
        "   <i>Проверяет таможню, корейский реестр, аукционы с фото</i>\n\n"
        "3. <b>Госномер + VIN вместе (рекомендуется):</b>\n"
        "   <code>01KG555ADF 1FTEW1E55KFB29513</code>\n"
        "   <i>Полный опрос всех 4 баз данных в 1 сообщении</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 <i>Отправьте номер сообщением или выберите быстрый пример:</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_start_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "<b>Инструкция по поиску CarCheck:</b>\n\n"
        "• <b>Госномер КР</b> (форматы: <code>01KG555ADF</code>, <code>01 555 ADF</code>, <code>B1234AB</code>) — для проверки штрафов ГУОБДД, задолженностей и ограничений.\n\n"
        "• <b>VIN номер</b> (17 символов) — для проверки таможенной декларации КР, базы вывоза из Кореи и страховых аукционов США.\n\n"
        "• <b>Оба номера сразу</b> (через пробел: <code>01KG555ADF 1FTEW1E55KFB29513</code>) — самый быстрый способ получить полный отчет без пропусков баз."
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

@router.callback_query(F.data.startswith("check:"))
async def cb_check_example(callback: CallbackQuery):
    query = callback.data.split(":", 1)[1]
    await callback.answer("Запрос отправлен в базы...")
    status_msg = await callback.message.answer(f"⏳ Опрос реестров по <code>{query}</code>...", parse_mode=ParseMode.HTML)
    
    data = await aggregator.check_all(query)
    report_text = format_telegram_report(data)
    
    await status_msg.edit_text(
        report_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_report_keyboard(query),
        disable_web_page_preview=True
    )

@router.callback_query(F.data.startswith("refresh:"))
async def cb_refresh(callback: CallbackQuery):
    query = callback.data.split(":", 1)[1]
    await callback.answer("Обновление...")
    
    data = await aggregator.check_all(query)
    report_text = format_telegram_report(data)
    
    try:
        await callback.message.edit_text(
            report_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_report_keyboard(query),
            disable_web_page_preview=True
        )
    except Exception:
        pass

@router.message(F.text)
async def handle_car_query(message: Message):
    raw_query = message.text.strip()
    if len(raw_query) < 3 or len(raw_query) > 50:
        await message.answer("⚠️ Введите госномер (напр. <code>01KG555ADF</code>) или 17-значный VIN код.")
        return

    status_msg = await message.answer("⏳ Запрос данных из реестров...", parse_mode=ParseMode.HTML)
    
    data = await aggregator.check_all(raw_query)
    report_text = format_telegram_report(data)
    
    await status_msg.edit_text(
        report_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_report_keyboard(data["query"]),
        disable_web_page_preview=True
    )
