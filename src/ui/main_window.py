import customtkinter as ctk
from decimal import Decimal
from src.services.purchase_manager import PurchaseManager
from src.services.calculator import Calculator
from src.ui.components.purchase_table import PurchaseTable
from src.ui.components.input_section import InputSection
from src.ui.components.results_section import ResultsSection
from src.ui.components.planning_section import PlanningSection
from src.utils.currency import Currency


class MainWindow(ctk.CTk):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация менеджера покупок
        self.purchase_manager = PurchaseManager()
        self.drawdown_percent = Decimal('15.0')
        self.currency = Currency.USD  # Валюта по умолчанию
        
        # Настройка окна
        self.title("Kalkulator uśredniania (Punkt bezstratny)")
        self.geometry("750x650")
        self.minsize(650, 550)
        
        # Настройка темы
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
        self._update_all()
    
    def _setup_ui(self):
        """Настройка интерфейса главного окна"""
        # Главный контейнер с прокруткой
        main_scrollable = ctk.CTkScrollableFrame(self)
        main_scrollable.pack(fill="both", expand=True, padx=15, pady=15)
        main_scrollable.grid_columnconfigure(0, weight=1)
        
        # Внутренний контейнер для правильного размещения элементов
        main_container = ctk.CTkFrame(main_scrollable, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Настройка grid для управления размерами
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1, minsize=120)  # Таблица может изменять размер
        
        # Верхняя панель: заголовок и выбор валюты
        top_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkLabel(
            top_frame,
            text="Kalkulator uśredniania",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w")
        
        # Выбор валюты
        currency_label = ctk.CTkLabel(
            top_frame,
            text="Waluta:",
            font=ctk.CTkFont(size=12)
        )
        currency_label.grid(row=0, column=1, padx=(20, 5), sticky="e")
        
        self.currency_menu = ctk.CTkOptionMenu(
            top_frame,
            values=[f"{c.symbol} ({c.code})" for c in Currency],
            command=self._on_currency_change,
            width=120,
            font=ctk.CTkFont(size=11)
        )
        self.currency_menu.set(f"{Currency.USD.symbol} ({Currency.USD.code})")
        self.currency_menu.grid(row=0, column=2, sticky="e")
        
        # Горизонтальный контейнер для результатов и ввода
        results_input_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        results_input_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        results_input_frame.grid_columnconfigure(0, weight=1)
        results_input_frame.grid_columnconfigure(1, weight=1)
        
        # Секция результатов (слева)
        self.results_section = ResultsSection(results_input_frame, currency=self.currency)
        self.results_section.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        
        # Секция добавления покупки (справа)
        self.input_section = InputSection(
            results_input_frame,
            on_add=self._on_add_purchase
        )
        self.input_section.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        
        # Секция истории покупок (с возможностью изменения размера)
        self.purchase_table = PurchaseTable(
            main_container,
            on_delete=self._on_delete_purchase,
            currency=self.currency
        )
        self.purchase_table.grid(row=2, column=0, pady=(0, 10), sticky="nsew")
        
        # Секция планирования
        self.planning_section = PlanningSection(
            main_container,
            on_drawdown_change=self._on_drawdown_change,
            currency=self.currency
        )
        self.planning_section.grid(row=4, column=0, sticky="ew")
    
    def _on_currency_change(self, value: str):
        """Обработчик изменения валюты"""
        # Находим валюту по символу и коду
        for currency in Currency:
            if f"{currency.symbol} ({currency.code})" == value:
                self.currency = currency
                break
        
        # Обновляем все компоненты с новой валютой
        self.results_section.set_currency(self.currency)
        self.purchase_table.set_currency(self.currency)
        self.planning_section.set_currency(self.currency)
        self._update_all()
    
    def _on_add_purchase(self, investment: float, price: float):
        """Обработчик добавления покупки"""
        try:
            investment_decimal = Decimal(str(investment))
            price_decimal = Decimal(str(price))
            
            self.purchase_manager.add_purchase(investment_decimal, price_decimal)
            self._update_all()
        except ValueError as e:
            self.input_section.error_label.configure(text=str(e))
    
    def _on_delete_purchase(self, purchase_id: int):
        """Обработчик удаления покупки"""
        self.purchase_manager.remove_purchase(purchase_id)
        self._update_all()
    
    def _on_drawdown_change(self, drawdown: Decimal):
        """Обработчик изменения процента просадки"""
        self.drawdown_percent = drawdown
        self._update_planning()
    
    def _update_all(self):
        """Обновляет все секции интерфейса"""
        purchases = self.purchase_manager.get_all_purchases()
        
        # Обновляем таблицу
        self.purchase_table.update_purchases(purchases, self.currency)
        
        # Обновляем результаты
        total_investment = Calculator.calculate_total_investment(purchases) if purchases else None
        total_quantity = Calculator.calculate_total_quantity(purchases) if purchases else None
        break_even = Calculator.calculate_break_even(purchases)
        
        self.results_section.update_results(
            total_investment,
            total_quantity,
            break_even,
            self.currency
        )
        
        # Обновляем планирование
        self._update_planning()
    
    def _update_planning(self):
        """Обновляет секцию планирования"""
        last_purchase = self.purchase_manager.get_last_purchase()
        last_price = last_purchase.price if last_purchase else None
        
        next_price = None
        if last_price:
            try:
                next_price = Calculator.calculate_next_purchase_price(
                    last_price,
                    self.drawdown_percent
                )
            except ValueError:
                pass
        
        self.planning_section.update_planning(
            last_price,
            self.drawdown_percent,
            next_price,
            self.currency
        )

