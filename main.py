import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# ==========================================
# ⚙️ FONCTIONS DE NETTOYAGE ET RECHERCHE
# ==========================================
def nettoyer_nom(nom):
    """Nettoyage pour correspondance fichier/dossier"""
    if pd.isna(nom) or nom == "": return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_logo(nom_recherche, dossier_racine="Logos"):
    """Fouille récursivement dans tous les sous-dossiers pour trouver un .png"""
    cible = nettoyer_nom(nom_recherche)
    if not cible or not os.path.exists(dossier_racine):
        return None
    
    # Variantes de noms pour les fichiers (ex: cdm au lieu de coupedumonde)
    variantes = [cible, cible.replace("coupedumonde", "cdm")]

    for racine, dirs, fichiers in os.walk(dossier_racine):
        for f in fichiers:
            if f.lower().endswith(".png"):
                nom_f = nettoyer_nom(os.path.splitext(f)[0])
                if nom_f in variantes:
                    return os.path.join(racine, f)
    return None

# ==========================================
# 🎨 TA BANQUE DE LOGOS LOCALE (FIXE)
# ==========================================
LOGOS_FIXES = {
    "Euro 2024": "Logos/Monde/Compétitions/normal/JO2024.png",
    "Champions League": "Logos/championsleague.png"
}

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
            df['Date'] = df['Date'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erreur CSV : {e}")
        return pd.DataFrame()

df = load_data()

# --- OUTIL : FICHES DE MATCHS ---
def afficher_resultats(df_res):
    if df_res.empty:
        st.warning("Aucun match trouvé.")
        return
    
    st.metric("Matchs trouvés", len(df_res))
    mode = st.radio("Affichage :", ["📊 Tableau", "🃏 Fiches"], horizontal=True)
    
    if mode == "📊 Tableau":
        st.dataframe(df_res, use_container_width=True)
    else:
        st.write("---")
        cols = st.columns(2)
        for i, (idx, row) in enumerate(df_res.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    # En-tête
                    st.caption(f"🗓️ {row.get('Date','')} | 🏆 {row.get('Compétition','')}")
                    
                    dom, ext, score = row['Domicile'], row['Extérieur'], row.get('Score','-')
                    
                    # Logos (Recherche automatique)
                    logo_dom = trouver_logo(dom)
                    logo_ext = trouver_logo(ext)
                    
                    c1, c2, c3 = st.columns([1, 1.5, 1])
                    with c1:
                        if logo_dom: st.image(logo_dom, width=65) # Taille réduite
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>{dom}</p>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<h1 style='text-align:center; margin-top:10px;'>{score}</h1>", unsafe_allow_html=True)
                    with c3:
                        if logo_ext: st.image(logo_ext, width=65) # Taille réduite
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>{ext}</p>", unsafe_allow_html=True)
                    
                    # Détails (Stade et Diffuseur plus gros)
                    st.markdown("---")
                    stade = f"🏟️ {row['Stade']}" if 'Stade' in row and pd.notna(row['Stade']) else ""
                    diff = f"📺 {row['Diffuseur']}" if 'Diffuseur' in row and pd.notna(row['Diffuseur']) else ""
                    
                    if stade or diff:
                        st.markdown(f"""
                            <p style='text-align: center; font-size: 15px; color: #dcdcdc;'>
                                {stade} &nbsp;&nbsp; | &nbsp;&nbsp; {diff}
                            </p>
                            """, unsafe_allow_html=True)

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'ed' not in st.session_state: st.session_state.ed = None

def reset():
    st.session_state.page = 'accueil'; st.session_state.chemin = []; st.session_state.ed = None

if st.session_state.page != 'accueil':
    if st.sidebar.button("🏠 Accueil"): reset(); st.rerun()

# --- PAGES ---
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'; st.rerun()

    # Éphéméride
    st.write("---")
    auj = datetime.now()
    if st.button(f"📅 Joués un {auj.day}/{auj.month}", use_container_width=True):
        st.session_state.page = 'ephemeride'; st.rerun()
    
    # Catégories
    st.write("---")
    st.subheader("📂 Compétitions")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🌍 NATIONS", use_container_width=True): st.session_state.page = 'arbo'; st.session_state.chemin = ['Nations']; st.rerun()
    with c2:
        if st.button("🏟️ CLUBS", use_container_width=True): st.session_state.page = 'arbo'; st.session_state.chemin = ['Clubs']; st.rerun()
    with c3:
        if st.button("🎲 DIVERS", use_container_width=True): st.session_state.page = 'arbo'; st.session_state.chemin = ['Divers']; st.rerun()

    # Recherche
    st.write("---")
    co1, co2 = st.columns(2)
    with co1:
        if st.button("🛡️ Par Équipe", use_container_width=True): st.session_state.page = 'equipe'; st.rerun()
    with co2:
        if st.button("⚔️ Face-à-Face", use_container_width=True): st.session_state.page = 'f2f'; st.rerun()

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    auj = datetime.now()
    motif = r'^0?' + str(auj.day) + r'/0?' + str(auj.month) + r'/'
    afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'equipe':
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    eq = st.selectbox("Équipe :", toutes)
    afficher_resultats(df[(df['Domicile']==eq) | (df['Extérieur']==eq)])

elif st.session_state.page == 'f2f':
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    e1 = st.selectbox("Équipe A", toutes, index=0)
    e2 = st.selectbox("Équipe B", toutes, index=1)
    afficher_resultats(df[((df['Domicile']==e1)&(df['Extérieur']==e2)) | ((df['Domicile']==e2)&(df['Extérieur']==e1))])

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
        cols = st.columns(3)
        for i, cle in enumerate(noeud.keys()):
            with cols[i%3]:
                if st.button(cle, use_container_width=True): st.session_state.chemin.append(cle); st.rerun()
    else:
        if st.session_state.ed is None:
            if isinstance(noeud, list): mask = df['Compétition'].isin(noeud)
            else:
                if "CDM_FINALE" in noeud: mask = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
                elif "CDM_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False, case=False)
                elif "EURO_FINALE" in noeud: mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
                elif "EURO_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Euro", na=False, case=False)
                else: mask = df['Compétition'].str.contains(noeud, na=False, case=False)
            
            eds = sorted(df[mask]['Compétition'].dropna().unique(), reverse=True)
            for e in eds:
                if st.button(e, use_container_width=True): st.session_state.ed = e; st.rerun()
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(st.session_state.ed)
            with c2:
                # Logo de la compétition
                l_comp = LOGOS_FIXES.get(st.session_state.ed) or trouver_logo(st.session_state.ed)
                if l_comp: st.image(l_comp, width=100)
            afficher_resultats(df[df['Compétition'] == st.session_state.ed])
