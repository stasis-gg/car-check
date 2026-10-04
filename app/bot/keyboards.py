from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.config import settings

def get_clean_webapp_url() -> str:
    url = settings.WEBAPP_URL.strip() if settings.WEBAPP_URL else ""
    if not url.startswith("https://"):
        return "https://carcheck-kg.onrender.com"
    return url.rstrip("/")

def get_report_keyboard(query: str) -> InlineKeyboardMarkup:
    """
    Клавиатура под результатом проверки
    """
    base_url = get_clean_webapp_url()
    web_app_url = f"{base_url}/report/{query}"
    
    buttons = [
        [
            InlineKeyboardButton(
                text="📊 Открыть подробный отчет",
                web_app=WebAppInfo(url=web_app_url)
            )
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh:{query}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура в стартовом сообщении с готовыми примерами
    """
    base_url = get_clean_webapp_url()
    web_app_url = f"{base_url}/"
    buttons = [
        [
            InlineKeyboardButton(
                text="🚀 Открыть CarCheck WebApp",
                web_app=WebAppInfo(url=web_app_url)
            )
        ],
        [
            InlineKeyboardButton(text="🇰🇬 Только номер (01KG555ADF)", callback_data="check:01KG555ADF"),
        ],
        [
            InlineKeyboardButton(text="🔑 Только VIN (1FTEW1E55...)", callback_data="check:1FTEW1E55KFB29513"),
        ],
        [
            InlineKeyboardButton(text="⚡ Номер + VIN (Все 4 базы)", callback_data="check:01KG555ADF 1FTEW1E55KFB29513")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

