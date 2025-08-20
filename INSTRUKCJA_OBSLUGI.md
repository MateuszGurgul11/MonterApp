# 📚 ROZBUDOWANA INSTRUKCJA OBSŁUGI APLIKACJI POMIARÓW

## 🎯 SPIS TREŚCI
1. [Wprowadzenie do systemu](#wprowadzenie-do-systemu)
2. [Struktura aplikacji](#struktura-aplikacji)
3. [Instrukcja dla Montera](#instrukcja-dla-montera)
4. [Instrukcja dla Sprzedawcy](#instrukcja-dla-sprzedawcy)
5. [System szkiców (kwarantanna)](#system-szkiców-kwarantanna)
6. [Foldery klientów](#foldery-klientów)
7. [Przegląd bazy danych](#przegląd-bazy-danych)
8. [Generowanie PDF](#generowanie-pdf)
9. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
10. [Często zadawane pytania](#często-zadawane-pytania)

---

## 🚀 WPROWADZENIE DO SYSTEMU

### Czym jest ta aplikacja?
Aplikacja **WORKFLOW MONTER-SPRZEDAWCA** to kompleksowy system do zarządzania pomiarami i zamówieniami produktów budowlanych. System umożliwia dwuetapowy proces:

1. **MONTER** 👷‍♂️ - wykonuje pomiary techniczne
2. **SPRZEDAWCA** 👔 - uzupełnia dane produktu i finalizuje zamówienie

### Kluczowe zalety:
- ✅ **Podział odpowiedzialności** - każdy robi to, co umie najlepiej
- ✅ **Mobilność** - dostęp z telefonu/tabletu/komputera
- ✅ **Bezpieczeństwo** - unikalne kody dostępu
- ✅ **Śledzenie procesu** - pełna kontrola nad statusem zamówień
- ✅ **Automatyzacja** - generowanie PDF, organizacja folderów
- ✅ **Praca offline** - system szkiców umożliwia pracę bez internetu

---

## 🏗️ STRUKTURA APLIKACJI

### Główne sekcje:

#### 📍 **Strona główna** (`main.py`)
- Podsumowanie statystyk bazy danych
- Podgląd wszystkich rekordów
- Możliwość usuwania rekordów
- Status połączenia z Firebase

#### 📝 **Formularz** (`pages/Formularz.py`)
- **Tryb Montera**: Formularze pomiarów
- **Tryb Sprzedawcy**: Uzupełnianie danych produktu
- Obsługa 3 typów produktów:
  - 🚪 **Drzwi** (standardowe)
  - 🚨 **Drzwi wejściowe** (zewnętrzne)
  - 🏠 **Podłogi**

#### 🗂️ **Wymiary** (`pages/Wymiary.py`)
- System szkiców/kwarantanny
- Edycja pomiarów przed zapisem
- Finalizacja szkiców

#### 📁 **Foldery** (`pages/Foldery.py`)
- Wirtualne foldery klientów
- Grupowanie pomiarów według klienta i daty
- Zaawansowane filtry

---

## 👷‍♂️ INSTRUKCJA DLA MONTERA

### 🚀 SZYBKI START

1. **Otwórz aplikację** w przeglądarce
2. **Przejdź do sekcji "Formularz"**
3. **Wybierz tryb "🔧 Pomiary (Monter)"**
4. **Wprowadź swoje ID** (np. imię i nazwisko)
5. **Wybierz typ produktu** do pomiarów

### 📏 POMIARY DRZWI STANDARDOWYCH

#### Krok 1: Podstawowe informacje
```
🏠 Pomieszczenie: np. "Salon", "Kuchnia", "Łazienka"
👤 Imię i Nazwisko: Imię i nazwisko klienta
📞 Telefon: Numer telefonu klienta (ważne dla folderów!)
```

#### Krok 2: Wymiary otworu
```
📐 Szerokość otworu: [cm]
📐 Wysokość otworu: [cm]
🧱 Grubość muru: [cm]
```

#### Krok 3: Dane techniczne
```
🏗️ Stan ściany: np. "tapeta", "płytki", "tynk"
🔧 Typ drzwi: Wybierz z listy
🔄 Strona otwierania: Na zewnątrz/do wewnątrz + lewe/prawe
```

#### Krok 4: Zapis
- **💾 Zapisz pomiary** - natychmiastowy zapis do bazy
- **🗂️ Zapisz do kwarantanny** - zapis szkicu do edycji

### 🚨 POMIARY DRZWI WEJŚCIOWYCH

Podobnie jak drzwi standardowe, ale z dodatkowymi polami:

#### Dodatkowe informacje:
```
📄 Numer strony: Numer protokołu
📏 Mierzona od: szkołówka/poziomu/podłogi/inne
🏗️ Skrót: Dodatkowy opis
🏠 Ościeżnica: Specyfikacja ościeżnicy
🌧️ Okapnik: Informacje o okapniku
🚪 Próg: Specyfikacja progu
👁️ Wizjer: Tak/Nie
🔌 Elektrozaczep: Opis elektrozaczępu
```

### 🏠 POMIARY PODŁÓG

#### Krok 1: Podstawowe informacje
```
🏠 Pomieszczenie: nazwa pomieszczenia
👤 Imię i Nazwisko: klient
📞 Telefon: numer telefonu
```

#### Krok 2: System montażu
```
🔧 System montażu: symetrycznie/niesymetrycznie
```

#### Krok 3: Specyfikacja
```
🏗️ Podkład: opis podkładu
📦 MDF możliwy: Tak/Nie
```

#### Krok 4: Pomiary listw
```
📏 NW (Narożnik Wewnętrzny): [mb]
📏 NZ (Narożnik Zewnętrzny): [mb]
📏 Ł (Ściana): [mb]
📏 ZL (Listwa Zaokrąglona Lewa): [mb]
📏 ZP (Listwa Zaokrąglona Prawa): [mb]
```

#### Krok 5: Listwy progowe
```
🚪 Jaka: opis typu listwy
🔢 Ile: ilość
📍 Gdzie: lokalizacja
```

### 💡 WSKAZÓWKI DLA MONTERA

#### ✅ DOBRE PRAKTYKI:
- **Dokładnie mierz** - błędy w pomiarach są kosztowne
- **Używaj szkiców** - jeśli nie jesteś pewien, zapisz szkic
- **Sprawdź telefon** - ostatnie 3 cyfry są ważne dla folderów
- **Opisuj stan ściany** - to pomoże w doborze produktu
- **Rób zdjęcia** - jako backup informacji

#### ⚠️ UWAGI:
- **Internet** - potrzebujesz połączenia do zapisu w bazie
- **Szkice** - działają bez internetu, zsynchronizują się później
- **Kody dostępu** - zawsze zapisz/sfotografuj kod dla sprzedawcy
- **Podwójne sprawdzenie** - skontroluj pomiary przed zapisem

### 📱 PRZEKAZYWANIE DANYCH SPRZEDAWCY

Po zapisaniu pomiarów otrzymasz:

#### 🔑 KOD DOSTĘPU
```
Format: AB12CD34 (8 znaków)
Użycie: Podaj sprzedawcy
```

#### 📱 QR CODE (jeśli dostępny)
```
Zawiera: kod dostępu + ID formularza
Użycie: Sprzedawca skanuje kodem
```

---

## 👔 INSTRUKCJA DLA SPRZEDAWCY

### 🚀 SZYBKI START

1. **Otwórz aplikację**
2. **Przejdź do sekcji "Formularz"**
3. **Wybierz tryb "💼 Sprzedaż (Sprzedawca)"**
4. **Wybierz typ produktu**
5. **Znajdź formularz** (kod lub lista)

### 🔍 SPOSOBY DOSTĘPU DO FORMULARZY

#### Opcja A: 🔑 KOD DOSTĘPU
```
1. Wybierz "🔑 Kod dostępu"
2. Wprowadź 8-znakowy kod od montera
3. Kliknij "🔍 Znajdź formularz"
4. Formularz się załaduje automatycznie
```

#### Opcja B: 📋 LISTA FORMULARZY
```
1. Wybierz "📋 Lista formularzy do uzupełnienia"
2. Użyj filtrów folderów (opcjonalnie)
3. Wybierz formularz z listy
4. Kliknij na wybrany rekord
```

### 💼 UZUPEŁNIANIE DANYCH DRZWI

#### Sekcja: Dane produktu
```
🏭 Producent: wybierz z listy lub dodaj nowy
🚪 Model: model drzwi
🎨 Kolor: kolor drzwi
🔧 Typ zamka: specyfikacja zamka
🔑 Ilość kluczy: liczba kluczy
💰 Cena: cena produktu [zł]
```

#### Sekcja: Dane klienta (dodatkowe)
```
📧 Email: adres email klienta
📍 Adres: pełny adres instalacji
📅 Preferowana data: data realizacji
📝 Uwagi: dodatkowe informacje
```

#### Sekcja: Specyfikacja (dodatkowa)
```
📐 Kierunek otwierania: weryfikacja/korekta
🔧 Dodatkowe wyposażenie: okucia, dodatki
⚙️ Specjalne wymagania: nietypowe specyfikacje
```

### 🚨 UZUPEŁNIANIE DANYCH DRZWI WEJŚCIOWYCH

Podobnie jak drzwi standardowe, plus:

#### Dodatkowe pola:
```
🛡️ Klasa bezpieczeństwa: wybierz klasę
🌡️ Izolacyjność termiczna: parametry
🔊 Izolacyjność akustyczna: parametry
🌧️ Odporność na warunki: zewnętrzne/wewnętrzne
🎨 Wykończenie zewnętrzne: materiał/kolor
🎨 Wykończenie wewnętrzne: materiał/kolor
```

### 🏠 UZUPEŁNIANIE DANYCH PODŁÓG

#### Dane produktu:
```
🏭 Producent: producent podłogi
📦 Seria/Kolekcja: nazwa serii
🎨 Kolor/Dekor: opis koloru
📏 Grubość: grubość paneli [mm]
📐 Wymiary panela: długość x szerokość
💰 Cena za m²: cena za metr kwadratowy
📦 Cena listwy: cena za mb listwy
```

#### Dane instalacji:
```
📅 Data montażu: planowana data
🔧 Typ montażu: klejona/pływająca/gwoździowana
🏗️ Przygotowanie podłoża: wymagania
📝 Uwagi montażowe: specjalne instrukcje
```

### 📄 FINALIZACJA ZAMÓWIENIA

Po uzupełnieniu wszystkich danych:

#### 1. SPRAWDZENIE
- ✅ Wszystkie pola wypełnione
- ✅ Ceny wprowadzone
- ✅ Dane kontaktowe poprawne

#### 2. FINALIZACJA
```
🏁 Finalizuj zamówienie: kliknij przycisk
📄 Zostanie wygenerowany PDF
💾 Zamówienie zostanie zapisane jako "aktywne"
```

#### 3. PDF ZAMÓWIENIA
- **Automatyczne generowanie**
- **Pełne dane techniczne i handlowe**
- **Gotowe do wysłania/druku**

---

## 🗂️ SYSTEM SZKICÓW (KWARANTANNA)

### 📝 CZYM SĄ SZKICE?

Szkice to pomiary zapisane tymczasowo, które:
- **Nie trafiają** od razu do głównej bazy
- **Można edytować** w dowolnym momencie
- **Działają offline** - zsynchronizują się gdy będzie internet
- **Można finalizować** - przenieść do głównej bazy

### 🔧 JAK KORZYSTAĆ ZE SZKICÓW?

#### Dla Montera:
```
1. Wypełnij formularz pomiarów
2. Zamiast "💾 Zapisz pomiary" kliknij "🗂️ Zapisz do kwarantanny"
3. Szkic zostanie zapisany lokalnie
4. Możesz wrócić i edytować szkic w sekcji "Wymiary"
```

#### Zarządzanie szkicami (sekcja "Wymiary"):
```
1. Przejdź do sekcji "🗂️ Wymiary"
2. Wprowadź swoje ID montera (filtr)
3. Zobacz listę swoich szkiców
4. Dla każdego szkicu możesz:
   - ✏️ Edytować
   - 🗑️ Usunąć
   - ✅ Sfinalizować (przenieść do bazy)
```

### 📋 EDYCJA SZKICÓW

#### Dostępne opcje edycji:

**Dla drzwi standardowych:**
- Wszystkie podstawowe pola
- Wymiary otworu
- Dane techniczne
- Strona otwierania

**Dla drzwi wejściowych:**
- Wszystkie pola z protokołu
- Dane techniczne
- Specyfikacja kompletna

**Dla podłóg:**
- Podstawowe informacje
- System montażu
- Wszystkie pomiary listw
- Specyfikacja podkładu

### ✅ FINALIZACJA SZKICÓW

```
1. Wybierz szkic do finalizacji
2. Sprawdź wszystkie dane
3. Kliknij "✅ Finalizuj szkic"
4. Szkic zostanie przeniesiony do głównej bazy
5. Otrzymasz kod dostępu dla sprzedawcy
6. Szkic zostanie automatycznie usunięty
```

---

## 📁 FOLDERY KLIENTÓW

### 🎯 SYSTEM WIRTUALNYCH FOLDERÓW

Aplikacja automatycznie organizuje pomiary w wirtualne foldery według wzorca:
```
Format: imie_nazwisko_XXX_DD_MM_YYYY
Przykład: jan_kowalski_321_14_08_2025

Gdzie:
- imie_nazwisko: znormalizowane imię i nazwisko
- XXX: ostatnie 3 cyfry numeru telefonu
- DD_MM_YYYY: dzień, miesiąc, rok pomiaru
```

### 🔍 PRZEGLĄDANIE FOLDERÓW

#### Dostęp:
```
1. Przejdź do sekcji "📁 Foldery"
2. Zobacz listę wszystkich folderów klientów
3. Użyj filtrów do wyszukiwania
4. Kliknij folder aby zobaczyć szczegóły
```

#### Dostępne filtry:
```
📅 Zakres dat:
   - Wszystko
   - Dziś
   - Ostatnie 7 dni
   - Ostatnie 30 dni
   - Zakres niestandardowy

👷‍♂️ Monter: filtruj po imieniu montera

📋 Typ pomiaru:
   - 🚪 Drzwi
   - 🚨 Drzwi wejściowe
   - 🏠 Podłogi
```

### 📊 INFORMACJE W FOLDERACH

Dla każdego folderu zobaczysz:
```
👤 Klient: imię i nazwisko
📞 Telefon: pełny numer (z ostatnimi 3 cyframi)
📅 Data: data pierwszego pomiaru
📊 Liczba pomiarów: ilość rekordów w folderze
📋 Typy: jakie typy produktów zmierzono
👷‍♂️ Monter: kto wykonał pomiary
```

### 🔎 FILTRY DLA SPRZEDAWCY

W formularzach sprzedawcy możesz filtrować po folderach:
```
1. W trybie sprzedawcy wybierz "📋 Lista formularzy"
2. Użyj listy "Folder klienta" na górze
3. Wybierz konkretny folder
4. Zobacz tylko pomiary z tego folderu
```

---

## 📊 PRZEGLĄD BAZY DANYCH

### 🏠 STRONA GŁÓWNA - DASHBOARD

#### Statystyki:
```
📊 Rekordy drzwi: liczba pomiarów drzwi
📊 Rekordy podłóg: liczba pomiarów podłóg
📊 Drzwi wejściowe: liczba pomiarów drzwi zewnętrznych
```

#### Podgląd danych:
```
🚪 Zakładka "Drzwi": wszystkie pomiary drzwi
🚨 Zakładka "Drzwi wejściowe": pomiary drzwi zewnętrznych
🏠 Zakładka "Podłogi": wszystkie pomiary podłóg
🗂️ Zakładka "Szkice": wszystkie szkice/kwarantanna
```

### 🔍 FUNKCJE PRZEGLĄDU

#### Dla każdego rekordu:
```
👁️ Podgląd JSON: pełne dane w formacie JSON
🗑️ Usuń: usunięcie rekordu z bazy (nieodwracalne!)
📄 Szczegóły: wszystkie pola w czytelnej formie
```

#### Tabela zawiera:
```
🆔 ID: unikalny identyfikator
👤 Klient: imię i nazwisko
📞 Telefon: numer telefonu
🏠 Pomieszczenie: lokalizacja
👷‍♂️ Monter: kto wykonał pomiary
📅 Data: kiedy wykonano pomiary
📋 Status: status zamówienia
🔑 Kod: kod dostępu (jeśli dostępny)
```

### ⚠️ UWAGI BEZPIECZEŃSTWA

#### Usuwanie rekordów:
- **Nieodwracalne** - nie ma kosza!
- **Tylko dla administratora** - potwierdź przed usunięciem
- **Backup** - zrób kopię przed usuwaniem ważnych danych
- **Sprawdź dwukrotnie** - upewnij się co usuwasz

---

## 📄 GENEROWANIE PDF

### 🎯 AUTOMATYCZNE GENEROWANIE

PDF jest generowany automatycznie przy finalizacji zamówienia przez sprzedawcę:

#### Zawartość PDF:

**Dla drzwi standardowych:**
```
📋 Nagłówek z logo i danymi firmy
👤 Dane klienta (imię, telefon, adres)
📏 Wymiary techniczne
🔧 Specyfikacja produktu
💰 Informacje handlowe
👷‍♂️ Dane montera i sprzedawcy
📅 Daty pomiarów i finalizacji
```

**Dla drzwi wejściowych:**
```
📋 Protokół kompletny
🛡️ Specyfikacja bezpieczeństwa
🌡️ Parametry izolacyjności
🎨 Wykończenia zewnętrzne/wewnętrzne
🔧 Wszystkie dane techniczne
💰 Kalkulacja kosztów
```

**Dla podłóg:**
```
📏 Wszystkie pomiary listw
🔧 Specyfikacja montażu
📦 Dane produktu
💰 Kalkulacja powierzchni i kosztów
🏗️ Wymagania podłoża
📅 Harmonogram montażu
```

### 💾 POBIERANIE PDF

```
1. PDF generuje się automatycznie po finalizacji
2. Pojawi się link do pobrania
3. Kliknij aby pobrać plik
4. PDF można wysłać mailem lub wydrukować
```

### 🔧 ROZWIĄZYWANIE PROBLEMÓW Z PDF

#### Jeśli PDF się nie generuje:
```
✅ Sprawdź czy wszystkie wymagane pola są wypełnione
✅ Sprawdź połączenie internetowe
✅ Odśwież stronę i spróbuj ponownie
✅ Sprawdź czy dane są kompletne
```

#### Błędy generowania:
```
❌ "Brak wymaganych danych" - uzupełnij wszystkie pola
❌ "Błąd formatowania" - sprawdź poprawność dat/liczb
❌ "Błąd serwera" - skontaktuj się z administratorem
```

---

## 🛠️ ROZWIĄZYWANIE PROBLEMÓW

### 🔥 NAJCZĘSTSZE PROBLEMY

#### 1. ❌ Brak połączenia z bazą danych
```
Objawy: "Baza danych nie jest zainicjalizowana"
Rozwiązania:
✅ Sprawdź połączenie internetowe
✅ Odśwież stronę (F5)
✅ Kliknij "🔄 Clear cache and retry"
✅ Skontaktuj się z administratorem
```

#### 2. 🚫 Nie można zapisać pomiarów
```
Objawy: "Błąd podczas zapisywania"
Rozwiązania:
✅ Sprawdź czy wszystkie wymagane pola są wypełnione
✅ Sprawdź połączenie internetowe
✅ Spróbuj zapisać jako szkic
✅ Odśwież stronę i spróbuj ponownie
```

#### 3. 🔍 Nie można znaleźć formularza
```
Objawy: "Formularz nie został znaleziony"
Rozwiązania:
✅ Sprawdź czy kod dostępu jest poprawny (8 znaków)
✅ Sprawdź czy formularz nie został już sfinalizowany
✅ Użyj listy formularzy zamiast kodu
✅ Skontaktuj się z monterem w sprawie kodu
```

#### 4. 📱 Problemy na urządzeniach mobilnych
```
Objawy: Elementy nie działają na telefonie
Rozwiązania:
✅ Użyj przeglądarki Chrome lub Safari
✅ Sprawdź czy masz najnowszą wersję przeglądarki
✅ Wyczyść cache przeglądarki
✅ Spróbuj w trybie prywatnym/incognito
```

#### 5. 🐌 Aplikacja działa wolno
```
Przyczyny i rozwiązania:
✅ Słabe połączenie internetowe - sprawdź WiFi/dane
✅ Przeładowana baza danych - skontaktuj się z administratorem
✅ Problem z przeglądarką - wypróbuj inną przeglądarkę
✅ Cache przeglądarki - wyczyść cache
```

### 🔧 KROK PO KROKU - TROUBLESHOOTING

#### Gdy coś nie działa:

```
1. ODŚWIEŻ STRONĘ
   - Naciśnij F5 lub Ctrl+R
   - Na telefonie pociągnij w dół

2. SPRAWDŹ INTERNET
   - Otwórz inną stronę internetową
   - Sprawdź czy masz połączenie

3. WYCZYŚĆ CACHE
   - Naciśnij Ctrl+Shift+Delete
   - Wyczyść cache i ciasteczka
   - Uruchom ponownie przeglądarkę

4. WYPRÓBUJ INNĄ PRZEGLĄDARKĘ
   - Chrome, Firefox, Safari, Edge
   - Sprawdź czy problem występuje wszędzie

5. SPRAWDŹ DANE
   - Czy wszystkie pola są wypełnione?
   - Czy numery telefonu są poprawne?
   - Czy nie ma błędów w tekście?

6. SKONTAKTUJ SIĘ Z POMOCĄ
   - Opisz dokładnie problem
   - Podaj kroki które wykonałeś
   - Załącz screenshot jeśli możliwe
```

### 📞 KONTAKT W SPRAWIE PROBLEMÓW

```
📧 Email: [podaj email administratora]
📱 Telefon: [podaj numer telefonu]
⏰ Godziny pomocy: [podaj godziny]

Przy zgłaszaniu problemu podaj:
🔹 Jaki problem występuje?
🔹 Kiedy się pojawił?
🔹 Jakie kroki wykonałeś?
🔹 Jakiej przeglądarki używasz?
🔹 Czy to telefon czy komputer?
```

---

## ❓ CZĘSTO ZADAWANE PYTANIA

### 🔑 KODY DOSTĘPU

**Q: Jak długo ważny jest kod dostępu?**
A: Kod jest ważny do momentu sfinalizowania zamówienia przez sprzedawcę.

**Q: Co zrobić gdy zgubię kod dostępu?**
A: Sprzedawca może użyć listy formularzy zamiast kodu. Kod można również odczytać ze strony głównej w podglądzie bazy danych.

**Q: Czy kod może się powtórzyć?**
A: Nie, każdy kod jest unikalny i generowany automatycznie.

### 💾 ZAPISYWANIE DANYCH

**Q: Czy dane są automatycznie zapisywane?**
A: Nie, musisz kliknąć przycisk "Zapisz". Szkice można zapisywać bez internetu.

**Q: Co się stanie gdy stracę internet podczas wypełniania?**
A: Użyj opcji "Zapisz do kwarantanny" - dane zapiszą się lokalnie i zsynchronizują gdy wróci internet.

**Q: Czy mogę edytować dane po zapisaniu?**
A: Dane główne nie - ale szkice tak. Zawsze sprawdź dane przed finalizacją.

### 📱 URZĄDZENIA I PRZEGLĄDARKI

**Q: Które przeglądarki są obsługiwane?**
A: Chrome, Firefox, Safari, Edge. Najlepiej działa w Chrome.

**Q: Czy aplikacja działa na telefonie?**
A: Tak, jest w pełni responsywna. Najlepiej działa na tabletach i większych telefonach.

**Q: Czy potrzebuję instalować aplikację?**
A: Nie, to aplikacja webowa - wystarczy przeglądarka.

### 👥 ROLE I UPRAWNIENIA

**Q: Czy monter może uzupełniać dane sprzedaży?**
A: Nie, system rozdziela role. Monter może tylko pomiary i szkice.

**Q: Czy sprzedawca może edytować pomiary?**
A: Nie, sprzedawca może tylko uzupełniać dane produktu. Pomiary są niezmienne.

**Q: Kto może usuwać rekordy?**
A: Tylko administrator w sekcji przeglądu bazy danych.

### 📊 ORGANIZACJA DANYCH

**Q: Jak działają foldery klientów?**
A: To wirtualne foldery bazujące na imieniu, nazwisku, telefonie i dacie. Organizują się automatycznie.

**Q: Dlaczego ważne są ostatnie 3 cyfry telefonu?**
A: Służą do unikalnej identyfikacji klienta w systemie folderów.

**Q: Czy mogę zmienić nazwę folderu?**
A: Nie, nazwy generują się automatycznie według stałego wzorca.

### 📄 PDF I DOKUMENTY

**Q: Kiedy generuje się PDF?**
A: Automatycznie po finalizacji zamówienia przez sprzedawcę.

**Q: Czy mogę wygenerować PDF przed finalizacją?**
A: Nie, PDF jest dostępny tylko dla kompletnych zamówień.

**Q: W jakim formacie jest PDF?**
A: Standardowy PDF A4, gotowy do druku i wysłania mailem.

### 🔧 PROBLEMY TECHNICZNE

**Q: Aplikacja nie ładuje się - co robić?**
A: Sprawdź internet, odśwież stronę, wyczyść cache przeglądarki, wypróbuj inną przeglądarkę.

**Q: Dane znikają po odświeżeniu strony?**
A: Streamlit nie zapisuje danych w formularzach. Zawsze kliknij "Zapisz" przed odświeżeniem.

**Q: Czy mogę pracować offline?**
A: Częściowo - szkice można zapisywać offline, ale główne funkcje wymagają internetu.

---

## 🎓 NAJLEPSZE PRAKTYKI

### 👷‍♂️ DLA MONTERÓW

#### ✅ DOBRE NAWYKI:
- **Zawsze rób pomiary dwukrotnie** - sprawdź przed zapisem
- **Używaj szkiców przy wątpliwościach** - lepiej bezpiecznie
- **Fotografuj trudne miejsca** - jako backup
- **Sprawdzaj numery telefonu** - ważne dla folderów
- **Opisuj stan ściany dokładnie** - pomoże w doborze produktu

#### ❌ CZEGO UNIKAĆ:
- Nie zapisuj niepewnych pomiarów od razu do bazy
- Nie pomijaj pól "uwagi" - czasem są kluczowe
- Nie zapominaj o kodzie dostępu dla sprzedawcy
- Nie pracuj bez szkiców w trudnych warunkach internetowych

### 👔 DLA SPRZEDAWCÓW

#### ✅ DOBRE NAWYKI:
- **Sprawdzaj pomiary montera** - czy są logiczne
- **Wypełniaj wszystkie pola** - kompletne dane to lepsze PDF
- **Używaj filtrów folderów** - szybsze znajdowanie klientów
- **Sprawdzaj ceny przed finalizacją** - błąd jest kosztowny
- **Kontaktuj się z klientem** - potwierdź specyfikację

#### ❌ CZEGO UNIKAĆ:
- Nie finalizuj zamówień z niepełnymi danymi
- Nie pomijaj kontaktu z klientem przy wątpliwościach
- Nie zapisuj błędnych cen - trudno je później zmienić
- Nie ignoruj uwag montera w pomiarach

### 🏢 DLA ADMINISTRATORÓW

#### ✅ DOBRE NAWYKI:
- **Regularnie sprawdzaj bazę danych** - czyszczenie błędnych rekordów
- **Monitoruj szkice** - pomagaj w finalizacji zawieszonych
- **Rób kopie zapasowe** - Firebase nie zawsze wystarczy
- **Szkolij użytkowników** - mniej problemów technicznych
- **Aktualizuj instrukcje** - wraz z rozwojem aplikacji

#### ❌ CZEGO UNIKAĆ:
- Nie usuwaj rekordów bez potwierdzenia użytkowników
- Nie zmieniaj struktury bazy bez testów
- Nie ignoruj raportów o błędach
- Nie zapominaj o aktualizacji dokumentacji

---

## 🚀 ROZWÓJ I PRZYSZŁOŚĆ

### 🔮 PLANOWANE FUNKCJE

- **📧 Wysyłanie PDF mailem** - bezpośrednio z aplikacji
- **📱 Aplikacja mobilna** - dedykowana aplikacja na telefon
- **🔔 Powiadomienia** - o nowych zamówieniach i statusach
- **📊 Raporty i statystyki** - analiza sprzedaży i efektywności
- **🔄 Synchronizacja offline** - pełna praca bez internetu
- **👥 Zarządzanie zespołem** - przypisywanie zadań
- **🎨 Personalizacja** - motywy i ustawienia użytkownika

### 💡 SUGESTIE I FEEDBACK

Masz pomysł na ulepszenie? Skontaktuj się:
- **📧 Email**: [email do sugestii]
- **📝 Formularz**: [link do formularza feedback]

Każda sugestja jest ważna i pomaga rozwijać aplikację!

---

## 📋 PODSUMOWANIE

### 🎯 KLUCZOWE PUNKTY:

1. **System dwuetapowy** - monter + sprzedawca = efektywność
2. **Szkice to bezpieczeństwo** - możliwość edycji przed finalizacją
3. **Foldery organizują** - automatyczne grupowanie klientów
4. **PDF to finał** - kompletna dokumentacja zamówienia
5. **Mobilność** - praca w terenie na każdym urządzeniu

### 🏆 SUKCES TO:
- ✅ Dokładne pomiary
- ✅ Kompletne dane
- ✅ Sprawna komunikacja monter-sprzedawca
- ✅ Zadowolony klient

---

**📞 POMOC I WSPARCIE**

W razie problemów nie wahaj się skontaktować z zespołem wsparcia. Jesteśmy tutaj, żeby pomóc!

---

*Instrukcja wersja 1.0 - [data]*
*© [Nazwa firmy] - Wszystkie prawa zastrzeżone*
