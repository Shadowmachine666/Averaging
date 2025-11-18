import customtkinter as ctk
from decimal import Decimal
from src.utils.formatters import format_currency, format_quantity
from src.utils.currency import Currency


class ResultsSection(ctk.CTkFrame):
    """Секция для отображения текущих результатов"""
    
    def __init__(self, parent, currency: Currency = Currency.PLN, **kwargs):
        super().__init__(parent, **kwargs)
        self.currency = currency
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса секции результатов"""
        # Заголовок
        title = ctk.CTkLabel(
            self,
            text="Aktualne wyniki",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=(0, 8))
        
        # Контейнер для метрик
        metrics_frame = ctk.CTkFrame(self)
        metrics_frame.pack(fill="x", pady=0)
        
        # Общая сумма
        self._create_metric(
            metrics_frame,
            "Całkowita suma:",
            "total_investment",
            row=0
        )
        
        # Общее количество
        self._create_metric(
            metrics_frame,
            "Całkowita ilość:",
            "total_quantity",
            row=1
        )
        
        # Безубыточная точка (выделенная)
        break_even_frame = ctk.CTkFrame(metrics_frame, fg_color=("gray85", "gray25"))
        break_even_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=3, pady=6)
        
        break_even_label = ctk.CTkLabel(
            break_even_frame,
            text="Punkt bezstratny:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        break_even_label.pack(side="left", padx=12, pady=6)
        
        self.break_even_value = ctk.CTkLabel(
            break_even_frame,
            text="—",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.break_even_value.pack(side="right", padx=12, pady=6)
    
    def _create_metric(self, parent, label_text: str, value_key: str, row: int):
        """Создает метрику с подписью и значением"""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=11)
        )
        label.grid(row=row, column=0, padx=12, pady=6, sticky="w")
        
        value_label = ctk.CTkLabel(
            parent,
            text="—",
            font=ctk.CTkFont(size=11)
        )
        value_label.grid(row=row, column=1, padx=12, pady=6, sticky="e")
        
        # Сохраняем ссылку на label для обновления
        setattr(self, value_key, value_label)
    
    def set_currency(self, currency: Currency):
        """Устанавливает валюту"""
        self.currency = currency
    
    def update_results(
        self,
        total_investment: Decimal | None,
        total_quantity: Decimal | None,
        break_even_price: Decimal | None,
        currency: Currency = None
    ):
        """Обновляет отображаемые результаты"""
        if currency:
            self.currency = currency
        
        self.total_investment.configure(
            text=format_currency(total_investment, self.currency) if total_investment else "—"
        )
        self.total_quantity.configure(
            text=format_quantity(total_quantity) if total_quantity else "—"
        )
        self.break_even_value.configure(
            text=format_currency(break_even_price, self.currency) if break_even_price else "—"
        )

