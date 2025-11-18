from decimal import Decimal
from typing import List
from src.models.purchase import Purchase


class Calculator:
    """Класс для выполнения расчетов безубыточной точки и прогнозирования"""
    
    @staticmethod
    def calculate_quantity(investment: Decimal, price: Decimal) -> Decimal:
        """Рассчитывает количество активов для покупки"""
        if price <= 0:
            raise ValueError("Цена должна быть больше нуля")
        return investment / price
    
    @staticmethod
    def calculate_total_investment(purchases: List[Purchase]) -> Decimal:
        """Суммирует все вложенные средства"""
        return sum(p.investment for p in purchases)
    
    @staticmethod
    def calculate_total_quantity(purchases: List[Purchase]) -> Decimal:
        """Суммирует все купленные активы"""
        return sum(p.quantity for p in purchases)
    
    @staticmethod
    def calculate_break_even(purchases: List[Purchase]) -> Decimal | None:
        """
        Рассчитывает среднюю цену входа (безубыточную точку)
        Формула: total_investment / total_quantity
        """
        if not purchases:
            return None
        
        total_investment = Calculator.calculate_total_investment(purchases)
        total_quantity = Calculator.calculate_total_quantity(purchases)
        
        if total_quantity == 0:
            return None
        
        return total_investment / total_quantity
    
    @staticmethod
    def calculate_next_purchase_price(last_price: Decimal, drawdown_percent: Decimal) -> Decimal | None:
        """
        Рассчитывает цену следующей докупки при заданной просадке
        Формула: last_price * (1 - drawdown_percent / 100)
        """
        if last_price is None or last_price <= 0:
            return None
        
        if drawdown_percent < 0 or drawdown_percent > 100:
            raise ValueError("Процент просадки должен быть от 0 до 100")
        
        return last_price * (Decimal('1') - drawdown_percent / Decimal('100'))

