from enum import Enum


class Currency(Enum):
    """Поддерживаемые валюты"""
    PLN = ("zł", "PLN", "Polski złoty")
    USD = ("$", "USD", "US Dollar")
    EUR = ("€", "EUR", "Euro")
    GBP = ("£", "GBP", "British Pound")
    BTC = ("₿", "BTC", "Bitcoin")
    ETH = ("Ξ", "ETH", "Ethereum")
    
    def __init__(self, symbol, code, full_name):
        self.symbol = symbol
        self.code = code
        self.full_name = full_name
    
    def __str__(self):
        return f"{self.symbol} ({self.code})"

