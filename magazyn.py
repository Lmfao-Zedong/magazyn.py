import streamlit as st
import pandas as pd

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(page_title="Panel Magazyniera v2", page_icon="📦")

# --- BAZA DANYCH (Zasoby początkowe) ---
# Zmieniona struktura na listę słowników - wygląda inaczej w kodzie
magazyn_produkty = [
    {"nazwa": "Laptop Dell", "sztuk": 5},
    {"nazwa": "Monitor LG", "sztuk": 12},
    {"nazwa": "Klawiatura Mechaniczna", "sztuk": 8}
]

# Cele do osiągnięcia
wymagany_stan = {
    "Laptop Dell": 10,
    "Monitor LG": 12,
    "Myszka Logitech": 15,
    "Klawiatura Mechaniczna": 5,
    "Podkładka Gamingowa": 20
}

# --- LOGIKA APLIKACJI ---

def operacja_przyjecia(produkt_nazwa, ile):
    """Zajmuje się dopisaniem towaru do bazy"""
    if produkt_nazwa == "":
        return False, "Błąd: Nazwa nie może być pusta!"
    
    znaleziono = False
    for p in magazyn_produkty:
        if p["nazwa"].lower() == produkt_nazwa.lower():
            p["sztuk"] += ile
            znaleziono = True
            break
            
    if not znaleziono:
        magazyn_produkty.append({"nazwa": produkt_nazwa, "sztuk": ile})
    
    return True, f"Pomyślnie przyjęto: {produkt_nazwa}"

def operacja_wydania(nazwa_z_listy, ile_wyjac):
    """Zajmuje się odejmowaniem towaru"""
    for p in magazyn_produkty:
        if p["nazwa"] == nazwa_z_listy:
            if p["sztuk"] < ile_wyjac:
                return False, "Błąd: Niewystarczająca ilość na stanie!"
            p["sztuk"] -= ile_wyjac
            if p["sztuk"] == 0:
                magazyn_produkty.remove(p)
            return True, "Towar wydany z magazynu."
    return False, "Nie znaleziono produktu."

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("📦 System Zarządzania Zapasami")
st.info("Tryb demonstracyjny: Dane resetują się po każdym odświeżeniu strony.")

# Zakładki zamiast sekcji jedna pod drugą - wygląda nowocześniej
tab1, tab2, tab3 = st.tabs(["📊 Przegląd i Braki", "📥 Przyjęcie Towaru", "📤 Wydanie Towaru"])

with tab1:
    st.subheader("Aktualne braki (do zamówienia)")
    
    lista_brakow = []
    # Tworzymy słownik pomocniczy dla łatwiejszego porównania
    aktualny_dict = {item["nazwa"]: item["sztuk"] for item in magazyn_produkty}
    
    for produkt, cel in wymagany_stan.items():
        obecnie = aktualny_dict.get(produkt, 0)
        if obecnie < cel:
            lista_brakow.append({
                "Produkt": produkt,
                "Brakuje [szt]": cel - obecnie,
                "Status": f"{obecnie} / {cel}"
            })
            
    if lista_brakow:
        st.table(pd.DataFrame(lista_brakow))
    else:
        st.success("Wszystkie stany magazynowe są zgodne z planem!")

    st.divider()
    st.subheader("Pełna lista magazynowa")
    st.dataframe(pd.DataFrame(magazyn_produkty), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Dodaj nowy ładunek")
    with st.container(border=True):
        input_nazwa = st.text_input("Wpisz nazwę produktu")
        input_ile = st.number_input("Ilość do dodania", min_value=1, step=1)
        
        if st.button("Potwierdź przychód", type="primary"):
            sukces, info = operacja_przyjecia(input_nazwa.strip(), input_ile)
            if sukces:
                st.toast(info) # Małe powiadomienie w rogu
                st.success(info)
            else:
                st.error(info)

with tab3:
    st.subheader("Wydaj towar z magazynu")
    if magazyn_produkty:
        lista_nazw = [p["nazwa"] for p in magazyn_produkty]
        wybrany = st.selectbox("Wybierz produkt z półki", lista_nazw)
        
        # Pobieramy max dostępną ilość dla wybranego produktu
        max_dostepne = next(p["sztuk"] for p in magazyn_produkty if p["nazwa"] == wybrany)
        
        ile_wydac = st.number_input("Ile sztuk wydać?", min_value=1, max_value=max_dostepne, value=1)
        
        if st.button("Zatwierdź wydanie"):
            sukces, info = operacja_wydania(wybrany, ile_wydac)
            if sukces:
                st.success(info)
            else:
                st.error(info)
    else:
        st.warning("Magazyn świeci pustkami. Brak produktów do wydania.")

st.sidebar.markdown("---")
st.sidebar.write(f"Suma pozycji w bazie: {len(magazyn_produkty)}")
