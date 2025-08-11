import streamlit as st
import pandas as pd
import qrcode
import io
import base64
from datetime import datetime
from firebase_config import (
    setup_database, save_pomiary_data, generate_share_link,
    get_forms_for_completion, complete_form_by_seller, get_form_by_access_code
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
        nazwisko = st.text_input("Nazwisko klienta:", key="nazwisko_monter")
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
            ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Inne"],
            key="typ_drzwi_monter"
        )
    
    with col4:
        oscieznica = st.text_input("Ościeżnica:", key="oscieznica_monter")
        st.caption("(zakres)")
        
        opaska = st.radio("Opaska:", ["6 cm", "8 cm"], key="opaska_monter")
        
        kat_zaciecia = st.text_input("Kąt zacięcia:", key="kat_zaciecia_monter")
        st.caption("(45°, 90°, inne...)")
        
        prog = st.text_input("Próg:", key="prog_monter")
        wizjer = st.text_input("Wizjer:", key="wizjer_monter")
    
    # Strona otwierania
    st.subheader("🚪 Strona otwierania")
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown("**LEWE (przylgowe/bezprzylgowe)**")
        lewe_przyl = st.checkbox("LEWE przylg.", key="lewe_przyl_monter")
    
    with col6:
        st.markdown("**PRAWE (przylgowe/bezprzylgowe)**")
        prawe_przyl = st.checkbox("PRAWE przylg.", key="prawe_przyl_monter")
    
    with col7:
        st.markdown("**LEWE (odwrotna przylga)**")
        lewe_odwr = st.checkbox("LEWE odwr.", key="lewe_odwr_monter")
    
    with col8:
        st.markdown("**PRAWE (odwrotna przylga)**")
        prawe_odwr = st.checkbox("PRAWE odwr.", key="prawe_odwr_monter")
    
    # Dodatkowe opisy przy ilustracji oraz szerokość
    col_top, col_mid, col_bottom = st.columns([2, 1, 2])
    with col_top:
        napis_nad_drzwiami = st.text_input("Pomieszczenie przed:", key="napis_nad_drzwiami")
    with col_mid:
        szerokosc_skrzydla = st.text_input("Szerokość (cm):", key="szerokosc_skrzydla")
    with col_bottom:
        napis_pod_drzwiami = st.text_input("Pomieszczenie za:", key="napis_pod_drzwiami")
    
    # Szkic i uwagi
    st.subheader("📝 Szkic i uwagi")
    norma = st.text_input("Norma/Szkic:", key="norma_monter")
    uwagi_montera = st.text_area("Uwagi montera:", height=100, key="uwagi_montera")
    
    # Przycisk zapisania
    if st.button("💾 Zapisz pomiary", type="primary"):
        dane_pomiary = {
            "pomieszczenie": pomieszczenie,
            "nazwisko": nazwisko,
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
            "napis_pod_drzwiami": napis_pod_drzwiami,
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
        
        if formularze:
            # Przygotuj dane do wyświetlenia
            display_data = []
            for form in formularze:
                data_str = form.get('data_pomiary', datetime.now()).strftime("%Y-%m-%d %H:%M") if form.get('data_pomiary') else "Brak daty"
                
                display_data.append({
                    "Kod dostępu": form.get('kod_dostepu', ''),
                    "Data pomiarów": data_str,
                    "Pomieszczenie": form.get('pomieszczenie', ''),
                    "Klient": form.get('nazwisko', ''),
                    "Telefon": form.get('telefon', ''),
                    "Wymiary": f"{form.get('szerokosc_otworu', '')} x {form.get('wysokosc_otworu', '')}",
                    "Monter": form.get('monter_id', '')
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Wybór formularza
            selected_code = st.selectbox(
                "Wybierz formularz do uzupełnienia:",
                options=[""] + [form['kod_dostepu'] for form in formularze],
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
            st.text(f"Klient: {formularz_data.get('nazwisko', '')}")
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
        kolor_osc = st.text_input("Kolor ość. (jeśli inna):", key="kolor_osc_sprzedawca")
    
    # Opcje dodatkowe
    st.subheader("➕ Opcje dodatkowe")
    opcje_dodatkowe = st.text_area("", height=100, key="opcje_sprzedawca")
    
    # Uwagi dla klienta
    st.subheader("💬 Uwagi dla klienta")
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

def formularz_sprzedawcy_podlogi():
    """Formularz uzupełniania danych produktu podłóg przez sprzedawcę"""
    st.header("💼 Uzupełnienie danych produktu - Sprzedawca (Podłogi)")
    
    db = setup_database()
    
    # Sposób dostępu do formularza
    sposob_dostepu = st.radio(
        "Wybierz sposób dostępu:",
        ["🔑 Kod dostępu", "📋 Lista formularzy do uzupełnienia"],
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
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Wybór formularza
            selected_code = st.selectbox(
                "Wybierz formularz do uzupełnienia:",
                options=[""] + [form['kod_dostepu'] for form in formularze],
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
            ["🚪 Drzwi", "🏠 Podłogi"],
            key="typ_pomiarow"
        )
        
        if typ_pomiarow == "🚪 Drzwi":
            formularz_montera_drzwi()
        else:
            formularz_montera_podlogi()
    
    else:
        st.sidebar.markdown("### 👔 Tryb: Sprzedawca")
        st.sidebar.markdown("Uzupełnij dane produktu i sfinalizuj zamówienie")
        
        # Wybór typu produktu dla sprzedawcy
        typ_produktu = st.selectbox(
            "🎯 Jaki produkt uzupełniasz?",
            ["🚪 Drzwi", "🏠 Podłogi"],
            key="typ_produktu"
        )
        
        if typ_produktu == "🚪 Drzwi":
            formularz_sprzedawcy_drzwi()
        else:
            formularz_sprzedawcy_podlogi()

if __name__ == "__main__":
    main()