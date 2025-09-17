import streamlit as st
import pandas as pd
import qrcode
import io
import base64
from datetime import datetime
from firebase_config import (
    setup_database, save_pomiary_data, generate_share_link,
    get_forms_for_completion, complete_form_by_seller, get_form_by_access_code,
    save_draft_data, display_images
)
import os
from pdf_generator import display_pdf_download_button

def display_door_options_gallery(selected_opening):
    """Wyświetla galerię wszystkich opcji otwierania drzwi z oznaczeniem wybranej"""
    
    # Definicje wszystkich opcji w kolejności
    door_options = [
        {
            'key': 'lewe_przyl',
            'label': 'LEWE',
            'files': ['lewe_przyl.png', 'lewe_przylgowe.png']
        },
        {
            'key': 'prawe_przyl', 
            'label': 'PRAWE',
            'files': ['prawe_przyl.png', 'prawe_przylgowe.png']
        },
        {
            'key': 'lewe_odwr',
            'label': 'LEWE odwrotna przylga', 
            'files': ['lewe_odwr.png', 'lewe_odwrotne.png']
        },
        {
            'key': 'prawe_odwr',
            'label': 'PRAWE odwrotna przylga',
            'files': ['prawe_odwr.png', 'prawe_odwrotne.png']
        }
    ]
    
    # Katalogi ze zdjęciami
    image_base_dirs = ["drzwi_pdf/", "drzwi/", "images/drzwi_pdf/"]
    
    # Znajdź wybrane opcje
    selected_keys = [key for key, value in selected_opening.items() if value]
    
    st.markdown("**🚪 WSZYSTKIE OPCJE OTWIERANIA:**")
    
    # Wyświetl w 4 kolumnach
    cols = st.columns(4)
    
    for i, option in enumerate(door_options):
        with cols[i]:
            # Znajdź obraz dla tej opcji
            image_path = None
            for base_dir in image_base_dirs:
                for filename in option['files']:
                    candidate = os.path.join(base_dir, filename)
                    if os.path.exists(candidate):
                        image_path = candidate
                        break
                if image_path:
                    break
            
            # Sprawdź czy ta opcja jest wybrana
            is_selected = option['key'] in selected_keys
            
            if image_path:
                try:
                    # Wyświetl obrazek
                    st.image(image_path, caption=option['label'], width=150)
                    
                    # Oznacz wybraną opcję
                    if is_selected:
                        st.success("✅ WYBRANE")
                    else:
                        st.write("")  # Puste miejsce dla wyrównania
                        
                except Exception as e:
                    st.error(f"Błąd: {e}")
                    st.write(option['label'])
                    if is_selected:
                        st.success("✅ WYBRANE")
            else:
                # Brak obrazu - tylko tekst
                st.write(option['label'])
                if is_selected:
                    st.success("✅ WYBRANE")

# ZABEZPIECZENIE - sprawdź logowanie przed załadowaniem strony
if not st.session_state.get('logged_in', False):
    st.error("🚫 **Dostęp zabroniony** - Wymagane logowanie!")
    st.markdown("### 👆 [Przejdź do logowania](?)")
    if st.button("🔙 Powrót do logowania", type="primary"):
        st.switch_page("main.py")
    st.stop()

def formularz_montera_drzwi():
    """Formularz pomiarów drzwi dla montera"""
    st.header("🔧 Pomiary drzwi - Monter")
    
    # Inicjalizacja bazy danych
    db = setup_database()
    
    # ID montera
    monter_id = st.text_input("🔑 Imię Montera:", value="", key="monter_id_drzwi")
    
    if not monter_id:
        st.warning("⚠️ Proszę podać Imię montera przed wypełnieniem formularza")
        return
    
    # Podstawowe informacje
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Podstawowe informacje")
        pomieszczenie = st.text_input("Pomieszczenie:", key="pomieszczenie_monter")
        imie_nazwisko = st.text_input("Imie i Nazwisko klienta:", key="imie_nazwisko_monter")
        telefon = st.text_input("Telefon klienta:", key="telefon_monter")
    
    with col2:
        st.subheader("📐 Pomiary otworu")
        szerokosc_otworu = st.text_input("Szerokość otworu:", key="szerokosc_monter")
        wysokosc_otworu = st.text_input("Wysokość otworu:", key="wysokosc_monter")
        mierzona_od = st.text_input("Mierzona od:", key="mierzona_od_monter")
        st.caption("(betonu, gotowej podłogi, inne?)")
    
    # Specyfikacja techniczna
    st.subheader("🔨 Specyfikacja techniczna")
    col3, col4 = st.columns(2)
    
    with col3:
        grubosc_muru = st.text_input("Grubość muru (cm):", key="grubosc_monter")
        st.caption("(faktyczna)")
        
        stan_sciany = st.text_input("Stan ściany:", key="stan_sciany_monter")
        st.caption("(sposób wykończenia: tapeta, płyta g-k itp.)")
        
        typ_drzwi = st.radio(
            "Typ drzwi:",
            ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"],
            key="typ_drzwi_monter"
        )
        
        # Pokaż obrazek dla wybranego typu
        if typ_drzwi == "Przylgowe":
            try:
                st.image("typ_drzwi/przylgowe.png", width=120, caption="Drzwi przylgowe")
            except:
                st.write("🖼️ Obrazek niedostępny")
        elif typ_drzwi == "Bezprzylgowe":
            try:
                st.image("typ_drzwi/bezprzylgowe.png", width=120, caption=typ_drzwi)
            except:
                st.write("🖼️ Obrazek niedostępny")
        elif typ_drzwi == "Odwrotna Przylga":
            try:
                st.image("typ_drzwi/odwrotna_przylga.png", width=120, caption="Odwrotna przylga")
            except:
                st.write("🖼️ Obrazek niedostępny")
        elif typ_drzwi == "Renova":
            try:
                st.image("typ_drzwi/inne.png", width=120, caption="Renova")
            except:
                st.write("🖼️ Obrazek niedostępny")
    
    with col4:
        oscieznica = st.text_input("Ościeżnica:", key="oscieznica_monter")
        st.caption("(zakres)")
        
        opaska = st.radio("Opaska:", ["6 cm", "8 cm"], key="opaska_monter")
        
        kat_zaciecia = st.selectbox("Kąt zacięcia:", ["45°", "90°", "0°"], key="kat_zaciecia_monter")
        st.caption("(45°, 90°, 0°)")
        
        prog = st.text_input("Próg:", key="prog_monter")
        wizjer = st.checkbox("Wizjer", key="wizjer_monter")
    
    # Strona otwierania
    st.subheader("🚪 Strona otwierania")
    
    strona_otwierania = st.radio(
        "Kierunek otwierania drzwi:",
        ["Nie wybrano", "LEWE", "PRAWE", "LEWE odwrotna przylga", "PRAWE odwrotna przylga"],
        key="strona_otwierania_monter",
        horizontal=True
    )
    
    col_img1, col_img2, col_img3, col_img4 = st.columns(4)
    
    with col_img1:
        if strona_otwierania == "LEWE":
            st.markdown("**✅ LEWE (przylgowe/bezprzylgowe)**")
        else:
            st.markdown("**LEWE (przylgowe/bezprzylgowe)**")
        try:
            st.image("drzwi/lewe_przyl.png", width=150)
        except:
            st.write("🖼️ Obrazek niedostępny")
    
    with col_img2:
        if strona_otwierania == "PRAWE":
            st.markdown("**✅ PRAWE (przylgowe/bezprzylgowe)**")
        else:
            st.markdown("**PRAWE (przylgowe/bezprzylgowe)**")
        try:
            st.image("drzwi/prawe_przyl.png", width=150)
        except:
            st.write("🖼️ Obrazek niedostępny")
    
    with col_img3:
        if strona_otwierania == "LEWE odwrotna przylga":
            st.markdown("**✅ LEWE (odwrotna przylga)**")
        else:
            st.markdown("**LEWE (odwrotna przylga)**")
        try:
            st.image("drzwi/lewe_odwr.png", width=150)
        except:
            st.write("🖼️ Obrazek niedostępny")
    
    with col_img4:
        if strona_otwierania == "PRAWE odwrotna przylga":
            st.markdown("**✅ PRAWE (odwrotna przylga)**")
        else:
            st.markdown("**PRAWE (odwrotna przylga)**")
        try:
            st.image("drzwi/prawe_odwr.png", width=150)
        except:
            st.write("🖼️ Obrazek niedostępny")
    # Dodatkowe opisy przy ilustracji oraz szerokość
    col_top, col_mid = st.columns([2, 1])
    with col_top:
        napis_nad_drzwiami = st.text_input("Otwierane na:", key="napis_nad_drzwiami")
    with col_mid:
        szerokosc_skrzydla = st.text_input("Szerokość (cm):", key="szerokosc_skrzydla")
    
    # Szkic i uwagi
    st.subheader("📝 Szkic i uwagi")
    norma = st.selectbox("Norma/Szkic:", ["PL", "CZ"], key="norma_monter")
    uwagi_montera = st.text_area("Uwagi montera:", height=100, key="uwagi_montera")
    
    save_draft_clicked = st.button("🗂️ Zapisz do przechowalni", type="primary")

    # ZAPIS DO PRZECHOWALNI (szkic)
    if save_draft_clicked:
        dane_pomiary = {
            "pomieszczenie": pomieszczenie,
            "imie_nazwisko": imie_nazwisko,
            "telefon": telefon,
            "szerokosc_otworu": szerokosc_otworu,
            "wysokosc_otworu": wysokosc_otworu,
            "mierzona_od": mierzona_od,
            "typ_drzwi": typ_drzwi,
            "norma": norma,
            "grubosc_muru": grubosc_muru,
            "stan_sciany": stan_sciany,
            "oscieznica": oscieznica,
            "opaska": opaska,
            "kat_zaciecia": kat_zaciecia,
            "prog": prog,
            "wizjer": wizjer,
            "strona_otwierania": {
                "lewe_przyl": strona_otwierania == "LEWE",
                "prawe_przyl": strona_otwierania == "PRAWE",
                "lewe_odwr": strona_otwierania == "LEWE odwrotna przylga",
                "prawe_odwr": strona_otwierania == "PRAWE odwrotna przylga"
            },
            "napis_nad_drzwiami": napis_nad_drzwiami,
            "szerokosc_skrzydla": szerokosc_skrzydla,
            "uwagi_montera": uwagi_montera,
        }

        # Pozwalamy zapisać szkic nawet z brakami
        with st.spinner("Zapisywanie szkicu..."):
            draft_id = save_draft_data(db, "drzwi", dane_pomiary, monter_id)
            if draft_id:
                st.success(f"🗂️ Szkic zapisany (ID: {draft_id}). Możesz wrócić i dokończyć później na stronie 'Przechowalnia'.")
                st.info("📷 **Zdjęcia można dodać w przechowalni po wybraniu szkicu**")
            else:
                st.error("❌ Nie udało się zapisać szkicu")

