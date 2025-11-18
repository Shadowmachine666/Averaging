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
        existing_assets: list[str] = None,
        get_current_currency: Callable[[], Currency] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.on_asset_selected = on_asset_selected
        self.on_asset_created = on_asset_created
        self.on_asset_deleted = on_asset_deleted
        self.get_current_currency = get_current_currency
        self.existing_assets = existing_assets or []
        self.current_asset: Optional[str] = None
        self._setup_ui()
        self._update_assets_list()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        title = ctk.CTkLabel(
            self,
            text="Aktyw:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Выбор существующего актива
        self.asset_menu = ctk.CTkOptionMenu(
            self,
            values=["Nowy aktyw..."] + self.existing_assets,
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
        self.delete_button.grid(row=0, column=4, sticky="w")
        self.delete_button.grid_remove()  # Скрываем по умолчанию
        
        # Сообщение об ошибке
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=10)
        )
        self.error_label.grid(row=1, column=0, columnspan=5, sticky="w", pady=(5, 0))
    
    def _on_asset_menu_change(self, value: str):
        """Обработчик изменения выбранного актива"""
        if value == "Nowy aktyw...":
            return
        
        self.current_asset = value
        self.delete_button.grid()  # Показываем кнопку удаления
        self.on_asset_selected(value)
        self.error_label.configure(text="")
    
    def _on_create_clicked(self):
        """Обработчик создания нового актива"""
        asset_name = self.new_asset_entry.get().strip()
        
        if not asset_name:
            self.error_label.configure(text="Wprowadź nazwę aktywu")
            return
        
        # Проверяем, не существует ли уже такой актив
        if asset_name in self.existing_assets:
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
        self.existing_assets.append(asset_name)
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
            if self.current_asset in self.existing_assets:
                self.existing_assets.remove(self.current_asset)
            
            self.current_asset = None
            self._update_assets_list()
            self.delete_button.grid_remove()
            self.error_label.configure(text="")
    
    def _update_assets_list(self):
        """Обновляет список активов в меню"""
        values = ["Nowy aktyw..."] + sorted(self.existing_assets)
        self.asset_menu.configure(values=values)
        if not self.current_asset:
            self.asset_menu.set("Nowy aktyw...")
    
    def set_current_asset(self, asset_name: str):
        """Устанавливает текущий актив"""
        if asset_name in self.existing_assets:
            self.current_asset = asset_name
            self.asset_menu.set(asset_name)
            self.delete_button.grid()
        else:
            self.current_asset = None
            self.asset_menu.set("Nowy aktyw...")
            self.delete_button.grid_remove()
    
    def update_assets_list(self, assets: list[str]):
        """Обновляет список доступных активов"""
        self.existing_assets = assets
        self._update_assets_list()

