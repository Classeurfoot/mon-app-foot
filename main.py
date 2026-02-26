import streamlit as st
import pandas as pd
import os

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# ==========================================
# 🎨 TA BANQUE DE LOGOS LOCALE
# ==========================================
LOGOS = {
    "Coupe du Monde 1998": "Logos/cdm1998.png",
    "Coupe du Monde 1978": "Logos/cdm1978.png",
"Coupe du Monde 1982": "Logos/cdm1982.png",
"Coupe du Monde 1986": "Logos/cdm1986.png",
"Coupe du Monde 1990": "Logos/cdm1990.png",
"Coupe du Monde 1994": "Logos/cdm1994.png",
"Coupe du Monde 2002": "Logos/cdm2002.png",
"Coupe du Monde 2006": "Logos/cdm2006.png",
"Coupe du Monde 2010": "Logos/cdm2010.png",
"Coupe du Monde 2014": "Logos/cdm2014.png",
"Coupe du Monde 2018": "Logos/cdm2018.png",
    "Coupe du Monde 2022": "Logos/cdm2022.png",
    "Euro 1992": "Logos/euro92.png",
"Euro 1996": "Logos/euro96.png",
"Euro 2000": "Logos/euro2000.png",
"Euro 2004": "Logos/euro2004.png",
"Euro 2008": "Logos/euro2008.png",
"Euro 2012": "Logos/euro2012.png",
"Euro 2016": "Logos/euro2016.png",
"Euro 2020": "Logos/euro2020.png",
"Euro 2024": "Logos/euro20024.png",
    "Ligue 1": "Logos/ligue1.png",
    "Champions League": "Logos/championsleague.png"
}

# ==========================================
# 🧠 LE CERVEAU DE L'ARBORESCENCE EXACTE
# ==========================================
MENU_ARBO = {
    "Nations": {
        "Coupe du Monde": {
            "Phase finale": "FILTER_CDM_FINALE",
            "Eliminatoires": "FILTER_CDM_ELIM"
        },
        "Championnat d'Europe": {
            "Phase finale": "FILTER_EURO_FINALE",
            "Eliminatoires": "FILTER_EURO_ELIM"
        },
        "Ligue des Nations": "Ligue des Nations",
        "Copa America": "Copa America",
        "Coupe des Confédérations": "Coupe des Confédérations",
        "Jeux Olympiques": "Jeux Olympiques"
    },
    "Clubs": {
        "Coupe d'Europe": {
            "C1": ["Coupe d'Europe des clubs champions", "Champions League"],
            "C2": ["Coupe des Coupes"],
            "C3": ["Coupe Intertoto", "Coupe UEFA", "Europa League"],
            "C4": ["Conference League"]
        },
        "Supercoupe d'Europe": "Supercoupe d'Europe",
        "Coupe intercontinentale": ["Coupe intercontinentale", "Coupe du Monde des clubs de la FIFA"],
        "Coupe du Monde des Clubs": ["Coupe du Monde des Clubs 2025"],
        "Championnat de France": ["Division 1", "Ligue 1", "Division 2", "Ligue 2"],
        "Coupe Nationale": ["Coupe de France", "Coupe de la Ligue", "Trophée des Champions"],
        "Championnats étrangers": {
            "Italie": ["Serie A", "Coppa Italia"],
            "Espagne": ["Liga", "Copa del Rey"],
            "Angleterre": ["Premier League", "FA Cup"],
            "Allemagne": ["Bundesliga"]
        }
    },
    "Divers": {
        "Amical": ["Amical", "Opel Master Cup"],
        "Tournoi international": ["Tournoi Hassan II", "Kirin Cup"]
    }
}

# 3. Chargement des données
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("matchs.csv", sep=None, engine="python", on_bad_lines='skip')
        df = df.dropna(subset=['Domicile', 'Extérieur'])
        df.columns = df.columns.str.strip()
        
        if 'Date' in df.columns:
            dates_numeriques = pd.to_numeric(df['Date'], errors='coerce')
            masque_excel = dates_numeriques.notna()
            dates_converties = pd.to_datetime(dates_numeriques[masque_excel], unit='D', origin='1899-12-30')
            df.loc[masque_excel, 'Date'] = dates_converties.dt.strftime('%d/%m/%Y')
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return pd.DataFrame()

df = load_data()

colonnes_possibles = ['Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Qualité']
colonnes_presentes = [c for c in colonnes_possibles if c in df.columns]

# --- GESTION DE LA NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'accueil'
if 'chemin' not in st.session_state:
    st.session_state.chemin = []
if 'edition_choisie' not in st.session_state:
    st.session_state.edition_choisie = None

def go_home():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.edition_choisie = None

# --- BARRE LATÉRALE ---
if st.session_state.page != 'accueil':
    if st.sidebar.button("🏠 Menu Principal", use_container_width=True):
        go_home()
        st.rerun()

# ==========================================
# PAGE D'ACCUEIL
# ==========================================
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state
