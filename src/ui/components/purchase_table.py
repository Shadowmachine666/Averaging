import customtkinter as ctk
from typing import List, Callable
from src.models.purchase import Purchase
from src.utils.formatters import format_currency, format_quantity
from src.utils.currency import Currency


class PurchaseTable(ctk.CTkFrame):
    """Таблица для отображения истории покупок"""
    
    def __init__(self, parent, on_delete: Callable[[int], None], currency: Currency = Currency.PLN, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_delete = on_delete
        self.currency = currency
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса таблицы"""
        # Используем grid для управления размерами
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Заголовок с кнопкой сворачивания
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Historia zakupów",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # Кнопка сворачивания/разворачивания
        self.collapse_button = ctk.CTkButton(
            header_frame,
            text="▼",
            width=30,
            height=25,
            font=ctk.CTkFont(size=12),
            command=self._toggle_collapse,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        self.collapse_button.grid(row=0, column=1, sticky="e")
        
        # Контейнер для таблицы с прокруткой
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(1, weight=1, minsize=100)
        self._is_collapsed = False
        
        # Заголовки таблицы
        headers_frame = ctk.CTkFrame(self.table_frame)
        headers_frame.grid(row=0, column=0, sticky="ew", padx=3, pady=(3, 0))
        headers_frame.grid_columnconfigure(0, weight=1)
        
        headers = ["№", "Suma", "Cena", "Ilość", ""]
        widths = [35, 110, 110, 110, 40]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=width
            )
            if i == 0:  # № - выравнивание влево
                label.grid(row=0, column=i, padx=1, pady=2, sticky="w")
            elif i == len(headers) - 1:  # Последняя колонка (кнопка) - выравнивание вправо
                label.grid(row=0, column=i, padx=1, pady=2, sticky="e")
            else:  # Остальные - выравнивание влево
                label.grid(row=0, column=i, padx=1, pady=2, sticky="w")
        
        # Scrollable frame для строк таблицы (растягивается по размеру)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.table_frame
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=3, pady=3)
        
        # Контейнер для строк (будет обновляться)
        self.rows_container = self.scrollable_frame
    
    def _toggle_collapse(self):
        """Переключает состояние сворачивания таблицы"""
        self._is_collapsed = not self._is_collapsed
        
        if self._is_collapsed:
            self.table_frame.grid_remove()
            self.collapse_button.configure(text="▶")
        else:
            self.table_frame.grid()
            self.collapse_button.configure(text="▼")
    
    def update_purchases(self, purchases: List[Purchase], currency: Currency = None):
        """Обновляет отображение таблицы покупок"""
        if currency:
            self.currency = currency
        
        # Очищаем старые строки
        for widget in self.rows_container.winfo_children():
            widget.destroy()
        
        if not purchases:
            empty_label = ctk.CTkLabel(
                self.rows_container,
                text="Brak zakupów",
                text_color="gray",
                font=ctk.CTkFont(size=11)
            )
            empty_label.pack(pady=15)
            return
        
        # Создаем строки для каждой покупки
        for index, purchase in enumerate(purchases):
            row_frame = ctk.CTkFrame(self.rows_container)
            row_frame.pack(fill="x", pady=1)
            
            # № (порядковый номер, начинается с 1)
            num_label = ctk.CTkLabel(
                row_frame,
                text=str(index + 1),
                width=35,
                font=ctk.CTkFont(size=11)
            )
            num_label.grid(row=0, column=0, padx=1, pady=1, sticky="w")
            
            # Сумма
            investment_label = ctk.CTkLabel(
                row_frame,
                text=format_currency(purchase.investment, self.currency),
                width=110,
                font=ctk.CTkFont(size=10)
            )
            investment_label.grid(row=0, column=1, padx=1, pady=1, sticky="w")
            
            # Цена
            price_label = ctk.CTkLabel(
                row_frame,
                text=format_currency(purchase.price, self.currency),
                width=110,
                font=ctk.CTkFont(size=10)
            )
            price_label.grid(row=0, column=2, padx=1, pady=1, sticky="w")
            
            # Количество
            quantity_label = ctk.CTkLabel(
                row_frame,
                text=format_quantity(purchase.quantity),
                width=110,
                font=ctk.CTkFont(size=10)
            )
            quantity_label.grid(row=0, column=3, padx=1, pady=1, sticky="w")
            
            # Кнопка удаления
            delete_btn = ctk.CTkButton(
                row_frame,
                text="🗑️",
                width=40,
                height=20,
                font=ctk.CTkFont(size=10),
                command=lambda pid=purchase.id: self.on_delete(pid),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            delete_btn.grid(row=0, column=4, padx=1, pady=1, sticky="e")
    
    def set_currency(self, currency: Currency):
        """Устанавливает валюту и обновляет отображение"""
        self.currency = currency

