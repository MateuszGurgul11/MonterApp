# 🔄 SYSTEM WORKFLOW MONTER-SPRZEDAWCA

## 📖 Opis systemu

Nowy system umożliwia dwuetapowe wypełnianie formularzy:
1. **Monter** - wykonuje pomiary i specyfikację techniczną
2. **Sprzedawca** - uzupełnia dane produktu i finalizuje zamówienie

## 🚀 Jak to działa?

### Etap 1: Monter 👷‍♂️
1. Otwiera stronę **"Monter"**
2. Wybiera tryb **"🔧 Pomiary (Monter)"**
3. Wypełnia swoje ID i dane pomiarów
4. Zapisuje formularz
5. **Otrzymuje kod dostępu i QR kod**
6. Przekazuje kod sprzedawcy

### Etap 2: Sprzedawca 👔
1. Otwiera stronę **"Monter"**
2. Wybiera tryb **"💼 Sprzedaż (Sprzedawca)"**
3. Ma dwie opcje dostępu:
   - **🔑 Kod dostępu** - wprowadza kod od montera
   - **📋 Lista formularzy** - wybiera z listy oczekujących
4. Uzupełnia dane produktu
5. Finalizuje zamówienie

## 📱 Sposoby udostępniania

### 1. Kod dostępu
- **Format:** 8-znakowy kod (np. `AB12CD34`)
- **Użycie:** Monter podaje kod sprzedawcy
- **Bezpieczny:** Unikalny dla każdego formularza

### 2. QR Code
- **Automatyczne generowanie** przy zapisie pomiarów
- **Zawiera:** Kod dostępu + ID formularza + typ
- **Użycie:** Sprzedawca skanuje QR code

### 3. Lista formularzy
- **Sprzedawca** widzi wszystkie formularze oczekujące
- **Filtry:** Data, klient, pomieszczenie
- **Wybór:** Kliknięcie na formularz

## 🔄 Statusy formularzy

| Status | Opis | Ikona |
|--------|------|-------|
| `pomiary_wykonane` | Monter zakończył pomiary | 📏 |
| `aktywny` | Sprzedawca sfinalizował | ✅ |
| `zakończony` | Zamówienie zakończone | 🏁 |
| `anulowany` | Zamówienie anulowane | ❌ |

## 🔍 Śledzenie procesu

### W przegląd danych:
- **Etap:** Pokazuje czy pomiary czy kompletny
- **Wypełnił:** Kto wypełnił (Monter/Sprzedawca)
- **Kod dostępu:** Widoczny dla montera/sprzedawcy
- **Data pomiarów/sprzedaży:** Kiedy został wypełniony każdy etap

## 💡 Zalety systemu

### ✅ Dla montera:
- Skupia się tylko na pomiarach
- Nie musi znać wszystkich produktów
- Szybkie wypełnianie
- Bezpieczne udostępnianie

### ✅ Dla sprzedawcy:
- Dostęp do pomiarów z terenu
- Może pracować zdalnie
- Skupia się na sprzedaży
- Wszystkie informacje techniczne dostępne

### ✅ Dla firmy:
- Lepszy podział pracy
- Szybsza obsługa klientów
- Mniej błędów
- Pełna kontrola procesu

## 🛠️ Instrukcja użytkowania

### Dla montera:

1. **Otwórz aplikację** na telefonie/tablecie
2. **Idź do strony "Monter"**
3. **Wybierz "🔧 Pomiary (Monter)"**
4. **Wybierz co mierzysz:** 🚪 Drzwi lub 🏠 Podłogi
5. **Wprowadź swoje ID** (np. nazwisko lub kod)

#### Dla drzwi:
6. **Wypełnij podstawowe informacje:**
   - Pomieszczenie, Nazwisko klienta, Telefon klienta
7. **Wykonaj i wprowadź pomiary:**
   - Szerokość/wysokość otworu
   - Grubość muru, Stan ściany
   - Typ drzwi, Strona otwierania
8. **Kliknij "💾 Zapisz pomiary"**

#### Dla podłóg:
6. **Wypełnij podstawowe informacje:**
   - Pomieszczenie, Telefon klienta
7. **Wybierz system montażu** (symetrycznie/niesymetrycznie)
8. **Wprowadź specyfikację:**
   - Podkład, czy MDF możliwy
9. **Wprowadź pomiary listw:** NW, NZ, Ł, ZL, ZP
10. **Podaj listwy progowe:** jaka, ile, gdzie
11. **Kliknij "💾 Zapisz pomiary podłóg"**

#### Finalnie:
9. **Przekaż sprzedawcy:**
   - Kod dostępu (8 znaków)
   - LUB QR code do zeskanowania

### Dla sprzedawcy:

