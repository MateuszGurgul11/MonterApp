import streamlit as st
import hashlib
import json
import os
from firebase_config import (
    setup_database,
    get_all_drzwi,
    get_all_podlogi,
    get_all_drzwi_wejsciowe,
    delete_record,
    get_drafts_for_monter,
    delete_draft,
)

# Plik z użytkownikami
USERS_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def init_users():
    users = load_users()
    if not users:
        # Domyślny admin
        users = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "name": "Administrator"
            }
        }
        save_users(users)
        st.info("🔧 Utworzono domyślnego użytkownika: admin / admin123")
    return users

def authenticate_user(username, password):
    """Sprawdza dane logowania"""
    users = load_users()
    if username in users:
        hashed_password = hash_password(password)
        if users[username]["password"] == hashed_password:
            return users[username]
    return None

def login_form():
    """Formularz logowania"""
    # Nie dodawaj tytułu tutaj - jest w main()
    
    with st.form("login_form"):
        st.subheader("Wprowadź dane logowania:")
        username = st.text_input("👤 Nazwa użytkownika:")
        password = st.text_input("🔑 Hasło:", type="password")
        submit = st.form_submit_button("🚀 Zaloguj się", type="primary")
        
        if submit:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    # Zapisz dane użytkownika w session_state
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_role = user["role"]
                    st.session_state.user_name = user["name"]
                    st.success(f"✅ Zalogowano jako {user['name']}")
                    st.rerun()
                else:
                    st.error("❌ Nieprawidłowa nazwa użytkownika lub hasło")
            else:
                st.warning("⚠️ Proszę wypełnić wszystkie pola")
    

def admin_panel():
    """Panel administracyjny do zarządzania użytkownikami"""
    st.header("👨‍💼 Panel Administratora")
    
    if st.session_state.user_role != "admin":
        st.error("❌ Brak uprawnień administratora")
        return
    
    users = load_users()
    
    tab1, tab2, tab3 = st.tabs(["👥 Lista użytkowników", "➕ Dodaj użytkownika", "🔧 Ustawienia"])
    
    with tab1:
        st.subheader("📋 Zarządzanie użytkownikami")
        
        if users:
            # Wyświetl listę użytkowników
            user_data = []
            for username, data in users.items():
                user_data.append({
                    "Użytkownik": username,
                    "Imię": data.get("name", ""),
                    "Rola": data.get("role", ""),
                    "Ostatnie logowanie": data.get("last_login", "Nigdy")
                })
            
            st.dataframe(user_data, use_container_width=True, hide_index=True)
            
            # Usuwanie użytkowników
            st.markdown("---")
            st.subheader("🗑️ Usuń użytkownika")
            
            user_to_delete = st.selectbox(
                "Wybierz użytkownika do usunięcia:",
                options=[""] + [u for u in users.keys() if u != "admin"],  # Nie można usunąć admina
                key="delete_user_select"
            )
            
            if user_to_delete:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.warning(f"⚠️ Czy na pewno chcesz usunąć użytkownika '{user_to_delete}'?")
                with col2:
                    if st.button("🗑️ Usuń", key="delete_user_btn"):
                        if user_to_delete != "admin":
                            del users[user_to_delete]
                            if save_users(users):
                                st.success(f"✅ Użytkownik '{user_to_delete}' został usunięty")
                                st.rerun()
                            else:
                                st.error("❌ Błąd podczas usuwania użytkownika")
                        else:
                            st.error("❌ Nie można usunąć administratora")
        else:
            st.info("📭 Brak użytkowników w systemie")
    
    with tab2:
        st.subheader("➕ Dodaj nowego użytkownika")
        
        with st.form("add_user_form"):
            new_username = st.text_input("👤 Nazwa użytkownika:")
            new_name = st.text_input("📝 Imię i nazwisko:")
            new_password = st.text_input("🔑 Hasło:", type="password")
            new_password_confirm = st.text_input("🔑 Potwierdź hasło:", type="password")
            new_role = st.selectbox("👑 Rola:", ["user", "admin"])
            
            submit_new_user = st.form_submit_button("➕ Dodaj użytkownika", type="primary")
            
            if submit_new_user:
                if new_username and new_name and new_password and new_password_confirm:
                    if new_password == new_password_confirm:
                        if new_username not in users:
                            # Dodaj nowego użytkownika
                            users[new_username] = {
                                "password": hash_password(new_password),
                                "role": new_role,
                                "name": new_name,
                                "created_by": st.session_state.username
                            }
                            
                            if save_users(users):
                                st.success(f"✅ Użytkownik '{new_username}' został dodany")
                                st.rerun()
                            else:
                                st.error("❌ Błąd podczas zapisywania użytkownika")
                        else:
                            st.error("❌ Użytkownik o tej nazwie już istnieje")
                    else:
                        st.error("❌ Hasła nie są identyczne")
                else:
                    st.warning("⚠️ Proszę wypełnić wszystkie pola")
    
    with tab3:
        st.subheader("🔧 Ustawienia systemu")
        
        st.info("📊 **Statystyki systemu:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Użytkownicy", len(users))
        with col2:
            admins = len([u for u in users.values() if u.get("role") == "admin"])
            st.metric("👨‍💼 Administratorzy", admins)
        with col3:
            regular_users = len([u for u in users.values() if u.get("role") == "user"])
            st.metric("👤 Zwykli użytkownicy", regular_users)
        
        st.markdown("---")
        
        # Reset hasła administratora
        st.subheader("🔄 Reset hasła administratora")
        with st.form("reset_admin_password"):
            new_admin_password = st.text_input("🔑 Nowe hasło dla admin:", type="password")
            new_admin_password_confirm = st.text_input("🔑 Potwierdź nowe hasło:", type="password")
            
            reset_submit = st.form_submit_button("🔄 Zmień hasło admina")
            
            if reset_submit:
                if new_admin_password and new_admin_password_confirm:
                    if new_admin_password == new_admin_password_confirm:
                        users["admin"]["password"] = hash_password(new_admin_password)
                        if save_users(users):
                            st.success("✅ Hasło administratora zostało zmienione")
                        else:
                            st.error("❌ Błąd podczas zmiany hasła")
                    else:
                        st.error("❌ Hasła nie są identyczne")
                else:
                    st.warning("⚠️ Proszę wypełnić oba pola")

