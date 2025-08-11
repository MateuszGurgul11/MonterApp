import streamlit as st
from firebase_config import setup_database, get_all_drzwi, get_all_podlogi

def main_interface():
    st.title("Strona główna")
    st.write("Witaj w aplikacji")
    st.write("Wybierz opcję z menu po lewej stronie")
    try:
        db = setup_database()
        st.success("Baza danych została zainicjalizowana")

        drzwi_count = len(get_all_drzwi(db))
        podlogi_count = len(get_all_podlogi(db))

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rekordy drzwi", drzwi_count)
        with col2:
            st.metric("Rekordy podłóg", podlogi_count)

    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main_interface()