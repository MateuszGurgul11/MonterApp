import streamlit as st
import pandas as pd
import qrcode
import io
import base64
from datetime import datetime
from firebase_config import (
    setup_database, save_pomiary_data, generate_share_link,
    get_forms_for_completion, complete_form_by_seller, get_form_by_access_code,
    save_draft_data, create_image_uploader, process_uploaded_images, 
    save_images_to_database, display_images
)
from pdf_generator import display_pdf_download_button

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
                st.image("typ_drzwi/inne.png", width=120, caption=typ_drzwi)
            except:
                st.write("🖼️ Obrazek niedostępny")
        elif typ_drzwi == "Odwrotna Przylga":
            try:
                st.image("typ_drzwi/odwrotna_przylga.png", width=120, caption="Odwrotna przylga")
            except:
                st.write("🖼️ Obrazek niedostępny")
        elif typ_drzwi == "Renova":
            try:
                st.image("typ_drzwi/renova.png", width=120, caption="Renova")
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
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown("**LEWE (przylgowe/bezprzylgowe)**")
        lewe_przyl = st.checkbox("LEWE przylg.", key="lewe_przyl_monter")
        try:
            st.image("drzwi/lewe_przyl.png", width=150, caption="Lewe przylgowe")
        except:
            st.write("🖼️ Obrazek niedostępny")
    
    with col6:
        st.markdown("**PRAWE (przylgowe/bezprzylgowe)**")
        prawe_przyl = st.checkbox("PRAWE przylg.", key="prawe_przyl_monter")
        try:
            st.image("drzwi/prawe_przyl.png", width=150, caption="Prawe przylgowe")
        except:
            st.write("🖼️ Obrazek niedostępny")
    
    with col7:
        st.markdown("**LEWE** **(odwrotna przylga)**")
        lewe_odwr = st.checkbox("LEWE odwr.", key="lewe_odwr_monter")
        try:
            st.image("drzwi/lewe_odwr.png", width=150, caption="Lewe odwrotne")
        except:
            st.write("🖼️ Obrazek niedostępny")
    
    with col8:
        st.markdown("**PRAWE (odwrotna przylga)**")
        prawe_odwr = st.checkbox("PRAWE odwr.", key="prawe_odwr_monter")
        try:
            st.image("drzwi/prawe_odwr.png", width=150, caption="Prawe odwrotne")
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
    
    # Sekcja zdjęć
    st.markdown("---")
    uploaded_files = create_image_uploader("drzwi_monter")
    
    col_save1, col_save2 = st.columns(2)

    with col_save1:
        save_clicked = st.button("💾 Zapisz pomiary", type="primary")
    with col_save2:
        save_draft_clicked = st.button("🗂️ Zapisz do kwarantanny (szkic)")

    # ZAPIS DO BAZY (finalizacja etapu montera)
    if save_clicked:
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
                "lewe_przyl": lewe_przyl,
                "prawe_przyl": prawe_przyl,
                "lewe_odwr": lewe_odwr,
                "prawe_odwr": prawe_odwr
            },
            # Opisy dla zdjęcia i szerokość skrzydła
            "napis_nad_drzwiami": napis_nad_drzwiami,
            "szerokosc_skrzydla": szerokosc_skrzydla,
            "uwagi_montera": uwagi_montera,
            # Pola sprzedawcy - puste na razie
            "producent": "",
            "seria": "",
            "typ": "",
            "rodzaj_okleiny": "",
            "ilosc_szyb": "",
            "zamek": "",
            "szyba": "",
            "wentylacja": "",
            "klamka": "",
            "kolor_wizjera": "",
            "opcje_dodatkowe": "",
            "uwagi_klienta": ""
        }
        
        # Sprawdź wymagane pola
        wymagane_pola = ["pomieszczenie", "telefon", "szerokosc_otworu", "wysokosc_otworu"]
        brakujace_pola = [pole for pole in wymagane_pola if not dane_pomiary.get(pole)]
        
        if brakujace_pola:
            st.error(f"❌ Proszę wypełnić wymagane pola: {', '.join(brakujace_pola)}")
        else:
            with st.spinner("Zapisywanie pomiarów..."):
                doc_id, kod_dostepu = save_pomiary_data(db, "drzwi", dane_pomiary, monter_id)
                
                if doc_id and kod_dostepu:
                    # Przetwórz i zapisz zdjęcia jeśli zostały przesłane
                    if uploaded_files:
                        with st.spinner("Zapisywanie zdjęć..."):
                            images_data = process_uploaded_images(uploaded_files, "drzwi", doc_id)
                            if images_data:
                                save_images_to_database(db, "drzwi", doc_id, images_data)
                                st.success(f"✅ Zapisano {len(images_data)} zdjęć")
                    
                    st.success(f"✅ Pomiary zostały zapisane! ID: {doc_id}")
                    
                    # Wyświetl kod dostępu i link
                    st.info(f"🔑 **Kod dostępu dla sprzedawcy:** {kod_dostepu}")
                    
                    # Generuj QR kod
                    link = generate_share_link(doc_id, kod_dostepu, "drzwi")
                    
                    col_qr1, col_qr2 = st.columns(2)
                    
                    with col_qr1:
                        st.subheader("📲 QR Code")
                        qr_code_data = f"KOD:{kod_dostepu}|ID:{doc_id}|TYP:drzwi"
                        
                        qr = qrcode.QRCode(version=1, box_size=10, border=5)
                        qr.add_data(qr_code_data)
                        qr.make(fit=True)
                        
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        
                        # Konwertuj do base64 dla wyświetlenia
                        buffer = io.BytesIO()
                        qr_img.save(buffer, format='PNG')
                        buffer.seek(0)
                        qr_b64 = base64.b64encode(buffer.getvalue()).decode()
                        
                        st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="200">', unsafe_allow_html=True)
                        st.caption("Kod do zeskanowania przez sprzedawcę")
                    
                    with col_qr2:
                        st.subheader("📋 Instrukcje")
                        st.markdown("""
                        **Przekaż sprzedawcy:**
                        1. 🔑 Kod dostępu: `{}`
                        2. 📱 Lub QR kod do zeskanowania
                        3. 📝 Sprzedawca uzupełni dane produktu
                        
                        **Status:** ✅ Pomiary wykonane
                        """.format(kod_dostepu))
                    
                    # Pokaż zapisane dane
                    with st.expander("Pokaż zapisane pomiary"):
                        st.json(dane_pomiary)
                else:
                    st.error("❌ Błąd podczas zapisywania pomiarów!")

    # ZAPIS DO KWARANTANNY (szkic)
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
                "lewe_przyl": lewe_przyl,
                "prawe_przyl": prawe_przyl,
                "lewe_odwr": lewe_odwr,
                "prawe_odwr": prawe_odwr
            },
            "napis_nad_drzwiami": napis_nad_drzwiami,
            "szerokosc_skrzydla": szerokosc_skrzydla,
            "uwagi_montera": uwagi_montera,
        }

        # Pozwalamy zapisać szkic nawet z brakami
        with st.spinner("Zapisywanie szkicu..."):
            draft_id = save_draft_data(db, "drzwi", dane_pomiary, monter_id)
            if draft_id:
                st.success(f"🗂️ Szkic zapisany (ID: {draft_id}). Możesz wrócić i dokończyć później na stronie 'Wymiary'.")
            else:
                st.error("❌ Nie udało się zapisać szkicu")

