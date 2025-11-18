from decimal import Decimal
from src.utils.currency import Currency


def format_currency(value: Decimal | None, currency: Currency = Currency.PLN, decimals: int = 2) -> str:
    """Форматирует денежную сумму с указанной валютой"""
    if value is None:
        return "—"
    
    # Для криптовалют используем больше знаков после запятой
    if currency in [Currency.BTC, Currency.ETH]:
        decimals = 8
    
    # Форматируем с разделителями тысяч и нужным количеством знаков
    formatted = f"{value:,.{decimals}f}"
    # Заменяем запятую на пробел для тысяч и точку на запятую для десятичных
    # Сначала заменяем точку на запятую, потом запятую на пробел
    formatted = formatted.replace('.', '|TEMP|').replace(',', ' ').replace('|TEMP|', ',')
    return f"{formatted} {currency.symbol}"


def format_percent(value: Decimal | None, decimals: int = 1) -> str:
    """Форматирует процент"""
    if value is None:
        return "—"
    return f"{value:.{decimals}f}%"


def format_quantity(value: Decimal | None, decimals: int = 8) -> str:
    """Форматирует количество активов"""
    if value is None:
        return "—"
    # Убираем лишние нули в конце
    formatted = f"{value:.{decimals}f}".rstrip('0').rstrip('.')
    # Если осталась только точка, убираем её
    if formatted.endswith('.'):
        formatted = formatted[:-1]
    # Заменяем точку на запятую для польского формата
    formatted = formatted.replace('.', ',')
    return formatted

