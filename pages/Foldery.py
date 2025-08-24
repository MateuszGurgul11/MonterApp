import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import unicodedata
import re

from firebase_config import (
    setup_database,
    get_all_drzwi,
    get_all_podlogi,
    get_all_drzwi_wejsciowe,
    get_document_by_id,
    update_document,
    display_images
)
from pdf_generator import display_pdf_download_button

# ZABEZPIECZENIE - sprawdź logowanie przed załadowaniem strony
if not st.session_state.get('logged_in', False):
    st.error("🚫 **Dostęp zabroniony** - Wymagane logowanie!")
    st.markdown("### 👆 [Przejdź do logowania](?)")
    if st.button("🔙 Powrót do logowania", type="primary"):
        st.switch_page("main.py")
    st.stop()


def _normalize_name(text: str) -> str:
    if not text:
        return "nieznany_klient"
    norm = unicodedata.normalize('NFKD', text)
    norm = norm.encode('ascii', 'ignore').decode('ascii')
    norm = re.sub(r'[^a-zA-Z0-9]+', '_', norm).strip('_').lower()
    return norm or "nieznany_klient"



def _as_dt(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return datetime.min
    return datetime.min


def _folder_name(rec: dict) -> tuple[str, datetime]:
    name = rec.get('imie_nazwisko') or rec.get('nazwisko') or ''
    # preferuj data_pomiary, w przeciwnym razie data_utworzenia
    dt = _as_dt(rec.get('data_pomiary') or rec.get('data_utworzenia'))
    day = dt.strftime('%d') if dt != datetime.min else '00'
    month = dt.strftime('%m') if dt != datetime.min else '00'
    year = dt.strftime('%Y') if dt != datetime.min else '0000'

    n = _normalize_name(name)
    folder = f"{n}_{day}_{month}_{year}"
    return folder, dt


def page_foldery():
    st.set_page_config(page_title="Foldery klientów", layout="wide")
    st.title("📁 Foldery klientów (wirtualne)")

    db = setup_database()
    if db is None:
        st.error("❌ Brak połączenia z bazą danych")
        st.stop()

    with st.spinner("Ładowanie danych..."):
        drzwi = get_all_drzwi(db)
        podlogi = get_all_podlogi(db)
        drzwi_wejsciowe = get_all_drzwi_wejsciowe(db)

    # Przygotuj rekordy z typem
    all_records = []
    for r in drzwi:
        r2 = r.copy()
        r2['__type'] = 'drzwi'
        all_records.append(r2)
    for r in podlogi:
        r2 = r.copy()
        r2['__type'] = 'podlogi'
        all_records.append(r2)
    for r in drzwi_wejsciowe:
        r2 = r.copy()
        r2['__type'] = 'drzwi_wejsciowe'
        all_records.append(r2)

    # Filtry
    st.subheader("🔎 Filtry")
    
    # Pierwszy rząd filtrów
    col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.2, 1.4, 1.2])
    with col_f1:
        date_filter = st.selectbox(
            "Zakres dat:",
            ["Wszystko", "Dziś", "Ostatnie 7 dni", "Ostatnie 30 dni", "Zakres..."],
        )
    start_date = end_date = None
    with col_f2:
        if date_filter == "Zakres...":
            start_date = st.date_input("Od:", value=date.today() - timedelta(days=7))
    with col_f3:
        if date_filter == "Zakres...":
            end_date = st.date_input("Do:", value=date.today())
    with col_f4:
        monter_filter = st.text_input("Monter (zawiera):", value="").strip()

    # Drugi rząd filtrów
    col_f5, col_f6 = st.columns([2, 2])
    with col_f5:
        klient_filter = st.text_input("Imię i nazwisko klienta (zawiera):", value="").strip()
    with col_f6:
        # Typy
        types_selected = st.multiselect(
            "Typ pomiaru:", ["drzwi", "drzwi_wejsciowe", "podlogi"], default=["drzwi", "drzwi_wejsciowe", "podlogi"],
        )

    # Zastosuj filtry
    def _in_date(dt: datetime) -> bool:
        d = dt.date()
        if date_filter == "Wszystko":
            return True
        if date_filter == "Dziś":
            return d == date.today()
        if date_filter == "Ostatnie 7 dni":
            return d >= date.today() - timedelta(days=7)
        if date_filter == "Ostatnie 30 dni":
            return d >= date.today() - timedelta(days=30)
        if date_filter == "Zakres...":
            if not (start_date and end_date):
                return True
            return start_date <= d <= end_date
        return True

    filtered = []
    for rec in all_records:
        if rec.get('__type') not in types_selected:
            continue
        folder, dt = _folder_name(rec)
        if not _in_date(dt):
            continue
        if monter_filter and monter_filter.lower() not in str(rec.get('monter_id', '')).lower():
            continue
        # Filtr po imieniu i nazwisku klienta
        if klient_filter and klient_filter.lower() not in str(rec.get('imie_nazwisko', '')).lower():
            continue
        rec['__folder'] = folder
        rec['__dt'] = dt
        filtered.append(rec)

    # Grupowanie po folderze
    groups = {}
    for rec in filtered:
        folder = rec['__folder']
        if folder not in groups:
            groups[folder] = {
                'dt': rec['__dt'],
                'items': [],
            }
        groups[folder]['items'].append(rec)

    # Statystyki
    st.markdown("---")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("📁 Liczba folderów", len(groups))
    with col_s2:
        st.metric("📄 Liczba pomiarów", len(filtered))
    with col_s3:
        today_count = sum(1 for g in groups.values() if g['dt'].date() == date.today())
        st.metric("🆕 Foldery z dziś", today_count)

    st.markdown("---")

    if not groups:
        st.info("📭 Brak folderów dla wybranych filtrów")
        return

    # Sortuj foldery po dacie malejąco
    sorted_groups = sorted(groups.items(), key=lambda kv: kv[1]['dt'], reverse=True)

    # Renderuj w akordeonach
    for folder_name, data in sorted_groups:
        items = data['items']
        dt = data['dt']
        nice_label = f"{folder_name}  ·  {dt.strftime('%Y-%m-%d %H:%M') if dt != datetime.min else ''}  ·  {len(items)} pomiar(y)"
        with st.expander(nice_label, expanded=False):
            rows = []
            for it in items:
                if it.get('__type') == 'drzwi':
                    dims = f"{it.get('szerokosc_otworu','')} x {it.get('wysokosc_otworu','')}"
                elif it.get('__type') == 'drzwi_wejsciowe':
                    dims = f"{it.get('szerokosc_otworu','')} x {it.get('wysokosc_otworu','')}"
                else:
                    # dla podłóg pokaż skrót (sumę listw)
                    dims = f"system: {it.get('system_montazu','')}"
                rows.append({
                    "Typ": it.get('__type'),
                    "ID": it.get('id',''),
                    "Data": it.get('data_pomiary') or it.get('data_utworzenia'),
                    "Pomieszczenie": it.get('pomieszczenie',''),
                    "Klient": it.get('imie_nazwisko',''),
                    "Telefon": it.get('telefon',''),
                    "Wymiary": dims,
                    "Monter": it.get('monter_id',''),
                    "Status": it.get('status',''),
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, hide_index=True, use_container_width=True)

            # Wybór akcji dla protokołu
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                sel_action = st.selectbox(
                    "Wybierz akcję:",
                    options=["", "📋 Wyświetl pełny protokół", "🔍 Podgląd JSON (Testy)"],
                    key=f"sel_action_{folder_name}"
                )
            
            with col_action2:
                if sel_action in ["📋 Wyświetl pełny protokół", "🔍 Podgląd JSON (Testy)"]:
                    # Utwórz opcje wyboru z pomieszczeniem i typem dla czytelności
                    protocol_options = ["Wybierz protokół..."] + [f"{r['Pomieszczenie']} ({r['Typ']}) - {r['ID'][:8]}..." for r in rows]
                    sel_protocol_idx = st.selectbox(
                        "Wybierz protokół:",
                        options=range(len(protocol_options)),
                        format_func=lambda x: protocol_options[x],
                        key=f"sel_protocol_{folder_name}"
                    )
                else:
                    sel_protocol_idx = 0
            
            if sel_action == "📋 Wyświetl pełny protokół" and sel_protocol_idx > 0:
                # Znajdź odpowiedni rekord na podstawie indeksu (odjęty o 1 przez "Wybierz protokół...")
                rec_idx = sel_protocol_idx - 1
                if 0 <= rec_idx < len(rows):
                    selected_id = rows[rec_idx]["ID"]
                    rec = next((x for x in items if x.get('id') == selected_id), None)
                    if rec:
                        st.markdown("---")
                        display_full_protocol(db, rec, folder_name)
            
            elif sel_action == "🔍 Podgląd JSON (Testy)" and sel_protocol_idx > 0:
                # Znajdź odpowiedni rekord na podstawie indeksu (odjęty o 1 przez "Wybierz protokół...")
                rec_idx = sel_protocol_idx - 1
                if 0 <= rec_idx < len(rows):
                    selected_id = rows[rec_idx]["ID"]
                    rec = next((x for x in items if x.get('id') == selected_id), None)
                    if rec:
                        st.json(rec)


def display_full_protocol(db, record, folder_name):
    """Wyświetla kompletny edytowalny protokół"""
    protocol_type = record.get('__type', '')
    doc_id = record.get('id', '')
    
    # Pobierz aktualne dane z bazy
    current_data = get_document_by_id(db, protocol_type, doc_id)
    if not current_data:
        st.error("❌ Nie można pobrać danych protokołu z bazy danych")
        return
    
    st.subheader(f"📋 Pełny protokół - {protocol_type.upper()}")
    st.info(f"**ID:** {doc_id} | **Folder:** {folder_name}")
    
    # Wyświetl pełny protokół w zależności od typu
    if protocol_type == 'drzwi':
        display_drzwi_protocol(db, current_data, doc_id)
    elif protocol_type == 'drzwi_wejsciowe':
        display_drzwi_wejsciowe_protocol(db, current_data, doc_id)
    elif protocol_type == 'podlogi':
        display_podlogi_protocol(db, current_data, doc_id)
    else:
        st.error(f"❌ Nieznany typ protokołu: {protocol_type}")

def display_drzwi_protocol(db, data, doc_id):
    """Wyświetla edytowalny protokół drzwi"""
    st.markdown("### 🚪 PROTOKÓŁ DRZWI WEWNĘTRZNYCH")
    
    # Klucz unikalne dla tego protokołu
    key_suffix = f"drzwi_{doc_id}"
    
    with st.form(f"edit_protocol_{key_suffix}"):
        # SEKCJA 1: Podstawowe informacje (część montera)
        st.markdown("#### 📋 Podstawowe informacje")
        col1, col2 = st.columns(2)
        
        with col1:
            pomieszczenie = st.text_input("Pomieszczenie:", value=data.get('pomieszczenie', ''), key=f"pomieszczenie_{key_suffix}")
            imie_nazwisko = st.text_input("Imię i nazwisko klienta:", value=data.get('imie_nazwisko', ''), key=f"imie_nazwisko_{key_suffix}")
            telefon = st.text_input("Telefon:", value=data.get('telefon', ''), key=f"telefon_{key_suffix}")
            monter_id = st.text_input("Monter:", value=data.get('monter_id', ''), key=f"monter_id_{key_suffix}")
        
        with col2:
            data_utworzenia = st.text_input("Data utworzenia:", value=str(data.get('data_utworzenia', '')), disabled=True, key=f"data_utworzenia_{key_suffix}")
            kod_dostepu = st.text_input("Kod dostępu:", value=data.get('kod_dostepu', ''), disabled=True, key=f"kod_dostepu_{key_suffix}")
            status = st.selectbox("Status:", ["szkic", "pomiary", "aktywny", "zakończony", "anulowany"], 
                                index=["szkic", "pomiary", "aktywny", "zakończony", "anulowany"].index(data.get('status', 'szkic')), 
                                key=f"status_{key_suffix}")
        
        # SEKCJA 2: Pomiary otworu (część montera)
        st.markdown("#### 📐 Pomiary otworu")
        col3, col4 = st.columns(2)
        
        with col3:
            szerokosc_otworu = st.text_input("Szerokość otworu:", value=data.get('szerokosc_otworu', ''), key=f"szerokosc_otworu_{key_suffix}")
            wysokosc_otworu = st.text_input("Wysokość otworu:", value=data.get('wysokosc_otworu', ''), key=f"wysokosc_otworu_{key_suffix}")
            mierzona_od = st.text_input("Mierzona od:", value=data.get('mierzona_od', ''), key=f"mierzona_od_{key_suffix}")
        
        with col4:
            grubosc_muru = st.text_input("Grubość muru (cm):", value=data.get('grubosc_muru', ''), key=f"grubosc_muru_{key_suffix}")
            stan_sciany = st.text_input("Stan ściany:", value=data.get('stan_sciany', ''), key=f"stan_sciany_{key_suffix}")
        
        # SEKCJA 3: Specyfikacja techniczna (część montera + sprzedawcy)
        st.markdown("#### 🔨 Specyfikacja techniczna")
        col5, col6 = st.columns(2)
        
        with col5:
            typ_drzwi = st.selectbox("Typ drzwi:", ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"],
                                   index=["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"].index(data.get('typ_drzwi', 'Przylgowe')) if data.get('typ_drzwi') in ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"] else 0,
                                   key=f"typ_drzwi_{key_suffix}")
            oscieznica = st.text_input("Ościeżnica:", value=data.get('oscieznica', ''), key=f"oscieznica_{key_suffix}")
            opaska = st.radio("Opaska:", ["6 cm", "8 cm"], 
                            index=["6 cm", "8 cm"].index(data.get('opaska', '6 cm')) if data.get('opaska') in ["6 cm", "8 cm"] else 0,
                            horizontal=True, key=f"opaska_{key_suffix}")
        
        with col6:
            kat_zaciecia = st.selectbox("Kąt zacięcia:", ["45°", "90°", "0°"],
                                      index=["45°", "90°", "0°"].index(data.get('kat_zaciecia', '45°')) if data.get('kat_zaciecia') in ["45°", "90°", "0°"] else 0,
                                      key=f"kat_zaciecia_{key_suffix}")
            prog = st.text_input("Próg:", value=data.get('prog', ''), key=f"prog_{key_suffix}")
            wizjer = st.checkbox("Wizjer", value=bool(data.get('wizjer', False)), key=f"wizjer_{key_suffix}")
        
        # SEKCJA 4: Strona otwierania (część montera)
        st.markdown("#### 🚪 Strona otwierania")
        strona_otw = data.get('strona_otwierania', {})
        
        # Określ obecny wybór dla radio buttons
        current_selection = "Nie wybrano"
        if strona_otw.get('lewe_przyl'):
            current_selection = "LEWE przylgowe"
        elif strona_otw.get('prawe_przyl'):
            current_selection = "PRAWE przylgowe"
        elif strona_otw.get('lewe_odwr'):
            current_selection = "LEWE odwrotna przylga"
        elif strona_otw.get('prawe_odwr'):
            current_selection = "PRAWE odwrotna przylga"
        
        # Radio buttons ułożone poziomo
        strona_otwierania_radio = st.radio(
            "Kierunek otwierania drzwi:",
            ["Nie wybrano", "LEWE przylgowe", "PRAWE przylgowe", "LEWE odwrotna przylga", "PRAWE odwrotna przylga"],
            index=["Nie wybrano", "LEWE przylgowe", "PRAWE przylgowe", "LEWE odwrotna przylga", "PRAWE odwrotna przylga"].index(current_selection),
            horizontal=True,
            key=f"strona_otwierania_radio_{key_suffix}"
        )
        
        # Wyświetl obrazki dla każdej opcji w 4 kolumnach
        col_img1, col_img2, col_img3, col_img4 = st.columns(4)
        
        with col_img1:
            if strona_otwierania_radio == "LEWE przylgowe":
                st.markdown("**✅ LEWE (przylgowe/bezprzylgowe)**")
            else:
                st.markdown("**LEWE (przylgowe/bezprzylgowe)**")
            try:
                st.image("drzwi/lewe_przyl.png", width=150, caption="Lewe przylgowe",use_container_width=False)
            except:
                st.write("🖼️ Obrazek niedostępny")
        
        with col_img2:
            if strona_otwierania_radio == "PRAWE przylgowe":
                st.markdown("**✅ PRAWE (przylgowe/bezprzylgowe)**")
            else:
                st.markdown("**PRAWE (przylgowe/bezprzylgowe)**")
            try:
                st.image("drzwi/prawe_przyl.png", width=150, caption="Prawe przylgowe",use_container_width=False)
            except:
                st.write("🖼️ Obrazek niedostępny")
        
        with col_img3:
            if strona_otwierania_radio == "LEWE odwrotna przylga":
                st.markdown("**✅ LEWE (odwrotna przylga)**")
            else:
                st.markdown("**LEWE (odwrotna przylga)**")
            try:
                st.image("drzwi/lewe_odwr.png", width=150, caption="Lewe odwrotne",use_container_width=False)
            except:
                st.write("🖼️ Obrazek niedostępny")
        
        with col_img4:
            if strona_otwierania_radio == "PRAWE odwrotna przylga":
                st.markdown("**✅ PRAWE (odwrotna przylga)**")
            else:
                st.markdown("**PRAWE (odwrotna przylga)**")
            try:
                st.image("drzwi/prawe_odwr.png", width=150, caption="Prawe odwrotne",use_container_width=False)
            except:
                st.write("🖼️ Obrazek niedostępny")
        
        # Pola dodatkowe
        col11, col12 = st.columns(2)
        with col11:
            napis_nad_drzwiami = st.text_input("Otwierane na:", value=data.get('napis_nad_drzwiami', ''), key=f"napis_nad_drzwiami_{key_suffix}")
        with col12:
            szerokosc_skrzydla = st.text_input("Szerokość skrzydła (cm):", value=data.get('szerokosc_skrzydla', ''), key=f"szerokosc_skrzydla_{key_suffix}")
        
        # SEKCJA 5: Dane produktu (część sprzedawcy)
        st.markdown("#### 🏷️ Dane produktu")
        col13, col14 = st.columns(2)
        
        with col13:
            producent = st.text_input("Producent:", value=data.get('producent', ''), key=f"producent_{key_suffix}")
            seria = st.text_input("Seria:", value=data.get('seria', ''), key=f"seria_{key_suffix}")
            typ_produktu = st.text_input("Typ:", value=data.get('typ', ''), key=f"typ_{key_suffix}")
            rodzaj_okleiny = st.text_input("Rodzaj okleiny:", value=data.get('rodzaj_okleiny', ''), key=f"rodzaj_okleiny_{key_suffix}")
            ilosc_szyb = st.text_input("Ilość szyb:", value=data.get('ilosc_szyb', ''), key=f"ilosc_szyb_{key_suffix}")
            zamek = st.text_input("Zamek:", value=data.get('zamek', ''), key=f"zamek_{key_suffix}")
        
        with col14:
            szyba = st.text_input("Szyba:", value=data.get('szyba', ''), key=f"szyba_{key_suffix}")
            wentylacja = st.text_input("Wentylacja:", value=data.get('wentylacja', ''), key=f"wentylacja_{key_suffix}")
            klamka = st.text_input("Klamka:", value=data.get('klamka', ''), key=f"klamka_{key_suffix}")
            kolor_wizjera = st.text_input("Kolor wizjera:", value=data.get('kolor_wizjera', ''), key=f"kolor_wizjera_{key_suffix}")
            wypelnienie = st.text_input("Wypełnienie:", value=data.get('wypelnienie', ''), key=f"wypelnienie_{key_suffix}")
            kolor_okuc = st.text_input("Kolor okucia:", value=data.get('kolor_okuc', ''), key=f"kolor_okuc_{key_suffix}")
        
        kolor_osc = st.text_input("Kolor ościeżnicy (jeśli inna):", value=data.get('kolor_osc', ''), key=f"kolor_osc_{key_suffix}")
        
        # SEKCJA 6: Uwagi i opcje
        st.markdown("#### 💬 Uwagi i opcje")
        opcje_dodatkowe = st.text_area("Opcje dodatkowe:", value=data.get('opcje_dodatkowe', ''), height=100, key=f"opcje_dodatkowe_{key_suffix}")
        uwagi_montera = st.text_area("Uwagi montera:", value=data.get('uwagi_montera', ''), height=100, key=f"uwagi_montera_{key_suffix}")
        uwagi_klienta = st.text_area("Uwagi dla klienta:", value=data.get('uwagi_klienta', ''), height=100, key=f"uwagi_klienta_{key_suffix}")
        
        # SEKCJA 7: Wykonawcy
        st.markdown("#### 👥 Wykonawcy")
        col15, col16 = st.columns(2)
        with col15:
            sprzedawca_id = st.text_input("Sprzedawca:", value=data.get('sprzedawca_id', ''), key=f"sprzedawca_id_{key_suffix}")
        with col16:
            norma = st.selectbox("Norma/Szkic:", ["PL", "CZ"], 
                               index=["PL", "CZ"].index(data.get('norma', 'PL')) if data.get('norma') in ["PL", "CZ"] else 0,
                               key=f"norma_{key_suffix}")
        
        # Przyciski akcji
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            submit_button = st.form_submit_button("💾 Zapisz zmiany", type="primary")
        
        # Obsługa akcji
        if submit_button:
            # Przygotuj dane do zapisu
            updated_data = {
                'pomieszczenie': pomieszczenie,
                'imie_nazwisko': imie_nazwisko,
                'telefon': telefon,
                'monter_id': monter_id,
                'status': status,
                'szerokosc_otworu': szerokosc_otworu,
                'wysokosc_otworu': wysokosc_otworu,
                'mierzona_od': mierzona_od,
                'grubosc_muru': grubosc_muru,
                'stan_sciany': stan_sciany,
                'typ_drzwi': typ_drzwi,
                'oscieznica': oscieznica,
                'opaska': opaska,
                'kat_zaciecia': kat_zaciecia,
                'prog': prog,
                'wizjer': wizjer,
                'strona_otwierania': {
                    'lewe_przyl': strona_otwierania_radio == "LEWE przylgowe",
                    'prawe_przyl': strona_otwierania_radio == "PRAWE przylgowe",
                    'lewe_odwr': strona_otwierania_radio == "LEWE odwrotna przylga",
                    'prawe_odwr': strona_otwierania_radio == "PRAWE odwrotna przylga"
                },
                'napis_nad_drzwiami': napis_nad_drzwiami,
                'szerokosc_skrzydla': szerokosc_skrzydla,
                'producent': producent,
                'seria': seria,
                'typ': typ_produktu,
                'rodzaj_okleiny': rodzaj_okleiny,
                'ilosc_szyb': ilosc_szyb,
                'zamek': zamek,
                'szyba': szyba,
                'wentylacja': wentylacja,
                'klamka': klamka,
                'kolor_wizjera': kolor_wizjera,
                'wypelnienie': wypelnienie,
                'kolor_okuc': kolor_okuc,
                'kolor_osc': kolor_osc,
                'opcje_dodatkowe': opcje_dodatkowe,
                'uwagi_montera': uwagi_montera,
                'uwagi_klienta': uwagi_klienta,
                'sprzedawca_id': sprzedawca_id,
                'norma': norma,
                'data_ostatniej_modyfikacji': datetime.now()
            }
            
            # Zapisz do bazy danych
            success = update_document(db, 'drzwi', doc_id, updated_data)
            if success:
                st.success("✅ Protokół został zaktualizowany!")
                st.rerun()
            else:
                st.error("❌ Błąd podczas zapisywania protokołu")
    
    # Obsługa PDF poza formularzem
    if st.button(f"📄 Pobierz PDF", key=f"pdf_download_{key_suffix}"):
        # Pobierz najnowsze dane
        latest_data = get_document_by_id(db, 'drzwi', doc_id)
        if latest_data:
            display_pdf_download_button(latest_data, 'drzwi', doc_id)
    
    # Wyświetl zdjęcia jeśli istnieją
    if 'zdjecia' in data and data['zdjecia']:
        display_images(data['zdjecia'], max_width=400)

def display_drzwi_wejsciowe_protocol(db, data, doc_id):
    """Wyświetla edytowalny protokół drzwi wejściowych"""
    st.markdown("### 🚨 PROTOKÓŁ DRZWI WEJŚCIOWYCH")
    
    key_suffix = f"drzwi_wej_{doc_id}"
    
    with st.form(f"edit_protocol_{key_suffix}"):
        # Podstawowe informacje
        st.markdown("#### 📋 Podstawowe informacje")
        col1, col2 = st.columns(2)
        
        with col1:
            numer_strony = st.text_input("Numer strony:", value=data.get('numer_strony', ''), key=f"numer_strony_{key_suffix}")
            imie_nazwisko = st.text_input("Imię i nazwisko:", value=data.get('imie_nazwisko', ''), key=f"imie_nazwisko_{key_suffix}")
            telefon = st.text_input("Telefon:", value=data.get('telefon', ''), key=f"telefon_{key_suffix}")
            pomieszczenie = st.text_input("Pomieszczenie:", value=data.get('pomieszczenie', ''), key=f"pomieszczenie_{key_suffix}")
        
        with col2:
            data_utworzenia = st.text_input("Data utworzenia:", value=str(data.get('data_utworzenia', '')), disabled=True, key=f"data_utworzenia_{key_suffix}")
            monter_id = st.text_input("Monter:", value=data.get('monter_id', ''), key=f"monter_id_{key_suffix}")
            status = st.selectbox("Status:", ["szkic", "pomiary", "aktywny", "zakończony", "anulowany"], 
                                index=["szkic", "pomiary", "aktywny", "zakończony", "anulowany"].index(data.get('status', 'szkic')), 
                                key=f"status_{key_suffix}")
        
        # Wymiary otworu
        st.markdown("#### 📏 Wymiary otworu")
        col3, col4 = st.columns(2)
        
        with col3:
            szerokosc_otworu = st.text_input("Szerokość otworu:", value=data.get('szerokosc_otworu', ''), key=f"szerokosc_otworu_{key_suffix}")
            wysokosc_otworu = st.text_input("Wysokość otworu:", value=data.get('wysokosc_otworu', ''), key=f"wysokosc_otworu_{key_suffix}")
        
        with col4:
            mierzona_od = st.text_input("Mierzona od:", value=data.get('mierzona_od', ''), key=f"mierzona_od_{key_suffix}")
            skrot = st.text_input("Skrót:", value=data.get('skrot', ''), key=f"skrot_{key_suffix}")
        
        # Dane techniczne
        st.markdown("#### 🏗️ Dane techniczne")
        col5, col6 = st.columns(2)
        
        with col5:
            grubosc_muru = st.text_input("Grubość muru (cm):", value=data.get('grubosc_muru', ''), key=f"grubosc_muru_{key_suffix}")
            stan_sciany = st.text_input("Stan ściany:", value=data.get('stan_sciany', ''), key=f"stan_sciany_{key_suffix}")
            oscieznica = st.text_input("Ościeżnica:", value=data.get('oscieznica', ''), key=f"oscieznica_{key_suffix}")
        
        with col6:
            okapnik = st.text_input("Okapnik:", value=data.get('okapnik', ''), key=f"okapnik_{key_suffix}")
            prog = st.text_input("Próg:", value=data.get('prog', ''), key=f"prog_{key_suffix}")
            wizjer = st.checkbox("Wizjer", value=bool(data.get('wizjer', False)), key=f"wizjer_{key_suffix}")
            elektrozaczep = st.text_input("Elektrozaczep:", value=data.get('elektrozaczep', ''), key=f"elektrozaczep_{key_suffix}")
        
        # Strona otwierania
        st.markdown("#### 🚪 Strona otwierania")
        strona_otw = data.get('strona_otwierania', {})
        col7, col8, col9, col10 = st.columns(4)
        
        with col7:
            na_zewnatrz = st.checkbox("Na zewnątrz", value=strona_otw.get('na_zewnatrz', False), key=f"na_zewnatrz_{key_suffix}")
        with col8:
            do_wewnatrz = st.checkbox("Do wewnątrz", value=strona_otw.get('do_wewnatrz', False), key=f"do_wewnatrz_{key_suffix}")
        with col9:
            lewe = st.checkbox("Lewe", value=strona_otw.get('lewe', False), key=f"lewe_{key_suffix}")
        with col10:
            prawe = st.checkbox("Prawe", value=strona_otw.get('prawe', False), key=f"prawe_{key_suffix}")
        
        # Dane produktu
        st.markdown("#### 🏷️ Dane produktu")
        col11, col12 = st.columns(2)
        
        with col11:
            producent = st.text_input("Producent:", value=data.get('producent', ''), key=f"producent_{key_suffix}")
            grubosc = st.text_input("Grubość:", value=data.get('grubosc', ''), key=f"grubosc_{key_suffix}")
            wzor = st.text_input("Wzór:", value=data.get('wzor', ''), key=f"wzor_{key_suffix}")
            rodzaj_okleiny = st.text_input("Rodzaj okleiny:", value=data.get('rodzaj_okleiny', ''), key=f"rodzaj_okleiny_{key_suffix}")
            ramka = st.text_input("Ramka:", value=data.get('ramka', ''), key=f"ramka_{key_suffix}")
        
        with col12:
            seria = st.text_input("Seria:", value=data.get('seria', ''), key=f"seria_{key_suffix}")
            wkladki = st.text_input("Wkładki:", value=data.get('wkladki', ''), key=f"wkladki_{key_suffix}")
            szyba = st.text_input("Szyba:", value=data.get('szyba', ''), key=f"szyba_{key_suffix}")
            klamka = st.text_input("Klamka:", value=data.get('klamka', ''), key=f"klamka_{key_suffix}")
            dostawka = st.text_input("Dostawka:", value=data.get('dostawka', ''), key=f"dostawka_{key_suffix}")
        
        # Uwagi
        st.markdown("#### 💬 Uwagi")
        opcje_dodatkowe = st.text_area("Opcje dodatkowe:", value=data.get('opcje_dodatkowe', ''), height=100, key=f"opcje_dodatkowe_{key_suffix}")
        uwagi_montera = st.text_area("Uwagi montera:", value=data.get('uwagi_montera', ''), height=100, key=f"uwagi_montera_{key_suffix}")
        uwagi_klienta = st.text_area("Uwagi dla klienta:", value=data.get('uwagi_klienta', ''), height=100, key=f"uwagi_klienta_{key_suffix}")
        
        # Wykonawcy
        st.markdown("#### 👥 Wykonawcy")
        sprzedawca_id = st.text_input("Sprzedawca:", value=data.get('sprzedawca_id', ''), key=f"sprzedawca_id_{key_suffix}")
        
        # Przyciski
        st.markdown("---")
        submit_button = st.form_submit_button("💾 Zapisz zmiany", type="primary")
        
        if submit_button:
            updated_data = {
                'numer_strony': numer_strony,
                'imie_nazwisko': imie_nazwisko,
                'telefon': telefon,
                'pomieszczenie': pomieszczenie,
                'monter_id': monter_id,
                'status': status,
                'szerokosc_otworu': szerokosc_otworu,
                'wysokosc_otworu': wysokosc_otworu,
                'mierzona_od': mierzona_od,
                'skrot': skrot,
                'grubosc_muru': grubosc_muru,
                'stan_sciany': stan_sciany,
                'oscieznica': oscieznica,
                'okapnik': okapnik,
                'prog': prog,
                'wizjer': wizjer,
                'elektrozaczep': elektrozaczep,
                'strona_otwierania': {
                    'na_zewnatrz': na_zewnatrz,
                    'do_wewnatrz': do_wewnatrz,
                    'lewe': lewe,
                    'prawe': prawe
                },
                'producent': producent,
                'grubosc': grubosc,
                'wzor': wzor,
                'rodzaj_okleiny': rodzaj_okleiny,
                'ramka': ramka,
                'seria': seria,
                'wkladki': wkladki,
                'szyba': szyba,
                'klamka': klamka,
                'dostawka': dostawka,
                'opcje_dodatkowe': opcje_dodatkowe,
                'uwagi_montera': uwagi_montera,
                'uwagi_klienta': uwagi_klienta,
                'sprzedawca_id': sprzedawca_id,
                'data_ostatniej_modyfikacji': datetime.now()
            }
            
            success = update_document(db, 'drzwi_wejsciowe', doc_id, updated_data)
            if success:
                st.success("✅ Protokół został zaktualizowany!")
                st.rerun()
            else:
                st.error("❌ Błąd podczas zapisywania protokołu")
    
    # PDF poza formularzem
    if st.button(f"📄 Pobierz PDF", key=f"pdf_download_{key_suffix}"):
        latest_data = get_document_by_id(db, 'drzwi_wejsciowe', doc_id)
        if latest_data:
            display_pdf_download_button(latest_data, 'drzwi_wejsciowe', doc_id)
    
    # Wyświetl zdjęcia
    if 'zdjecia' in data and data['zdjecia']:
        st.markdown("#### 📸 Zdjęcia")
        display_images(data['zdjecia'], max_width=400)

def display_podlogi_protocol(db, data, doc_id):
    """Wyświetla edytowalny protokół podłóg"""
    st.markdown("### 🏠 PROTOKÓŁ PODŁÓG")
    
    key_suffix = f"podlogi_{doc_id}"
    
    with st.form(f"edit_protocol_{key_suffix}"):
        # Podstawowe informacje
        st.markdown("#### 📋 Podstawowe informacje")
        col1, col2 = st.columns(2)
        
        with col1:
            pomieszczenie = st.text_input("Pomieszczenie:", value=data.get('pomieszczenie', ''), key=f"pomieszczenie_{key_suffix}")
            telefon = st.text_input("Telefon:", value=data.get('telefon', ''), key=f"telefon_{key_suffix}")
            monter_id = st.text_input("Monter:", value=data.get('monter_id', ''), key=f"monter_id_{key_suffix}")
        
        with col2:
            data_utworzenia = st.text_input("Data utworzenia:", value=str(data.get('data_utworzenia', '')), disabled=True, key=f"data_utworzenia_{key_suffix}")
            status = st.selectbox("Status:", ["szkic", "pomiary", "aktywny", "zakończony", "anulowany"], 
                                index=["szkic", "pomiary", "aktywny", "zakończony", "anulowany"].index(data.get('status', 'szkic')), 
                                key=f"status_{key_suffix}")
        
        # System montażu
        st.markdown("#### 🔨 System montażu")
        col3, col4 = st.columns(2)
        
        with col3:
            system_montazu = st.text_input("System montażu:", value=data.get('system_montazu', ''), key=f"system_montazu_{key_suffix}")
            podklad = st.text_input("Podkład:", value=data.get('podklad', ''), key=f"podklad_{key_suffix}")
        
        with col4:
            mdf_mozliwy = st.text_input("MDF możliwy:", value=data.get('mdf_mozliwy', ''), key=f"mdf_mozliwy_{key_suffix}")
        
        # Pomiary listw
        st.markdown("#### 📏 Pomiary listw")
        col5, col6, col7, col8, col9 = st.columns(5)
        
        with col5:
            nw = st.number_input("NW:", min_value=0, value=int(data.get('nw', 0)), key=f"nw_{key_suffix}")
        with col6:
            nz = st.number_input("NZ:", min_value=0, value=int(data.get('nz', 0)), key=f"nz_{key_suffix}")
        with col7:
            l = st.number_input("Ł:", min_value=0, value=int(data.get('l', 0)), key=f"l_{key_suffix}")
        with col8:
            zl = st.number_input("ZL:", min_value=0, value=int(data.get('zl', 0)), key=f"zl_{key_suffix}")
        with col9:
            zp = st.number_input("ZP:", min_value=0, value=int(data.get('zp', 0)), key=f"zp_{key_suffix}")
        
        suma_listw = nw + nz + l + zl + zp
        st.markdown(f"**SUMA LISTW: {suma_listw} szt.**")
        
        # Listwy progowe
        st.markdown("#### 🚪 Listwy progowe")
        col10, col11, col12 = st.columns(3)
        
        with col10:
            listwy_jaka = st.text_input("Jaka:", value=data.get('listwy_jaka', ''), key=f"listwy_jaka_{key_suffix}")
        with col11:
            listwy_ile = st.text_input("Ile:", value=data.get('listwy_ile', ''), key=f"listwy_ile_{key_suffix}")
        with col12:
            listwy_gdzie = st.text_input("Gdzie:", value=data.get('listwy_gdzie', ''), key=f"listwy_gdzie_{key_suffix}")
        
        # Dane produktu
        st.markdown("#### 🏷️ Dane produktu")
        col13, col14 = st.columns(2)
        
        with col13:
            rodzaj_podlogi = st.text_input("Rodzaj podłogi:", value=data.get('rodzaj_podlogi', ''), key=f"rodzaj_podlogi_{key_suffix}")
            seria = st.text_input("Seria:", value=data.get('seria', ''), key=f"seria_{key_suffix}")
            kolor = st.text_input("Kolor:", value=data.get('kolor', ''), key=f"kolor_{key_suffix}")
        
        with col14:
            folia = st.text_input("Folia:", value=data.get('folia', ''), key=f"folia_{key_suffix}")
            listwa_przypodlogowa = st.text_input("Listwa przypodłogowa:", value=data.get('listwa_przypodlogowa', ''), key=f"listwa_przypodlogowa_{key_suffix}")
        
        # Uwagi
        st.markdown("#### 💬 Uwagi")
        uwagi_montera = st.text_area("Uwagi montera:", value=data.get('uwagi_montera', ''), height=100, key=f"uwagi_montera_{key_suffix}")
        uwagi = st.text_area("Uwagi dla klienta:", value=data.get('uwagi', ''), height=100, key=f"uwagi_{key_suffix}")
        
        # Wykonawcy
        st.markdown("#### 👥 Wykonawcy")
        sprzedawca_id = st.text_input("Sprzedawca:", value=data.get('sprzedawca_id', ''), key=f"sprzedawca_id_{key_suffix}")
        
        # Ostrzeżenie
        st.warning("⚠️ UWAGA!! Podłoże powinno być suche i równe!!")
        
        # Przyciski
        st.markdown("---")
        submit_button = st.form_submit_button("💾 Zapisz zmiany", type="primary")
        
        if submit_button:
            updated_data = {
                'pomieszczenie': pomieszczenie,
                'telefon': telefon,
                'monter_id': monter_id,
                'status': status,
                'system_montazu': system_montazu,
                'podklad': podklad,
                'mdf_mozliwy': mdf_mozliwy,
                'nw': nw,
                'nz': nz,
                'l': l,
                'zl': zl,
                'zp': zp,
                'listwy_jaka': listwy_jaka,
                'listwy_ile': listwy_ile,
                'listwy_gdzie': listwy_gdzie,
                'rodzaj_podlogi': rodzaj_podlogi,
                'seria': seria,
                'kolor': kolor,
                'folia': folia,
                'listwa_przypodlogowa': listwa_przypodlogowa,
                'uwagi_montera': uwagi_montera,
                'uwagi': uwagi,
                'sprzedawca_id': sprzedawca_id,
                'data_ostatniej_modyfikacji': datetime.now()
            }
            
            success = update_document(db, 'podlogi', doc_id, updated_data)
            if success:
                st.success("✅ Protokół został zaktualizowany!")
                st.rerun()
            else:
                st.error("❌ Błąd podczas zapisywania protokołu")
    
    # PDF poza formularzem
    if st.button(f"📄 Pobierz PDF", key=f"pdf_download_{key_suffix}"):
        latest_data = get_document_by_id(db, 'podlogi', doc_id)
        if latest_data:
            display_pdf_download_button(latest_data, 'podlogi', doc_id)
    
    # Wyświetl zdjęcia
    if 'zdjecia' in data and data['zdjecia']:
        st.markdown("#### 📸 Zdjęcia")
        display_images(data['zdjecia'], max_width=400)


if __name__ == "__main__":
    page_foldery()