def formularz_sprzedawcy_drzwi():
    """Formularz uzupełniania danych produktu przez sprzedawcę"""
    st.header("💼 Uzupełnienie danych produktu - Sprzedawca")
    
    db = setup_database()
    
    # Sposób dostępu do formularza
    sposob_dostepu = st.radio(
        "Wybierz sposób dostępu:",
        ["📋 Lista formularzy do uzupełnienia", "🔑 Kod dostępu"],
        key="sposob_dostepu"
    )
    
    selected_form = None
    
    if sposob_dostepu == "🔑 Kod dostępu":
        # Dostęp przez kod
        col1, col2 = st.columns([2, 1])
        
        with col1:
            kod_dostepu = st.text_input("Wprowadź kod dostępu:", key="kod_dostepu_input")
        
        with col2:
            if st.button("🔍 Znajdź formularz"):
                if kod_dostepu:
                    with st.spinner("Wyszukiwanie formularza..."):
                        selected_form = get_form_by_access_code(db, "drzwi", kod_dostepu)
                        
                        if selected_form:
                            st.success("✅ Formularz znaleziony!")
                        else:
                            st.error("❌ Nie znaleziono formularza z tym kodem")
                else:
                    st.warning("⚠️ Proszę wprowadzić kod dostępu")
    
    else:
        # Lista formularzy do uzupełnienia
        st.subheader("📋 Formularze oczekujące na uzupełnienie")

        with st.spinner("Ładowanie formularzy..."):
            formularze = get_forms_for_completion(db, "drzwi")

        # Grupowanie po wirtualnych folderach
        def _norm_name(t):
            import unicodedata, re
            if not t:
                return "nieznany_klient"
            t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii')
            t = re.sub(r'[^a-zA-Z0-9]+','_',t).strip('_').lower()
            return t or "nieznany_klient"

        def _folder_key(f):
            from datetime import datetime
            dt = f.get('data_pomiary') or f.get('data_utworzenia') or datetime.min
            day = dt.strftime('%d') if hasattr(dt, 'strftime') else '00'
            month = dt.strftime('%m') if hasattr(dt, 'strftime') else '00'
            year = dt.strftime('%Y') if hasattr(dt, 'strftime') else '0000'
            return f"{_norm_name(f.get('imie_nazwisko',''))}_{day}_{month}_{year}"
        
        if formularze:
            # Przygotuj dane do wyświetlenia
            display_data = []
            for form in formularze:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Klient": form.get('imie_nazwisko', ''),
                    "Telefon": form.get('telefon', ''),
                    "Wymiary": f"{form.get('szerokosc_otworu', '')} x {form.get('wysokosc_otworu', '')}",
                    "Monter": form.get('monter_id', '')
                })
            
            # Filtr po folderze
            folders = {}
            for f in formularze:
                key = _folder_key(f)
                folders.setdefault(key, 0)
                folders[key] += 1

            st.markdown("**Filtr folderów**")
            col_f1, col_f2 = st.columns([2,1])
            with col_f1:
                selected_folder = st.selectbox(
                    "Wybierz folder:",
                    options=[""] + sorted(folders.keys(), reverse=True),
                    format_func=lambda x: x if x else "Wszystkie foldery"
                )

            # Zastosuj filtr folderu
            filtered_forms = formularze
            if selected_folder:
                filtered_forms = [f for f in formularze if _folder_key(f) == selected_folder]

            display_data = []
            for form in filtered_forms:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Folder": _folder_key(form),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Klient": form.get('imie_nazwisko', ''),
                    "Telefon": form.get('telefon', ''),
                    "Wymiary": f"{form.get('szerokosc_otworu', '')} x {form.get('wysokosc_otworu', '')}",
                    "Monter": form.get('monter_id', '')
                })

            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Wybór formularza
            form_options = [""] + [f"🏠 {form['pomieszczenie']} | 👤 {form.get('imie_nazwisko', 'Brak danych')} | 🔑 {form.get('kod_dostepu', 'Brak danych')}" for form in filtered_forms]
            selected_display = st.selectbox(
                "🏠 Wybierz formularz do uzupełnienia:",
                options=form_options,
                format_func=lambda x: x if x else "Wybierz formularz..."
            )
            
            if selected_display:
                # Znajdź formularz na podstawie wybranego displayu
                selected_index = form_options.index(selected_display) - 1  # -1 bo pierwszy element to pusty
                selected_form = filtered_forms[selected_index]
        else:
            st.info("📭 Brak formularzy oczekujących na uzupełnienie")
    
    # Jeśli mamy wybrany formularz, pokaż formularz uzupełniania
    if selected_form:
        st.markdown("---")
        uzupelnij_formularz_drzwi(db, selected_form)