def formularz_sprzedawcy_drzwi():
    """Formularz uzupełniania danych produktu przez sprzedawcę"""
    st.header("💼 Uzupełnienie danych produktu - Sprzedawca")
    
    db = setup_database()
    
    # Sposób dostępu do formularza
    sposob_dostepu = st.radio(
        "Wybierz sposób dostępu:",
        ["🔑 Kod dostępu", "📋 Lista formularzy do uzupełnienia"],
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

        def _last3(phone):
            import re
            if not phone:
                return "000"
            d = re.sub(r'\D','', str(phone))
            return (d[-3:] if len(d)>=3 else d.zfill(3))

        def _folder_key(f):
            from datetime import datetime
            dt = f.get('data_pomiary') or f.get('data_utworzenia') or datetime.min
            day = dt.strftime('%d') if hasattr(dt, 'strftime') else '00'
            month = dt.strftime('%m') if hasattr(dt, 'strftime') else '00'
            year = dt.strftime('%Y') if hasattr(dt, 'strftime') else '0000'
            return f"{_norm_name(f.get('imie_nazwisko',''))}_{_last3(f.get('telefon',''))}_{day}_{month}_{year}"
        
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
            selected_code = st.selectbox(
                "Wybierz formularz do uzupełnienia:",
                options=[""] + [form['kod_dostepu'] for form in filtered_forms],
                format_func=lambda x: f"Kod: {x}" if x else "Wybierz formularz..."
            )
            
            if selected_code:
                selected_form = next((form for form in formularze if form['kod_dostepu'] == selected_code), None)
        else:
            st.info("📭 Brak formularzy oczekujących na uzupełnienie")
    
    # Jeśli mamy wybrany formularz, pokaż formularz uzupełniania
    if selected_form:
        st.markdown("---")
        uzupelnij_formularz_drzwi(db, selected_form)

def uzupelnij_formularz_drzwi(db, formularz_data):
    """Formularz uzupełniania danych produktu"""
    st.subheader("🎯 Uzupełnienie danych produktu")
    
    # Pokaż podstawowe informacje z pomiarów
    with st.expander("📋 Informacje z pomiarów (tylko do odczytu)"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.text(f"Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"Klient: {formularz_data.get('imie_nazwisko', '')}")
            st.text(f"Telefon: {formularz_data.get('telefon', '')}")
        
        with col_info2:
            st.text(f"Wymiary: {formularz_data.get('szerokosc_otworu', '')} x {formularz_data.get('wysokosc_otworu', '')}")
            st.text(f"Typ: {formularz_data.get('typ_drzwi', '')}")
            st.text(f"Data pomiarów: {formularz_data.get('data_pomiary', datetime.now()).strftime('%Y-%m-%d %H:%M') if formularz_data.get('data_pomiary') else 'Brak'}")
        

    
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
    col1, col2 = st.columns(2)
    
    with col1:
        producent = st.text_input("1. Producent:", key="producent_sprzedawca")
        seria = st.text_input("2. Seria:", key="seria_sprzedawca")
        typ_produktu = st.text_input("3. Typ:", key="typ_sprzedawca")
        rodzaj_okleiny = st.text_input("4. Rodzaj okleiny:", key="okleina_sprzedawca")
        ilosc_szyb = st.text_input("5. Ilość szyb:", key="szyby_sprzedawca")
    
    with col2:
        zamek = st.text_input("6. Zamek:", key="zamek_sprzedawca")
        szyba = st.text_input("7. Szyba:", key="szyba_sprzedawca")
        wentylacja = st.text_input("8. Wentylacja:", key="wentylacja_sprzedawca")
        klamka = st.text_input("9. Klamka:", key="klamka_sprzedawca")
        kolor_wizjera = st.text_input("10. Kolor wizjera:", key="kolor_wizjera_sprzedawca")
        kolor_osc = st.checkbox("Inny kolor ościeżnicy")
        if kolor_osc:
            kolor_osc = st.text_input("Kolor ość. (jeśli inna):", key="kolor_osc_sprzedawca")
    
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
            "opcje_dodatkowe": opcje_dodatkowe,
            "uwagi_klienta": uwagi_klienta
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
                    
                    with col_pdf2:
                        st.subheader("📋 Akcje")
                        if st.button("📊 Przejdź do przeglądu danych", key="goto_overview_drzwi"):
                            st.info("💡 Przejdź do strony 'Drzwi' → zakładka 'Przegląd danych'")
                    
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
    
    # Sekcja zdjęć
    st.markdown("---")
    uploaded_files_podlogi = create_image_uploader("podlogi_monter")
    
    # Przycisk zapisania
    if st.button("💾 Zapisz pomiary podłóg", type="primary"):
        dane_pomiary = {
            "pomieszczenie": pomieszczenie,
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
        wymagane_pola = ["pomieszczenie", "telefon"]
        brakujace_pola = [pole for pole in wymagane_pola if not dane_pomiary.get(pole)]
        
        if brakujace_pola:
            st.error(f"❌ Proszę wypełnić wymagane pola: {', '.join(brakujace_pola)}")
        else:
            with st.spinner("Zapisywanie pomiarów..."):
                doc_id, kod_dostepu = save_pomiary_data(db, "podlogi", dane_pomiary, monter_id)
                
                if doc_id and kod_dostepu:
                    # Przetwórz i zapisz zdjęcia jeśli zostały przesłane
                    if uploaded_files_podlogi:
                        with st.spinner("Zapisywanie zdjęć..."):
                            images_data = process_uploaded_images(uploaded_files_podlogi, "podlogi", doc_id)
                            if images_data:
                                save_images_to_database(db, "podlogi", doc_id, images_data)
                                st.success(f"✅ Zapisano {len(images_data)} zdjęć")
                    
                    st.success(f"✅ Pomiary zostały zapisane! ID: {doc_id}")
                    
                    # Wyświetl kod dostępu i link
                    st.info(f"🔑 **Kod dostępu dla sprzedawcy:** {kod_dostepu}")
                    
                    # Generuj QR kod
                    link = generate_share_link(doc_id, kod_dostepu, "podlogi")
                    
                    col_qr1, col_qr2 = st.columns(2)
                    
                    with col_qr1:
                        st.subheader("📲 QR Code")
                        qr_code_data = f"KOD:{kod_dostepu}|ID:{doc_id}|TYP:podlogi"
                        
                        qr = qrcode.QRCode(version=1, box_size=10, border=5)
                        qr.add_data(qr_code_data)
                        qr.make(fit=True)
                        
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        
                        # Konwertuj do base64 dla wyświetlenia
                        buffer = io.BytesIO()
                        qr_img.save(buffer, format='PNG')
                        buffer.seek(0)
                        qr_b64 = base64.b64encode(buffer.getvalue()).decode()
                        
                        st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="200">', unsafe_allow_html=True)
                        st.caption("Kod do zeskanowania przez sprzedawcę")
                    
                    with col_qr2:
                        st.subheader("📋 Instrukcje")
                        st.markdown("""
                        **Przekaż sprzedawcy:**
                        1. 🔑 Kod dostępu: `{}`
                        2. 📱 Lub QR kod do zeskanowania
                        3. 📝 Sprzedawca uzupełni dane produktu
                        
                        **Status:** ✅ Pomiary wykonane
                        """.format(kod_dostepu))
                    
                    # Pokaż zapisane dane
                    with st.expander("Pokaż zapisane pomiary"):
                        st.json(dane_pomiary)
                else:
                    st.error("❌ Błąd podczas zapisywania pomiarów!")


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
    
    # Sekcja zdjęć
    st.markdown("---")
    uploaded_files_we = create_image_uploader("drzwi_wejsciowe_monter")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        zapisz_button = st.button("💾 Zapisz pomiary", type="primary")
    
    with col_btn2:
        szkic_button = st.button("🗂️ Zapisz do przechowalni")
    
    if zapisz_button:
        # Przygotuj dane do zapisu
        dane_formularza = {
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
                "uwagi_montera": uwagi_montera
        }
        with st.spinner("Zapisywanie pomiarów..."):
            doc_id, kod_dostepu = save_pomiary_data(db, "drzwi_wejsciowe", dane_formularza, monter_id)
            
            if doc_id:
                # Przetwórz i zapisz zdjęcia jeśli zostały przesłane
                if uploaded_files_we:
                    with st.spinner("Zapisywanie zdjęć..."):
                        images_data = process_uploaded_images(uploaded_files_we, "drzwi_wejsciowe", doc_id)
                        if images_data:
                            save_images_to_database(db, "drzwi_wejsciowe", doc_id, images_data)
                            st.success(f"✅ Zapisano {len(images_data)} zdjęć")
                
                st.success("✅ Pomiary zostały zapisane pomyślnie!")
                st.info(f"🔑 **Kod dostępu dla sprzedawcy:** `{kod_dostepu}`")
                st.info("📋 Sprzedawca może teraz uzupełnić dane produktu używając tego kodu")
                
                # Pokaż zapisane dane
                with st.expander("📄 Zapisane dane"):
                    st.json(dane_formularza)
            else:
                st.error("❌ Błąd podczas zapisywania pomiarów!")
    
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
                st.info("💡 Możesz kontynuować edycję w zakładce 'Wymiary'")
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
                def _last3_local(phone):
                    if not phone:
                        return "000"
                    d = re.sub(r'\D','', str(phone))
                    return (d[-3:] if len(d)>=3 else d.zfill(3))
                dt = f.get('data_pomiary') or f.get('data_utworzenia') or datetime.min
                day = dt.strftime('%d') if hasattr(dt, 'strftime') else '00'
                month = dt.strftime('%m') if hasattr(dt, 'strftime') else '00'
                year = dt.strftime('%Y') if hasattr(dt, 'strftime') else '0000'
                return f"{_norm_name_local(f.get('imie_nazwisko',''))}_{_last3_local(f.get('telefon',''))}_{day}_{month}_{year}"

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
            selected_code = st.selectbox(
                "Wybierz formularz do uzupełnienia:",
                options=[""] + [form['kod_dostepu'] for form in filtered_forms_p],
                format_func=lambda x: f"Kod: {x}" if x else "Wybierz formularz...",
                key="select_form_podlogi"
            )
            
            if selected_code:
                selected_form = next((form for form in formularze if form['kod_dostepu'] == selected_code), None)
        else:
            st.info("📭 Brak formularzy oczekujących na uzupełnienie")
    
    # Jeśli mamy wybrany formularz, pokaż formularz uzupełniania
    if selected_form:
        st.markdown("---")
        uzupelnij_formularz_podlogi(db, selected_form)

def uzupelnij_formularz_podlogi(db, formularz_data):
    """Formularz uzupełniania danych produktu podłóg"""
    st.subheader("🎯 Uzupełnienie danych produktu - Podłogi")
    
    # Pokaż podstawowe informacje z pomiarów
    with st.expander("📋 Informacje z pomiarów (tylko do odczytu)"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.text(f"Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"Telefon: {formularz_data.get('telefon', '')}")
            st.text(f"System montażu: {formularz_data.get('system_montazu', '')}")
            st.text(f"Podkład: {formularz_data.get('podklad', '')}")
        
        with col_info2:
            suma_listw = (formularz_data.get('nw', 0) + formularz_data.get('nz', 0) + 
                         formularz_data.get('l', 0) + formularz_data.get('zl', 0) + formularz_data.get('zp', 0))
            st.text(f"Suma listw: {suma_listw}")
            st.text(f"MDF możliwy: {formularz_data.get('mdf_mozliwy', '')}")
            st.text(f"Data pomiarów: {formularz_data.get('data_pomiary', datetime.now()).strftime('%Y-%m-%d %H:%M') if formularz_data.get('data_pomiary') else 'Brak'}")
        

    
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
            "uwagi": uwagi
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
                    
                    with col_pdf2:
                        st.subheader("📋 Akcje")
                        if st.button("📊 Przejdź do przeglądu danych", key="goto_overview_podlogi"):
                            st.info("💡 Przejdź do strony 'Podłogi' → zakładka 'Przegląd danych'")
                    
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
        ["🔑 Kod dostępu", "📋 Lista formularzy do uzupełnienia"],
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

        def _last3(phone):
            import re
            if not phone:
                return "000"
            d = re.sub(r'\D','', str(phone))
            return (d[-3:] if len(d)>=3 else d.zfill(3))

        def _folder_key(f):
            from datetime import datetime
            dt = f.get('data_pomiary') or f.get('data_utworzenia') or datetime.min
            day = dt.strftime('%d') if hasattr(dt, 'strftime') else '00'
            month = dt.strftime('%m') if hasattr(dt, 'strftime') else '00'
            year = dt.strftime('%Y') if hasattr(dt, 'strftime') else '0000'
            return f"{_norm_name(f.get('imie_nazwisko',''))}_{_last3(f.get('telefon',''))}_{day}_{month}_{year}"
        
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
            selected_code = st.selectbox(
                "Wybierz formularz do uzupełnienia:",
                options=[""] + [form['kod_dostepu'] for form in filtered_forms],
                format_func=lambda x: f"Kod: {x}" if x else "Wybierz formularz..."
            )
            
            if selected_code:
                selected_form = next((form for form in formularze if form['kod_dostepu'] == selected_code), None)
        else:
            st.info("📭 Brak formularzy oczekujących na uzupełnienie")
    
    # Jeśli mamy wybrany formularz, pokaż formularz uzupełniania
    if selected_form:
        st.markdown("---")
        uzupelnij_formularz_drzwi_wejsciowe(db, selected_form)

def uzupelnij_formularz_drzwi_wejsciowe(db, formularz_data):
    """Formularz uzupełniania danych produktu"""
    st.subheader("🎯 Uzupełnienie danych produktu")
    
    # Pokaż podstawowe informacje z pomiarów
    with st.expander("📋 Informacje z pomiarów (tylko do odczytu)"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.text(f"Pomieszczenie: {formularz_data.get('pomieszczenie', '')}")
            st.text(f"Klient: {formularz_data.get('imie_nazwisko', '')}")
            st.text(f"Telefon: {formularz_data.get('telefon', '')}")
        
        with col_info2:
            st.text(f"Wymiary: {formularz_data.get('szerokosc_otworu', '')} x {formularz_data.get('wysokosc_otworu', '')}")
            st.text(f"Typ: {formularz_data.get('typ_drzwi', '')}")
            st.text(f"Data pomiarów: {formularz_data.get('data_pomiary', datetime.now()).strftime('%Y-%m-%d %H:%M') if formularz_data.get('data_pomiary') else 'Brak'}")
        

    
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
            "uwagi_klienta": uwagi_klienta
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
                    
                    with col_pdf2:
                        st.subheader("📋 Akcje")
                        if st.button("📊 Przejdź do przeglądu danych", key="goto_overview_drzwi_wejsciowe"):
                            st.info("💡 Przejdź do strony 'Drzwi wejściowe' → zakładka 'Przegląd danych'")
                    
                    # Pokaż kompletne dane
                    with st.expander("📄 Kompletne dane zamówienia"):
                        st.json(complete_data)
                        
                    st.info("ℹ️ Formularz został przeniesiony do listy aktywnych zamówień")
                else:
                    st.error("❌ Błąd podczas finalizacji zamówienia!")


def main():
    st.set_page_config(page_title="Workflow Monter-Sprzedawca", layout="wide")
    st.title("🔄 WORKFLOW MONTER-SPRZEDAWCA")
    
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