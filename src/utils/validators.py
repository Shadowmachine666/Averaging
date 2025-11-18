from decimal import Decimal, InvalidOperation


def validate_positive_decimal(value: str) -> tuple[bool, str, Decimal | None]:
    """
    Валидирует строку как положительное десятичное число
    Возвращает: (is_valid, error_message, decimal_value)
    """
    if not value or not value.strip():
        return False, "Поле не может быть пустым", None
    
    try:
        # Заменяем запятую на точку для поддержки обоих форматов
        normalized_value = value.replace(',', '.')
        decimal_value = Decimal(normalized_value)
        
        if decimal_value <= 0:
            return False, "Значение должно быть больше нуля", None
        
        return True, "", decimal_value
    
    except (InvalidOperation, ValueError):
        return False, "Введите корректное число", None


def validate_percent(value: str) -> tuple[bool, str, Decimal | None]:
    """
    Валидирует процент (0-100)
    Возвращает: (is_valid, error_message, decimal_value)
    """
    if not value or not value.strip():
        return False, "Поле не может быть пустым", None
    
    try:
        normalized_value = value.replace(',', '.')
        decimal_value = Decimal(normalized_value)
        
        if decimal_value < 0 or decimal_value > 100:
            return False, "Процент должен быть от 0 до 100", None
        
        return True, "", decimal_value
    
    except (InvalidOperation, ValueError):
        return False, "Введите корректное число", None

