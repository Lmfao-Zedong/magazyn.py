import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client

# --- KONFIGURACJA ---
st.set_page_config(page_title="Magazyn Chmurowy v3", page_icon="☁️", layout="wide")

# Podłączanie do bazy (Zalecane użycie st.secrets na GitHubie)
# Jeśli testujesz lokalnie, możesz wpisać dane w cudzysłów
URL = https://ioyuvcamccqvgszjxycv.supabase.co
KEY = sb_publishable_SvkL-WiUqpudkMBtvWKFBA_WNykg-t1

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- FUNKCJE BAZY DANYCH ---

def pobierz_dane():
    # Pobiera wszystkie wiersze z tabeli 'magazyn'
    res = supabase.table("magazyn").select("*").execute()
    return res.data

def zapisz_towar(nazwa, ile, cena):
    # Sprawdza czy produkt istnieje (case-insensitive)
    istnieje = supabase.table("magazyn").select("*").eq("nazwa", nazwa).execute()
    
    if istnieje.data:
        nowa_ilosc = istnieje.data[0]['sztuk'] + ile
        supabase.table("magazyn").update({"sztuk": nowa_ilosc, "cena": cena}).eq("nazwa", nazwa).execute()
    else:
        supabase.table("magazyn").insert({"nazwa": nazwa, "sztuk": ile, "cena": cena}).execute()

def wydaj_towar(nazwa, ile):
    res = supabase.table("magazyn").select("sztuk").eq("nazwa", nazwa).single().execute()
    obecnie = res.data['sztuk']
    if obecnie >= ile:
        nowy = obecnie - ile
        if nowy == 0:
            supabase.table("magazyn").delete().eq("nazwa", nazwa).execute()
        else:
            supabase.table("magazyn").update({"sztuk": nowy}).eq("nazwa", nazwa).execute()
        return True
    return False

# --- UI APLIKACJI ---

st.title("📦 System Magazynowy PRO (Chmura)")

# Pobieranie danych do DF
dane = pobierz_dane()
df = pd.DataFrame(dane)

if not df.empty:
    # Wykres Kolorowy
    df['Kolor'] = df['sztuk'].apply(lambda x: 'Braki' if x < 5 else 'OK')
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('nazwa:N', sort='-y'),
        y='sztuk:Q',
        color=alt.Color('Kolor:N', scale=alt.Scale(domain=['Braki', 'OK'], range=['#FF4B4B', '#1F77B4']), legend=None),
        tooltip=['nazwa', 'sztuk', 'cena']
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

# Zakładki
t1, t2, t3, t4 = st.tabs(["📊 Stan", "📥 Przyjęcie/Cena", "📤 Wydanie", "💰 Finanse"])

with t1:
    st.subheader("Aktualne zapasy")
    st.dataframe(df, hide_index=True, use_container_width=True)

with t2:
    with st.form("form_add"):
        c1, c2, c3 = st.columns(3)
        n = c1.text_input("Nazwa produktu")
        i = c2.number_input("Ilość", min_value=1)
        c = c3.number_input("Cena (PLN)", min_value=0.0)
        if st.form_submit_button("Zatwierdź do bazy"):
            zapisz_towar(n.strip(), i, c)
            st.rerun()

with t3:
    if not df.empty:
        with st.form("form_out"):
            wybor = st.selectbox("Wybierz do wydania", df['nazwa'])
            ile_w = st.number_input("Ile sztuk", min_value=1)
            if st.form_submit_button("Wydaj"):
                if wydaj_towar(wybor, ile_w):
                    st.rerun()
                else:
                    st.error("Błąd ilości!")

with t4:
    if not df.empty:
        df['Wartość'] = df['sztuk'] * df['cena']
        st.metric("Całkowita wartość magazynu", f"{df['Wartość'].sum():,.2f} PLN")
        st.dataframe(df[['nazwa', 'sztuk', 'cena', 'Wartość']], hide_index=True)
        
