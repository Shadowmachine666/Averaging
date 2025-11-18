from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class Purchase:
    """Модель покупки актива"""
    id: int
    investment: Decimal  # Сумма вложенных денег
    price: Decimal  # Цена актива на момент покупки
    quantity: Decimal  # Количество купленных активов (investment / price)
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