def uzupelnij_formularz_drzwi(db, formularz_data):
    """Formularz uzupełniania danych produktu"""
    st.subheader("🎯 Uzupełnienie danych produktu")
    
    # Informacje z pomiarów - część tylko do odczytu i część edytowalna
    with st.expander("📋 Informacje z pomiarów montera", expanded=True):
        # Pola TYLKO DO ODCZYTU (niezmienne przez sprzedawcę)
        st.markdown("**🔒 DANE NIEZMIENNE (z pomiarów montera):**")
        col_readonly1, col_readonly2 = st.columns(2)
        
        with col_readonly1:
            st.text(f"🏠 Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"📏 Szerokość otworu: {formularz_data.get('szerokosc_otworu', '')} cm")
            st.text(f"📏 Wysokość otworu: {formularz_data.get('wysokosc_otworu', '')} cm")
            st.text(f"🧱 Grubość muru: {formularz_data.get('grubosc_muru', '')} cm")
            st.text(f"📐 Mierzona od: {formularz_data.get('mierzona_od', '')}")
        
        with col_readonly2:
            st.text(f"🏗️ Stan ściany: {formularz_data.get('stan_sciany', '')}")
            st.text(f"👤 Klient: {formularz_data.get('imie_nazwisko', '')}")
            st.text(f"📞 Telefon: {formularz_data.get('telefon', '')}")
            st.text(f"👷 Monter: {formularz_data.get('monter_id', '')}")
            st.text(f"📅 Data: {formularz_data.get('data_pomiary', datetime.now()).strftime('%Y-%m-%d %H:%M') if formularz_data.get('data_pomiary') else 'Brak'}")
        
        # Strona otwierania (TYLKO DO ODCZYTU)
        strona_otw = formularz_data.get('strona_otwierania', {}) or {}
        if any(strona_otw.values()):
            st.markdown("**🚪 STRONA OTWIERANIA (niezmienne):**")
            strony_txt = []
            if strona_otw.get('lewe_przyl'): strony_txt.append("Lewe")
            if strona_otw.get('prawe_przyl'): strony_txt.append("Prawe")
            if strona_otw.get('lewe_odwr'): strony_txt.append("Lewe odwrotna przylga")
            if strona_otw.get('prawe_odwr'): strony_txt.append("Prawe odwrotna przylga")
            st.text(f"🔒 Kierunek: {', '.join(strony_txt)}")
            
            if formularz_data.get('napis_nad_drzwiami'):
                st.text(f"🔒 Otwierane na: {formularz_data.get('napis_nad_drzwiami', '')}")
            if formularz_data.get('szerokosc_skrzydla'):
                st.text(f"🔒 Szerokość skrzydła: {formularz_data.get('szerokosc_skrzydla', '')} cm")
                
            # Wyświetl galerię wszystkich opcji otwierania
            st.markdown("---")
            display_door_options_gallery(strona_otw)
        
        # Uwagi montera (TYLKO DO ODCZYTU)
        if formularz_data.get('uwagi_montera'):
            st.markdown("**💬 UWAGI MONTERA (niezmienne):**")
            st.text_area("", value=formularz_data.get('uwagi_montera', ''), height=80, disabled=True, key="readonly_uwagi_montera")
        
        # Norma/Szkic (TYLKO DO ODCZYTU)
        if formularz_data.get('norma'):
            st.text(f"🔒 Norma/Szkic: {formularz_data.get('norma', '')}")
        
        st.markdown("---")
        
        # Pola EDYTOWALNE przez sprzedawcę
        st.markdown("**✏️ DANE TECHNICZNE DO EDYCJI:**")
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            typ_drzwi_edit = st.selectbox("Typ drzwi:", 
                                        ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"], 
                                        index=["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"].index(formularz_data.get('typ_drzwi', 'Przylgowe')) if formularz_data.get('typ_drzwi') in ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"] else 0,
                                        key="typ_drzwi_edit")
            
            oscieznica_edit = st.text_input("Ościeżnica:", 
                                          value=formularz_data.get('oscieznica', ''), 
                                          key="oscieznica_edit")
            
            opaska_edit = st.radio("Opaska:", 
                                 ["6 cm", "8 cm"], 
                                 index=["6 cm", "8 cm"].index(formularz_data.get('opaska', '6 cm')) if formularz_data.get('opaska') in ["6 cm", "8 cm"] else 0,
                                 horizontal=True,
                                 key="opaska_edit")
        
        with col_edit2:
            kat_zaciecia_edit = st.selectbox("Kąt zacięcia:", 
                                           ["45°", "90°", "0°"], 
                                           index=["45°", "90°", "0°"].index(formularz_data.get('kat_zaciecia', '45°')) if formularz_data.get('kat_zaciecia') in ["45°", "90°", "0°"] else 0,
                                           key="kat_zaciecia_edit")
            
            prog_edit = st.text_input("Próg:", 
                                    value=formularz_data.get('prog', ''), 
                                    key="prog_edit")
            
            wizjer_edit = st.checkbox("Wizjer", 
                                    value=bool(formularz_data.get('wizjer', False)),
                                    key="wizjer_edit")

    
    # ID sprzedawcy
    sprzedawca_id = st.text_input("🔑 Imię Sprzedawcy:", key="sprzedawca_id")
    
    if not sprzedawca_id:
        st.warning("⚠️ Proszę podać Imię sprzedawcy")
        return
    
    # Wyświetl wszystkie zdjęcia z pomiarów w głównej sekcji
    if 'zdjecia' in formularz_data and formularz_data['zdjecia']:
        display_images(formularz_data['zdjecia'], max_width=400)
        st.markdown("---")
    
    # Formularz danych produktu
    st.subheader("🏷️ Dane produktu")
    
    # Inicjalizacja auto-fill values w session_state
    if 'autofill_drzwi' not in st.session_state:
        st.session_state.autofill_drzwi = {}
    
    st.info("💡 **Auto-fill:** Zaznacz checkbox obok pól, które mają być automatycznie kopiowane do następnych protokołów tego samego klienta")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Producent z auto-fill
        col_prod1, col_prod2 = st.columns([4, 1])
        with col_prod1:
            producent_value = st.session_state.autofill_drzwi.get('producent', '') if st.session_state.autofill_drzwi.get('producent_auto', False) else ''
            producent = st.text_input("1. Producent:", value=producent_value, key="producent_sprzedawca")
        with col_prod2:
            producent_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('producent_auto', False), key="producent_auto", help="Auto-fill dla następnych protokołów")
        
        # Seria z auto-fill
        col_seria1, col_seria2 = st.columns([4, 1])
        with col_seria1:
            seria_value = st.session_state.autofill_drzwi.get('seria', '') if st.session_state.autofill_drzwi.get('seria_auto', False) else ''
            seria = st.text_input("2. Seria:", value=seria_value, key="seria_sprzedawca")
        with col_seria2:
            seria_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('seria_auto', False), key="seria_auto", help="Auto-fill dla następnych protokołów")
        
        # Typ z auto-fill
        col_typ1, col_typ2 = st.columns([4, 1])
        with col_typ1:
            typ_value = st.session_state.autofill_drzwi.get('typ', '') if st.session_state.autofill_drzwi.get('typ_auto', False) else ''
            typ_produktu = st.text_input("3. Typ:", value=typ_value, key="typ_sprzedawca")
        with col_typ2:
            typ_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('typ_auto', False), key="typ_auto", help="Auto-fill dla następnych protokołów")
        
        # Okleina z auto-fill
        col_okl1, col_okl2 = st.columns([4, 1])
        with col_okl1:
            okleina_value = st.session_state.autofill_drzwi.get('rodzaj_okleiny', '') if st.session_state.autofill_drzwi.get('okleina_auto', False) else ''
            rodzaj_okleiny = st.text_input("4. Rodzaj okleiny:", value=okleina_value, key="okleina_sprzedawca")
        with col_okl2:
            okleina_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('okleina_auto', False), key="okleina_auto", help="Auto-fill dla następnych protokołów")
        
        # Szyby z auto-fill
        col_szyby1, col_szyby2 = st.columns([4, 1])
        with col_szyby1:
            szyby_value = st.session_state.autofill_drzwi.get('ilosc_szyb', '') if st.session_state.autofill_drzwi.get('szyby_auto', False) else ''
            ilosc_szyb = st.text_input("5. Ilość szyb:", value=szyby_value, key="szyby_sprzedawca")
        with col_szyby2:
            szyby_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('szyby_auto', False), key="szyby_auto", help="Auto-fill dla następnych protokołów")
    
    with col2:
        # Zamek z auto-fill
        col_zamek1, col_zamek2 = st.columns([4, 1])
        with col_zamek1:
            zamek_value = st.session_state.autofill_drzwi.get('zamek', '') if st.session_state.autofill_drzwi.get('zamek_auto', False) else ''
            zamek = st.text_input("6. Zamek:", value=zamek_value, key="zamek_sprzedawca")
        with col_zamek2:
            zamek_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('zamek_auto', False), key="zamek_auto", help="Auto-fill dla następnych protokołów")
        
        # Szyba z auto-fill
        col_szyba1, col_szyba2 = st.columns([4, 1])
        with col_szyba1:
            szyba_value = st.session_state.autofill_drzwi.get('szyba', '') if st.session_state.autofill_drzwi.get('szyba_auto', False) else ''
            szyba = st.text_input("7. Szyba:", value=szyba_value, key="szyba_sprzedawca")
        with col_szyba2:
            szyba_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('szyba_auto', False), key="szyba_auto", help="Auto-fill dla następnych protokołów")
        
        # Wentylacja z auto-fill
        col_went1, col_went2 = st.columns([4, 1])
        with col_went1:
            went_value = st.session_state.autofill_drzwi.get('wentylacja', '') if st.session_state.autofill_drzwi.get('wentylacja_auto', False) else ''
            wentylacja = st.text_input("8. Wentylacja:", value=went_value, key="wentylacja_sprzedawca")
        with col_went2:
            wentylacja_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('wentylacja_auto', False), key="wentylacja_auto", help="Auto-fill dla następnych protokołów")
        
        # Klamka z auto-fill
        col_klamka1, col_klamka2 = st.columns([4, 1])
        with col_klamka1:
            klamka_value = st.session_state.autofill_drzwi.get('klamka', '') if st.session_state.autofill_drzwi.get('klamka_auto', False) else ''
            klamka = st.text_input("9. Klamka:", value=klamka_value, key="klamka_sprzedawca")
        with col_klamka2:
            klamka_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('klamka_auto', False), key="klamka_auto", help="Auto-fill dla następnych protokołów")
        
        # Kolor wizjera z auto-fill
        col_wiz1, col_wiz2 = st.columns([4, 1])
        with col_wiz1:
            wiz_value = st.session_state.autofill_drzwi.get('kolor_wizjera', '') if st.session_state.autofill_drzwi.get('wizjer_auto', False) else ''
            kolor_wizjera = st.text_input("10. Kolor wizjera:", value=wiz_value, key="kolor_wizjera_sprzedawca")
        with col_wiz2:
            wizjer_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('wizjer_auto', False), key="wizjer_auto", help="Auto-fill dla następnych protokołów")
        
        # Wypełnienie z auto-fill
        col_wyp1, col_wyp2 = st.columns([4, 1])
        with col_wyp1:
            wyp_value = st.session_state.autofill_drzwi.get('wypelnienie', '') if st.session_state.autofill_drzwi.get('wypelnienie_auto', False) else ''
            wypelnienie = st.text_input("11. Wypełnienie:", value=wyp_value, key="wypelnienie_sprzedawca")
        with col_wyp2:
            wypelnienie_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('wypelnienie_auto', False), key="wypelnienie_auto", help="Auto-fill dla następnych protokołów")
        
        # Kolor okucia z auto-fill
        col_okuc1, col_okuc2 = st.columns([4, 1])
        with col_okuc1:
            okuc_value = st.session_state.autofill_drzwi.get('kolor_okuc', '') if st.session_state.autofill_drzwi.get('okuc_auto', False) else ''
            kolor_okuc = st.text_input("12. Kolor okucia:", value=okuc_value, key="kolor_okuc_sprzedawca")
        with col_okuc2:
            okuc_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('okuc_auto', False), key="okuc_auto", help="Auto-fill dla następnych protokołów")
        
        kolor_osc = st.checkbox("Inny kolor ościeżnicy")
        if kolor_osc:
            col_osc1, col_osc2 = st.columns([4, 1])
            with col_osc1:
                osc_value = st.session_state.autofill_drzwi.get('kolor_osc', '') if st.session_state.autofill_drzwi.get('osc_auto', False) else ''
                kolor_osc = st.text_input("Kolor ość. (jeśli inna):", value=osc_value, key="kolor_osc_sprzedawca")
            with col_osc2:
                osc_auto = st.checkbox("🔄", value=st.session_state.autofill_drzwi.get('osc_auto', False), key="osc_auto", help="Auto-fill dla następnych protokołów")
    
    st.subheader("➕ Opcje dodatkowe")
    opcje_dodatkowe = st.text_area("", height=100, key="opcje_sprzedawca")
    
    # Uwagi dla klienta
    st.subheader("💬 Uwagi dla klienta")
    uwagi_klienta = st.checkbox("Uwagi dla klienta")
    if uwagi_klienta:
        uwagi_klienta = st.text_area("", height=100, key="uwagi_klienta_sprzedawca")
    
    # Przycisk finalizacji
    if st.button("✅ Finalizuj zamówienie", type="primary"):
        # Aktualizuj auto-fill values w session_state
        if producent_auto:
            st.session_state.autofill_drzwi['producent'] = producent
            st.session_state.autofill_drzwi['producent_auto'] = True
        elif 'producent_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['producent_auto']
            
        if seria_auto:
            st.session_state.autofill_drzwi['seria'] = seria
            st.session_state.autofill_drzwi['seria_auto'] = True
        elif 'seria_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['seria_auto']
            
        if typ_auto:
            st.session_state.autofill_drzwi['typ'] = typ_produktu
            st.session_state.autofill_drzwi['typ_auto'] = True
        elif 'typ_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['typ_auto']
            
        if okleina_auto:
            st.session_state.autofill_drzwi['rodzaj_okleiny'] = rodzaj_okleiny
            st.session_state.autofill_drzwi['okleina_auto'] = True
        elif 'okleina_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['okleina_auto']
            
        if szyby_auto:
            st.session_state.autofill_drzwi['ilosc_szyb'] = ilosc_szyb
            st.session_state.autofill_drzwi['szyby_auto'] = True
        elif 'szyby_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['szyby_auto']
            
        if zamek_auto:
            st.session_state.autofill_drzwi['zamek'] = zamek
            st.session_state.autofill_drzwi['zamek_auto'] = True
        elif 'zamek_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['zamek_auto']
            
        if szyba_auto:
            st.session_state.autofill_drzwi['szyba'] = szyba
            st.session_state.autofill_drzwi['szyba_auto'] = True
        elif 'szyba_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['szyba_auto']
            
        if wentylacja_auto:
            st.session_state.autofill_drzwi['wentylacja'] = wentylacja
            st.session_state.autofill_drzwi['wentylacja_auto'] = True
        elif 'wentylacja_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['wentylacja_auto']
            
        if klamka_auto:
            st.session_state.autofill_drzwi['klamka'] = klamka
            st.session_state.autofill_drzwi['klamka_auto'] = True
        elif 'klamka_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['klamka_auto']
            
        if wizjer_auto:
            st.session_state.autofill_drzwi['kolor_wizjera'] = kolor_wizjera
            st.session_state.autofill_drzwi['wizjer_auto'] = True
        elif 'wizjer_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['wizjer_auto']
            
        if wypelnienie_auto:
            st.session_state.autofill_drzwi['wypelnienie'] = wypelnienie
            st.session_state.autofill_drzwi['wypelnienie_auto'] = True
        elif 'wypelnienie_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['wypelnienie_auto']
            
        if okuc_auto:
            st.session_state.autofill_drzwi['kolor_okuc'] = kolor_okuc
            st.session_state.autofill_drzwi['okuc_auto'] = True
        elif 'okuc_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['okuc_auto']
            
        # Auto-fill dla koloru ościeżnicy (tylko jeśli checkbox jest zaznaczony)
        if kolor_osc and 'osc_auto' in locals() and osc_auto:
            st.session_state.autofill_drzwi['kolor_osc'] = kolor_osc
            st.session_state.autofill_drzwi['osc_auto'] = True
        elif 'osc_auto' in st.session_state.autofill_drzwi:
            del st.session_state.autofill_drzwi['osc_auto']
            
        dane_sprzedawcy = {
            "producent": producent,
            "seria": seria,
            "typ": typ_produktu,
            "rodzaj_okleiny": rodzaj_okleiny,
            "ilosc_szyb": ilosc_szyb,
            "zamek": zamek,
            "szyba": szyba,
            "wentylacja": wentylacja,
            "klamka": klamka,
            "kolor_wizjera": kolor_wizjera,
            "kolor_osc": kolor_osc,
            "wypelnienie": wypelnienie,
            "kolor_okuc": kolor_okuc,
            "opcje_dodatkowe": opcje_dodatkowe,
            "uwagi_klienta": uwagi_klienta,
            # Edytowane dane techniczne przez sprzedawcę
            "typ_drzwi": typ_drzwi_edit,
            "oscieznica": oscieznica_edit,
            "opaska": opaska_edit,
            "kat_zaciecia": kat_zaciecia_edit,
            "prog": prog_edit,
            "wizjer": wizjer_edit
        }
        
        # Sprawdź wymagane pola
        wymagane_pola = ["producent", "seria"]
        brakujace_pola = [pole for pole in wymagane_pola if not dane_sprzedawcy.get(pole)]
        
        if brakujace_pola:
            st.error(f"❌ Proszę wypełnić wymagane pola: {', '.join(brakujace_pola)}")
        else:
            with st.spinner("Finalizowanie zamówienia..."):
                success = complete_form_by_seller(
                    db, "drzwi", formularz_data['id'], 
                    dane_sprzedawcy, sprzedawca_id
                )
                
                if success:
                    st.success("🎉 Zamówienie zostało sfinalizowane!")
                    st.balloons()
                    
                    # Przygotuj kompletne dane do PDF
                    complete_data = formularz_data.copy()
                    complete_data.update(dane_sprzedawcy)
                    
                    # Przycisk pobierania PDF
                    col_pdf1, col_pdf2 = st.columns(2)
                    
                    with col_pdf1:
                        st.subheader("📄 Pobierz dokumenty")
                        display_pdf_download_button(complete_data, 'drzwi', formularz_data['id'])
                    
                    # Pokaż kompletne dane
                    with st.expander("📄 Kompletne dane zamówienia"):
                        st.json(complete_data)
                        
                    st.info("ℹ️ Formularz został przeniesiony do listy aktywnych zamówień")
                else:
                    st.error("❌ Błąd podczas finalizacji zamówienia!")

