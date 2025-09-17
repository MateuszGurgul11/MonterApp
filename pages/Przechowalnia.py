import streamlit as st
import pandas as pd
from datetime import datetime

from firebase_config import (
    setup_database,
    get_drafts_for_monter,
    update_draft_data,
    delete_draft,
    finalize_draft,
    display_images_with_edit,
    add_images_to_draft,
    update_draft_images,
    create_image_uploader,
    process_uploaded_images,
)

# ZABEZPIECZENIE - sprawdź logowanie przed załadowaniem strony
if not st.session_state.get('logged_in', False):
    st.error("🚫 **Dostęp zabroniony** - Wymagane logowanie!")
    st.markdown("### 👆 [Przejdź do logowania](?)")
    if st.button("🔙 Powrót do logowania", type="primary"):
        st.switch_page("main.py")
    st.stop()


def finalize_all_drafts(db, drafts):
    if not drafts:
        st.warning("⚠️ Brak protokołów do finalizacji")
        return
    
    success_count = 0
    error_count = 0
    results = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_drafts = len(drafts)
    
    for i, draft in enumerate(drafts):
        draft_id = draft.get('id')
        if not draft_id:
            error_count += 1
            continue
            
        # Aktualizuj progress
        progress = (i + 1) / total_drafts
        progress_bar.progress(progress)
        status_text.text(f"Przetwarzanie protokołu {i+1}/{total_drafts}...")
        
        try:
            # Finalizuj szkic
            doc_id, kod = finalize_draft(db, draft_id)
            if doc_id:
                success_count += 1
                results.append({
                    'draft_id': draft_id,
                    'doc_id': doc_id,
                    'kod': kod,
                    'status': 'success',
                    'typ': draft.get('collection_target', ''),
                    'klient': draft.get('imie_nazwisko', ''),
                    'pomieszczenie': draft.get('pomieszczenie', '')
                })
            else:
                error_count += 1
                results.append({
                    'draft_id': draft_id,
                    'status': 'error',
                    'typ': draft.get('collection_target', ''),
                    'klient': draft.get('imie_nazwisko', ''),
                    'pomieszczenie': draft.get('pomieszczenie', '')
                })
        except Exception as e:
            error_count += 1
            results.append({
                'draft_id': draft_id,
                'status': 'error',
                'error': str(e),
                'typ': draft.get('collection_target', ''),
                'klient': draft.get('imie_nazwisko', ''),
                'pomieszczenie': draft.get('pomieszczenie', '')
            })
    
    # Ukryj progress bar
    progress_bar.empty()
    status_text.empty()
    
    # Pokaż wyniki
    if success_count > 0:
        st.success(f"🎉 **Sukces!** Sfinalizowano {success_count} protokół(y)")
        if success_count == total_drafts:
            st.balloons()
    
    if error_count > 0:
        st.error(f"❌ **Błędy:** {error_count} protokół(y) nie zostało sfinalizowanych")
    
    # Szczegółowe wyniki
    with st.expander(f"📋 Szczegóły operacji ({len(results)} protokółów)", expanded=error_count > 0):
        for result in results:
            if result['status'] == 'success':
                st.success(f"✅ **{result['typ']}** - {result['klient']} ({result['pomieszczenie']}) "
                          f"→ ID: {result['doc_id']} | Kod: {result['kod']}")
            else:
                error_msg = result.get('error', 'Nieznany błąd')
                st.error(f"❌ **{result['typ']}** - {result['klient']} ({result['pomieszczenie']}) "
                        f"→ Błąd: {error_msg}")
    
    # Odśwież stronę po operacji
    if success_count > 0:
        st.info("🔄 Odświeżanie strony...")
        st.rerun()


