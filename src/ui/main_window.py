import customtkinter as ctk
from decimal import Decimal
from src.services.asset_manager import AssetManager
from src.services.calculator import Calculator
from src.ui.components.purchase_table import PurchaseTable
from src.ui.components.input_section import InputSection
from src.ui.components.results_section import ResultsSection
from src.ui.components.planning_section import PlanningSection
from src.ui.components.asset_selector import AssetSelector
from src.utils.currency import Currency


class MainWindow(ctk.CTk):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация менеджера активов
        self.asset_manager = AssetManager()
        
        # Настройка окна
        self.title("Kalkulator uśredniania (Punkt bezstratny)")
        self.geometry("750x650")
        self.minsize(650, 550)
        
        # Настройка темы
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
        
        # Загружаем список активов и обновляем селектор
        # (вызывается после создания всех компонентов)
        self.after(100, self._initialize_assets)
    
    def _initialize_assets(self):
        """Инициализирует список активов после создания UI"""
        assets = self.asset_manager.list_assets()
        self.asset_selector.update_assets_list(assets)
    
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
        main_container.grid_rowconfigure(4, weight=1, minsize=120)  # Таблица может изменять размер
        
        # Верхняя панель: заголовок
        header = ctk.CTkLabel(
            main_container,
            text="Kalkulator uśredniania",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Селектор активов
        self.asset_selector = AssetSelector(
            main_container,
            on_asset_selected=self._on_asset_selected,
            on_asset_created=self._on_asset_created,
            on_asset_deleted=self._on_asset_deleted,
            existing_assets=[],
            get_current_currency=lambda: self._get_current_currency_from_menu()
        )
        self.asset_selector.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Верхняя панель: выбор валюты
        top_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        top_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(0, weight=1)
        
        currency_label = ctk.CTkLabel(
            top_frame,
            text="Waluta:",
            font=ctk.CTkFont(size=12)
        )
        currency_label.grid(row=0, column=0, padx=(0, 5), sticky="e")
        
        self.currency_menu = ctk.CTkOptionMenu(
            top_frame,
            values=[f"{c.symbol} ({c.code})" for c in Currency],
            command=self._on_currency_change,
            width=120,
            font=ctk.CTkFont(size=11)
        )
        self.currency_menu.set(f"{Currency.USD.symbol} ({Currency.USD.code})")
        self.currency_menu.grid(row=0, column=1, sticky="e")
        
        # Горизонтальный контейнер для результатов и ввода
        results_input_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        results_input_frame.grid(row=3, column=0, pady=(0, 10), sticky="ew")
        results_input_frame.grid_columnconfigure(0, weight=1)
        results_input_frame.grid_columnconfigure(1, weight=1)
        
        # Секция результатов (слева)
        self.results_section = ResultsSection(
            results_input_frame,
            currency=Currency.USD
        )
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
            currency=Currency.USD
        )
        self.purchase_table.grid(row=4, column=0, pady=(0, 10), sticky="nsew")
        
        # Секция планирования
        self.planning_section = PlanningSection(
            main_container,
            on_drawdown_change=self._on_drawdown_change,
            currency=Currency.USD
        )
        self.planning_section.grid(row=5, column=0, sticky="ew")
    
    def _on_asset_selected(self, asset_name: str):
        """Обработчик выбора актива"""
        asset = self.asset_manager.load_asset(asset_name)
        if asset:
            self._load_asset_data(asset)
            # Обновляем селектор
            self.asset_selector.set_current_asset(asset_name)
            # Обновляем заголовок окна
            self.title(f"Kalkulator uśredniania - {asset_name}")
    
    def _on_asset_created(self, asset_name: str, currency: Currency):
        """Обработчик создания нового актива"""
        asset = self.asset_manager.create_asset(asset_name, currency)
        self._load_asset_data(asset)
        # Обновляем список активов
        assets = self.asset_manager.list_assets()
        self.asset_selector.update_assets_list(assets)
        # Обновляем селектор
        self.asset_selector.set_current_asset(asset_name)
        # Обновляем заголовок окна
        self.title(f"Kalkulator uśredniania - {asset_name}")
    
    def _on_asset_deleted(self, asset_name: str):
        """Обработчик удаления актива"""
        success = self.asset_manager.delete_asset(asset_name)
        if success:
            # Очищаем интерфейс
            self._clear_ui()
            # Обновляем заголовок окна
            self.title("Kalkulator uśredniania (Punkt bezstratny)")
            # Обновляем список активов
            assets = self.asset_manager.list_assets()
            self.asset_selector.update_assets_list(assets)
    
    def _load_asset_data(self, asset):
        """Загружает данные актива в интерфейс"""
        # Обновляем валюту
        currency = asset.currency
        self.currency_menu.set(f"{currency.symbol} ({currency.code})")
        
        # Обновляем процент просадки
        drawdown = asset.drawdown_percent
        self.planning_section.drawdown_entry.delete(0, "end")
        self.planning_section.drawdown_entry.insert(0, str(drawdown))
        
        # Обновляем все компоненты
        self._update_all()
    
    def _clear_ui(self):
        """Очищает интерфейс"""
        self.purchase_table.update_purchases([], Currency.USD)
        self.results_section.update_results(None, None, None, Currency.USD)
        self.planning_section.update_planning(None, Decimal('15.0'), None, Currency.USD)
    
    def _get_current_currency_from_menu(self) -> Currency:
        """Возвращает текущую валюту из меню"""
        value = self.currency_menu.get()
        for currency in Currency:
            if f"{currency.symbol} ({currency.code})" == value:
                return currency
        return Currency.USD
    
    def _on_currency_change(self, value: str):
        """Обработчик изменения валюты"""
        # Находим валюту по символу и коду
        currency = Currency.USD
        for c in Currency:
            if f"{c.symbol} ({c.code})" == value:
                currency = c
                break
        
        # Обновляем валюту в текущем активе
        if self.asset_manager.current_asset:
            self.asset_manager.set_currency(currency)
        
        # Обновляем все компоненты с новой валютой
        self.results_section.set_currency(currency)
        self.purchase_table.set_currency(currency)
        self.planning_section.set_currency(currency)
        self._update_all()
    
    def _on_add_purchase(self, investment: float, price: float):
        """Обработчик добавления покупки"""
        if not self.asset_manager.current_asset:
            self.input_section.error_label.configure(text="Najpierw wybierz lub utwórz aktyw")
            return
        
        try:
            investment_decimal = Decimal(str(investment))
            price_decimal = Decimal(str(price))
            
            self.asset_manager.add_purchase(investment_decimal, price_decimal)
            # Автоматическое сохранение уже происходит в AssetManager
            self._update_all()
        except ValueError as e:
            self.input_section.error_label.configure(text=str(e))
    
    def _on_delete_purchase(self, purchase_id: int):
        """Обработчик удаления покупки"""
        if not self.asset_manager.current_asset:
            return
        
        self.asset_manager.remove_purchase(purchase_id)
        # Автоматическое сохранение уже происходит в AssetManager
        self._update_all()
    
    def _on_drawdown_change(self, drawdown: Decimal):
        """Обработчик изменения процента просадки"""
        if self.asset_manager.current_asset:
            self.asset_manager.set_drawdown_percent(drawdown)
            # Автоматическое сохранение уже происходит в AssetManager
        self._update_planning()
    
    def _update_all(self):
        """Обновляет все секции интерфейса"""
        if not self.asset_manager.current_asset:
            self._clear_ui()
            return
        
        purchases = self.asset_manager.get_all_purchases()
        currency = self.asset_manager.get_currency()
        
        # Обновляем таблицу
        self.purchase_table.update_purchases(purchases, currency)
        
        # Обновляем результаты
        total_investment = Calculator.calculate_total_investment(purchases) if purchases else None
        total_quantity = Calculator.calculate_total_quantity(purchases) if purchases else None
        break_even = Calculator.calculate_break_even(purchases)
        
        self.results_section.update_results(
            total_investment,
            total_quantity,
            break_even,
            currency
        )
        
        # Обновляем планирование
        self._update_planning()
    
    def _update_planning(self):
        """Обновляет секцию планирования"""
        if not self.asset_manager.current_asset:
            return
        
        last_purchase = self.asset_manager.get_last_purchase()
        last_price = last_purchase.price if last_purchase else None
        
        drawdown = self.asset_manager.get_drawdown_percent()
        currency = self.asset_manager.get_currency()
        
        next_price = None
        if last_price:
            try:
                next_price = Calculator.calculate_next_purchase_price(
                    last_price,
                    drawdown
                )
            except ValueError:
                pass
        
        self.planning_section.update_planning(
            last_price,
            drawdown,
            next_price,
            currency
        )