def formularz_montera_podlogi():
    """Formularz pomiarów podłóg dla montera"""
    st.header("🔧 Pomiary podłóg - Monter")
    
    # Inicjalizacja bazy danych
    db = setup_database()
    
    # ID montera
    monter_id = st.text_input("🔑 Imię Montera:", value="", key="monter_id_podlogi")
    
    if not monter_id:
        st.warning("⚠️ Proszę podać Imię montera przed wypełnieniem formularza")
        return
    
    # Podstawowe informacje
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Podstawowe informacje")
        pomieszczenie = st.text_input("Pomieszczenie:", key="pomieszczenie_monter_podlogi")
        imie_nazwisko = st.text_input("Imię i nazwisko klienta:", key="imie_nazwisko_monter_podlogi")
        telefon = st.text_input("Telefon klienta:", key="telefon_monter_podlogi")
        
        # System montażu
        st.subheader("🔨 System montażu")
        system_montazu = st.radio(
            "Wybierz system montażu:",
            ["Symetrycznie (cegiełka)", "Niesymetrycznie"],
            key="system_montazu_monter"
        )
    
    with col2:
        st.subheader("📐 Specyfikacja")
        podklad = st.text_input("Podkład:", key="podklad_monter")
        
        # Czy może być MDF
        mdf_mozliwy = st.radio(
            "Czy może być MDF?",
            ["TAK", "NIE"],
            key="mdf_mozliwy_monter"
        )
    
    # Pomiary listw
    st.subheader("📏 Pomiary listw")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        nw = st.number_input("NW (szt.):", min_value=0, step=1, key="nw_monter")
        nz = st.number_input("NZ (szt.):", min_value=0, step=1, key="nz_monter")
    
    with col4:
        l = st.number_input("Ł (szt.):", min_value=0, step=1, key="l_monter")
        zl = st.number_input("ZL (szt.):", min_value=0, step=1, key="zl_monter")
    
    with col5:
        zp = st.number_input("ZP (szt.):", min_value=0, step=1, key="zp_monter")
    
    # Listwy progowe
    st.subheader("🚪 Listwy progowe")
    col6, col7, col8 = st.columns(3)
    
    with col6:
        listwy_jaka = st.text_input("Jaka?", key="listwy_jaka_monter")
    
    with col7:
        listwy_ile = st.text_input("Ile?", key="listwy_ile_monter")
    
    with col8:
        listwy_gdzie = st.text_input("Gdzie?", key="listwy_gdzie_monter")
    
    # Uwagi montera
    st.subheader("📝 Uwagi montera")
    uwagi_montera = st.text_area("Uwagi dotyczące pomiarów:", height=100, key="uwagi_montera_podlogi")
    
    # Ostrzeżenie
    st.warning("⚠️ UWAGA!! Podłoże powinno być suche i równe!!")
    
    # Zapisz do przechowalni
    if st.button("🗂️ Zapisz do przechowalni", type="primary"):
        dane_pomiary = {
            "pomieszczenie": pomieszczenie,
            "imie_nazwisko": imie_nazwisko,
            "telefon": telefon,
            "system_montazu": system_montazu,
            "podklad": podklad,
            "mdf_mozliwy": mdf_mozliwy,
            "nw": nw,
            "nz": nz,
            "l": l,
            "zl": zl,
            "zp": zp,
            "listwy_jaka": listwy_jaka,
            "listwy_ile": listwy_ile,
            "listwy_gdzie": listwy_gdzie,
            "uwagi_montera": uwagi_montera,
            # Pola sprzedawcy - puste na razie
            "rodzaj_podlogi": "",
            "seria": "",
            "kolor": "",
            "folia": "",
            "listwa_przypodlogowa": "",
            "uwagi": ""
        }
        
        # Sprawdź wymagane pola
        wymagane_pola = ["pomieszczenie", "imie_nazwisko", "telefon"]
        brakujace_pola = [pole for pole in wymagane_pola if not dane_pomiary.get(pole)]
        
        if brakujace_pola:
            st.error(f"❌ Proszę wypełnić wymagane pola: {', '.join(brakujace_pola)}")
        else:
            with st.spinner("Zapisywanie szkicu do przechowalni..."):
                draft_id = save_draft_data(db, "podlogi", dane_pomiary, monter_id)
                
                if draft_id:
                    st.success(f"✅ Szkic pomiarów został zapisany do przechowalni! ID: {draft_id}")
                    st.info("📋 **Szkic można teraz edytować i finalizować w sekcji 'Przechowalnia'**")
                    st.info("📷 **Zdjęcia można dodać w przechowalni po wybraniu szkicu**")
                    
                    # Pokaż zapisane dane
                    with st.expander("Pokaż zapisany szkic"):
                        st.json(dane_pomiary)
                else:
                    st.error("❌ Błąd podczas zapisywania szkicu!")


