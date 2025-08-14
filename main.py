import streamlit as st
from firebase_config import (
    setup_database,
    get_all_drzwi,
    get_all_podlogi,
    get_all_drzwi_wejsciowe,
    delete_record,
    get_drafts_for_monter,
    delete_draft,
)

def main_interface():
    st.title("Strona główna")
    st.write("Witaj w aplikacji")
    st.write("Wybierz opcję z menu po lewej stronie")
    try:
        db = setup_database()
        
        if db is not None:
            st.success("✅ Baza danych została zainicjalizowana")

            drzwi_count = len(get_all_drzwi(db))
            podlogi_count = len(get_all_podlogi(db))
            drzwi_wejsciowe_count = len(get_all_drzwi_wejsciowe(db))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rekordy drzwi", drzwi_count)
            with col2:
                st.metric("Rekordy podłóg", podlogi_count)
            with col3:
                st.metric("Drzwi wejściowe", drzwi_wejsciowe_count)
            st.markdown("---")
            st.subheader("📚 Podgląd bazy danych")

            tab1, tab2, tab3, tab4 = st.tabs(["🚪 Drzwi", "🚨 Drzwi wejściowe", "🏠 Podłogi", "🗂️ Szkice (Wymiary)"])

            with tab1:
                drzwi = get_all_drzwi(db)
                if drzwi:
                    display = []
                    for r in drzwi:
                        display.append({
                            "ID": r.get("id",""),
                            "Data": r.get("data_utworzenia",""),
                            "Pomieszczenie": r.get("pomieszczenie",""),
                            "Klient": r.get("imie_nazwisko",""),
                            "Telefon": r.get("telefon",""),
                            "Wymiary": f"{r.get('szerokosc_otworu','')} x {r.get('wysokosc_otworu','')}",
                            "Monter": r.get("monter_id",""),
                            "Status": r.get("status",""),
                        })
                    st.dataframe(display, use_container_width=True, hide_index=True)

                    st.markdown("**Akcje**")
                    col_d1, col_d2 = st.columns([3,1])
                    with col_d1:
                        drzwi_ids = [r["ID"] for r in display]
                        selected_drzwi = st.selectbox("Wybierz rekord do podglądu/usunięcia:", options=[""]+drzwi_ids)
                        if selected_drzwi:
                            rec = next((x for x in drzwi if x.get('id')==selected_drzwi), None)
                            if rec:
                                with st.expander("Podgląd danych (JSON)"):
                                    st.json(rec)
                    with col_d2:
                        if selected_drzwi and st.button("🗑️ Usuń rekord drzwi", key="delete_drzwi"):
                            if delete_record(db, "drzwi", selected_drzwi):
                                st.success("✅ Usunięto rekord")
                                st.experimental_rerun()
                            else:
                                st.error("❌ Nie udało się usunąć rekordu")
                else:
                    st.info("📭 Brak rekordów w kolekcji 'drzwi'")

            with tab2:
                drzwi_wejsciowe = get_all_drzwi_wejsciowe(db)
                if drzwi_wejsciowe:
                    display_we = []
                    for r in drzwi_wejsciowe:
                        display_we.append({
                            "ID": r.get("id",""),
                            "Data": r.get("data_utworzenia",""),
                            "Pomieszczenie": r.get("pomieszczenie",""),
                            "Nazwisko": r.get("nazwisko",""),
                            "Telefon": r.get("telefon",""),
                            "Wymiary": f"{r.get('szerokosc_otworu','')} x {r.get('wysokosc_otworu','')}",
                            "Monter": r.get("monter_id",""),
                            "Status": r.get("status",""),
                        })
                    st.dataframe(display_we, use_container_width=True, hide_index=True)

                    st.markdown("**Akcje**")
                    col_we1, col_we2 = st.columns([3,1])
                    with col_we1:
                        drzwi_we_ids = [r["ID"] for r in display_we]
                        selected_drzwi_we = st.selectbox("Wybierz rekord do podglądu/usunięcia:", options=[""]+drzwi_we_ids, key="select_drzwi_we")
                        if selected_drzwi_we:
                            rec_we = next((x for x in drzwi_wejsciowe if x.get('id')==selected_drzwi_we), None)
                            if rec_we:
                                with st.expander("Podgląd danych (JSON)"):
                                    st.json(rec_we)
                    with col_we2:
                        if selected_drzwi_we and st.button("🗑️ Usuń rekord drzwi wejściowych", key="delete_drzwi_we"):
                            if delete_record(db, "drzwi_wejsciowe", selected_drzwi_we):
                                st.success("✅ Usunięto rekord")
                                st.experimental_rerun()
                            else:
                                st.error("❌ Nie udało się usunąć rekordu")
                else:
                    st.info("📭 Brak rekordów w kolekcji 'drzwi_wejsciowe'")

            with tab3:
                podlogi = get_all_podlogi(db)
                if podlogi:
                    display = []
                    for r in podlogi:
                        display.append({
                            "ID": r.get("id",""),
                            "Data": r.get("data_utworzenia",""),
                            "Pomieszczenie": r.get("pomieszczenie",""),
                            "Telefon": r.get("telefon",""),
                            "System": r.get("system_montazu",""),
                            "Monter": r.get("monter_id",""),
                            "Status": r.get("status",""),
                        })
                    st.dataframe(display, use_container_width=True, hide_index=True)

                    st.markdown("**Akcje**")
                    col_p1, col_p2 = st.columns([3,1])
                    with col_p1:
                        podlogi_ids = [r["ID"] for r in display]
                        selected_podlogi = st.selectbox("Wybierz rekord do podglądu/usunięcia:", options=[""]+podlogi_ids, key="sel_podlogi")
                        if selected_podlogi:
                            rec = next((x for x in podlogi if x.get('id')==selected_podlogi), None)
                            if rec:
                                with st.expander("Podgląd danych (JSON)"):
                                    st.json(rec)
                    with col_p2:
                        if selected_podlogi and st.button("🗑️ Usuń rekord podłóg", key="delete_podlogi"):
                            if delete_record(db, "podlogi", selected_podlogi):
                                st.success("✅ Usunięto rekord")
                                st.experimental_rerun()
                            else:
                                st.error("❌ Nie udało się usunąć rekordu")
                else:
                    st.info("📭 Brak rekordów w kolekcji 'podlogi'")

            with tab4:
                szkice = get_drafts_for_monter(db)
                if szkice:
                    display = []
                    for r in szkice:
                        display.append({
                            "ID": r.get("id",""),
                            "Typ": r.get("collection_target",""),
                            "Monter": r.get("monter_id",""),
                            "Klient": r.get("imie_nazwisko",""),
                            "Telefon": r.get("telefon",""),
                            "Pomieszczenie": r.get("pomieszczenie",""),
                            "Utworzono": r.get("created_at",""),
                            "Aktualizowano": r.get("updated_at",""),
                        })
                    st.dataframe(display, use_container_width=True, hide_index=True)

                    st.markdown("**Akcje**")
                    col_s1, col_s2 = st.columns([3,1])
                    with col_s1:
                        szkice_ids = [r["ID"] for r in display]
                        selected_szkic = st.selectbox("Wybierz szkic do podglądu/usunięcia:", options=[""]+szkice_ids, key="sel_szkic")
                        if selected_szkic:
                            rec = next((x for x in szkice if x.get('id')==selected_szkic), None)
                            if rec:
                                with st.expander("Podgląd szkicu (JSON)"):
                                    st.json(rec)
                    with col_s2:
                        if selected_szkic and st.button("🗑️ Usuń szkic", key="delete_szkic"):
                            if delete_draft(db, selected_szkic):
                                st.success("✅ Usunięto szkic")
                                st.experimental_rerun()
                            else:
                                st.error("❌ Nie udało się usunąć szkicu")

        else:
            st.warning("⚠️ Baza danych nie jest dostępna")
            st.info("🔧 Sprawdź konfigurację Firebase w pliku credentials")
            st.info(f"📄 Wymagany plik: `marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json`")
            
            # Sprawdź czy plik istnieje
            import os
            if os.path.exists("marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json"):
                st.success("✅ Plik credentials istnieje")
                st.info("🔄 Spróbuj wyczyścić cache i odświeżyć stronę")
                
                if st.button("🔄 Wyczyść cache i spróbuj ponownie"):
                    st.cache_resource.clear()
                    st.experimental_rerun()
            else:
                st.error("❌ Plik credentials nie został znaleziony")

    except Exception as e:
        st.error(f"❌ Błąd aplikacji: {e}")

if __name__ == "__main__":
    main_interface()