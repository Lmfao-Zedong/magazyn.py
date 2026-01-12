import streamlit as st
import pandas as pd
import altair as alt  # Biblioteka do wykresów

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(page_title="Panel Magazyniera v2", page_icon="📦")

# --- TRWAŁOŚĆ DANYCH (st.session_state) ---
# Inicjalizacja bazy w pamięci sesji, aby dane nie znikały
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = [
        {"nazwa": "Laptop Dell", "sztuk": 5},
        {"nazwa": "Monitor LG", "sztuk": 12},
        {"nazwa": "Klawiatura Mechaniczna", "sztuk": 8}
    ]

# Cele (stałe)
wymagany_stan = {
    "Laptop Dell": 10,
    "Monitor LG": 12,
    "Myszka Logitech": 15,
    "Klawiatura Mechaniczna": 5,
    "Podkładka Gamingowa": 20
}

# --- LOGIKA APLIKACJI ---

def operacja_przyjecia(produkt_nazwa, ile):
    if produkt_nazwa == "":
        return False, "Błąd: Nazwa nie może być pusta!"
    
    znaleziono = False
    for p in st.session_state.magazyn:
        if p["nazwa"].lower() == produkt_nazwa.lower():
            p["sztuk"] += ile
            znaleziono = True
            break
            
    if not znaleziono:
        st.session_state.magazyn.append({"nazwa": produkt_nazwa, "sztuk": ile})
    return True, f"Pomyślnie przyjęto: {produkt_nazwa}"

def operacja_wydania(nazwa_z_listy, ile_wyjac):
    for p in st.session_state.magazyn:
        if p["nazwa"] == nazwa_z_listy:
            if p["sztuk"] < ile_wyjac:
                return False, "Błąd: Niewystarczająca ilość na stanie!"
            p["sztuk"] -= ile_wyjac
            if p["sztuk"] == 0:
                st.session_state.magazyn.remove(p)
            return True, "Towar wydany z magazynu."
    return False, "Nie znaleziono produktu."

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("📦 System Zarządzania Zapasami")

# --- SEKCJA WYKRESU (Nowość) ---
st.subheader("📊 Wizualizacja Stanów")
df_plot = pd.DataFrame(st.session_state.magazyn)

if not df_plot.empty:
    # Definiujemy kolor: czerwony jeśli < 5 sztuk, niebieski dla reszty
    df_plot['Kolor'] = df_plot['sztuk'].apply(lambda x: 'Braki' if x < 5 else 'OK')
    
    chart = alt.Chart(df_plot).mark_bar().encode(
        x=alt.X('nazwa:N', title='Produkt', sort='-y'),
        y=alt.Y('sztuk:Q', title='Ilość'),
        color=alt.Color('Kolor:N', scale=alt.Scale(domain=['Braki', 'OK'], range=['#FF4B4B', '#1F77B4']), legend=None),
        tooltip=['nazwa', 'sztuk']
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["📋 Lista i Braki", "📥 Przyjęcie", "📤 Wydanie"])

with tab1:
    col1, col2 = st.columns(2)
    
    aktualny_dict = {item["nazwa"]: item["sztuk"] for item in st.session_state.magazyn}
    lista_brakow = []
    for produkt, cel in wymagany_stan.items():
        obecnie = aktualny_dict.get(produkt, 0)
        if obecnie < cel:
            lista_brakow.append({"Produkt": produkt, "Do zamówienia": cel - obecnie, "Stan": f"{obecnie}/{cel}"})

    with col1:
        st.write("**⚠️ Wykryte braki:**")
        if lista_brakow:
            st.dataframe(pd.DataFrame(lista_brakow), hide_index=True)
        else:
            st.success("Stany pełne!")

    with col2:
        st.write("**📦 Pełny stan:**")
        st.dataframe(df_plot[['nazwa', 'sztuk']], hide_index=True)

with tab2:
    with st.form("form_przyjecie"):
        input_nazwa = st.text_input("Nazwa produktu")
        input_ile = st.number_input("Ilość", min_value=1, step=1)
        if st.form_submit_button("Dodaj do magazynu"):
            sukces, info = operacja_przyjecia(input_nazwa.strip(), input_ile)
            if sukces: 
                st.success(info)
                st.rerun() # Odśwież, by zaktualizować wykres
            else: st.error(info)

with tab3:
    if st.session_state.magazyn:
        with st.form("form_wydanie"):
            lista_nazw = [p["nazwa"] for p in st.session_state.magazyn]
            wybrany = st.selectbox("Produkt", lista_nazw)
            ile_wydac = st.number_input("Ilość do wydania", min_value=1)
            if st.form_submit_button("Wydaj towar"):
                sukces, info = operacja_wydania(wybrany, ile_wydac)
                if sukces: 
                    st.success(info)
                    st.rerun()
                else: st.error(info)
    else:
        st.warning("Brak towaru.")

# --- BOCZNY PANEL: MOTYW ---
st.sidebar.title("Ustawienia")
st.sidebar.info("💡 **Motyw:** Streamlit automatycznie dopasowuje motyw do systemu operacyjnego Twojego komputera.")

# Instrukcja wymuszenia trybu ciemnego w kodzie (poniżej wyjaśnienie)
