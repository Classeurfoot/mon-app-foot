import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# CSS pour forcer le centrage des images et des blocs d'équipe
st.markdown("""
    <style>
    /* Centre toutes les images du site */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    /* Style pour les noms de clubs centrés */
    .club-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .club-name {
        font-weight: bold;
        font-size: 16px;
        display: block;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ FONCTIONS DE NETTOYAGE ET RECHERCHE
# ==========================================
def nettoyer_nom_equipe(nom):
    """Transforme 'Côte d'Ivoire' en 'cotedivoire' pour trouver l'image"""
    if pd.isna(nom) or nom == "": return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_logo_equipe(nom_equipe, dossier_racine="Logos"):
    """Fouille récursivement dans tous les sous-dossiers pour trouver le logo .png"""
    cible = nettoyer_nom_equipe(nom_equipe)
    if not cible or not os.path.exists(dossier_racine):
        return None
    
    for racine, dirs, fichiers in os.walk(dossier_racine):
        for f in fichiers:
            if f.lower().endswith(".png"):
                if nettoyer_nom_equipe(os.path.splitext(f)[0]) == cible:
                    return os.path.join(racine, f)
    return None

# ==========================================
# 🎨 BANQUE DE LOGOS (COMPÉTITIONS)
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
# 🧠 ARBORESCENCE DES MENUS
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
        "Tournois internationaux clubs": {
            "Coupe Intercontinentale": "Coupe intercontinentale",
            "Coupe du Monde des clubs de la FIFA": "Coupe du Monde des clubs de la FIFA",
            "Coupe du Monde des Clubs 2025": "Coupe du Monde des Clubs 2025"
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
            dates_num = pd.to_numeric(df['Date'], errors='coerce')
            masque = dates_num.notna()
            df.loc[masque, 'Date'] = pd.to_datetime(dates_num[masque], unit='D', origin='1899-12-30').dt.strftime('%d/%m/%Y')
            df['Date'] = df['Date'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erreur CSV : {e}")
        return pd.DataFrame()

df = load_data()
colonnes_possibles = ['Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Qualité']
colonnes_presentes = [c for c in colonnes_possibles if c in df.columns]

# --- OUTIL : FICHES DE MATCHS (LOGOS CENTRÉS SOUS LE NOM) ---
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucun match trouvé.")
        return
        
    st.metric("Matchs trouvés", len(df_resultats))
    mode = st.radio("Affichage :", ["📊 Tableau", "🃏 Fiches"], horizontal=True)
    
    if mode == "📊 Tableau":
        st.dataframe(df_resultats[colonnes_presentes], use_container_width=True)
    else:
        st.write("---")
        cols = st.columns(2)
        for i, (index, row) in enumerate(df_resultats.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    # En-tête de la fiche
                    st.caption(f"🗓️ {row.get('Date','')} | 🏆 {row.get('Compétition','')}")
                    
                    dom, ext, score = row['Domicile'], row['Extérieur'], row.get('Score','-')
                    path_dom, path_ext = trouver_logo_equipe(dom), trouver_logo_equipe(ext)
                    
                    # Disposition [NOM+LOGO] | [SCORE] | [NOM+LOGO]
                    c1, c2, c3 = st.columns([1, 1, 1])
                    
                    with c1:
                        st.markdown(f"<div class='club-container'><span class='club-name'>{dom}</span></div>", unsafe_allow_html=True)
                        if path_dom:
                            st.image(path_dom, width=70)
                        
                    with c2:
                        st.markdown(f"<h1 style='text-align: center; margin-top: 25px;'>{score}</h1>", unsafe_allow_html=True)
                        
                    with c3:
                        st.markdown(f"<div class='club-container'><span class='club-name'>{ext}</span></div>", unsafe_allow_html=True)
                        if path_ext:
                            st.image(path_ext, width=70)
                    
                    # Détails Stade / Diffuseur
                    stade = f"🏟️ {row['Stade']}" if 'Stade' in row and pd.notna(row['Stade']) else ""
                    diff = f"📺 {row['Diffuseur']}" if 'Diffuseur' in row and pd.notna(row['Diffuseur']) else ""
                    
                    if stade or diff:
                        st.markdown(f"""
                            <p style='text-align: center; font-size: 14px; color: gray; border-top: 0.5px solid #444; padding-top: 10px;'>
                                {stade} &nbsp;&nbsp; | &nbsp;&nbsp; {diff}
                            </p>
                            """, unsafe_allow_html=True)

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'ed' not in st.session_state: st.session_state.ed = None

def go_home():
    st.session_state.page = 'accueil'; st.session_state.chemin = []; st.session_state.ed = None

if st.session_state.page != 'accueil':
    if st.sidebar.button("🏠 Menu Principal", use_container_width=True):
        go_home(); st.rerun()

# ==========================================
# PAGES
# ==========================================
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'; st.rerun()

    auj = datetime.now()
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"📅 Joués un {auj.day}/{auj.month}", use_container_width=True):
            st.session_state.page = 'ephemeride'; st.rerun()
    with c2:
        if st.button("🔎 Recherche par date", use_container_width=True):
            st.session_state.page = 'recherche_date'; st.rerun()
    
    st.write("---")
    st.subheader("📂 Compétitions")
    cn, cc, cd = st.columns(3)
    with cn:
        if st.button("🌍 NATIONS", use_container_width=True): st.session_state.page = 'arbo'; st.session_state.chemin = ['Nations']; st.rerun()
    with cc:
        if st.button("🏟️ CLUBS", use_container_width=True): st.session_state.page = 'arbo'; st.session_state.chemin = ['Clubs']; st.rerun()
    with cd:
        if st.button("🎲 DIVERS", use_container_width=True): st.session_state.page = 'arbo'; st.session_state.chemin = ['Divers']; st.rerun()

    st.write("---")
    st.subheader("🔍 Outils")
    co1, co2 = st.columns(2)
    with co1:
        if st.button("🛡️ Par Équipe", use_container_width=True): st.session_state.page = 'equipe'; st.rerun()
    with co2:
        if st.button("⚔️ Face-à-Face", use_container_width=True): st.session_state.page = 'f2f'; st.rerun()

# --- PAGES SECONDAIRES (Logique identique à la référence) ---
elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    auj = datetime.now()
    motif = r'^0?' + str(auj.day) + r'/0?' + str(auj.month) + r'/'
    afficher_resultats(df[df['Date'].str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'recherche_date':
    st.header("🔎 Date spécifique")
    c1, c2 = st.columns(2)
    j = c1.selectbox("Jour", [str(i) for i in range(1, 32)])
    m_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    m_nom = c2.selectbox("Mois", m_list)
    motif = r'^0?' + str(j) + r'/0?' + str(m_list.index(m_nom)+1) + r'/'
    afficher_resultats(df[df['Date'].str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'equipe':
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).unique())
    eq = st.selectbox("Équipe", toutes)
    afficher_resultats(df[(df['Domicile']==eq) | (df['Extérieur']==eq)])

elif st.session_state.page == 'f2f':
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).unique())
    e1 = st.selectbox("Équipe A", toutes, index=0)
    e2 = st.selectbox("Équipe B", toutes, index=1)
    afficher_resultats(df[((df['Domicile']==e1)&(df['Extérieur']==e2)) | ((df['Domicile']==e2)&(df['Extérieur']==e1))])

elif st.session_state.page == 'arbo':
    noeud = MENU_ARBO
    for e in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[e]
        elif isinstance(noeud, list): noeud = e

    st.caption(f"📍 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.ed: st.session_state.ed = None
        else:
            st.session_state.chemin.pop()
            if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()
    st.divider()

    if isinstance(noeud, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud.keys()):
            with cols[i%3]:
                if st.button(cle, use_container_width=True): st.session_state.chemin.append(cle); st.rerun()
    elif isinstance(noeud, list):
        for el in noeud:
            if st.button(el, use_container_width=True): st.session_state.chemin.append(el); st.rerun()
    else:
        if st.session_state.ed is None:
            if "FILTER_" in noeud:
                if "CDM_FINALE" in noeud: mask = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
                elif "CDM_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False, case=False)
                elif "EURO_FINALE" in noeud: mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
                elif "EURO_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Euro", na=False, case=False)
                eds = sorted(df[mask]['Compétition'].unique(), reverse=True)
                cols = st.columns(4)
                for i, ed in enumerate(eds):
                    with cols[i%4]:
                        if st.button(ed, use_container_width=True): st.session_state.ed = ed; st.rerun()
            else:
                afficher_resultats(df[df['Compétition'].str.contains(noeud, na=False, case=False)])
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(st.session_state.ed)
            with c2:
                if st.session_state.ed in LOGOS: st.image(LOGOS[st.session_state.ed], width=100)
            afficher_resultats(df[df['Compétition'] == st.session_state.ed])