def formularz_montera_drzwi_wejsciowe():
    """Formularz pomiarów dla drzwi wejściowych - monter"""
    st.header("🚨 PROTOKÓŁ POMIARÓW DRZWI WEJŚCIOWYCH")

    db = setup_database()
    
    # ID montera
    monter_id = st.text_input("🔑 Imię Montera:", value="", key="monter_id_we")
    
    if not monter_id:
        st.warning("⚠️ Proszę podać Imię montera przed wypełnieniem formularza")
        return
    
    st.subheader("📋 Podstawowe informacje")
    numer_strony = st.text_input("Numer strony:", key="numer_strony_we")
    imie_nazwisko = st.text_input("Imię i Nazwisko:", key="imie_nazwisko_we")
    telefon = st.text_input("Telefon:", key="telefon_we")
    pomieszczenie = st.text_input("Pomieszczenie:", key="pomieszczenie_we")
    
    st.subheader("📏 Wymiary otworu")
    col_wym1, col_wym2, col_wym3 = st.columns(3)
    
    with col_wym1:
        szerokosc_otworu = st.text_input("Szerokość otworu:", key="szerokosc_we")
    with col_wym2:
        wysokosc_otworu = st.text_input("Wysokość otworu:", key="wysokosc_we")
    with col_wym3:
        mierzona_od = st.selectbox("Mierzona od:", 
                                 ["szkolenia", "poziomu", "podłogi", "inne"], 
                                 key="mierzona_od_we")
        if mierzona_od == "inne":
            mierzona_od_inne = st.text_input("Inne:", key="mierzona_od_inne_we")
            mierzona_od = mierzona_od_inne      

    col_tech1, col_tech2 = st.columns(2)
    
    with col_tech1:
        st.subheader("🏗️ Dane techniczne")
        skrot = st.text_input("Skrót:", key="skrot_we")
        grubosc_muru = st.text_input("Grubość muru (cm):", key="grubosc_muru_we")
        stan_sciany = st.text_input("Stan ściany (wykończenie):", 
                                  help="np. tapeta, płyta g-k, itp.", key="stan_sciany_we")
        oscieznica = st.text_input("Ościeżnica:", key="oscieznica_we")
        okapnik = st.text_input("Okapnik:", key="okapnik_we")
        prog = st.text_input("Próg:", key="prog_we")
        wizjer = st.checkbox("Wizjer:", key="wizjer_we")
        elektrozaczep = st.text_input("Elektrozaczep:", key="elektrozaczep_we")
        uwagi_montera_checkbox = st.checkbox("Uwagi montera:", key="uwagi_montera_checkbox_we")
        uwagi_montera = ""
        if uwagi_montera_checkbox:
            uwagi_montera = st.text_area("Uwagi montera:", height=100, key="uwagi_montera_text_we")
    
    with col_tech2:
        st.subheader("🚪 Strona otwierania")
        st.markdown("**Kierunek otwierania:**")
        na_zewnatrz = st.checkbox("Na zewnątrz", key="na_zewnatrz_we")
        do_wewnatrz = st.checkbox("Do wewnątrz", key="do_wewnatrz_we")
        
        st.markdown("**Strona zawiasów:**")
        lewe = st.checkbox("Lewe", key="lewe_we")
        prawe = st.checkbox("Prawe", key="prawe_we")
            
        # Tutaj można dodać obrazki podobnie jak w zwykłych drzwiach
        if lewe:
            st.markdown("*Lewe otwieranie*")
        if prawe:
            st.markdown("*Prawe otwieranie*")
    
    szkic_button = st.button("🗂️ Zapisz do przechowalni", type="primary")
    
    if szkic_button:
        dane_szkicu = {
            "numer_strony": numer_strony,
                "imie_nazwisko": imie_nazwisko,
                "telefon": telefon,
                "pomieszczenie": pomieszczenie,
                "szerokosc_otworu": szerokosc_otworu,
                "wysokosc_otworu": wysokosc_otworu,
                "mierzona_od": mierzona_od,
                "skrot": skrot,
                "grubosc_muru": grubosc_muru,
                "stan_sciany": stan_sciany,
                "oscieznica": oscieznica,
                "okapnik": okapnik,
                "prog": prog,
                "wizjer": wizjer,
                "elektrozaczep": elektrozaczep,
                "strona_otwierania": {
                    "na_zewnatrz": na_zewnatrz,
                    "do_wewnatrz": do_wewnatrz,
                    "lewe": lewe,
                    "prawe": prawe
                },
                "uwagi_montera": uwagi_montera,
                "collection_target": "drzwi_wejsciowe"  # Ważne dla szkiców
        }
            
        with st.spinner("Zapisywanie szkicu..."):
            success = save_draft_data(db, "drzwi_wejsciowe", dane_szkicu, monter_id)
            
            if success:
                st.success("📝 Szkic został zapisany w kwarantannie!")
                st.info("💡 Możesz kontynuować edycję w zakładce 'Przechowalnia'")
                st.info("📷 **Zdjęcia można dodać w przechowalni po wybraniu szkicu**")
            else:
                st.error("❌ Błąd podczas zapisywania szkicu!")


