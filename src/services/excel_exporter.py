import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import List
import pandas as pd
from src.models.asset import Asset
from src.models.purchase import Purchase
from src.utils.currency import Currency


class ExcelExporter:
    """Класс для экспорта и импорта данных активов в Excel"""
    
    ASSETS_DIR = "Assets"
    
    @staticmethod
    def _ensure_assets_dir():
        """Создает папку Assets если её нет"""
        assets_path = Path(ExcelExporter.ASSETS_DIR)
        assets_path.mkdir(exist_ok=True)
        return assets_path
    
    @staticmethod
    def _get_filepath(asset_name: str) -> Path:
        """Возвращает путь к файлу актива"""
        assets_dir = ExcelExporter._ensure_assets_dir()
        # Используем название актива как имя файла
        filename = f"{asset_name}.xlsx"
        return assets_dir / filename
    
    @staticmethod
    def export_asset(asset: Asset) -> bool:
        """
        Экспортирует актив в Excel файл
        Возвращает True если успешно, False если ошибка
        """
        try:
            filepath = ExcelExporter._get_filepath(asset.name)
            
            # Обновляем дату обновления
            asset.updated_at = datetime.now()
            
            # Создаем DataFrame для покупок
            purchases_data = []
            for idx, purchase in enumerate(asset.purchases, start=1):
                purchases_data.append({
                    "№": idx,
                    "Дата": purchase.timestamp.strftime("%Y-%m-%d %H:%M:%S") if purchase.timestamp else "",
                    "Сумма вложений": float(purchase.investment),
                    "Цена покупки": float(purchase.price),
                    "Количество": float(purchase.quantity)
                })
            
            # Создаем DataFrame даже если покупок нет (с заголовками)
            if purchases_data:
                purchases_df = pd.DataFrame(purchases_data)
            else:
                purchases_df = pd.DataFrame(columns=["№", "Дата", "Сумма вложений", "Цена покупки", "Количество"])
            
            # Создаем DataFrame для настроек
            settings_data = {
                "Параметр": ["Валюта", "Процент просадки", "Дата создания", "Дата обновления"],
                "Значение": [
                    asset.currency.code,
                    float(asset.drawdown_percent),
                    asset.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    asset.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            settings_df = pd.DataFrame(settings_data)
            
            # Записываем в Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                purchases_df.to_excel(writer, sheet_name='Purchases', index=False)
                settings_df.to_excel(writer, sheet_name='Settings', index=False)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении актива: {e}")
            return False
    
    @staticmethod
    def import_asset(asset_name: str) -> Asset | None:
        """
        Импортирует актив из Excel файла
        Возвращает Asset или None если файл не найден или ошибка
        """
        try:
            filepath = ExcelExporter._get_filepath(asset_name)
            
            if not filepath.exists():
                return None
            
            # Читаем настройки
            try:
                settings_df = pd.read_excel(filepath, sheet_name='Settings')
                settings_dict = dict(zip(settings_df['Параметр'], settings_df['Значение']))
            except Exception:
                # Если лист Settings не существует, используем значения по умолчанию
                settings_dict = {}
            
            # Определяем валюту
            currency_code = str(settings_dict.get('Валюта', 'USD'))
            currency = Currency.USD
            for c in Currency:
                if c.code == currency_code:
                    currency = c
                    break
            
            # Парсим даты с обработкой ошибок
            def parse_datetime(value, default=None):
                if default is None:
                    default = datetime.now()
                if pd.isna(value):
                    return default
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    try:
                        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    except:
                        try:
                            return datetime.strptime(value, "%Y-%m-%d")
                        except:
                            return default
                return default
            
            created_at = parse_datetime(settings_dict.get('Дата создания'))
            updated_at = parse_datetime(settings_dict.get('Дата обновления'))
            
            # Создаем актив
            asset = Asset(
                name=asset_name,
                currency=currency,
                drawdown_percent=Decimal(str(settings_dict.get('Процент просадки', 15.0))),
                created_at=created_at,
                updated_at=updated_at
            )
            
            # Читаем покупки
            try:
                purchases_df = pd.read_excel(filepath, sheet_name='Purchases')
                
                for _, row in purchases_df.iterrows():
                    if pd.isna(row.get('№')):
                        continue
                    
                    purchase = Purchase(
                        id=int(row['№']),
                        investment=Decimal(str(row['Сумма вложений'])),
                        price=Decimal(str(row['Цена покупки'])),
                        quantity=Decimal(str(row['Количество'])),
                        timestamp=parse_datetime(row.get('Дата'))
                    )
                    asset.purchases.append(purchase)
            except Exception as e:
                # Если лист Purchases пустой или не существует, просто продолжаем
                print(f"Ошибка при чтении покупок: {e}")
            
            return asset
        except Exception as e:
            print(f"Ошибка при загрузке актива: {e}")
            return None
    
    @staticmethod
    def delete_asset(asset_name: str) -> bool:
        """
        Удаляет файл актива
        Возвращает True если успешно, False если ошибка
        """
        try:
            filepath = ExcelExporter._get_filepath(asset_name)
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении актива: {e}")
            return False
    
    @staticmethod
    def list_assets() -> List[str]:
        """
        Возвращает список названий всех активов (файлов в папке Assets)
        """
        try:
            assets_dir = ExcelExporter._ensure_assets_dir()
            assets = []
            for file in assets_dir.glob("*.xlsx"):
                # Убираем расширение .xlsx
                asset_name = file.stem
                assets.append(asset_name)
            return sorted(assets)
        except Exception as e:
            print(f"Ошибка при получении списка активов: {e}")
            return []

