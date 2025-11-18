from decimal import Decimal
from typing import Optional, List
from src.models.asset import Asset
from src.models.purchase import Purchase
from src.utils.currency import Currency
from src.services.excel_exporter import ExcelExporter
from src.services.calculator import Calculator


class AssetManager:
    """Менеджер для управления активами"""
    
    def __init__(self):
        self.current_asset: Optional[Asset] = None
    
    def create_asset(self, name: str, currency: Currency = Currency.USD, drawdown_percent: Decimal = Decimal('15.0')) -> Asset:
        """Создает новый актив"""
        asset = Asset(
            name=name,
            currency=currency,
            drawdown_percent=drawdown_percent,
            purchases=[]
        )
        self.current_asset = asset
        # Сохраняем сразу при создании
        ExcelExporter.export_asset(asset)
        return asset
    
    def load_asset(self, name: str) -> Optional[Asset]:
        """Загружает актив из файла"""
        asset = ExcelExporter.import_asset(name)
        if asset:
            self.current_asset = asset
        return asset
    
    def save_current_asset(self) -> bool:
        """Сохраняет текущий актив в файл"""
        if self.current_asset:
            return ExcelExporter.export_asset(self.current_asset)
        return False
    
    def delete_asset(self, name: str) -> bool:
        """Удаляет актив и его файл"""
        success = ExcelExporter.delete_asset(name)
        # Если удаляемый актив был текущим, очищаем его
        if success and self.current_asset and self.current_asset.name == name:
            self.current_asset = None
        return success
    
    def list_assets(self) -> List[str]:
        """Возвращает список всех доступных активов"""
        return ExcelExporter.list_assets()
    
    def add_purchase(self, investment: Decimal, price: Decimal) -> Optional[Purchase]:
        """Добавляет покупку к текущему активу"""
        if not self.current_asset:
            return None
        
        if investment <= 0 or price <= 0:
            raise ValueError("Сумма вложений и цена должны быть больше нуля")
        
        # Определяем следующий ID
        next_id = max([p.id for p in self.current_asset.purchases], default=0) + 1
        
        quantity = Calculator.calculate_quantity(investment, price)
        purchase = Purchase(
            id=next_id,
            investment=investment,
            price=price,
            quantity=quantity
        )
        
        self.current_asset.purchases.append(purchase)
        # Автоматически сохраняем
        self.save_current_asset()
        return purchase
    
    def remove_purchase(self, purchase_id: int) -> bool:
        """Удаляет покупку из текущего актива"""
        if not self.current_asset:
            return False
        
        for i, purchase in enumerate(self.current_asset.purchases):
            if purchase.id == purchase_id:
                self.current_asset.purchases.pop(i)
                # Автоматически сохраняем
                self.save_current_asset()
                return True
        return False
    
    def get_all_purchases(self) -> List[Purchase]:
        """Возвращает все покупки текущего актива"""
        if not self.current_asset:
            return []
        return self.current_asset.purchases.copy()
    
    def get_last_purchase(self) -> Optional[Purchase]:
        """Возвращает последнюю покупку текущего актива"""
        if not self.current_asset or not self.current_asset.purchases:
            return None
        return self.current_asset.purchases[-1]
    
    def set_drawdown_percent(self, drawdown: Decimal):
        """Устанавливает процент просадки для текущего актива"""
        if self.current_asset:
            self.current_asset.drawdown_percent = drawdown
            # Автоматически сохраняем
            self.save_current_asset()
    
    def set_currency(self, currency: Currency):
        """Устанавливает валюту для текущего актива"""
        if self.current_asset:
            self.current_asset.currency = currency
            # Автоматически сохраняем
            self.save_current_asset()
    
    def get_drawdown_percent(self) -> Decimal:
        """Возвращает процент просадки текущего актива"""
        if self.current_asset:
            return self.current_asset.drawdown_percent
        return Decimal('15.0')
    
    def get_currency(self) -> Currency:
        """Возвращает валюту текущего актива"""
        if self.current_asset:
            return self.current_asset.currency
        return Currency.USD
    
    def get_current_asset_name(self) -> Optional[str]:
        """Возвращает название текущего актива"""
        if self.current_asset:
            return self.current_asset.name
        return None