def formularz_sprzedawcy_podlogi():
    """Formularz uzupełniania danych produktu podłóg przez sprzedawcę"""
    st.header("💼 Uzupełnienie danych produktu - Sprzedawca (Podłogi)")
    
    db = setup_database()
    
    # Sposób dostępu do formularza
    sposob_dostepu = st.radio(
        "Wybierz sposób dostępu:",
        ["📋 Lista formularzy do uzupełnienia", "🔑 Kod dostępu"],
        key="sposob_dostepu_podlogi"
    )
    
    selected_form = None
    
    if sposob_dostepu == "🔑 Kod dostępu":
        # Dostęp przez kod
        col1, col2 = st.columns([2, 1])
        
        with col1:
            kod_dostepu = st.text_input("Wprowadź kod dostępu:", key="kod_dostepu_input_podlogi")
        
        with col2:
            if st.button("🔍 Znajdź formularz", key="znajdz_podlogi"):
                if kod_dostepu:
                    with st.spinner("Wyszukiwanie formularza..."):
                        selected_form = get_form_by_access_code(db, "podlogi", kod_dostepu)
                        
                        if selected_form:
                            st.success("✅ Formularz znaleziony!")
                        else:
                            st.error("❌ Nie znaleziono formularza z tym kodem")
                else:
                    st.warning("⚠️ Proszę wprowadzić kod dostępu")
    
    else:
        # Lista formularzy do uzupełnienia
        st.subheader("📋 Formularze oczekujące na uzupełnienie")
        
        with st.spinner("Ładowanie formularzy..."):
            formularze = get_forms_for_completion(db, "podlogi")
        
        if formularze:
            # Przygotuj dane do wyświetlenia
            display_data = []
            for form in formularze:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                suma_listw = (form.get('nw', 0) + form.get('nz', 0) + form.get('l', 0) + 
                             form.get('zl', 0) + form.get('zp', 0))
                
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Telefon": form.get('telefon', ''),
                    "System montażu": form.get('system_montazu', ''),
                    "Suma listw": suma_listw,
                    "MDF możliwy": form.get('mdf_mozliwy', ''),
                    "Monter": form.get('monter_id', '')
                })
            
            # Filtr po folderze (dla podłóg)
            def _folder_key_p(f):
                from datetime import datetime
                import unicodedata, re
                def _norm_name_local(t):
                    if not t:
                        return "nieznany_klient"
                    t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii')
                    t = re.sub(r'[^a-zA-Z0-9]+','_',t).strip('_').lower()
                    return t or "nieznany_klient"
                dt = f.get('data_pomiary') or f.get('data_utworzenia') or datetime.min
                day = dt.strftime('%d') if hasattr(dt, 'strftime') else '00'
                month = dt.strftime('%m') if hasattr(dt, 'strftime') else '00'
                year = dt.strftime('%Y') if hasattr(dt, 'strftime') else '0000'
                return f"{_norm_name_local(f.get('imie_nazwisko',''))}_{day}_{month}_{year}"

            folders_p = {}
            for f in formularze:
                keyf = _folder_key_p(f)
                folders_p.setdefault(keyf, 0)
                folders_p[keyf] += 1

            st.markdown("**Filtr folderów**")
            col_pf1, col_pf2 = st.columns([2,1])
            with col_pf1:
                selected_folder_p = st.selectbox(
                    "Wybierz folder:",
                    options=[""] + sorted(folders_p.keys(), reverse=True),
                    format_func=lambda x: x if x else "Wszystkie foldery",
                    key="folder_select_podlogi"
                )

            filtered_forms_p = formularze
            if selected_folder_p:
                filtered_forms_p = [f for f in formularze if _folder_key_p(f) == selected_folder_p]

            display_data = []
            for form in filtered_forms_p:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                suma_listw = (form.get('nw', 0) + form.get('nz', 0) + form.get('l', 0) + 
                             form.get('zl', 0) + form.get('zp', 0))
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Folder": _folder_key_p(form),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Telefon": form.get('telefon', ''),
                    "System montażu": form.get('system_montazu', ''),
                    "Suma listw": suma_listw,
                    "MDF możliwy": form.get('mdf_mozliwy', ''),
                    "Monter": form.get('monter_id', '')
                })

            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Wybór formularza
            form_options_p = [""] + [f"🏠 {form['pomieszczenie']} | 👤 {form.get('imie_nazwisko', 'Brak danych')} | 📅 {form.get('data_pomiaru', 'Brak danych')} | 🔑 {form.get('kod_dostepu', 'Brak danych')}" for form in filtered_forms_p]
            selected_display = st.selectbox(
                "🏠 Wybierz formularz do uzupełnienia:",
                options=form_options_p,
                format_func=lambda x: x if x else "Wybierz formularz...",
                key="select_form_podlogi"
            )
            
            if selected_display:
                # Znajdź formularz na podstawie wybranego displayu
                selected_index = form_options_p.index(selected_display) - 1  # -1 bo pierwszy element to pusty
                selected_form = filtered_forms_p[selected_index]
        else:
            st.info("📭 Brak formularzy oczekujących na uzupełnienie")
    
    # Jeśli mamy wybrany formularz, pokaż formularz uzupełniania
    if selected_form:
        st.markdown("---")
        uzupelnij_formularz_podlogi(db, selected_form)

