from dataclasses import dataclass, field
from decimal import Decimal
from typing import List
from datetime import datetime
from src.models.purchase import Purchase
from src.utils.currency import Currency


@dataclass
class Asset:
    """Модель актива"""
    name: str  # Название актива (BTC, ETH, AAPL и т.д.)
    currency: Currency  # Валюта для этого актива
    drawdown_percent: Decimal  # Процент просадки
    purchases: List[Purchase] = field(default_factory=list)  # Список покупок
    created_at: datetime = field(default_factory=datetime.now)  # Дата создания
    updated_at: datetime = field(default_factory=datetime.now)  # Дата последнего обновления

