import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from datetime import datetime
import json

# Inicjalizacja Firebase
def initialize_firebase():
    """
    Inicjalizuje połączenie z Firebase Firestore
    """
    if not firebase_admin._apps:
        try:
            # Pierwszy sposób - sekrety Streamlit
            firebase_secrets = st.secrets["firebase_admin"]
            cred = credentials.Certificate(firebase_secrets)
            
            # Sprawdź czy jest project_id w sekretach
            if 'project_id' in firebase_secrets:
                firebase_admin.initialize_app(cred, {
                    'projectId': firebase_secrets['project_id']
                })
            else:
                firebase_admin.initialize_app(cred)
                
        except Exception as e:
            st.error(f"Błąd inicjalizacji Firebase: {e}")
            try:
                # Drugi sposób - z pliku JSON (dla lokalnego rozwoju)
                cred = credentials.Certificate("marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json")
                firebase_admin.initialize_app(cred)
            except Exception as e2:
                st.error(f"Błąd ładowania z pliku: {e2}")
                # Ostatni fallback - zmienne środowiskowe
                import os
                if 'GOOGLE_CLOUD_PROJECT' not in os.environ:
                    os.environ['GOOGLE_CLOUD_PROJECT'] = 'marbabud'
                firebase_admin.initialize_app()
    
    return firestore.client()

def create_tables_if_not_exist(db):
    """
    Tworzy kolekcje w Firestore jeśli nie istnieją
    Definiuje strukturę danych na podstawie formularzy
    """
    
    # Struktura tabeli dla DRZWI
    drzwi_schema = {
        "id": "",  # Automatyczne ID dokumentu
        "data_utworzenia": datetime.now(),
        "pomieszczenie": "",
        "nazwisko": "",
        "telefon": "",
        "szerokosc_otworu": "",
        "wysokosc_otworu": "",
        "mierzona_od": "",
        "typ_drzwi": "",
        "norma": "",
        "grubosc_muru": "",
        "stan_sciany": "",
        "oscieznica": "",
        "kolor_osc": "",
        "opaska": "",
        "kat_zaciecia": "",
        "prog": "",
        "wizjer": "",
        "strona_otwierania": {
            "lewe_przyl": False,
            "prawe_przyl": False,
            "lewe_odwr": False,
            "prawe_odwr": False
        },
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
        "podpis_sprzedawcy": "",
        "podpis_montera": "",
        "podpis_klienta": "",
        "uwagi_klienta": "",
        "podpis_klienta_2": "",
        "status": "aktywny",  # aktywny, zakończony, anulowany
        "etap_formularza": "pomiary",  # pomiary, kompletny
        "wypelnil_monter": False,
        "data_pomiary": None,
        "monter_id": "",
        "wypelnil_sprzedawca": False, 
        "data_sprzedaz": None,
        "sprzedawca_id": "",
        "kod_dostepu": "",  # Unikalny kod do udostępnienia
        "link_udostepniony": False
    }
    
    # Struktura tabeli dla PODŁÓG
    podlogi_schema = {
        "id": "",  # Automatyczne ID dokumentu
        "data_utworzenia": datetime.now(),
        "pomieszczenie": "",
        "telefon": "",
        "system_montazu": "",
        "rodzaj_podlogi": "",
        "seria": "",
        "kolor": "",
        "folia": "",
        "podklad": "",
        "listwa_przypodlogowa": "",
        "mdf_mozliwy": "",
        "nw": 0,
        "nz": 0,
        "l": 0,
        "zl": 0,
        "zp": 0,
        "listwy_jaka": "",
        "listwy_ile": "",
        "listwy_gdzie": "",
        "podpis_sprzedawcy": "",
        "podpis_klienta": "",
        "podpis_klienta_2": "",
        "podpis_montera": "",
        "uwagi": "",
        "status": "aktywny",  # aktywny, zakończony, anulowany
        "etap_formularza": "pomiary",  # pomiary, kompletny
        "wypelnil_monter": False,
        "data_pomiary": None,
        "monter_id": "",
        "wypelnil_sprzedawca": False, 
        "data_sprzedaz": None,
        "sprzedawca_id": "",
        "kod_dostepu": "",  # Unikalny kod do udostępnienia
        "link_udostepniony": False
    }
    
    try:
        # Sprawdź czy kolekcja 'drzwi' istnieje
        drzwi_ref = db.collection('drzwi')
        drzwi_docs = drzwi_ref.limit(1).get()
        
        if len(drzwi_docs) == 0:
            # Utwórz przykładowy dokument w kolekcji drzwi
            sample_drzwi = drzwi_schema.copy()
            sample_drzwi["pomieszczenie"] = "Przykład - Salon"
            sample_drzwi["uwagi_klienta"] = "Kolekcja utworzona automatycznie"
            drzwi_ref.add(sample_drzwi)
            print("✅ Kolekcja 'drzwi' została utworzona")
        
        # Sprawdź czy kolekcja 'podlogi' istnieje
        podlogi_ref = db.collection('podlogi')
        podlogi_docs = podlogi_ref.limit(1).get()
        
        if len(podlogi_docs) == 0:
            # Utwórz przykładowy dokument w kolekcji podlogi
            sample_podlogi = podlogi_schema.copy()
            sample_podlogi["pomieszczenie"] = "Przykład - Pokój"
            sample_podlogi["uwagi"] = "Kolekcja utworzona automatycznie"
            podlogi_ref.add(sample_podlogi)
            print("✅ Kolekcja 'podlogi' została utworzona")
            
    except Exception as e:
        print(f"❌ Błąd podczas tworzenia kolekcji: {e}")

