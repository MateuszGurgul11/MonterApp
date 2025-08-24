import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st
from datetime import datetime
import json
import os
import secrets
import string
import base64
from PIL import Image
import io

def initialize_firebase():
    """Inicjalizuje połączenie z Firebase Firestore bez pliku na dysku."""
    if firebase_admin._apps:
        return firestore.client()

    try:
        # Sprawdź najpierw czy mamy secrets (bez logowania błędów)
        has_secrets = False
        try:
            has_secrets = "firebase_admin" in st.secrets
        except:
            pass  # Ignore secrets errors
        
        # Metoda 1: Streamlit secrets 
        if has_secrets:
            st.info("🔧 Inicjalizacja Firebase ze Streamlit secrets")
            firebase_creds = dict(st.secrets["firebase_admin"])
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            return firestore.client()

        # Metoda 2: Plik JSON
        else:
            credentials_file = "marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json"
            
            if os.path.exists(credentials_file):
                st.info(f"🔧 Inicjalizacja Firebase z pliku: {credentials_file}")
                cred = credentials.Certificate(credentials_file)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                
                # Test połączenia
                try:
                    # Sprawdź czy można się połączyć
                    collections = list(db.collections())
                    st.success("✅ Połączenie z Firebase Firestore nawiązane")
                    return db
                except Exception as test_error:
                    st.error(f"❌ Problemy z połączeniem Firestore: {test_error}")
                    return None
            else:
                st.error(f"❌ Nie znaleziono pliku credentials: {credentials_file}")
                st.error("Upewnij się, że plik istnieje w katalogu projektu")
                return None

    except Exception as e:
        st.error(f"❌ Błąd inicjalizacji Firebase: {e}")
        
        # Dodatkowe informacje diagnostyczne
        credentials_file = "marbabud-firebase-adminsdk-fbsvc-b4355b7a63.json"
        if os.path.exists(credentials_file):
            st.error("📄 Plik credentials istnieje, ale wystąpił błąd podczas inicjalizacji")
        else:
            st.error("📄 Plik credentials nie istnieje")
        
        return None

@st.cache_resource
def setup_database():
    """Inicjalizuje bazę danych z pełną obsługą błędów"""
    try:
        db = initialize_firebase()
        if db is None:
            st.error("❌ Nie udało się zainicjalizować bazy danych Firebase!")
            st.error("🔧 Sprawdź konfigurację Firebase")
            return None
        
        # Test czy baza faktycznie działa
        try:
            # Sprawdź czy możemy się połączyć
            collections = list(db.collections())
            return db
        except Exception as test_error:
            st.error(f"❌ Problemy z połączeniem z bazą: {test_error}")
            return None
            
    except Exception as e:
        st.error(f"❌ Krytyczny błąd inicjalizacji: {e}")
        return None