def page_wymiary():
    st.set_page_config(page_title="Wymiary (kwarantanna)", layout="wide")
    st.title("🗂️ Wymiary")

    db = setup_database()

    st.markdown("""
    Na tej stronie znajdują się protokoły pomiarów zapisane przez montera, które nie zostały jeszcze
    ostatecznie zapisane do bazy danych. Możesz je edytować, usunąć lub sfinalizować.
    """)

    # Filtry
    colf1, colf2, colf3 = st.columns([2, 2, 1])
    with colf1:
        monter_id = st.text_input("🔑 Filtruj po imieniu montera (opcjonalnie):", value="")
    
    # Pobierz wszystkie protokoły aby wyciągnąć unikalne pomieszczenia
    all_drafts = get_drafts_for_monter(db, monter_id if monter_id else None)
    
    with colf2:
        # Utwórz listę unikalnych pomieszczeń z liczbą protokołów
        room_counts = {}
        for d in all_drafts:
            room = d.get('pomieszczenie', '')
            if room:
                room_counts[room] = room_counts.get(room, 0) + 1
        
        unique_rooms = [""] + sorted(room_counts.keys())
        selected_room = st.selectbox(
            "🏠 Filtruj po pomieszczeniu:", 
            options=unique_rooms,
            format_func=lambda x: f"{x} ({room_counts.get(x, 0)} protokołów)" if x else f"Wszystkie pomieszczenia ({len(all_drafts)} protokołów)"
        )
    
    with colf3:
        if st.button("🔄 Odśwież"):
            st.rerun()
    
    # Filtruj protokoły według wybranych kryteriów
    drafts = all_drafts
    if selected_room:
        drafts = [d for d in drafts if d.get('pomieszczenie', '') == selected_room]

    if not drafts:
        st.info("📭 Brak protokołów dla wybranych filtrów")
        return
    
    # Sekcja masowej finalizacji
    st.markdown("---")
    st.markdown("### 🚀 Akcje masowe")
    
    col_mass1, col_mass2, col_mass3 = st.columns([2, 2, 2])
    
    with col_mass1:
        st.metric("📊 Protokoły do finalizacji", len(drafts))
    
    with col_mass2:
        if st.button("📚 FINALIZUJ WSZYSTKIE PROTOKOŁY", type="primary", help="Finalizuje wszystkie widoczne protokoły"):
            st.session_state.show_mass_confirm = True
    
    with col_mass3:
        if len(drafts) > 0:
            # Policz typy protokołów
            drzwi_count = len([d for d in drafts if d.get('collection_target') == 'drzwi'])
            wejsciowe_count = len([d for d in drafts if d.get('collection_target') == 'drzwi_wejsciowe'])
            podlogi_count = len([d for d in drafts if d.get('collection_target') == 'podlogi'])
            st.info(f"📝 Drzwi: {drzwi_count} | Wejściowe: {wejsciowe_count} | Podłogi: {podlogi_count}")
    
    # Potwierdzenie masowej operacji
    if st.session_state.get('show_mass_confirm', False):
        st.warning(f"⚠️ **UWAGA!** Czy na pewno chcesz sfinalizować **{len(drafts)} protokół(y)**?")
        st.warning("📝 Ta operacja przeniesie wszystkie protokoły do gotowych protokołów i usunie je z przechowalni.")
        
        col_confirm1, col_confirm2 = st.columns(2)
        with col_confirm1:
            if st.button("✅ TAK - FINALIZUJ WSZYSTKIE", type="primary"):
                finalize_all_drafts(db, drafts)
                st.session_state.show_mass_confirm = False
                st.rerun()
        with col_confirm2:
            if st.button("❌ ANULUJ"):
                st.session_state.show_mass_confirm = False
                st.rerun()
    
    st.markdown("---")

    # Tabela przeglądowa
    display_rows = []
    for d in drafts:
        display_rows.append({
            "Klient": d.get('imie_nazwisko', ''),
            "Pomieszczenie": d.get('pomieszczenie', ''),
            "Typ": d.get('collection_target', ''),
            "Monter": d.get('monter_id', ''),
            "Telefon": d.get('telefon', ''),
            "Utworzono": d.get('created_at', ''),
            "Aktualizowano": d.get('updated_at', ''),
            "ID": d.get('id', ''),
            "Status": d.get('status', ''),
        })

    st.subheader("📋 Lista protokołów")
    df = pd.DataFrame(display_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Wybór protokołu
    st.subheader("✏️ Edycja / Finalizacja protokołu")
    
    def format_draft_option(draft_id):
        if not draft_id:
            return "Wybierz protokół..."
        
        draft = next((d for d in drafts if d['id'] == draft_id), None)
        if not draft:
            return draft_id
            
        # Formatuj czytelny opis protokołu
        pomieszczenie = draft.get('pomieszczenie', 'Nieznane')
        typ = draft.get('collection_target', 'nieznany')
        klient = draft.get('imie_nazwisko', 'Nieznany klient')
        created = draft.get('created_at', '')
        
        # Formatuj datę jeśli dostępna
        date_str = ""
        if created:
            try:
                if hasattr(created, 'strftime'):
                    date_str = created.strftime("%d.%m %H:%M")
                else:
                    date_str = str(created)[:16]  # Obetnij długi string
            except:
                date_str = ""
        
        return f"🏠 {pomieszczenie} | {typ.upper()} | {klient} | {date_str}"
    
    draft_ids = [d['id'] for d in drafts]
    selected_id = st.selectbox("Wybierz protokół:", options=[""] + draft_ids, format_func=format_draft_option)

    if selected_id:
        # Pobierz najświeższe dane szkicu z bazy danych
        try:
            fresh_draft_doc = db.collection('wymiary_draft').document(selected_id).get()
            if not fresh_draft_doc.exists:
                st.error("❌ Nie znaleziono protokołu")
                return
            draft = fresh_draft_doc.to_dict()
            draft['id'] = fresh_draft_doc.id

        except Exception as e:
            st.error(f"❌ Błąd podczas pobierania protokołu: {e}")
            return

        st.markdown("---")
        st.markdown(f"**ID szkicu:** `{selected_id}` | **Typ:** `{draft.get('collection_target','')}` | **Monter:** `{draft.get('monter_id','')}`")

        # Pełna edycja protokołu w zależności od typu szkicu
        collection_target = draft.get('collection_target', 'drzwi')
        updates = {}

        if collection_target == 'drzwi':
            st.subheader("📋 Podstawowe informacje")
            col1, col2 = st.columns(2)

            with col1:
                pomieszczenie = st.text_input("Pomieszczenie:", value=draft.get('pomieszczenie', ''))
                imie_nazwisko = st.text_input("Imię i Nazwisko:", value=draft.get('imie_nazwisko', ''))
                telefon = st.text_input("Telefon:", value=draft.get('telefon', ''))
                szer = st.text_input("Szerokość otworu:", value=draft.get('szerokosc_otworu', ''))
                wys = st.text_input("Wysokość otworu:", value=draft.get('wysokosc_otworu', ''))
                mierzona_od = st.text_input("Mierzona od:", value=draft.get('mierzona_od', ''))

            with col2:
                st.subheader("📐 Specyfikacja")
                grubosc_muru = st.text_input("Grubość muru (cm):", value=str(draft.get('grubosc_muru', '')))
                stan_sciany = st.text_input("Stan ściany:", value=draft.get('stan_sciany', ''))
                typ_drzwi = st.radio(
                    "Typ drzwi:",
                    ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"],
                    index=["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"].index(draft.get('typ_drzwi', 'Przylgowe')) if draft.get('typ_drzwi') in ["Przylgowe", "Bezprzylgowe", "Odwrotna Przylga", "Renova"] else 0,
                    horizontal=True
                )
                oscieznica = st.text_input("Ościeżnica:", value=draft.get('oscieznica', ''))
                opaska = st.radio("Opaska:", ["6 cm", "8 cm"], index=["6 cm","8 cm"].index(draft.get('opaska', '6 cm')) if draft.get('opaska') in ["6 cm","8 cm"] else 0, horizontal=True)
                kat_zaciecia = st.selectbox("Kąt zacięcia:", ["45°", "90°", "0°"], index=["45°","90°","0°"].index(draft.get('kat_zaciecia', '45°')) if draft.get('kat_zaciecia') in ["45°","90°","0°"] else 0)
                prog = st.text_input("Próg:", value=draft.get('prog', ''))
                wizjer = st.checkbox("Wizjer", value=bool(draft.get('wizjer', False)))

            st.subheader("🚪 Strona otwierania")
            so = draft.get('strona_otwierania', {}) or {}
            
            current_choice = "Nie wybrano"
            if so.get('lewe_przyl'):
                current_choice = "LEWE"
            elif so.get('prawe_przyl'):
                current_choice = "PRAWE"
            elif so.get('lewe_odwr'):
                current_choice = "LEWE odwrotna przylga"
            elif so.get('prawe_odwr'):
                current_choice = "PRAWE odwrotna przylga"
            
            strona_otwierania_szkic = st.radio(
                "Kierunek otwierania drzwi:",
                ["Nie wybrano", "LEWE", "PRAWE", "LEWE odwrotna przylga", "PRAWE odwrotna przylga"],
                index=["Nie wybrano", "LEWE", "PRAWE", "LEWE odwrotna przylga", "PRAWE odwrotna przylga"].index(current_choice),
                key=f"strona_otwierania_szkic_{selected_id}",
                horizontal=True
            )

            st.subheader("📝 Dodatkowe")
            cold1, cold2 = st.columns([2, 1])
            with cold1:
                napis_nad_drzwiami = st.text_input("Otwierane na:", value=draft.get('napis_nad_drzwiami', ''))
                uwagi_montera = st.text_area("Uwagi montera:", value=draft.get('uwagi_montera', ''), height=100)
            with cold2:
                szerokosc_skrzydla = st.text_input("Szerokość skrzydła (cm):", value=str(draft.get('szerokosc_skrzydla', '')))
            norma = st.text_input("Norma/Szkic:", value=draft.get('norma', ''))

            with st.expander("🏷️ Dane sprzedawcy (opcjonalne)"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    producent = st.text_input("Producent:", value=draft.get('producent', ''))
                    seria = st.text_input("Seria:", value=draft.get('seria', ''))
                    typ_prod = st.text_input("Typ:", value=draft.get('typ', ''))
                    rodzaj_okleiny = st.text_input("Rodzaj okleiny:", value=draft.get('rodzaj_okleiny', ''))
                    ilosc_szyb = st.text_input("Ilość szyb:", value=draft.get('ilosc_szyb', ''))
                with col_s2:
                    zamek = st.text_input("Zamek:", value=draft.get('zamek', ''))
                    szyba = st.text_input("Szyba:", value=draft.get('szyba', ''))
                    wentylacja = st.text_input("Wentylacja:", value=draft.get('wentylacja', ''))
                    klamka = st.text_input("Klamka:", value=draft.get('klamka', ''))
                    kolor_wizjera = st.text_input("Kolor wizjera:", value=draft.get('kolor_wizjera', ''))
                    wypelnienie = st.text_input("Wypełnienie:", value=draft.get('wypelnienie', ''))
                    kolor_okuc = st.text_input("Kolor okucia:", value=draft.get('kolor_okuc', ''))
                    kolor_osc = st.text_input("Kolor ość. (jeśli inna):", value=draft.get('kolor_osc', ''))
                opcje_dodatkowe = st.text_area("Opcje dodatkowe:", value=draft.get('opcje_dodatkowe', ''), height=80)
                uwagi_klienta = st.text_area("Uwagi dla klienta:", value=draft.get('uwagi_klienta', ''), height=80)

            # Złóż aktualizacje
            updates = {
                'pomieszczenie': pomieszczenie,
                'imie_nazwisko': imie_nazwisko,
                'telefon': telefon,
                'szerokosc_otworu': szer,
                'wysokosc_otworu': wys,
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
                    'lewe_przyl': strona_otwierania_szkic == "LEWE przylgowe",
                    'prawe_przyl': strona_otwierania_szkic == "PRAWE przylgowe",
                    'lewe_odwr': strona_otwierania_szkic == "LEWE odwrotna przylga",
                    'prawe_odwr': strona_otwierania_szkic == "PRAWE odwrotna przylga",
                },
                'napis_nad_drzwiami': napis_nad_drzwiami,
                'szerokosc_skrzydla': szerokosc_skrzydla,
                'uwagi_montera': uwagi_montera,
                'norma': norma,
                # opcjonalne sprzedawcy
                'producent': producent if 'producent' in locals() else draft.get('producent',''),
                'seria': seria if 'seria' in locals() else draft.get('seria',''),
                'typ': typ_prod if 'typ_prod' in locals() else draft.get('typ',''),
                'rodzaj_okleiny': rodzaj_okleiny if 'rodzaj_okleiny' in locals() else draft.get('rodzaj_okleiny',''),
                'ilosc_szyb': ilosc_szyb if 'ilosc_szyb' in locals() else draft.get('ilosc_szyb',''),
                'zamek': zamek if 'zamek' in locals() else draft.get('zamek',''),
                'szyba': szyba if 'szyba' in locals() else draft.get('szyba',''),
                'wentylacja': wentylacja if 'wentylacja' in locals() else draft.get('wentylacja',''),
                'klamka': klamka if 'klamka' in locals() else draft.get('klamka',''),
                'kolor_wizjera': kolor_wizjera if 'kolor_wizjera' in locals() else draft.get('kolor_wizjera',''),
                'wypelnienie': wypelnienie if 'wypelnienie' in locals() else draft.get('wypelnienie',''),
                'kolor_okuc': kolor_okuc if 'kolor_okuc' in locals() else draft.get('kolor_okuc',''),
                'kolor_osc': kolor_osc if 'kolor_osc' in locals() else draft.get('kolor_osc',''),
                'opcje_dodatkowe': opcje_dodatkowe if 'opcje_dodatkowe' in locals() else draft.get('opcje_dodatkowe',''),
                'uwagi_klienta': uwagi_klienta if 'uwagi_klienta' in locals() else draft.get('uwagi_klienta',''),
            }

        elif collection_target == 'drzwi_wejsciowe':
            st.subheader("📋 Podstawowe informacje")
            col1, col2 = st.columns(2)

            with col1:
                numer_strony = st.text_input("Numer strony:", value=draft.get('numer_strony', ''))
                imie_nazwisko = st.text_input("Imię i Nazwisko:", value=draft.get('imie_nazwisko', ''))
                telefon = st.text_input("Telefon:", value=draft.get('telefon', ''))
                pomieszczenie = st.text_input("Pomieszczenie:", value=draft.get('pomieszczenie', ''))

            with col2:
                szer = st.text_input("Szerokość otworu:", value=draft.get('szerokosc_otworu', ''))
                wys = st.text_input("Wysokość otworu:", value=draft.get('wysokosc_otworu', ''))
                mierzona_od = st.selectbox("Mierzona od:", 
                                         ["szkolenia", "poziomu", "podłogi", "inne"], 
                                         index=["szkolenia", "poziomu", "podłogi", "inne"].index(draft.get('mierzona_od', 'szkolenia')) if draft.get('mierzona_od') in ["szkolenia", "poziomu", "podłogi", "inne"] else 0)
                skrot = st.text_input("Skrót:", value=draft.get('skrot', ''))

            st.subheader("🏗️ Dane techniczne")
            col3, col4 = st.columns(2)

            with col3:
                grubosc_muru = st.text_input("Grubość muru (cm):", value=str(draft.get('grubosc_muru', '')))
                stan_sciany = st.text_input("Stan ściany:", value=draft.get('stan_sciany', ''))
                oscieznica = st.text_input("Ościeżnica:", value=draft.get('oscieznica', ''))
                okapnik = st.text_input("Okapnik:", value=draft.get('okapnik', ''))

            with col4:
                prog = st.text_input("Próg:", value=draft.get('prog', ''))
                wizjer = st.checkbox("Wizjer", value=bool(draft.get('wizjer', False)))
                elektrozaczep = st.text_input("Elektrozaczep:", value=draft.get('elektrozaczep', ''))
                uwagi_montera = st.text_area("Uwagi montera:", value=draft.get('uwagi_montera', ''), height=100)

            st.subheader("🚪 Strona otwierania")
            col5, col6 = st.columns(2)
            so = draft.get('strona_otwierania', {}) or {}

            with col5:
                st.markdown("**Kierunek otwierania:**")
                na_zewnatrz = st.checkbox("Na zewnątrz", value=bool(so.get('na_zewnatrz', False)))
                do_wewnatrz = st.checkbox("Do wewnątrz", value=bool(so.get('do_wewnatrz', False)))

            with col6:
                st.markdown("**Strona zawiasów:**")
                lewe = st.checkbox("Lewe", value=bool(so.get('lewe', False)))
                prawe = st.checkbox("Prawe", value=bool(so.get('prawe', False)))

            updates = {
                'numer_strony': numer_strony,
                'imie_nazwisko': imie_nazwisko,
                'telefon': telefon,
                'pomieszczenie': pomieszczenie,
                'szerokosc_otworu': szer,
                'wysokosc_otworu': wys,
                'mierzona_od': mierzona_od,
                'skrot': skrot,
                'grubosc_muru': grubosc_muru,
                'stan_sciany': stan_sciany,
                'oscieznica': oscieznica,
                'okapnik': okapnik,
                'prog': prog,
                'wizjer': wizjer,
                'elektrozaczep': elektrozaczep,
                'uwagi_montera': uwagi_montera,
                'strona_otwierania': {
                    'na_zewnatrz': na_zewnatrz,
                    'do_wewnatrz': do_wewnatrz,
                    'lewe': lewe,
                    'prawe': prawe
                }
            }

        else:  # podlogi
            st.subheader("📋 Podstawowe informacje")
            col1, col2 = st.columns(2)
            with col1:
                pomieszczenie = st.text_input("Pomieszczenie:", value=draft.get('pomieszczenie', ''))
                telefon = st.text_input("Telefon klienta:", value=draft.get('telefon', ''))
                system_montazu = st.radio(
                    "System montażu:",
                    ["Symetrycznie (cegiełka)", "Niesymetrycznie"],
                    index=["Symetrycznie (cegiełka)", "Niesymetrycznie"].index(draft.get('system_montazu','Symetrycznie (cegiełka)')) if draft.get('system_montazu') in ["Symetrycznie (cegiełka)", "Niesymetrycznie"] else 0,
                    horizontal=True
                )
            with col2:
                podklad = st.text_input("Podkład:", value=draft.get('podklad', ''))
                mdf_mozliwy = st.radio("Czy może być MDF?", ["TAK", "NIE"], index=["TAK","NIE"].index(draft.get('mdf_mozliwy','TAK')) if draft.get('mdf_mozliwy') in ["TAK","NIE"] else 0, horizontal=True)

            st.subheader("📏 Pomiary listw")
            col3, col4, col5 = st.columns(3)
            with col3:
                nw = st.number_input("NW (szt.):", min_value=0, step=1, value=int(draft.get('nw', 0)))
                nz = st.number_input("NZ (szt.):", min_value=0, step=1, value=int(draft.get('nz', 0)))
            with col4:
                l = st.number_input("Ł (szt.):", min_value=0, step=1, value=int(draft.get('l', 0)))
                zl = st.number_input("ZL (szt.):", min_value=0, step=1, value=int(draft.get('zl', 0)))
            with col5:
                zp = st.number_input("ZP (szt.):", min_value=0, step=1, value=int(draft.get('zp', 0)))

            st.subheader("🚪 Listwy progowe")
            col6, col7, col8 = st.columns(3)
            with col6:
                listwy_jaka = st.text_input("Jaka?", value=draft.get('listwy_jaka', ''))
            with col7:
                listwy_ile = st.text_input("Ile?", value=draft.get('listwy_ile', ''))
            with col8:
                listwy_gdzie = st.text_input("Gdzie?", value=draft.get('listwy_gdzie', ''))

            st.subheader("📝 Uwagi montera")
            uwagi_montera = st.text_area("Uwagi dotyczące pomiarów:", value=draft.get('uwagi_montera', ''), height=100)

            updates = {
                'pomieszczenie': pomieszczenie,
                'telefon': telefon,
                'system_montazu': system_montazu,
                'podklad': podklad,
                'mdf_mozliwy': mdf_mozliwy,
                'nw': int(nw),
                'nz': int(nz),
                'l': int(l),
                'zl': int(zl),
                'zp': int(zp),
                'listwy_jaka': listwy_jaka,
                'listwy_ile': listwy_ile,
                'listwy_gdzie': listwy_gdzie,
                'uwagi_montera': uwagi_montera,
            }

        # ========================
        # ZARZĄDZANIE ZDJĘCIAMI
        # ========================
        st.markdown("---")
        
        existing_images = draft.get('zdjecia', [])
        
        if existing_images:
            remaining_images = display_images_with_edit(existing_images, selected_id, max_width=250)
            
            if len(remaining_images) != len(existing_images):
                if update_draft_images(db, selected_id, remaining_images):
                    st.success(f"✅ Zaktualizowano zdjęcia w szkicu (pozostało: {len(remaining_images)})")
                    if len(remaining_images) == 0:
                        st.info("📷 Wszystkie zdjęcia zostały usunięte ze szkicu")
                    st.rerun() 
                else:
                    st.error("❌ Błąd podczas aktualizacji zdjęć")
        else:
            st.info("📷 Ten szkic nie zawiera jeszcze żadnych zdjęć")
        
        # Formularz dodawania nowych zdjęć
        st.markdown("#### ➕ Dodaj nowe zdjęcia")
        
        with st.expander("📷 Dodaj zdjęcia do szkicu", expanded=False):
            new_uploaded_files = create_image_uploader(f"draft_edit_{selected_id}", max_files=5)
            
            if new_uploaded_files:
                col_upload1, col_upload2 = st.columns([2, 1])
                
                with col_upload1:
                    st.write(f"**Wybrano {len(new_uploaded_files)} nowych zdjęć:**")
                    for file in new_uploaded_files:
                        st.write(f"• {file.name} ({file.size/1024:.1f} KB)")
                
                with col_upload2:
                    if st.button("📤 Dodaj do szkicu", type="primary", key=f"add_images_{selected_id}"):
                        with st.spinner("Przetwarzanie i dodawanie zdjęć..."):
                            # Przetwórz nowe zdjęcia
                            new_images_data = process_uploaded_images(
                                new_uploaded_files, 
                                draft.get('collection_target', 'szkic'), 
                                selected_id
                            )
                            
                            if new_images_data:
                                # Dodaj do szkicu
                                if add_images_to_draft(db, selected_id, new_images_data):
                                    st.success(f"✅ Dodano {len(new_images_data)} nowych zdjęć do szkicu!")
                                    st.rerun()
                                else:
                                    st.error("❌ Błąd podczas dodawania zdjęć do szkicu")
                            else:
                                st.error("❌ Nie udało się przetworzyć zdjęć")

        st.markdown("---")
        st.subheader("⚙️ Akcje na szkicu")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("💾 Zapisz zmiany"):
                if update_draft_data(db, selected_id, updates):
                    st.success("✅ Zapisano zmiany w szkicu")
        with col_b:
            if st.button("🗑️ Usuń szkic"):
                st.session_state[f'confirm_delete_{selected_id}'] = True
        with col_c:
            if st.button("✅ Finalizuj (zapisz do bazy)", type="primary"):
                with st.spinner("Finalizowanie szkicu..."):
                    doc_id, kod = finalize_draft(db, selected_id)
                    if doc_id:
                        st.success(f"🎉 Zapisano do bazy. ID: {doc_id} | Kod dostępu: {kod}")
                        st.balloons()
                    else:
                        st.error("❌ Nie udało się sfinalizować szkicu")
        
        # Potwierdzenie usunięcia szkicu
        if st.session_state.get(f'confirm_delete_{selected_id}', False):
            st.warning("⚠️ **UWAGA!** Czy na pewno chcesz usunąć ten szkic?")
            st.warning("🗑️ Ta operacja jest nieodwracalna - wszystkie dane zostaną trwale usunięte!")
            
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ TAK - USUŃ SZKIC", type="primary"):
                    if delete_draft(db, selected_id):
                        st.success("✅ Szkic usunięty")
                        st.session_state[f'confirm_delete_{selected_id}'] = False
                        st.rerun()
                    else:
                        st.error("❌ Błąd podczas usuwania szkicu")
            with col_confirm2:
                if st.button("❌ ANULUJ"):
                    st.session_state[f'confirm_delete_{selected_id}'] = False
                    st.rerun()


if __name__ == "__main__":
    page_wymiary()