#### Opcja A: Kod dostępu
1. **Otwórz aplikację**
2. **Idź do strony "Monter"**
3. **Wybierz "💼 Sprzedaż (Sprzedawca)"**
4. **Wybierz typ produktu:** 🚪 Drzwi lub 🏠 Podłogi
5. **Wybierz "🔑 Kod dostępu"**
6. **Wprowadź kod** otrzymany od montera
7. **Kliknij "🔍 Znajdź formularz"**

#### Opcja B: Lista formularzy
1. **Otwórz aplikację**
2. **Idź do strony "Monter"**
3. **Wybierz "💼 Sprzedaż (Sprzedawca)"**
4. **Wybierz typ produktu:** 🚪 Drzwi lub 🏠 Podłogi
5. **Wybierz "📋 Lista formularzy do uzupełnienia"**
6. **Wybierz formularz** z listy

#### Dalsze kroki dla drzwi:
7. **Sprawdź pomiary** (sekcja tylko do odczytu)
8. **Wprowadź swoje ID**
9. **Wypełnij dane produktu:**
   - Producent, seria, typ
   - Rodzaj okleiny, szyby
   - Zamek, klamka, dodatki
10. **Dodaj uwagi dla klienta**
11. **Kliknij "✅ Finalizuj zamówienie"**

#### Dalsze kroki dla podłóg:
7. **Sprawdź pomiary** (sekcja tylko do odczytu)
8. **Wprowadź swoje ID**
9. **Wypełnij dane produktu:**
   - Rodzaj podłogi, seria, kolor
   - Folia, listwa przypodłogowa
10. **Dodaj uwagi dla klienta**
11. **Kliknij "✅ Finalizuj zamówienie podłóg"**

## 🔒 Bezpieczeństwo

- **Unikalne kody dostępu** dla każdego formularza
- **Śledzenie ID** montera i sprzedawcy
- **Znaczniki czasowe** dla każdego etapu
- **Niemożność edycji** pomiarów przez sprzedawcę
- **Kontrola dostępu** przez kody

## 📄 Generowanie PDF

### Po finalizacji zamówienia:
- **Automatyczny przycisk pobierania PDF** pojawia się po ukończeniu
- **Stylowy dokument** z logo firmy i profesjonalnym formatowaniem
- **Kompletne dane** od montera i sprzedawcy w jednym dokumencie

### Zawartość PDF:
#### Dla drzwi:
- Informacje podstawowe (klient, kontakt, data)
- Pomiary otworu (wymiary, specyfikacja)
- Dane techniczne (typ, ościeżnica, strona otwierania)
- **🎨 DIAGRAM DRZWI** - wizualna ilustracja kierunku otwierania
- Dane produktu (producent, seria, zamek, klamka)
- Uwagi i opcje dodatkowe
- Historia wykonawców (monter, sprzedawca, daty)

#### Dla podłóg:
- Informacje podstawowe (klient, kontakt, data)
- System montażu i specyfikacja
- Pomiary listw (szczegółowy breakdown)
- Dane produktu (rodzaj, seria, kolor, folia)
- Uwagi i ostrzeżenia
- Historia wykonawców

### Dostęp do PDF:
1. **Po finalizacji** - przycisk pojawia się automatycznie
2. **W przegląd danych** - dla każdego rekordu osobno
3. **Format nazwy:** `typ_pomieszczenie_data_ID.pdf`

## 📊 Raporty i analiza

System umożliwia analizę:
- **Czas wykonania** pomiarów vs sprzedaży
- **Efektywność** montera/sprzedawcy
- **Najpopularniejsze produkty**
- **Statystyki** według regionów/montera
- **Dokumenty PDF** do archiwizacji i wysyłki

## 🛠️ Instalacja dodatkowych pakietów

```bash
# Zainstaluj wymagane pakiety
pip install reportlab qrcode[pil] firebase-admin

# Test generatora PDF (opcjonalnie)
python test_pdf.py
```

### 🎨 Nowe funkcje w PDF:

#### **Ilustracje drzwi:**
- **Automatyczne rysowanie** diagramów kierunku otwierania
- **Kolorowe strzałki** pokazujące ruch drzwi
- **Złota klamka** w odpowiedniej pozycji
- **Etykiety** z opisem (LEWE/PRAWE PRZYLGOWE/ODWROTNA)

#### **Polskie znaki:**
- **Automatyczna konwersja** problematycznych znaków
- **Fallback system** dla różnych fontów systemowych
- **Bezpieczne kodowanie** UTF-8 gdzie to możliwe

#### **Przykłady diagramów:**
- 🚪 **Lewe przylgowe** - łuk otwierania w lewo z przodu
- 🚪 **Prawe przylgowe** - łuk otwierania w prawo z przodu  
- 🚪 **Lewe odwrotna** - łuk otwierania w lewo do tyłu
- 🚪 **Prawe odwrotna** - łuk otwierania w prawo do tyłu

---

**Potrzebujesz pomocy?** Skontaktuj się z administratorem systemu.