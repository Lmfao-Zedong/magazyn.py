import streamlit as st
import pandas as pd
import altair as alt

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(page_title="Panel Magazyniera PRO", page_icon="📦", layout="wide")

# --- TRWAŁOŚĆ DANYCH ---
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = [
        {"nazwa": "Laptop Dell", "sztuk": 5, "cena": 3500.0},
        {"nazwa": "Monitor LG", "sztuk": 12, "cena": 800.0},
        {"nazwa": "Klawiatura Mechaniczna", "sztuk": 8, "cena": 250.0}
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

def operacja_przyjecia(produkt_nazwa, ile, cena):
    if produkt_nazwa == "":
        return False, "Błąd: Nazwa nie może być pusta!"
    
    znaleziono = False
    for p in st.session_state.magazyn:
        if p["nazwa"].lower() == produkt_nazwa.lower():
            p["sztuk"] += ile
            p["cena"] = cena # Aktualizacja ceny przy dostawie
            znaleziono = True
            break
            
    if not znaleziono:
        st.session_state.magazyn.append({"nazwa": produkt_nazwa, "sztuk": ile, "cena": cena})
    return True, f"Pomyślnie przyjęto: {produkt_nazwa}"

def zmien_cene(nazwa_produktu, nowa_cena):
    for p in st.session_state.magazyn:
        if p["nazwa"] == nazwa_produktu:
            p["cena"] = nowa_cena
            return True
    return False

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("📦 System Magazynowy z Finansami")

# Wykres na górze
df_magazyn = pd.DataFrame(st.session_state.magazyn)
if not df_magazyn.empty:
    df_magazyn['Kolor'] = df_magazyn['sztuk'].apply(lambda x: 'Braki' if x < 5 else 'OK')
    chart = alt.Chart(df_magazyn).mark_bar().encode(
        x=alt.X('nazwa:N', title='Produkt', sort='-y'),
        y=alt.Y('sztuk:Q', title='Ilość sztuk'),
        color=alt.Color('Kolor:N', scale=alt.Scale(domain=['Braki', 'OK'], range=['#FF4B4B', '#1F77B4']), legend=None),
        tooltip=['nazwa', 'sztuk', 'cena']
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

# Zakładki
tab1, tab2, tab3, tab4 = st.tabs(["📊 Przegląd", "📥 Przyjęcie i Ceny", "📤 Wydanie", "💰 Finanse"])

with tab1:
    st.subheader("Aktualny stan i braki")
    aktualny_dict = {item["nazwa"]: item["sztuk"] for item in st.session_state.magazyn}
    
    lista_brakow = []
    for produkt, cel in wymagany_stan.items():
        obecnie = aktualny_dict.get(produkt, 0)
        if obecnie < cel:
            lista_brakow.append({"Produkt": produkt, "Brakuje": cel - obecnie, "Stan": f"{obecnie}/{cel}"})
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**⚠️ Do zamówienia:**")
        st.table(pd.DataFrame(lista_brakow)) if lista_brakow else st.success("Brak braków!")
    with col2:
        st.write("**📦 Lista produktów:**")
        st.dataframe(df_magazyn[['nazwa', 'sztuk', 'cena']], hide_index=True, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Dodaj / Przyjmij towar")
        with st.form("form_dodaj"):
            n_nazwa = st.text_input("Nazwa produktu")
            n_ile = st.number_input("Ilość", min_value=1)
            n_cena = st.number_input("Cena jednostkowa (PLN)", min_value=0.01, format="%.2f")
            if st.form_submit_button("Zatwierdź przychód"):
                sukces, msg = operacja_przyjecia(n_nazwa.strip(), n_ile, n_cena)
                if sukces: st.rerun()
    
    with col_b:
        st.subheader("Aktualizuj tylko cenę")
        if not df_magazyn.empty:
            with st.form("form_cena"):
                wybierz_p = st.selectbox("Wybierz produkt", df_magazyn['nazwa'])
                nowa_c = st.number_input("Nowa cena", min_value=0.01, format="%.2f")
                if st.form_submit_button("Zmień cenę"):
                    if zmien_cene(wybierz_p, nowa_c): st.rerun()

with tab3:
    st.subheader("Wydanie towaru")
    if not df_magazyn.empty:
        with st.form("form_wydanie"):
            w_wybor = st.selectbox("Produkt", df_magazyn['nazwa'])
            max_w = int(df_magazyn[df_magazyn['nazwa'] == w_wybor]['sztuk'].iloc[0])
            w_ile = st.number_input("Ilość", min_value=1, max_value=max_w)
            if st.form_submit_button("Wydaj z magazynu"):
                for p in st.session_state.magazyn:
                    if p["nazwa"] == w_wybor:
                        p["sztuk"] -= w_ile
                        if p["sztuk"] <= 0: st.session_state.magazyn.remove(p)
                        st.rerun()

with tab4:
    st.subheader("Analiza finansowa")
    if not df_magazyn.empty:
        # Obliczenia
        df_fin = df_magazyn.copy()
        df_fin['Wartość łączna'] = df_fin['sztuk'] * df_fin['cena']
        suma_total = df_fin['Wartość łączna'].sum()
        
        # Wyświetlanie sumy
        st.metric("Całkowita wartość magazynu", f"{suma_total:,.2f} PLN")
        
        # Tabela finansowa
        st.write("**Szczegółowa wartość pozycji:**")
        st.dataframe(df_fin[['nazwa', 'sztuk', 'cena', 'Wartość łączna']], 
                     column_config={
                         "cena": st.column_config.NumberColumn("Cena jedn.", format="%.2f PLN"),
                         "Wartość łączna": st.column_config.NumberColumn("Wartość pozycji", format="%.2f PLN")
                     },
                     hide_index=True, use_container_width=True)
    else:
        st.warning("Magazyn jest pusty, brak danych finansowych.")
        