def create_tables_if_not_exist(db):
    """
    Tworzy kolekcje w Firestore jeśli nie istnieją
    Definiuje strukturę danych na podstawie formularzy
    """
    
    # Struktura tabeli dla DRZWI WEJŚCIOWYCH
    drzwi_wejsciowe_schema = {
        "id": "", 
        "data_utworzenia": datetime.now(),
        "numer_strony": "",
        "nazwisko": "",
        "telefon": "",
        "pomieszczenie": "",
        "szerokosc_otworu": "",
        "wysokosc_otworu": "",
        "mierzona_od": "",  # szkolenia, poziomu, podłogi, inne
        "skrot": "",
        "grubosc_muru": "",  # cm
        "stan_sciany": "",   # sposób wykończenia: tapeta, płyta g-k, itp.
        "oscieznica": "",
        "okapnik": "",
        "prog": "",
        "wizjer": "",
        "elektrozaczep": "",
        "strona_otwierania": {
            "na_zewnatrz": False,
            "do_wewnatrz": False,
            "lewe": False,
            "prawe": False
        },
        # Dane produktu (pola 1-9)
        "producent": "",           # 1. Producent
        "grubosc": "",            # 2. Grubość
        "wzor": "",               # 3. Wzór
        "rodzaj_okleiny": "",     # 4. Rodzaj okleiny
        "ramka": "",              # 5. Ramka (czarna, inox, laminowana)
        "wkladki": "",            # 6. Wkładki
        "szyba": "",              # 7. Szyba
        "klamka": "",             # 8. Klamka
        "dostawa": "",            # 9. Dostawa (jeśli jest)
        
        # Podpisy i uwagi
        "podpis_sprzedawcy": "",
        "podpis_klienta": "",
        "uwagi_dla_klienta": "",
        "podpis_klienta_2": "",   # drugi podpis klienta
        "podpis_montera": "",
        
        # Dodatkowe pola systemowe
        "monter_id": "",
        "data_pomiary": None,
        "kod_dostepu": "",
        "sprzedawca_id": "",
        "status": "oczekuje_na_uzupelnienie",
        "uwagi_montera": ""
    }

    # Struktura tabeli dla DRZWI
    drzwi_schema = {
        "id": "", 
        "data_utworzenia": datetime.now(),
        "pomieszczenie": "",
        "imie_nazwisko": "",
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
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return []
        
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
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return []
        
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

def get_all_drzwi_wejsciowe(db):
    """
    Pobiera wszystkie rekordy drzwi wejściowych z bazy danych
    """
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return []
        
    try:
        docs = db.collection('drzwi_wejsciowe').order_by('data_utworzenia', direction=firestore.Query.DESCENDING).get()
        drzwi_wejsciowe_list = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            drzwi_wejsciowe_list.append(data)
        return drzwi_wejsciowe_list
    except Exception as e:
        st.error(f"Błąd podczas pobierania danych drzwi wejściowych: {e}")
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
        docs = db.collection(collection_name).where(filter=firestore.FieldFilter('kod_dostepu', '==', kod_dostepu)).limit(1).get()
        
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
        docs = db.collection(collection_name).where(filter=firestore.FieldFilter('wypelnil_monter', '==', True)).get()
        
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

def get_document_by_id(db, collection_name, doc_id):
    """
    Pobiera pojedynczy dokument z bazy danych po ID
    """
    try:
        doc_ref = db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        else:
            return None
            
    except Exception as e:
        st.error(f"Błąd podczas pobierania dokumentu: {e}")
        return None

def update_document(db, collection_name, doc_id, updated_data):
    """
    Aktualizuje dokument w bazie danych
    """
    try:
        doc_ref = db.collection(collection_name).document(doc_id)
        doc_ref.update(updated_data)
        return True
        
    except Exception as e:
        st.error(f"Błąd podczas aktualizacji dokumentu: {e}")
        return False

# =====================
# Kwarantanna (Szkice)
# =====================

def save_draft_data(db, collection_target, dane_formularza, monter_id):
    """
    Zapisuje szkic (kwarantanna) pomiarów bez finalizacji do głównej kolekcji.
    collection_target: 'drzwi', 'drzwi_wejsciowe' lub 'podlogi'
    """
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return None

    try:
        now = datetime.now()
        dane = dane_formularza.copy()
        dane.update({
            "collection_target": collection_target,
            "status": "draft",
            "created_at": now,
            "updated_at": now,
            "monter_id": monter_id,
        })
        doc_ref = db.collection('wymiary_draft').add(dane)
        draft_id = doc_ref[1].id
        print(f"✅ Zapisano szkic {collection_target} z ID: {draft_id}")
        return draft_id
    except Exception as e:
        st.error(f"❌ Błąd podczas zapisywania szkicu: {e}")
        return None

def get_drafts_for_monter(db, monter_id=None):
    """
    Pobiera szkice (kwarantanna). Jeśli podano monter_id – filtruje po monterze.
    """
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return []

    try:
        ref = db.collection('wymiary_draft')
        if monter_id:
            query = ref.where(filter=firestore.FieldFilter('monter_id', '==', monter_id))
        else:
            query = ref
        docs = query.order_by('updated_at', direction=firestore.Query.DESCENDING).get()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results
    except Exception as e:
        st.error(f"❌ Błąd podczas pobierania szkiców: {e}")
        return []

def update_draft_data(db, draft_id, updates):
    """Aktualizuje szkic"""
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return False
    try:
        updates = updates.copy()
        updates['updated_at'] = datetime.now()
        db.collection('wymiary_draft').document(draft_id).update(updates)
        return True
    except Exception as e:
        st.error(f"❌ Błąd podczas aktualizacji szkicu: {e}")
        return False

def delete_draft(db, draft_id):
    """Usuwa szkic"""
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return False
    try:
        db.collection('wymiary_draft').document(draft_id).delete()
        return True
    except Exception as e:
        st.error(f"❌ Błąd podczas usuwania szkicu: {e}")
        return False

def finalize_draft(db, draft_id):
    """
    Finalizuje szkic: przenosi dane do docelowej kolekcji ('drzwi', 'drzwi_wejsciowe' lub 'podlogi')
    i usuwa szkic. Zwraca (doc_id, kod_dostepu) lub (None, None) w razie błędu.
    """
    if db is None:
        st.error("❌ Baza danych nie jest zainicjalizowana")
        return None, None
    try:
        snap = db.collection('wymiary_draft').document(draft_id).get()
        if not snap.exists:
            st.error("❌ Szkic nie istnieje")
            return None, None

        data = snap.to_dict()
        collection_target = data.get('collection_target')
        monter_id = data.get('monter_id', '')
        if collection_target not in ['drzwi', 'drzwi_wejsciowe', 'podlogi']:
            st.error("❌ Nieprawidłowy typ szkicu")
            return None, None

        # Usuń meta szkicu
        payload = data.copy()
        for meta_key in ['collection_target', 'status', 'created_at', 'updated_at', 'id']:
            payload.pop(meta_key, None)

        # Zapisz jako pomiary (monter)
        doc_id, kod = save_pomiary_data(db, collection_target, payload, monter_id)
        if doc_id:
            # Usuń szkic
            db.collection('wymiary_draft').document(draft_id).delete()
            return doc_id, kod
        else:
            return None, None
    except Exception as e:
        st.error(f"❌ Błąd podczas finalizacji szkicu: {e}")
        return None, None

def generate_share_link(doc_id, kod_dostepu, collection_name):
    """
    Generuje link do udostępnienia formularza
    """
    # W rzeczywistej aplikacji użyłbyś prawdziwego URL
    return f"https://twoja-aplikacja.com/uzupelnij/{collection_name}/{doc_id}?kod={kod_dostepu}"

# ===================
# Obsługa zdjęć
# ===================

def upload_image_to_firebase(uploaded_file, folder_name, doc_id):
    """
    Przesyła zdjęcie do Firebase Storage
    Zwraca URL zdjęcia lub None w przypadku błędu
    """
    try:
        if uploaded_file is None:
            return None
            
        # Sprawdź format pliku
        if not uploaded_file.type.startswith('image/'):
            st.error("❌ Można przesyłać tylko pliki obrazów!")
            return None
            
        # Sprawdź rozmiar (maksymalnie 5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("❌ Plik jest za duży! Maksymalny rozmiar to 5MB")
            return None
            
        # Utwórz unikalną nazwę pliku
        file_extension = uploaded_file.name.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{folder_name}/{doc_id}/{timestamp}_{uploaded_file.name}"
        
        # Konwertuj i zmniejsz obraz jeśli potrzeba
        image = Image.open(uploaded_file)
        
        # Zmniejsz obraz jeśli jest za duży (maksymalnie 1920x1080)
        max_width = 1920
        max_height = 1080
        if image.width > max_width or image.height > max_height:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Konwertuj do JPEG dla zmniejszenia rozmiaru
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Zapisz do bufora
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # Przesyłanie do Firebase Storage wymaga konfiguracji bucket
        # Na razie zapisujemy jako base64 w bazie danych
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
        
    except Exception as e:
        st.error(f"❌ Błąd podczas przesyłania zdjęcia: {e}")
        return None

def save_images_to_database(db, collection_name, doc_id, images_data):
    """
    Zapisuje dane zdjęć do dokumentu w bazie danych
    """
    try:
        db.collection(collection_name).document(doc_id).update({
            'zdjecia': images_data,
            'data_aktualizacji_zdjec': datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"❌ Błąd podczas zapisywania zdjęć: {e}")
        return False

def display_images(images_data, max_width=300):
    """
    Wyświetla zdjęcia z danych base64
    """
    if not images_data:
        st.info("📷 Brak zdjęć dla tego pomiaru")
        return
        
    st.subheader("📸 Zdjęcia z pomiarów")
    
    # Wyświetl zdjęcia w kolumnach
    cols = st.columns(3)
    for i, img_data in enumerate(images_data):
        with cols[i % 3]:
            try:
                # Dekoduj base64
                img_bytes = base64.b64decode(img_data['data'])
                
                # Wyświetl zdjęcie
                st.image(img_bytes, caption=img_data.get('nazwa', f'Zdjęcie {i+1}'), width=max_width)
                
                # Pokaż informacje o zdjęciu
                if 'data_dodania' in img_data:
                    st.caption(f"Dodano: {img_data['data_dodania'].strftime('%Y-%m-%d %H:%M')}")
                    
            except Exception as e:
                st.error(f"❌ Błąd wyświetlania zdjęcia {i+1}: {e}")

def create_image_uploader(key_prefix, max_files=5):
    """
    Tworzy interfejs do przesyłania zdjęć
    Zwraca listę przesłanych plików
    """
    st.subheader("📷 Dodaj zdjęcia z pomiarów")
    st.write("Możesz dodać maksymalnie 5 zdjęć (formaty: JPG, PNG, maksymalnie 5MB każde)")
    
    uploaded_files = st.file_uploader(
        "Wybierz zdjęcia:",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        key=f"{key_prefix}_image_uploader"
    )
    
    if uploaded_files:
        if len(uploaded_files) > max_files:
            st.warning(f"⚠️ Możesz przesłać maksymalnie {max_files} zdjęć. Wybrano pierwsze {max_files}.")
            uploaded_files = uploaded_files[:max_files]
            
        # Pokaż podgląd zdjęć
        st.write("**Podgląd zdjęć:**")
        cols = st.columns(min(len(uploaded_files), 3))
        
        for i, uploaded_file in enumerate(uploaded_files):
            with cols[i % 3]:
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, width=200)
                    st.write(f"Rozmiar: {uploaded_file.size/1024:.1f} KB")
                except Exception as e:
                    st.error(f"❌ Błąd podglądu: {e}")
                    
    return uploaded_files

def process_uploaded_images(uploaded_files, folder_name, doc_id):
    """
    Przetwarza przesłane zdjęcia i zwraca dane do zapisania w bazie
    """
    if not uploaded_files:
        return []
        
    images_data = []
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"Przetwarzanie {uploaded_file.name}..."):
            img_base64 = upload_image_to_firebase(uploaded_file, folder_name, doc_id)
            
            if img_base64:
                images_data.append({
                    'nazwa': uploaded_file.name,
                    'data': img_base64,
                    'rozmiar': uploaded_file.size,
                    'typ': uploaded_file.type,
                    'data_dodania': datetime.now()
                })
                
    return images_data

