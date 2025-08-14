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
)


def _normalize_name(text: str) -> str:
    if not text:
        return "nieznany_klient"
    norm = unicodedata.normalize('NFKD', text)
    norm = norm.encode('ascii', 'ignore').decode('ascii')
    norm = re.sub(r'[^a-zA-Z0-9]+', '_', norm).strip('_').lower()
    return norm or "nieznany_klient"


def _last3(phone: str) -> str:
    if not phone:
        return "000"
    digits = re.sub(r'\D', '', str(phone))
    return (digits[-3:] if len(digits) >= 3 else digits.zfill(3)) or "000"


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
    phone = rec.get('telefon', '')
    # preferuj data_pomiary, w przeciwnym razie data_utworzenia
    dt = _as_dt(rec.get('data_pomiary') or rec.get('data_utworzenia'))
    day = dt.strftime('%d') if dt != datetime.min else '00'
    month = dt.strftime('%m') if dt != datetime.min else '00'
    year = dt.strftime('%Y') if dt != datetime.min else '0000'

    n = _normalize_name(name)
    suf = _last3(phone)
    folder = f"{n}_{suf}_{day}_{month}_{year}"
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

            # Opcjonalny podgląd konkretnego rekordu
            sel = st.selectbox(
                "Podgląd rekordu (JSON):",
                options=[""] + [r["ID"] for r in rows],
                key=f"sel_json_{folder_name}"
            )
            if sel:
                rec = next((x for x in items if x.get('id') == sel), None)
                if rec:
                    st.json(rec)


if __name__ == "__main__":
    page_foldery()


