import customtkinter as ctk
from typing import Callable, Optional
from src.utils.currency import Currency


class AssetSelector(ctk.CTkFrame):
    """Компонент для выбора, создания и удаления активов"""
    
    def __init__(
        self,
        parent,
        on_asset_selected: Callable[[str], None],
        on_asset_created: Callable[[str, Currency], None],
        on_asset_deleted: Callable[[str], None],
        on_currency_change: Callable[[Currency], None],
        existing_assets: list[str] = None,
        get_current_currency: Callable[[], Currency] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.on_asset_selected = on_asset_selected
        self.on_asset_created = on_asset_created
        self.on_asset_deleted = on_asset_deleted
        self.on_currency_change = on_currency_change
        self.get_current_currency = get_current_currency
        self.all_assets = existing_assets or []  # Полный список активов
        self.filtered_assets = self.all_assets.copy()  # Отфильтрованный список
        self.current_asset: Optional[str] = None
        self.search_results_frame = None  # Выпадающий список результатов
        self._setup_ui()
        self._update_assets_list()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Настройка grid
        self.grid_columnconfigure(1, weight=1)
        
        # Заголовок
        title = ctk.CTkLabel(
            self,
            text="Aktyw:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Выбор существующего актива (используем ComboBox для интерактивного поиска)
        self.asset_menu = ctk.CTkComboBox(
            self,
            values=["Nowy aktyw..."] + self.filtered_assets,
            command=self._on_asset_menu_change,
            width=150,
            font=ctk.CTkFont(size=11)
        )
        self.asset_menu.grid(row=0, column=1, padx=(0, 10), sticky="w")
        
        # Поле ввода для нового актива
        self.new_asset_entry = ctk.CTkEntry(
            self,
            placeholder_text="Nazwa aktywu",
            width=150,
            font=ctk.CTkFont(size=11)
        )
        self.new_asset_entry.grid(row=0, column=2, padx=(0, 10), sticky="w")
        self.new_asset_entry.bind("<Return>", lambda e: self._on_create_clicked())
        
        # Кнопка создания
        self.create_button = ctk.CTkButton(
            self,
            text="Utwórz",
            command=self._on_create_clicked,
            width=80,
            font=ctk.CTkFont(size=11)
        )
        self.create_button.grid(row=0, column=3, padx=(0, 10), sticky="w")
        
        # Кнопка удаления
        self.delete_button = ctk.CTkButton(
            self,
            text="Usuń aktyw",
            command=self._on_delete_clicked,
            width=100,
            fg_color="red",
            hover_color="darkred",
            font=ctk.CTkFont(size=11)
        )
        self.delete_button.grid(row=0, column=4, padx=(0, 10), sticky="w")
        self.delete_button.grid_remove()  # Скрываем по умолчанию
        
        # Выбор валюты (справа на том же уровне)
        currency_label = ctk.CTkLabel(
            self,
            text="Waluta:",
            font=ctk.CTkFont(size=12)
        )
        currency_label.grid(row=0, column=5, padx=(10, 5), sticky="e")
        
        self.currency_menu = ctk.CTkOptionMenu(
            self,
            values=[f"{c.symbol} ({c.code})" for c in Currency],
            command=self._on_currency_change,
            width=120,
            font=ctk.CTkFont(size=11)
        )
        # По умолчанию USD, можно обновить позже через set_currency
        self.currency_menu.set(f"{Currency.USD.symbol} ({Currency.USD.code})")
        self.currency_menu.grid(row=0, column=6, sticky="e")
        
        # Поле поиска активов
        search_label = ctk.CTkLabel(
            self,
            text="Szukaj:",
            font=ctk.CTkFont(size=11)
        )
        search_label.grid(row=1, column=0, padx=(0, 10), sticky="w", pady=(8, 0))
        
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Szukaj aktywu...",
            width=200,
            font=ctk.CTkFont(size=11)
        )
        self.search_entry.grid(row=1, column=1, padx=(0, 10), sticky="w", pady=(8, 0))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        
        # Кнопка "Szukaj"
        self.search_button = ctk.CTkButton(
            self,
            text="Szukaj",
            command=self._on_search_button_clicked,
            width=70,
            font=ctk.CTkFont(size=11)
        )
        self.search_button.grid(row=1, column=2, padx=(0, 10), sticky="w", pady=(8, 0))
        
        # Индикатор результатов поиска
        self.search_indicator = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        self.search_indicator.grid(row=1, column=3, padx=(0, 10), sticky="w", pady=(8, 0))
        
        # Сообщение об ошибке
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=10)
        )
        self.error_label.grid(row=1, column=4, columnspan=3, sticky="w", pady=(8, 0))
        
        # Выпадающий список результатов поиска (создается динамически)
        self._create_search_results_frame()
    
    def _on_currency_change(self, value: str):
        """Обработчик изменения валюты"""
        for currency in Currency:
            if f"{currency.symbol} ({currency.code})" == value:
                self.on_currency_change(currency)
                break
    
    def _create_search_results_frame(self):
        """Создает выпадающий список результатов поиска"""
        # Создаем фрейм для результатов (будет позиционироваться через place)
        self.search_results_frame = ctk.CTkFrame(self, border_width=1, corner_radius=5)
        self.search_results_frame.place_forget()  # Скрываем по умолчанию
        
        # Прокручиваемый контейнер для результатов
        self.search_results_scroll = ctk.CTkScrollableFrame(
            self.search_results_frame,
            width=200,
            height=150
        )
        self.search_results_scroll.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Привязываем клик на фрейм результатов, чтобы он не скрывался при клике на него
        self.search_results_frame.bind("<Button-1>", lambda e: "break")
        self.search_results_scroll.bind("<Button-1>", lambda e: "break")
    
    def _show_search_results(self):
        """Показывает выпадающий список результатов"""
        if not self.search_results_frame:
            return
        
        search_text = self.search_entry.get().strip()
        if not search_text or not self.filtered_assets:
            self._hide_search_results()
            return
        
        # Очищаем предыдущие результаты
        for widget in self.search_results_scroll.winfo_children():
            widget.destroy()
        
        # Добавляем кнопки для каждого найденного актива
        for asset in sorted(self.filtered_assets):
            btn = ctk.CTkButton(
                self.search_results_scroll,
                text=asset,
                command=lambda a=asset: self._select_search_result(a),
                width=190,
                height=30,
                font=ctk.CTkFont(size=11),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.pack(fill="x", padx=2, pady=1)
        
        # Позиционируем и показываем список под полем поиска
        self._position_search_results()
        
        # Поднимаем поверх других элементов
        self.search_results_frame.lift()
        
        # Обновляем геометрию для правильного отображения
        self.update_idletasks()
    
    def _position_search_results(self):
        """Позиционирует выпадающий список под полем поиска"""
        if not self.search_results_frame:
            return
        
        # Обновляем геометрию для получения актуальных координат
        self.update_idletasks()
        
        # Получаем координаты поля поиска относительно родительского виджета
        search_x = self.search_entry.winfo_x()
        search_y = self.search_entry.winfo_y()
        search_height = self.search_entry.winfo_height()
        
        # Позиционируем под полем поиска
        x = search_x
        y = search_y + search_height + 2
        
        # Показываем фрейм с правильной позицией
        self.search_results_frame.place(in_=self, x=x, y=y)
    
    def _hide_search_results(self):
        """Скрывает выпадающий список результатов"""
        if self.search_results_frame:
            self.search_results_frame.place_forget()
    
    def _select_search_result(self, asset_name: str):
        """Обработчик выбора результата из списка поиска"""
        # Сначала скрываем результаты, чтобы избежать проблем с фокусом
        self._hide_search_results()
        
        # Устанавливаем актив
        self.current_asset = asset_name
        self.asset_menu.set(asset_name)
        self.delete_button.grid()
        self.on_asset_selected(asset_name)
        self.error_label.configure(text="")
        
        # Очищаем поиск
        self.search_entry.delete(0, "end")
        self.search_indicator.configure(text="")
        self._on_search_changed()
    
    def _on_search_button_clicked(self):
        """Обработчик нажатия кнопки 'Szukaj'"""
        # Сначала выполняем поиск
        self._on_search_changed()
        
        # Показываем результаты если есть текст и найдены активы
        search_text = self.search_entry.get().strip()
        if search_text and self.filtered_assets:
            # Даем фокус полю поиска, чтобы список показался
            self.search_entry.focus_set()
            self._show_search_results()
        elif search_text and not self.filtered_assets:
            # Если текст есть, но результатов нет - скрываем список
            self._hide_search_results()
        else:
            # Если текста нет - скрываем список
            self._hide_search_results()
    
    def _on_search_focus_in(self, event=None):
        """Обработчик получения фокуса полем поиска"""
        search_text = self.search_entry.get().strip()
        if search_text and self.filtered_assets:
            self._show_search_results()
    
    def _on_search_focus_out(self, event=None):
        """Обработчик потери фокуса полем поиска"""
        # Проверяем, не кликнули ли мы на результаты поиска
        if event and event.widget:
            # Если клик был на фрейме результатов или его дочерних элементах, не скрываем
            widget = event.widget
            while widget:
                if widget == self.search_results_frame:
                    return  # Клик был на списке результатов, не скрываем
                widget = widget.master
        
        # Увеличиваем задержку, чтобы клик по результату успел обработаться
        self.after(200, self._check_and_hide_results)
    
    def _check_and_hide_results(self):
        """Проверяет и скрывает результаты, если фокус не на поле поиска или списке"""
        # Проверяем, есть ли фокус на поле поиска или списке результатов
        focus_widget = self.focus_get()
        if focus_widget != self.search_entry:
            # Проверяем, не является ли виджет с фокусом частью списка результатов
            widget = focus_widget
            while widget:
                if widget == self.search_results_frame:
                    return  # Фокус на списке результатов, не скрываем
                widget = widget.master if hasattr(widget, 'master') else None
            self._hide_search_results()
    
    def _on_search_changed(self, event=None):
        """Обработчик изменения текста поиска"""
        search_text = self.search_entry.get().strip().lower()
        
        if not search_text:
            self.filtered_assets = self.all_assets.copy()
            self.search_indicator.configure(text="")
            self._hide_search_results()
        else:
            self.filtered_assets = [
                asset for asset in self.all_assets
                if search_text in asset.lower()
            ]
            # Обновляем индикатор результатов
            count = len(self.filtered_assets)
            if count == 0:
                self.search_indicator.configure(text="Brak wyników", text_color="red")
                self._hide_search_results()
            else:
                self.search_indicator.configure(
                    text=f"Znaleziono: {count}",
                    text_color=("gray50", "gray50")
                )
                # Показываем результаты если поле поиска в фокусе
                if self.search_entry.focus_get() == self.search_entry:
                    self._show_search_results()
        
        # Обновляем список в комбобоксе
        self._update_assets_list()
    
    def _on_asset_menu_change(self, value: str):
        """Обработчик изменения выбранного актива"""
        if not value or value == "Nowy aktyw...":
            return
        
        self.current_asset = value
        self.delete_button.grid()  # Показываем кнопку удаления
        self.on_asset_selected(value)
        self.error_label.configure(text="")
        # Очищаем поиск после выбора
        self.search_entry.delete(0, "end")
        self.search_indicator.configure(text="")
        self._hide_search_results()
        self._on_search_changed()
    
    def _on_create_clicked(self):
        """Обработчик создания нового актива"""
        asset_name = self.new_asset_entry.get().strip()
        
        if not asset_name:
            self.error_label.configure(text="Wprowadź nazwę aktywu")
            return
        
        # Проверяем, не существует ли уже такой актив
        if asset_name in self.all_assets:
            self.error_label.configure(text=f"Aktyw '{asset_name}' już istnieje")
            return
        
        # Валидация имени файла (убираем недопустимые символы)
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in asset_name for char in invalid_chars):
            self.error_label.configure(text="Nazwa zawiera niedozwolone znaki")
            return
        
        self.error_label.configure(text="")
        self.new_asset_entry.delete(0, "end")
        
        # Создаем актив с текущей валютой или USD по умолчанию
        currency = Currency.USD
        if self.get_current_currency:
            currency = self.get_current_currency()
        self.on_asset_created(asset_name, currency)
        
        # Обновляем список
        self.all_assets.append(asset_name)
        self.filtered_assets = self.all_assets.copy()
        self._update_assets_list()
        
        # Выбираем созданный актив
        self.asset_menu.set(asset_name)
        self.current_asset = asset_name
        self.delete_button.grid()
    
    def _on_delete_clicked(self):
        """Обработчик удаления актива"""
        if not self.current_asset:
            return
        
        # Подтверждение удаления
        import tkinter.messagebox as messagebox
        result = messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz usunąć aktyw '{self.current_asset}'?\n"
            f"Wszystkie dane zostaną trwale usunięte."
        )
        
        if result:
            self.on_asset_deleted(self.current_asset)
            
            # Удаляем из списка
            if self.current_asset in self.all_assets:
                self.all_assets.remove(self.current_asset)
            if self.current_asset in self.filtered_assets:
                self.filtered_assets.remove(self.current_asset)
            
            self.current_asset = None
            self._update_assets_list()
            self.delete_button.grid_remove()
            self.error_label.configure(text="")
            # Очищаем поиск
            self.search_entry.delete(0, "end")
            self.search_indicator.configure(text="")
            self._hide_search_results()
            self._on_search_changed()
    
    def _update_assets_list(self):
        """Обновляет список активов в комбобоксе"""
        values = ["Nowy aktyw..."] + sorted(self.filtered_assets)
        
        # Сохраняем текущее значение перед обновлением
        current_value = self.asset_menu.get()
        
        # Обновляем список значений
        self.asset_menu.configure(values=values)
        
        # Восстанавливаем или устанавливаем правильное значение
        if not self.current_asset or self.current_asset not in self.filtered_assets:
            # Если текущий актив не в отфильтрованном списке, сбрасываем
            if current_value not in values:
                self.asset_menu.set("Nowy aktyw...")
        elif self.current_asset in self.filtered_assets:
            # Если текущий актив в списке, устанавливаем его
            self.asset_menu.set(self.current_asset)
        elif current_value in values:
            # Если предыдущее значение все еще в списке, оставляем его
            self.asset_menu.set(current_value)
        else:
            # Иначе сбрасываем
            self.asset_menu.set("Nowy aktyw...")
    
    def set_current_asset(self, asset_name: str):
        """Устанавливает текущий актив"""
        if asset_name in self.all_assets:
            self.current_asset = asset_name
            # Обновляем отфильтрованный список, чтобы актив был виден
            if asset_name not in self.filtered_assets:
                self.filtered_assets = self.all_assets.copy()
                self.search_entry.delete(0, "end")
            self._update_assets_list()
            self.delete_button.grid()
        else:
            self.current_asset = None
            self._update_assets_list()
            self.delete_button.grid_remove()
    
    def update_assets_list(self, assets: list[str]):
        """Обновляет список доступных активов"""
        self.all_assets = assets
        self.filtered_assets = assets.copy()
        self._update_assets_list()
    
    def get_currency_menu(self):
        """Возвращает меню валют для доступа извне"""
        return self.currency_menu
    
    def set_currency(self, currency: Currency):
        """Устанавливает валюту в меню"""
        self.currency_menu.set(f"{currency.symbol} ({currency.code})")