def display_images_with_edit(images_data, draft_id, max_width=300):
    """
    Wyświetla zdjęcia z możliwością usuwania (dla przechowalni)
    """
    if not images_data:
        st.info("📷 Brak zdjęć dla tego szkicu")
        return images_data
        
    st.subheader("📸 Zdjęcia w szkicu")
    
    # Sprawdź czy jakieś zdjęcie zostało zaznaczone do usunięcia
    images_to_delete = []
    
    # Wyświetl zdjęcia w kolumnach
    cols_per_row = 3
    for i in range(0, len(images_data), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(images_data):
                img_data = images_data[idx]
                with cols[j]:
                    try:
                        # Dekoduj base64
                        img_bytes = base64.b64decode(img_data['data'])
                        
                        # Wyświetl zdjęcie
                        st.image(img_bytes, caption=img_data.get('nazwa', f'Zdjęcie {idx+1}'), width=max_width)
                        
                        # Pokaż informacje o zdjęciu
                        if 'data_dodania' in img_data:
                            try:
                                if hasattr(img_data['data_dodania'], 'strftime'):
                                    date_str = img_data['data_dodania'].strftime('%Y-%m-%d %H:%M')
                                else:
                                    date_str = str(img_data['data_dodania'])
                                st.caption(f"Dodano: {date_str}")
                            except:
                                st.caption("Dodano: nieznana data")
                        
                        # Przycisk usuwania
                        if st.button(f"🗑️ Usuń", key=f"delete_img_{draft_id}_{idx}", help=f"Usuń zdjęcie: {img_data.get('nazwa', f'Zdjęcie {idx+1}')}"):
                            images_to_delete.append(idx)
                            
                    except Exception as e:
                        st.error(f"❌ Błąd wyświetlania zdjęcia {idx+1}: {e}")
    
    # Jeśli jakieś zdjęcie zostało zaznaczone do usunięcia
    if images_to_delete:
        # Utwórz nową listę bez usuniętych zdjęć
        images_to_keep = [img for i, img in enumerate(images_data) if i not in images_to_delete]
        return images_to_keep
    
    # Jeśli nic nie zostało usunięte, zwróć oryginalne dane
    return images_data

def add_images_to_draft(db, draft_id, new_images_data):
    """
    Dodaje nowe zdjęcia do istniejącego szkicu
    """
    try:
        # Pobierz obecne dane szkicu
        draft_doc = db.collection('wymiary_draft').document(draft_id).get()
        if not draft_doc.exists:
            st.error("❌ Szkic nie istnieje")
            return False
            
        draft_data = draft_doc.to_dict()
        existing_images = draft_data.get('zdjecia', [])
        
        # Dodaj nowe zdjęcia do istniejących
        all_images = existing_images + new_images_data
        
        # Aktualizuj szkic
        db.collection('wymiary_draft').document(draft_id).update({
            'zdjecia': all_images,
            'data_aktualizacji_zdjec': datetime.now(),
            'updated_at': datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"❌ Błąd podczas dodawania zdjęć: {e}")
        return False

def update_draft_images(db, draft_id, images_data):
    """
    Aktualizuje zdjęcia w szkicu (używane przy usuwaniu)
    """
    try:
        db.collection('wymiary_draft').document(draft_id).update({
            'zdjecia': images_data,
            'data_aktualizacji_zdjec': datetime.now(),
            'updated_at': datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"❌ Błąd podczas aktualizacji zdjęć: {e}")
        return False

# Funkcja inicjalizacyjna do wywołania przy starcie aplikacji
@st.cache_resource
def setup_database():
    """
    Inicjalizuje bazę danych i tworzy niezbędne kolekcje
    """
    db = initialize_firebase()
    create_tables_if_not_exist(db)
    return db