def save_drzwi_data(db, dane_formularza):
    """
    Zapisuje dane formularza drzwi do bazy danych
    """
    try:
        # Dodaj metadane
        dane_formularza["data_utworzenia"] = datetime.now()
        dane_formularza["status"] = "aktywny"
        
        # Zapisz do kolekcji 'drzwi'
        doc_ref = db.collection('drzwi').add(dane_formularza)
        
        # doc_ref to tuple (timestamp, DocumentReference)
        document_id = doc_ref[1].id
        print(f"✅ Zapisano dane drzwi z ID: {document_id}")
        return document_id
        
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania danych drzwi: {e}")
        return None

def save_podlogi_data(db, dane_formularza):
    """
    Zapisuje dane formularza podłóg do bazy danych
    """
    try:
        # Dodaj metadane
        dane_formularza["data_utworzenia"] = datetime.now()
        dane_formularza["status"] = "aktywny"
        
        # Zapisz do kolekcji 'podlogi'
        doc_ref = db.collection('podlogi').add(dane_formularza)
        
        # doc_ref to tuple (timestamp, DocumentReference)
        document_id = doc_ref[1].id
        print(f"✅ Zapisano dane podłóg z ID: {document_id}")
        return document_id
        
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania danych podłóg: {e}")
        return None

def get_all_drzwi(db):
    """
    Pobiera wszystkie rekordy drzwi z bazy danych
    """
    try:
        docs = db.collection('drzwi').order_by('data_utworzenia', direction=firestore.Query.DESCENDING).get()
        drzwi_list = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            drzwi_list.append(data)
        return drzwi_list
    except Exception as e:
        st.error(f"Błąd podczas pobierania danych drzwi: {e}")
        return []

def get_all_podlogi(db):
    """
    Pobiera wszystkie rekordy podłóg z bazy danych
    """
    try:
        docs = db.collection('podlogi').order_by('data_utworzenia', direction=firestore.Query.DESCENDING).get()
        podlogi_list = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            podlogi_list.append(data)
        return podlogi_list
    except Exception as e:
        st.error(f"Błąd podczas pobierania danych podłóg: {e}")
        return []

