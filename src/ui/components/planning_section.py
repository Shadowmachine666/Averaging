import customtkinter as ctk
from decimal import Decimal
from typing import Callable
from src.utils.formatters import format_currency, format_percent
from src.utils.validators import validate_percent
from src.utils.currency import Currency


class PlanningSection(ctk.CTkFrame):
    """Секция для планирования следующей покупки"""
    
    def __init__(self, parent, on_drawdown_change: Callable[[Decimal], None], currency: Currency = Currency.PLN, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_drawdown_change = on_drawdown_change
        self.currency = currency
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса секции планирования"""
        # Заголовок
        title = ctk.CTkLabel(
            self,
            text="Planowanie następnego zakupu",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=(0, 8))
        
        # Контейнер для полей
        fields_frame = ctk.CTkFrame(self)
        fields_frame.pack(fill="x", pady=0)
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=0)
        fields_frame.grid_columnconfigure(2, weight=1)
        
        # Фрейм для последней цены (слева)
        last_price_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        last_price_frame.grid(row=0, column=0, padx=12, pady=6, sticky="ew")
        last_price_frame.grid_columnconfigure(0, weight=1)
        
        last_price_label = ctk.CTkLabel(
            last_price_frame,
            text="Cena ostatniego zakupu:",
            font=ctk.CTkFont(size=11)
        )
        last_price_label.grid(row=0, column=0, sticky="w")
        
        self.last_price_value = ctk.CTkLabel(
            last_price_frame,
            text="—",
            font=ctk.CTkFont(size=11)
        )
        self.last_price_value.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Фрейм для следующей цены (справа на том же уровне)
        next_price_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        next_price_frame.grid(row=0, column=2, padx=12, pady=6, sticky="ew")
        next_price_frame.grid_columnconfigure(0, weight=1)
        
        next_price_label = ctk.CTkLabel(
            next_price_frame,
            text="Cena następnego zakupu:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        next_price_label.grid(row=0, column=0, sticky="w")
        
        self.next_price_value = ctk.CTkLabel(
            next_price_frame,
            text="—",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.next_price_value.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Процент просадки
        drawdown_label = ctk.CTkLabel(
            fields_frame,
            text="Procent spadku:",
            font=ctk.CTkFont(size=11)
        )
        drawdown_label.grid(row=1, column=0, padx=12, pady=6, sticky="w")
        
        drawdown_input_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        drawdown_input_frame.grid(row=1, column=0, padx=12, pady=6, sticky="e")
        
        self.drawdown_entry = ctk.CTkEntry(
            drawdown_input_frame,
            placeholder_text="15.0",
            width=80,
            font=ctk.CTkFont(size=11)
        )
        self.drawdown_entry.pack(side="left", padx=(0, 3))
        self.drawdown_entry.insert(0, "15.0")
        self.drawdown_entry.bind("<FocusOut>", self._on_drawdown_changed)
        self.drawdown_entry.bind("<Return>", lambda e: self._on_drawdown_changed())
        self._is_user_editing = False
        
        percent_label = ctk.CTkLabel(
            drawdown_input_frame,
            text="%",
            font=ctk.CTkFont(size=11)
        )
        percent_label.pack(side="left")
        
        # Сообщение об ошибке
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=10)
        )
        self.error_label.pack(pady=(3, 0))
    
    def _on_drawdown_changed(self, event=None):
        """Обработчик изменения процента просадки"""
        drawdown_str = self.drawdown_entry.get()
        
        valid, error, drawdown = validate_percent(drawdown_str)
        
        if not valid:
            self.error_label.configure(text=error)
            return
        
        self.error_label.configure(text="")
        self._is_user_editing = True
        self.on_drawdown_change(drawdown)
    
    def set_currency(self, currency: Currency):
        """Устанавливает валюту"""
        self.currency = currency
    
    def update_planning(
        self,
        last_price: Decimal | None,
        drawdown_percent: Decimal,
        next_price: Decimal | None,
        currency: Currency = None
    ):
        """Обновляет отображаемые данные планирования"""
        if currency:
            self.currency = currency
        
        self.last_price_value.configure(
            text=format_currency(last_price, self.currency) if last_price else "—"
        )
        
        # Обновляем поле просадки только если пользователь его не редактирует
        # и поле пустое или значение не совпадает
        if not self._is_user_editing:
            current_value = self.drawdown_entry.get().strip()
            if not current_value or current_value != str(drawdown_percent):
                # Проверяем, не в фокусе ли поле
                if self.drawdown_entry.cget("state") != "disabled":
                    try:
                        # Сохраняем фокус
                        has_focus = self.drawdown_entry.focus_get() == self.drawdown_entry
                        if not has_focus:
                            self.drawdown_entry.delete(0, "end")
                            self.drawdown_entry.insert(0, str(drawdown_percent))
                    except:
                        pass
        else:
            self._is_user_editing = False
        
        self.next_price_value.configure(
            text=format_currency(next_price, self.currency) if next_price else "—"
        )
    
    def get_drawdown_percent(self) -> Decimal:
        """Возвращает текущий процент просадки"""
        drawdown_str = self.drawdown_entry.get()
        valid, _, drawdown = validate_percent(drawdown_str)
        return drawdown if valid else Decimal('15.0')

