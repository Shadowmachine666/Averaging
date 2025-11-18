import customtkinter as ctk
from typing import Callable
from src.utils.validators import validate_positive_decimal


class InputSection(ctk.CTkFrame):
    """Секция для добавления новой покупки"""
    
    def __init__(self, parent, on_add: Callable[[float, float], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_add = on_add
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса секции ввода"""
        # Заголовок
        title = ctk.CTkLabel(
            self,
            text="Dodaj zakup",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=(0, 8))
        
        # Контейнер для полей ввода
        inputs_frame = ctk.CTkFrame(self)
        inputs_frame.pack(fill="x", pady=0)
        
        # Поле "Сумма вложений"
        investment_label = ctk.CTkLabel(
            inputs_frame,
            text="Suma inwestycji:",
            font=ctk.CTkFont(size=11)
        )
        investment_label.grid(row=0, column=0, padx=12, pady=6, sticky="w")
        
        self.investment_entry = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="0.00",
            width=180,
            font=ctk.CTkFont(size=11)
        )
        self.investment_entry.grid(row=0, column=1, padx=12, pady=6)
        self.investment_entry.bind("<Return>", lambda e: self._on_add_clicked())
        
        # Поле "Цена покупки"
        price_label = ctk.CTkLabel(
            inputs_frame,
            text="Cena zakupu:",
            font=ctk.CTkFont(size=11)
        )
        price_label.grid(row=1, column=0, padx=12, pady=6, sticky="w")
        
        self.price_entry = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="0.00",
            width=180,
            font=ctk.CTkFont(size=11)
        )
        self.price_entry.grid(row=1, column=1, padx=12, pady=6)
        self.price_entry.bind("<Return>", lambda e: self._on_add_clicked())
        
        # Сообщение об ошибке
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=10)
        )
        self.error_label.pack(pady=(3, 0))
        
        # Кнопка добавления
        self.add_button = ctk.CTkButton(
            self,
            text="➕ Dodaj zakup",
            command=self._on_add_clicked,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=30
        )
        self.add_button.pack(pady=(8, 0))
    
    def _on_add_clicked(self):
        """Обработчик нажатия кнопки добавления"""
        investment_str = self.investment_entry.get()
        price_str = self.price_entry.get()
        
        # Валидация
        inv_valid, inv_error, investment = validate_positive_decimal(investment_str)
        price_valid, price_error, price = validate_positive_decimal(price_str)
        
        if not inv_valid:
            self.error_label.configure(text=inv_error)
            return
        
        if not price_valid:
            self.error_label.configure(text=price_error)
            return
        
        # Очищаем ошибки и вызываем callback
        self.error_label.configure(text="")
        self.on_add(float(investment), float(price))
        
        # Очищаем поля и устанавливаем фокус
        self.investment_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.after(10, lambda: self.investment_entry.focus_set())
    
    def clear_error(self):
        """Очищает сообщение об ошибке"""
        self.error_label.configure(text="")

