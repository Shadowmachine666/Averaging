from decimal import Decimal
from typing import List, Optional
from src.models.purchase import Purchase
from src.services.calculator import Calculator


class PurchaseManager:
    """Менеджер для управления списком покупок"""
    
    def __init__(self):
        self._purchases: List[Purchase] = []
        self._next_id = 1
    
    def add_purchase(self, investment: Decimal, price: Decimal) -> Purchase:
        """Добавляет новую покупку в список"""
        if investment <= 0:
            raise ValueError("Сумма вложений должна быть больше нуля")
        if price <= 0:
            raise ValueError("Цена должна быть больше нуля")
        
        quantity = Calculator.calculate_quantity(investment, price)
        purchase = Purchase(
            id=self._next_id,
            investment=investment,
            price=price,
            quantity=quantity
        )
        
        self._purchases.append(purchase)
        self._next_id += 1
        return purchase
    
    def remove_purchase(self, purchase_id: int) -> bool:
        """Удаляет покупку по ID"""
        for i, purchase in enumerate(self._purchases):
            if purchase.id == purchase_id:
                self._purchases.pop(i)
                return True
        return False
    
    def get_all_purchases(self) -> List[Purchase]:
        """Возвращает список всех покупок"""
        return self._purchases.copy()
    
    def get_last_purchase(self) -> Optional[Purchase]:
        """Возвращает последнюю покупку или None"""
        return self._purchases[-1] if self._purchases else None
    
    def clear_all(self) -> None:
        """Очищает весь список покупок"""
        self._purchases.clear()
        self._next_id = 1
    
    def get_purchase_count(self) -> int:
        """Возвращает количество покупок"""
        return len(self._purchases)