def update_record_status(db, collection_name, doc_id, new_status):
    """
    Aktualizuje status rekordu (aktywny, zakończony, anulowany)
    """
    try:
        db.collection(collection_name).document(doc_id).update({
            'status': new_status,
            'data_modyfikacji': datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"Błąd podczas aktualizacji statusu: {e}")
        return False

def delete_record(db, collection_name, doc_id):
    """
    Usuwa rekord z bazy danych
    """
    try:
        db.collection(collection_name).document(doc_id).delete()
        return True
    except Exception as e:
        st.error(f"Błąd podczas usuwania rekordu: {e}")
        return False

# Funkcje dla workflow dwuetapowego
import secrets
import string

def generate_access_code():
    """Generuje unikalny kod dostępu dla formularza"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def save_pomiary_data(db, collection_name, dane_formularza, monter_id):
    """
    Zapisuje część formularza wypełnioną przez montera (pomiary)
    """
    try:
        # Dodaj metadane dla etapu pomiarów
        dane_formularza["data_utworzenia"] = datetime.now()
        dane_formularza["etap_formularza"] = "pomiary"
        dane_formularza["wypelnil_monter"] = True
        dane_formularza["data_pomiary"] = datetime.now()
        dane_formularza["monter_id"] = monter_id
        dane_formularza["kod_dostepu"] = generate_access_code()
        dane_formularza["status"] = "pomiary_wykonane"
        
        # Zapisz do odpowiedniej kolekcji
        doc_ref = db.collection(collection_name).add(dane_formularza)
        document_id = doc_ref[1].id
        
        print(f"✅ Zapisano pomiary {collection_name} z ID: {document_id}")
        return document_id, dane_formularza["kod_dostepu"]
        
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania pomiarów {collection_name}: {e}")
        return None, None

def complete_form_by_seller(db, collection_name, doc_id, dane_sprzedawcy, sprzedawca_id):
    """
    Uzupełnia formularz danymi od sprzedawcy
    """
    try:
        # Aktualizuj dokument o dane sprzedawcy
        update_data = dane_sprzedawcy.copy()
        update_data.update({
            "wypelnil_sprzedawca": True,
            "data_sprzedaz": datetime.now(),
            "sprzedawca_id": sprzedawca_id,
            "etap_formularza": "kompletny",
            "status": "aktywny"
        })
        
        db.collection(collection_name).document(doc_id).update(update_data)
        
        print(f"✅ Formularz {collection_name} został ukończony przez sprzedawcę")
        return True
        
    except Exception as e:
        print(f"❌ Błąd podczas uzupełniania formularza: {e}")
        return False

def get_form_by_access_code(db, collection_name, kod_dostepu):
    """
    Pobiera formularz na podstawie kodu dostępu
    """
    try:
        docs = db.collection(collection_name).where('kod_dostepu', '==', kod_dostepu).limit(1).get()
        
        if docs:
            doc = docs[0]
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        else:
            return None
            
    except Exception as e:
        st.error(f"Błąd podczas wyszukiwania formularza: {e}")
        return None

def get_forms_for_completion(db, collection_name):
    """
    Pobiera formularze gotowe do uzupełnienia przez sprzedawcę
    Używa prostszego zapytania aby uniknąć problemów z indeksami
    """
    try:
        # Najpierw pobierz wszystkie dokumenty gdzie monter wypełnił
        docs = db.collection(collection_name).where('wypelnil_monter', '==', True).get()
        
        forms_list = []
        for doc in docs:
            data = doc.to_dict()
            # Filtruj tylko te w etapie pomiarów
            if data.get('etap_formularza') == 'pomiary':
                data['id'] = doc.id
                forms_list.append(data)
        
        # Sortuj według daty (najnowsze pierwsze)
        forms_list.sort(key=lambda x: x.get('data_utworzenia', datetime.min), reverse=True)
        return forms_list
        
    except Exception as e:
        st.error(f"Błąd podczas pobierania formularzy do uzupełnienia: {e}")
        return []

def generate_share_link(doc_id, kod_dostepu, collection_name):
    """
    Generuje link do udostępnienia formularza
    """
    # W rzeczywistej aplikacji użyłbyś prawdziwego URL
    return f"https://twoja-aplikacja.com/uzupelnij/{collection_name}/{doc_id}?kod={kod_dostepu}"

# Funkcja inicjalizacyjna do wywołania przy starcie aplikacji
@st.cache_resource
def setup_database():
    """
    Inicjalizuje bazę danych i tworzy niezbędne kolekcje
    """
    db = initialize_firebase()
    create_tables_if_not_exist(db)
    return db

