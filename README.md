# Kalkulator uśredniania (Punkt bezstratny)

Kalkulator do obliczania średniej ceny wejścia (punktu bezstratnego) po kilku zakupach jednego aktywa oraz prognozowania ceny następnego zakupu przy zadanym spadku.

## Instalacja

1. Zainstaluj wymagane zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python main.py
```

## Funkcje

- **Dodawanie zakupów**: Wprowadź sumę inwestycji i cenę zakupu
- **Historia zakupów**: Przeglądaj wszystkie zakupy w formie tabeli
- **Obliczanie punktu bezstratnego**: Automatyczne obliczanie średniej ceny wejścia
- **Planowanie następnego zakupu**: Prognozowanie ceny przy zadanym procencie spadku

## Struktura projektu

```
averaging/
├── src/
│   ├── models/          # Modele danych
│   ├── services/        # Logika biznesowa
│   ├── ui/              # Interfejs użytkownika
│   └── utils/           # Narzędzia pomocnicze
└── main.py              # Punkt wejścia
```

