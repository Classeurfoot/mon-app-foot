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
    if pd.isna(nom) or nom == "": return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_image(nom_recherche, dossier_racine="Logos"):
    nom_cible = nettoyer_nom(nom_recherche)
    if not nom_cible: return None
    variantes = [nom_cible, nom_cible.replace("coupedumonde", "cdm")]
    if not os.path.exists(dossier_racine): return None
    for racine, dossiers, fichiers in os.walk(dossier_racine):
        for fichier in fichiers:
            if fichier.lower().endswith(".png"):
                nom_fichier_clean = nettoyer_nom(os.path.splitext(fichier)[0])
                if nom_fichier_clean in variantes:
                    return os.path.join(racine, fichier)
    return None

# ==========================================
# 🧠 ARBORESCENCE DES MENUS
# ==========================================
MENU_ARBO = {
    "🌍 NATIONS": {
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
    "🏟️ CLUBS": {
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
    "🎲 DIVERS": {
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
            df['Date'] = df['Date'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erreur CSV : {e}")
        return pd.DataFrame()

df = load_data()

# --- AFFICHAGE DES RÉSULTATS ---
def afficher_resultats(df_res):
    if df_res.empty:
        st.warning("Aucun match trouvé.")
        return
    st.metric("Matchs trouvés", len(df_res))
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
                    path_dom = trouver_image(dom)
                    path_ext = trouver_image(ext)
                    c1, c2, c3 = st.columns([1, 1.2, 1])
                    with c1:
                        if path_dom: st.image(path_dom, use_column_width=True)
                        st.markdown(f"<p style='text-align:center;font-size:12px;'><b>{dom}</b></p>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<h2 style='text-align:center;'>{score}</h2>", unsafe_allow_html=True)
                    with c3:
                        if path_ext: st.image(path_ext, use_column_width=True)
                        st.markdown(f"<p style='text-align:center;font-size:12px;'><b>{ext}</b></p>", unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'ed' not in st.session_state: st.session_state.ed = None

def reset_nav():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.ed = None

if st.session_state.page != 'accueil':
    if st.sidebar.button("🏠 Retour à l'accueil", use_container_width=True):
        reset_nav()
        st.rerun()

# ==========================================
# PAGES
# ==========================================

if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    
    # 1. CATALOGUE COMPLET
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()

    st.write("---")
    st.subheader("📂 Explorer par catégorie")
    
    # 2. LES TROIS GRANDS BOUTONS DE L'ARBORESCENCE
    col_n, col_c, col_d = st.columns(3)
    with col_n:
        if st.button("🌍 NATIONS", use_container_width=True):
            st.session_state.page = 'arbo'
            st.session_state.chemin = ["🌍 NATIONS"]
            st.rerun()
    with col_c:
        if st.button("🏟️ CLUBS", use_container_width=True):
            st.session_state.page = 'arbo'
            st.session_state.chemin = ["🏟️ CLUBS"]
            st.rerun()
    with col_d:
        if st.button("🎲 DIVERS", use_container_width=True):
            st.session_state.page = 'arbo'
            st.session_state.chemin = ["🎲 DIVERS"]
            st.rerun()

    st.write("---")
    st.subheader("🔍 Outils de recherche")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🛡️ Par Équipe", use_container_width=True):
            st.session_state.page = 'recherche_equipe'
            st.rerun()
    with col_r2:
        if st.button("⚔️ Face-à-Face", use_container_width=True):
            st.session_state.page = 'face_a_face'
            st.rerun()

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'arbo':
    noeud = MENU_ARBO
    for e in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[e]
    
    st.caption(f"📍 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.ed: st.session_state.ed = None
        elif len(st.session_state.chemin) > 1: st.session_state.chemin.pop()
        else: reset_nav()
        st.rerun()

    if isinstance(noeud, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud.keys()):
            with cols[i%3]:
                if st.button(cle, use_container_width=True):
                    st.session_state.chemin.append(cle)
                    st.rerun()
    else:
        if st.session_state.ed is None:
            if isinstance(noeud, str) and "FILTER_" in noeud:
                if "CDM_FINALE" in noeud: m = df['Compétition'].str.contains("Coupe du Monde", na=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False)
                elif "CDM_ELIM" in noeud: m = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False)
                elif "EURO_FINALE" in noeud: m = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False)
                elif "EURO_ELIM" in noeud: m = df['Compétition'].str.contains("Eliminatoires Euro", na=False)
                eds = sorted(df[m]['Compétition'].unique(), reverse=True)
            else:
                target = noeud if isinstance(noeud, list) else [noeud]
                eds = sorted(df[df['Compétition'].isin(target)]['Compétition'].unique(), reverse=True)
            
            if eds:
                st.write("Choisissez une édition :")
                for e in eds:
                    if st.button(e, use_container_width=True):
                        st.session_state.ed = e
                        st.rerun()
            else:
                st.warning("Aucun match trouvé.")
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(st.session_state.ed)
            with c2:
                path_logo_comp = trouver_image(st.session_state.ed)
                if path_logo_comp: st.image(path_logo_comp, width=120)
            afficher_resultats(df[df['Compétition'] == st.session_state.ed])

elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Recherche par Équipe")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Équipe :", toutes)
    if choix: afficher_resultats(df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)])

elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    e1 = st.selectbox("Équipe A", toutes, index=0)
    e2 = st.selectbox("Équipe B", toutes, index=1 if len(toutes)>1 else 0)
    if e1 and e2: afficher_resultats(df[((df['Domicile']==e1)&(df['Extérieur']==e2))|((df['Domicile']==e2)&(df['Extérieur']==e1))])
