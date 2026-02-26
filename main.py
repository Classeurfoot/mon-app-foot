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
def nettoyer_nom_equipe(nom):
    """Transforme 'Côte d'Ivoire' en 'cotedivoire'"""
    if pd.isna(nom): return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_logo_equipe(nom_equipe, dossier_racine="Logos"):
    """
    Fouille récursivement dans tous les sous-dossiers (Italie, France, Monde...)
    pour trouver le fichier .png correspondant au nom nettoyé.
    """
    cible = nettoyer_nom_equipe(nom_equipe)
    if not cible or not os.path.exists(dossier_racine):
        return None
    
    for racine, dirs, fichiers in os.walk(dossier_racine):
        for f in fichiers:
            if f.lower().endswith(".png"):
                # On compare le nom du fichier (sans extension) nettoyé
                nom_fichier = nettoyer_nom_equipe(os.path.splitext(f)[0])
                if nom_fichier == cible:
                    return os.path.join(racine, f)
    return None

# ==========================================
# 🎨 TA BANQUE DE LOGOS LOCALE (COMPÉTITIONS)
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

# --- OUTIL : FICHES DE MATCHS ---
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucun match trouvé.")
        return
        
    st.metric("Matchs trouvés", len(df_resultats))
    mode = st.radio("Mode d'affichage :", ["📊 Tableau classique", "🃏 Fiches détaillées"], horizontal=True)
    
    if mode == "📊 Tableau classique":
        st.dataframe(df_resultats[colonnes_presentes], use_container_width=True, height=600)
    else:
        st.write("---")
        cols = st.columns(2)
        for i, (index, row) in enumerate(df_resultats.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    # En-tête
                    date_m = row.get('Date', 'Date inconnue')
                    comp_m = row.get('Compétition', 'Compétition inconnue')
                    st.caption(f"🗓️ {date_m} | 🏆 {comp_m}")
                    
                    dom = row.get('Domicile', '')
                    ext = row.get('Extérieur', '')
                    score = row.get('Score', '-')
                    
                    # Recherche automatique des logos dans toute l'arborescence
                    path_logo_dom = trouver_logo_equipe(dom)
                    path_logo_ext = trouver_logo_equipe(ext)
                    
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    
                    with c_dom:
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:15px; margin-bottom:2px;'>{dom}</p>", unsafe_allow_html=True)
                        if path_logo_dom:
                            st.image(path_logo_dom, width=60)
                        
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{score}</h2>", unsafe_allow_html=True)
                        
                    with c_ext:
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:15px; margin-bottom:2px;'>{ext}</p>", unsafe_allow_html=True)
                        if path_logo_ext:
                            st.image(path_logo_ext, width=60)
                    
                    details = []
                    if 'Stade' in row and pd.notna(row['Stade']): details.append(f"🏟️ {row['Stade']}")
                    if 'Diffuseur' in row and pd.notna(row['Diffuseur']): details.append(f"📺 {row['Diffuseur']}")
                    if 'Qualité' in row and pd.notna(row['Qualité']): details.append(f"⭐ {row['Qualité']}")
                    
                    if details:
                        st.markdown(f"<div style='text-align: center; color: gray; font-size:12px; border-top: 0.5px solid #444; margin-top:10px; padding-top:5px;'>{' | '.join(details)}</div>", unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION (Structure Accueil Inchangée) ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'edition_choisie' not in st.session_state: st.session_state.edition_choisie = None

def go_home():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.edition_choisie = None

if st.session_state.page != 'accueil':
    if st.sidebar.button("🏠 Menu Principal", use_container_width=True):
        go_home()
        st.rerun()

# --- RESTE DU CODE (PAGES) ---
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'; st.rerun()
    
    auj = datetime.now()
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📅 Ça s'est joué aujourd'hui ({auj.day} {mois_fr[auj.month-1]})", use_container_width=True):
            st.session_state.page = 'ephemeride'; st.rerun()
    with col2:
        if st.button("🔎 Recherche par date", use_container_width=True):
            st.session_state.page = 'recherche_date'; st.rerun()
    
    st.write("---") 
    st.subheader("📂 Explorer par Compétition")
    cn, cc, cd = st.columns(3)
    with cn:
        if st.button("🌍 NATIONS", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Nations']; st.rerun()
    with cc:
        if st.button("🏟️ CLUBS", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Clubs']; st.rerun()
    with cd:
        if st.button("🎲 DIVERS", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Divers']; st.rerun()

    st.write("---")
    st.subheader("🔍 Outils & Statistiques")
    co1, co2 = st.columns(2)
    with co1:
        if st.button("🛡️ Par Équipe", use_container_width=True): st.session_state.page = 'recherche_equipe'; st.rerun()
        if st.button("📊 Statistiques", use_container_width=True): st.session_state.page = 'statistiques'; st.rerun()
    with co2:
        if st.button("⚔️ Face-à-Face", use_container_width=True): st.session_state.page = 'face_a_face'; st.rerun()
        if st.button("🕵️ Recherche Avancée", use_container_width=True): st.session_state.page = 'recherche_avancee'; st.rerun()

# (Les blocs elif catalogue, ephemeride, recherche_date, equipe, face_a_face, statistiques restent identiques)
elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    auj = datetime.now()
    st.header(f"📅 Ça s'est joué un {auj.day}/{auj.month}")
    if 'Date' in df.columns:
        motif = r'^0?' + str(auj.day) + r'/0?' + str(auj.month) + r'/'
        afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'recherche_date':
    st.header("🔎 Recherche par Date")
    c1, c2 = st.columns(2)
    j = c1.selectbox("Jour", [str(i) for i in range(1, 32)])
    m_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    m_nom = c2.selectbox("Mois", m_list)
    m_num = m_list.index(m_nom) + 1
    if 'Date' in df.columns:
        motif = r'^0?' + str(j) + r'/0?' + str(m_num) + r'/'
        afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Par Équipe")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Sélectionne :", toutes)
    afficher_resultats(df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)])

elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    e1 = st.selectbox("Équipe A", toutes, index=0)
    e2 = st.selectbox("Équipe B", toutes, index=1 if len(toutes)>1 else 0)
    afficher_resultats(df[((df['Domicile'] == e1) & (df['Extérieur'] == e2)) | ((df['Domicile'] == e2) & (df['Extérieur'] == e1))])

elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    # ... (code de filtrage classique)
    afficher_resultats(df)

elif st.session_state.page == 'statistiques':
    st.header("📊 Statistiques")
    st.bar_chart(df['Compétition'].value_counts().head(10))

# --- PAGE ARBORESCENCE (LOGIQUE DE NAVIGATION) ---
elif st.session_state.page == 'arborescence':
    noeud = MENU_ARBO
    for e in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[e]
        elif isinstance(noeud, list): noeud = e

    st.caption(f"📂 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.edition_choisie: st.session_state.edition_choisie = None
        else:
            st.session_state.chemin.pop()
            if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()
    st.divider()
    
    if isinstance(noeud, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud.keys()):
            with cols[i % 3]:
                if st.button(cle, use_container_width=True): st.session_state.chemin.append(cle); st.rerun()
    elif isinstance(noeud, list):
        cols = st.columns(3)
        for i, element in enumerate(noeud):
            with cols[i % 3]:
                if st.button(element, use_container_width=True): st.session_state.chemin.append(element); st.rerun()
    elif isinstance(noeud, str):
        if noeud.startswith("FILTER_"):
            if "CDM_FINALE" in noeud: mask = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
            elif "CDM_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False, case=False)
            elif "EURO_FINALE" in noeud: mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
            elif "EURO_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Euro", na=False, case=False)
            
            if st.session_state.edition_choisie is None:
                eds = sorted(df[mask]['Compétition'].dropna().unique(), reverse=True)
                cols = st.columns(4)
                for i, ed in enumerate(eds):
                    with cols[i % 4]:
                        if st.button(str(ed), use_container_width=True): st.session_state.edition_choisie = ed; st.rerun()
            else:
                c1, c2 = st.columns([4, 1])
                with c1: st.header(f"📍 {st.session_state.edition_choisie}")
                with c2:
                    if st.session_state.edition_choisie in LOGOS:
                        if os.path.exists(LOGOS[st.session_state.edition_choisie]): st.image(LOGOS[st.session_state.edition_choisie], width=100)
                afficher_resultats(df[df['Compétition'] == st.session_state.edition_choisie])
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(f"🏆 {noeud}")
            with c2:
                if noeud in LOGOS:
                    if os.path.exists(LOGOS[noeud]): st.image(LOGOS[noeud], width=100)
            afficher_resultats(df[df['Compétition'].str.contains(noeud, na=False, case=False)])