def uzupelnij_formularz_podlogi(db, formularz_data):
    """Formularz uzupełniania danych produktu podłóg"""
    st.subheader("🎯 Uzupełnienie danych produktu - Podłogi")
    
    # Informacje z pomiarów - część tylko do odczytu i część edytowalna
    with st.expander("📋 Informacje z pomiarów montera", expanded=True):
        # Pola TYLKO DO ODCZYTU (niezmienne przez sprzedawcę)
        st.markdown("**🔒 DANE NIEZMIENNE (z pomiarów montera):**")
        col_readonly1, col_readonly2 = st.columns(2)
        
        with col_readonly1:
            st.text(f"🏠 Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"📞 Telefon: {formularz_data.get('telefon', '')}")
            st.text(f"👷 Monter: {formularz_data.get('monter_id', '')}")
        
        with col_readonly2:
            st.text(f"📅 Data: {formularz_data.get('data_pomiary', datetime.now()).strftime('%Y-%m-%d %H:%M') if formularz_data.get('data_pomiary') else 'Brak'}")
            st.text(f"🔑 Kod dostępu: {formularz_data.get('kod_dostepu', '')}")
        
        st.markdown("---")
        
        # Pola EDYTOWALNE przez sprzedawcę
        st.markdown("**✏️ SPECYFIKACJA MONTAŻU DO EDYCJI:**")
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            system_montazu_edit = st.text_input("System montażu:", 
                                              value=formularz_data.get('system_montazu', ''), 
                                              key="system_montazu_edit")
            podklad_edit = st.text_input("Podkład:", 
                                       value=formularz_data.get('podklad', ''), 
                                       key="podklad_edit")
        
        with col_edit2:
            mdf_mozliwy_edit = st.text_input("MDF możliwy:", 
                                           value=formularz_data.get('mdf_mozliwy', ''), 
                                           key="mdf_mozliwy_edit")
        
        st.markdown("**✏️ POMIARY LISTW DO EDYCJI:**")
        col_listwy1, col_listwy2, col_listwy3 = st.columns(3)
        
        with col_listwy1:
            nw_edit = st.number_input("NW (Narożnik Wewnętrzny):", 
                                    min_value=0, 
                                    value=int(formularz_data.get('nw', 0)), 
                                    key="nw_edit")
            nz_edit = st.number_input("NZ (Narożnik Zewnętrzny):", 
                                    min_value=0, 
                                    value=int(formularz_data.get('nz', 0)), 
                                    key="nz_edit")
        
        with col_listwy2:
            l_edit = st.number_input("Ł (Łącznik):", 
                                   min_value=0, 
                                   value=int(formularz_data.get('l', 0)), 
                                   key="l_edit")
            zl_edit = st.number_input("ZL (Zakończenie Lewe):", 
                                    min_value=0, 
                                    value=int(formularz_data.get('zl', 0)), 
                                    key="zl_edit")
        
        with col_listwy3:
            zp_edit = st.number_input("ZP (Zakończenie Prawe):", 
                                    min_value=0, 
                                    value=int(formularz_data.get('zp', 0)), 
                                    key="zp_edit")
            suma_listw_edit = nw_edit + nz_edit + l_edit + zl_edit + zp_edit
            st.markdown(f"**SUMA LISTW: {suma_listw_edit} szt.**")
        
        st.markdown("**✏️ LISTWY PROGOWE DO EDYCJI:**")
        col_prog1, col_prog2, col_prog3 = st.columns(3)
        
        with col_prog1:
            listwy_jaka_edit = st.text_input("Jaka:", 
                                           value=formularz_data.get('listwy_jaka', ''), 
                                           key="listwy_jaka_edit")
        
        with col_prog2:
            listwy_ile_edit = st.text_input("Ile:", 
                                          value=formularz_data.get('listwy_ile', ''), 
                                          key="listwy_ile_edit")
        
        with col_prog3:
            listwy_gdzie_edit = st.text_input("Gdzie:", 
                                            value=formularz_data.get('listwy_gdzie', ''), 
                                            key="listwy_gdzie_edit")
        
        # Uwagi montera (TYLKO DO ODCZYTU)
        if formularz_data.get('uwagi_montera'):
            st.markdown("---")
            st.markdown("**💬 UWAGI MONTERA (niezmienne):**")
            st.text_area("", value=formularz_data.get('uwagi_montera', ''), height=80, disabled=True, key="readonly_uwagi_montera_podlogi")

    
    # ID sprzedawcy
    sprzedawca_id = st.text_input("🔑 Imię Sprzedawcy:", key="sprzedawca_id_podlogi")
    
    if not sprzedawca_id:
        st.warning("⚠️ Proszę podać Imię sprzedawcy")
        return
    
    # Wyświetl wszystkie zdjęcia z pomiarów w głównej sekcji
    if 'zdjecia' in formularz_data and formularz_data['zdjecia']:
        st.subheader("📸 Zdjęcia z pomiarów wykonanych przez montera")
        display_images(formularz_data['zdjecia'], max_width=400)
        st.markdown("---")
    
    # Formularz danych produktu
    st.subheader("🏷️ Dane produktu")
    col1, col2 = st.columns(2)
    
    with col1:
        rodzaj_podlogi = st.text_input("1. Rodzaj podłogi:", key="rodzaj_podlogi_sprzedawca")
        seria = st.text_input("2. Seria:", key="seria_podlogi_sprzedawca")
        kolor = st.text_input("3. Kolor:", key="kolor_sprzedawca")
    
    with col2:
        folia = st.text_input("4. Folia:", key="folia_sprzedawca")
        listwa_przypodlogowa = st.text_input("5. Listwa przypodłogowa:", key="listwa_sprzedawca")
    
    # Uwagi
    st.subheader("💬 Uwagi")
    uwagi = st.text_area("Uwagi dla klienta:", height=100, key="uwagi_podlogi_sprzedawca")
    
    # Przycisk finalizacji
    if st.button("✅ Finalizuj zamówienie podłóg", type="primary"):
        dane_sprzedawcy = {
            "rodzaj_podlogi": rodzaj_podlogi,
            "seria": seria,
            "kolor": kolor,
            "folia": folia,
            "listwa_przypodlogowa": listwa_przypodlogowa,
            "uwagi": uwagi,
            # Edytowane dane techniczne przez sprzedawcę
            "system_montazu": system_montazu_edit,
            "podklad": podklad_edit,
            "mdf_mozliwy": mdf_mozliwy_edit,
            "nw": nw_edit,
            "nz": nz_edit,
            "l": l_edit,
            "zl": zl_edit,
            "zp": zp_edit,
            "listwy_jaka": listwy_jaka_edit,
            "listwy_ile": listwy_ile_edit,
            "listwy_gdzie": listwy_gdzie_edit
        }
        
        # Sprawdź wymagane pola
        wymagane_pola = ["rodzaj_podlogi", "seria"]
        brakujace_pola = [pole for pole in wymagane_pola if not dane_sprzedawcy.get(pole)]
        
        if brakujace_pola:
            st.error(f"❌ Proszę wypełnić wymagane pola: {', '.join(brakujace_pola)}")
        else:
            with st.spinner("Finalizowanie zamówienia..."):
                success = complete_form_by_seller(
                    db, "podlogi", formularz_data['id'], 
                    dane_sprzedawcy, sprzedawca_id
                )
                
                if success:
                    st.success("🎉 Zamówienie podłóg zostało sfinalizowane!")
                    st.balloons()
                    
                    # Przygotuj kompletne dane do PDF
                    complete_data = formularz_data.copy()
                    complete_data.update(dane_sprzedawcy)
                    
                    # Przycisk pobierania PDF
                    col_pdf1, col_pdf2 = st.columns(2)
                    
                    with col_pdf1:
                        st.subheader("📄 Pobierz dokumenty")
                        display_pdf_download_button(complete_data, 'podlogi', formularz_data['id'])
                    
                    # Pokaż kompletne dane
                    with st.expander("📄 Kompletne dane zamówienia"):
                        st.json(complete_data)
                        
                    st.info("ℹ️ Formularz został przeniesiony do listy aktywnych zamówień")
                else:
                    st.error("❌ Błąd podczas finalizacji zamówienia!")

def formularz_sprzedawcy_drzwi_wejsciowe():
    st.header("💼 Uzupełnienie danych drzwi wejściowych - Sprzedawca")
    
    db = setup_database()
    
    # Sposób dostępu do formularza
    sposob_dostepu = st.radio(
        "Wybierz sposób dostępu:",
        ["📋 Lista formularzy do uzupełnienia", "🔑 Kod dostępu"],
        key="sposob_dostepu"
    )
    
    selected_form = None
    
    if sposob_dostepu == "🔑 Kod dostępu":
        # Dostęp przez kod
        col1, col2 = st.columns([2, 1])
        
        with col1:
            kod_dostepu = st.text_input("Wprowadź kod dostępu:", key="kod_dostepu_input")
        
        with col2:
            if st.button("🔍 Znajdź formularz"):
                if kod_dostepu:
                    with st.spinner("Wyszukiwanie formularza..."):
                        selected_form = get_form_by_access_code(db, "drzwi_wejsciowe", kod_dostepu)
                        
                        if selected_form:
                            st.success("✅ Formularz znaleziony!")
                        else:
                            st.error("❌ Nie znaleziono formularza z tym kodem")
                else:
                    st.warning("⚠️ Proszę wprowadzić kod dostępu")
    
    else:
        # Lista formularzy do uzupełnienia
        st.subheader("📋 Formularze oczekujące na uzupełnienie")

        with st.spinner("Ładowanie formularzy..."):
            formularze = get_forms_for_completion(db, "drzwi_wejsciowe")

        # Grupowanie po wirtualnych folderach
        def _norm_name(t):
            import unicodedata, re
            if not t:
                return "nieznany_klient"
            t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii')
            t = re.sub(r'[^a-zA-Z0-9]+','_',t).strip('_').lower()
            return t or "nieznany_klient"

        def _folder_key(f):
            from datetime import datetime
            dt = f.get('data_pomiary') or f.get('data_utworzenia') or datetime.min
            day = dt.strftime('%d') if hasattr(dt, 'strftime') else '00'
            month = dt.strftime('%m') if hasattr(dt, 'strftime') else '00'
            year = dt.strftime('%Y') if hasattr(dt, 'strftime') else '0000'
            return f"{_norm_name(f.get('imie_nazwisko',''))}_{day}_{month}_{year}"
        
        if formularze:
            # Przygotuj dane do wyświetlenia
            display_data = []
            for form in formularze:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Klient": form.get('imie_nazwisko', ''),
                    "Telefon": form.get('telefon', ''),
                    "Wymiary": f"{form.get('szerokosc_otworu', '')} x {form.get('wysokosc_otworu', '')}",
                    "Monter": form.get('monter_id', '')
                })
            
            # Filtr po folderze
            folders = {}
            for f in formularze:
                key = _folder_key(f)
                folders.setdefault(key, 0)
                folders[key] += 1

            st.markdown("**Filtr folderów**")
            col_f1, col_f2 = st.columns([2,1])
            with col_f1:
                selected_folder = st.selectbox(
                    "Wybierz folder:",
                    options=[""] + sorted(folders.keys(), reverse=True),
                    format_func=lambda x: x if x else "Wszystkie foldery"
                )

            # Zastosuj filtr folderu
            filtered_forms = formularze
            if selected_folder:
                filtered_forms = [f for f in formularze if _folder_key(f) == selected_folder]

            display_data = []
            for form in filtered_forms:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Folder": _folder_key(form),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Klient": form.get('imie_nazwisko', ''),
                    "Telefon": form.get('telefon', ''),
                    "Wymiary": f"{form.get('szerokosc_otworu', '')} x {form.get('wysokosc_otworu', '')}",
                    "Monter": form.get('monter_id', '')
                })

            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Wybór formularza
            form_options_dw = [""] + [f"🏠 {form['pomieszczenie']} | 👤 {form.get('imie_nazwisko', 'Brak danych')} | 📅 {form.get('data_pomiaru', 'Brak danych')} | 🔑 {form.get('kod_dostepu', 'Brak danych')}" for form in filtered_forms]
            selected_display = st.selectbox(
                "🏠 Wybierz formularz do uzupełnienia:",
                options=form_options_dw,
                format_func=lambda x: x if x else "Wybierz formularz...",
                key="select_form_drzwi_wejsciowe"
            )
            
            if selected_display:
                # Znajdź formularz na podstawie wybranego displayu
                selected_index = form_options_dw.index(selected_display) - 1  # -1 bo pierwszy element to pusty
                selected_form = filtered_forms[selected_index]
        else:
            st.info("📭 Brak formularzy oczekujących na uzupełnienie")
    
    # Jeśli mamy wybrany formularz, pokaż formularz uzupełniania
    if selected_form:
        st.markdown("---")
        uzupelnij_formularz_drzwi_wejsciowe(db, selected_form)

