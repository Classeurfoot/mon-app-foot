import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re

# 1. Configuration de la page
st.set_page_config(page_title="Archives Football", layout="wide")

# ==========================================
# ⚙️ FONCTIONS DE NETTOYAGE ET RECHERCHE
# ==========================================

def nettoyer_nom(nom):
    """Transforme 'Coupe du Monde' en 'coupedumonde'"""
    if pd.isna(nom) or nom == "": return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_image(nom_recherche, dossier_racine="Logos"):
    """
    Cherche récursivement un fichier .png dans tous les sous-dossiers.
    Ex: si on cherche 'cdm1998', il va scanner Logos/Monde/Compétitions/normal/ etc.
    """
    nom_cible = nettoyer_nom(nom_recherche)
    if not nom_cible: return None
    
    # On définit aussi des variantes communes pour aider la recherche
    variantes = [nom_cible, nom_cible.replace("coupedumonde", "cdm")]

    for racine, dossiers, fichiers in os.walk(dossier_racine):
        for fichier in fichiers:
            if fichier.lower().endswith(".png"):
                nom_fichier = nettoyer_nom(os.path.splitext(fichier)[0])
                if nom_fichier in variantes:
                    return os.path.join(racine, fichier)
    return None

# ==========================================
# 🧠 LE CERVEAU DE L'ARBORESCENCE
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
        "Jeux Olympiques": "Jeux Olympiques"
    },
    "Clubs": {
        "Coupe d'Europe": {
            "C1": ["Coupe d'Europe des clubs champions", "Champions League"],
            "C2": ["Coupe des Coupes"],
            "C3": ["Coupe Intertoto", "Coupe UEFA", "Europa League"],
            "C4": ["Conference League"]
        },
        "Championnat de France": ["Division 1", "Ligue 1", "Division 2", "Ligue 2"],
        "Championnats étrangers": {
            "Italie": ["Serie A", "Coppa Italia"],
            "Espagne": ["Liga", "Copa del Rey"],
            "Angleterre": ["Premier League", "FA Cup"],
            "Allemagne": ["Bundesliga"]
        }
    },
    "Divers": {
        "Amical": ["Amical", "Opel Master Cup"]
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
            dates_num = pd.to_numeric(df['Date'], errors='coerce')
            masque = dates_num.notna()
            df.loc[masque, 'Date'] = pd.to_datetime(dates_num[masque], unit='D', origin='1899-12-30').dt.strftime('%d/%m/%Y')
        return df
    except Exception as e:
        st.error(f"Erreur CSV : {e}")
        return pd.DataFrame()

df = load_data()

# --- AFFICHAGE DES RÉSULTATS ---
def afficher_resultats(df_res):
    if df_res.empty:
        st.warning("Aucun match.")
        return
    st.metric("Matchs", len(df_res))
    mode = st.radio("Affichage", ["📊 Tableau", "🃏 Fiches"], horizontal=True)
    
    if mode == "📊 Tableau":
        st.dataframe(df_res, use_container_width=True)
    else:
        st.write("---")
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_res.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    st.caption(f"🗓️ {row.get('Date','')} | 🏆 {row.get('Compétition','')}")
                    
                    dom, ext, score = row['Domicile'], row['Extérieur'], row.get('Score','-')
                    
                    # Recherche automatique des logos d'équipes partout dans Logos/
                    path_dom = trouver_image(dom)
                    path_ext = trouver_image(ext)
                    
                    c1, c2, c3 = st.columns([1, 1.5, 1])
                    with c1:
                        if path_dom: st.image(path_dom, use_column_width=True)
                        st.markdown(f"<p style='text-align:center;font-size:12px;'><b>{dom}</b></p>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<h2 style='text-align:center;'>{score}</h2>", unsafe_allow_html=True)
                    with c3:
                        if path_ext: st.image(path_ext, use_column_width=True)
                        st.markdown(f"<p style='text-align:center;font-size:12px;'><b>{ext}</b></p>", unsafe_allow_html=True)

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'ed' not in st.session_state: st.session_state.ed = None

if st.session_state.page != 'accueil':
    if st.sidebar.button("🏠 Menu"):
        st.session_state.page = 'accueil'; st.session_state.chemin = []; st.session_state.ed = None
        st.rerun()

# --- PAGES ---
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    if st.button("📂 EXPLORER PAR COMPÉTITION", use_container_width=True):
        st.session_state.page = 'arbo'; st.session_state.chemin = ['Nations']; st.rerun()
    # Ajoute d'autres boutons ici si besoin...

elif st.session_state.page == 'arbo':
    noeud = MENU_ARBO
    for e in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[e]
    
    st.caption(f"📍 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.ed: st.session_state.ed = None
        else:
            st.session_state.chemin.pop()
            if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()

    if isinstance(noeud, dict):
        for cle in noeud.keys():
            if st.button(cle, use_container_width=True):
                st.session_state.chemin.append(cle); st.rerun()
    else:
        # On est au niveau des éditions (ex: Coupe du Monde 1998)
        if st.session_state.ed is None:
            # Filtre spécial CDM/EURO ou liste simple
            if isinstance(noeud, str) and "FILTER_" in noeud:
                if "CDM_FINALE" in noeud: m = df['Compétition'].str.contains("Coupe du Monde", na=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False)
                elif "CDM_ELIM" in noeud: m = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False)
                # ... etc ...
                eds = sorted(df[m]['Compétition'].unique(), reverse=True)
            else:
                eds = sorted(df[df['Compétition'].isin(noeud if isinstance(noeud, list) else [noeud])]['Compétition'].unique(), reverse=True)
            
            for e in eds:
                if st.button(e): st.session_state.ed = e; st.rerun()
        else:
            # AFFICHAGE FINAL DE LA COMPÉTITION
            c1, c2 = st.columns([4, 1])
            with c1: st.header(st.session_state.ed)
            with c2:
                # RECHERCHE DU LOGO DE COMPÉTITION PARTOUT DANS /Logos
                path_logo_comp = trouver_image(st.session_state.ed)
                if path_logo_comp: st.image(path_logo_comp, width=120)
            
            afficher_resultats(df[df['Compétition'] == st.session_state.ed])