def main_interface():
    """Główny interfejs aplikacji (po zalogowaniu)"""
    st.title("📊 Panel Główny")
    
    # Header z informacją o użytkowniku
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"👋 Witaj, **{st.session_state.user_name}** ({st.session_state.user_role})")
    with col2:
        if st.session_state.user_role == "admin":
            if st.button("👨‍💼 Panel Admina"):
                st.session_state.show_admin_panel = True
                st.rerun()
    with col3:
        if st.button("🚪 Wyloguj"):
            # Wyczyść dane sesji
            for key in ['logged_in', 'username', 'user_role', 'user_name', 'show_admin_panel']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Jeśli admin chce zobaczyć panel
    if st.session_state.get('show_admin_panel', False):
        if st.button("⬅️ Powrót do panelu głównego"):
            st.session_state.show_admin_panel = False
            st.rerun()
        admin_panel()
        return
    
    # Główny panel z danymi
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

                    if st.session_state.user_role == "admin":  # Tylko admin może usuwać
                        st.markdown("**Akcje administratora**")
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
                                    st.rerun()
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

                    if st.session_state.user_role == "admin":
                        st.markdown("**Akcje administratora**")
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
                                    st.rerun()
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

                    if st.session_state.user_role == "admin":
                        st.markdown("**Akcje administratora**")
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
                                    st.rerun()
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

                    if st.session_state.user_role == "admin":
                        st.markdown("**Akcje administratora**")
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
                                    st.rerun()
                                else:
                                    st.error("❌ Nie udało się usunąć szkicu")
                else:
                    st.info("📭 Brak szkiców w systemie")

        else:
            st.warning("⚠️ Baza danych nie jest dostępna")
            st.info("🔧 Sprawdź konfigurację Firebase w pliku credentials")
            st.info(f"📄 Wymagany plik: `marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json`")
            
            # Sprawdź czy plik istnieje
            if os.path.exists("marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json"):
                st.success("✅ Plik credentials istnieje")
                st.info("🔄 Spróbuj wyczyścić cache i odświeżyć stronę")
                
                if st.button("🔄 Wyczyść cache i spróbuj ponownie"):
                    st.cache_resource.clear()
                    st.rerun()
            else:
                st.error("❌ Plik credentials nie został znaleziony")

    except Exception as e:
        st.error(f"❌ Błąd aplikacji: {e}")

def main():
    # Konfiguracja strony
    st.set_page_config(
        page_title="System Pomiarów",
        page_icon="📏",
        layout="wide"
    )
    
    # Inicjalizacja systemu użytkowników
    init_users()
    
    if not st.session_state.get('logged_in', False):
        # UKRYJ NAWIGACJĘ PRZED LOGOWANIEM
        st.markdown("""
        <style>
        .stSidebar {
            display: none;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
        .css-1d391kg {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Wycentruj formularz logowania
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 🔐 Logowanie do systemu")
            st.markdown("---")
            login_form()
    else:
        # POKAŻ NAWIGACJĘ PO ZALOGOWANIU
        st.markdown("""
        <style>
        .stSidebar {
            display: block;
        }
        [data-testid="stSidebarNav"] {
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)
        
        main_interface()

if __name__ == "__main__":
    main()