def uzupelnij_formularz_drzwi_wejsciowe(db, formularz_data):
    """Formularz uzupełniania danych produktu"""
    st.subheader("🎯 Uzupełnienie danych produktu")
    
    # Pokaż wszystkie informacje z pomiarów
    with st.expander("📋 Szczegółowe informacje z pomiarów (tylko do odczytu)", expanded=True):
        # Podstawowe informacje
        st.markdown("**👤 PODSTAWOWE INFORMACJE:**")
        col_basic1, col_basic2 = st.columns(2)
        
        with col_basic1:
            st.text(f"Numer strony: {formularz_data.get('numer_strony', '')}")
            st.text(f"Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"Klient: {formularz_data.get('imie_nazwisko', '')}")
            st.text(f"Telefon: {formularz_data.get('telefon', '')}")
            st.text(f"Monter: {formularz_data.get('monter_id', '')}")
        
        with col_basic2:
            st.text(f"📅 Data: {formularz_data.get('data_pomiary', datetime.now()).strftime('%Y-%m-%d %H:%M') if formularz_data.get('data_pomiary') else 'Brak'}")
            st.text(f"🔑 Kod dostępu: {formularz_data.get('kod_dostepu', '')}")
            st.text(f"📐 Mierzona od: {formularz_data.get('mierzona_od', '')}")
            st.text(f"🔍 Skrót: {formularz_data.get('skrot', '')}")
        
        st.markdown("---")
        
        # Pola TYLKO DO ODCZYTU (niezmienne przez sprzedawcę)
        st.markdown("**🔒 DANE NIEZMIENNE (z pomiarów montera):**")
        col_readonly1, col_readonly2 = st.columns(2)
        
        with col_readonly1:
            st.text(f"🏠 Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"📏 Szerokość otworu: {formularz_data.get('szerokosc_otworu', '')} cm")
            st.text(f"📏 Wysokość otworu: {formularz_data.get('wysokosc_otworu', '')} cm")
            st.text(f"🧱 Grubość muru: {formularz_data.get('grubosc_muru', '')} cm")
        
        with col_readonly2:
            st.text(f"🏗️ Stan ściany: {formularz_data.get('stan_sciany', '')}")
            st.text(f"👤 Klient: {formularz_data.get('imie_nazwisko', '')}")
            st.text(f"📞 Telefon: {formularz_data.get('telefon', '')}")
            st.text(f"👷 Monter: {formularz_data.get('monter_id', '')}")
        
        # Strona otwierania (TYLKO DO ODCZYTU)
        strona_otw = formularz_data.get('strona_otwierania', {}) or {}
        if any(strona_otw.values()):
            st.markdown("**🚪 STRONA OTWIERANIA (niezmienne):**")
            col_dir1, col_dir2 = st.columns(2)
            
            with col_dir1:
                st.markdown("*Kierunek otwierania:*")
                if strona_otw.get('na_zewnatrz'): st.text("🔒 Na zewnątrz")
                if strona_otw.get('do_wewnatrz'): st.text("🔒 Do wewnątrz")
            
            with col_dir2:
                st.markdown("*Strona zawiasów:*")
                if strona_otw.get('lewe'): st.text("🔒 Lewe")
                if strona_otw.get('prawe'): st.text("🔒 Prawe")
        
        # Uwagi montera (TYLKO DO ODCZYTU)
        if formularz_data.get('uwagi_montera'):
            st.markdown("---")
            st.markdown("**💬 UWAGI MONTERA (niezmienne):**")
            st.text_area("", value=formularz_data.get('uwagi_montera', ''), height=80, disabled=True, key="readonly_uwagi_montera_wejsciowe")
        
        st.markdown("---")
        
        # Pola EDYTOWALNE przez sprzedawcę
        st.markdown("**✏️ DANE TECHNICZNE DO EDYCJI:**")
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            oscieznica_edit_we = st.text_input("Ościeżnica:", 
                                              value=formularz_data.get('oscieznica', ''), 
                                              key="oscieznica_edit_we")
            
            okapnik_edit_we = st.text_input("Okapnik:", 
                                           value=formularz_data.get('okapnik', ''), 
                                           key="okapnik_edit_we")
            
            prog_edit_we = st.text_input("Próg:", 
                                        value=formularz_data.get('prog', ''), 
                                        key="prog_edit_we")
        
        with col_edit2:
            wizjer_edit_we = st.checkbox("Wizjer", 
                                        value=bool(formularz_data.get('wizjer', False)),
                                        key="wizjer_edit_we")
            
            elektrozaczep_edit_we = st.text_input("Elektrozaczep:", 
                                                 value=formularz_data.get('elektrozaczep', ''), 
                                                 key="elektrozaczep_edit_we")

    
    # ID sprzedawcy
    sprzedawca_id = st.text_input("🔑 Imię Sprzedawcy:", key="sprzedawca_id")
    
    if not sprzedawca_id:
        st.warning("⚠️ Proszę podać Imię sprzedawcy")
        return
    
    # Wyświetl wszystkie zdjęcia z pomiarów w głównej sekcji
    if 'zdjecia' in formularz_data and formularz_data['zdjecia']:
        st.subheader("📸 Zdjęcia z pomiarów wykonanych przez montera")
        display_images(formularz_data['zdjecia'], max_width=400)
        st.markdown("---")
    
    # Formularz danych produktu
    st.subheader("🏷️ Dane produktu")
    col1, col2 = st.columns(2)
    
    with col1:
        producent = st.text_input("1. Producent:", key="producent_sprzedawca")
        grubosc = st.text_input("2. Grubość:", key="grubosc_sprzedawca")
        wzor = st.text_input("3. Wzór:", key="wzor_sprzedawca")
        rodzaj_okleiny = st.text_input("4. Rodzaj okleiny:", key="okleina_sprzedawca")
        ramka = st.text_input("5. Ramka:", key="ramka_sprzedawca")
        seria = st.text_input("6. Seria:", key="seria_sprzedawca")
    
    with col2:
        wkladki = st.text_input("7. Wkładki:", key="wkladki_sprzedawca")
        szyba = st.text_input("8. Szyba:", key="szyba_sprzedawca")
        klamka = st.text_input("9. Klamka:", key="klamka_sprzedawca_wejsciowe")
        dostawka = st.text_input("10. Dostawka:", key="dostawka_sprzedawca")

    
    # Opcje dodatkowe
    st.subheader("➕ Opcje dodatkowe")
    opcje_dodatkowe = st.text_area("", height=100, key="opcje_sprzedawca")
    
    # Uwagi dla klienta
    st.subheader("💬 Uwagi dla klienta")
    uwagi_klienta = st.checkbox("Uwagi dla klienta")
    if uwagi_klienta:
        uwagi_klienta = st.text_area("", height=100, key="uwagi_klienta_sprzedawca")
    
    # Przycisk finalizacji
    if st.button("✅ Finalizuj zamówienie", type="primary"):
        dane_sprzedawcy = {
            "producent": producent,
            "grubosc": grubosc,
            "wzor": wzor,
            "rodzaj_okleiny": rodzaj_okleiny,
            "ramka": ramka,
            "seria": seria,
            "wkladki": wkladki,
            "szyba": szyba,
            "klamka": klamka,
            "dostawka": dostawka,
            "opcje_dodatkowe": opcje_dodatkowe,
            "uwagi_klienta": uwagi_klienta,
            # Edytowane dane techniczne przez sprzedawcę
            "oscieznica": oscieznica_edit_we,
            "okapnik": okapnik_edit_we,
            "prog": prog_edit_we,
            "wizjer": wizjer_edit_we,
            "elektrozaczep": elektrozaczep_edit_we
        }
        
        # Sprawdź wymagane pola
        wymagane_pola = ["producent", "seria"]
        brakujace_pola = [pole for pole in wymagane_pola if not dane_sprzedawcy.get(pole)]
        
        if brakujace_pola:
            st.error(f"❌ Proszę wypełnić wymagane pola: {', '.join(brakujace_pola)}")
        else:
            with st.spinner("Finalizowanie zamówienia..."):
                success = complete_form_by_seller(
                    db, "drzwi_wejsciowe", formularz_data['id'], 
                    dane_sprzedawcy, sprzedawca_id
                )
                
                if success:
                    st.success("🎉 Zamówienie zostało sfinalizowane!")
                    st.balloons()
                    
                    # Przygotuj kompletne dane do PDF
                    complete_data = formularz_data.copy()
                    complete_data.update(dane_sprzedawcy)
                    
                    # Przycisk pobierania PDF
                    col_pdf1, col_pdf2 = st.columns(2)
                    
                    with col_pdf1:
                        st.subheader("📄 Pobierz dokumenty")
                        display_pdf_download_button(complete_data, 'drzwi_wejsciowe', formularz_data['id'])
                    
                    # Pokaż kompletne dane
                    with st.expander("📄 Kompletne dane zamówienia"):
                        st.json(complete_data)
                        
                    st.info("ℹ️ Formularz został przeniesiony do listy aktywnych zamówień")
                else:
                    st.error("❌ Błąd podczas finalizacji zamówienia!")


def main():
    st.set_page_config(page_title=" Protokół Pomiaru", layout="wide")
    st.title("🔄 Protokół Pomiaru")
    
    # Wybór trybu
    tryb = st.sidebar.radio(
        "Wybierz tryb pracy:",
        ["🔧 Pomiary (Monter)", "💼 Sprzedaż (Sprzedawca)"]
    )
    
    if tryb == "🔧 Pomiary (Monter)":
        st.sidebar.markdown("### 👷‍♂️ Tryb: Monter")
        st.sidebar.markdown("Wypełnij pomiary i dane techniczne")
        
        # Wybór typu pomiarów
        typ_pomiarow = st.selectbox(
            "🎯 Co mierzysz?",
            ["🚪 Drzwi", "🚨 Drzwi wejściowe", "🏠 Podłogi"],
            key="typ_pomiarow"
        )
        
        if typ_pomiarow == "🚪 Drzwi":
            formularz_montera_drzwi()
        elif typ_pomiarow == "🚨 Drzwi wejściowe":
            formularz_montera_drzwi_wejsciowe()
        else:
            formularz_montera_podlogi()
    
    else:
        st.sidebar.markdown("### 👔 Tryb: Sprzedawca")
        st.sidebar.markdown("Uzupełnij dane produktu i sfinalizuj zamówienie")
        
        # Wybór typu produktu dla sprzedawcy
        typ_produktu = st.selectbox(
            "🎯 Jaki produkt uzupełniasz?",
            ["🚪 Drzwi", "🚨 Drzwi wejściowe", "🏠 Podłogi"],
            key="typ_produktu"
        )
        
        if typ_produktu == "🚪 Drzwi":
            formularz_sprzedawcy_drzwi()
        elif typ_produktu == "🚨 Drzwi wejściowe":
            formularz_sprzedawcy_drzwi_wejsciowe()
        else:
            formularz_sprzedawcy_podlogi()


if __name__ == "__main__":
    main()