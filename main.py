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
    if pd.isna(nom) or nom == "": return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_logo_equipe(nom_equipe, dossier_racine="Logos/Equipes"):
    """Fouille dans tous les sous-dossiers de Logos/Equipes pour trouver le bon .png"""
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
# 🎨 TA BANQUE DE LOGOS LOCALE (COMPÉTITIONS)
# ==========================================
LOGOS = {
    "Coupe du Monde 1998": "Logos/coupedumonde1998.png",
    "Coupe du Monde 1978": "Logos/coupedumonde1978.png",
    "Coupe du Monde 1982": "Logos/cdm1982.png",
    "Coupe du Monde 1986": "Logos/cdm1986.png",
    "Coupe du Monde 1990": "Logos/cdm1990.png",
    "Coupe du Monde 1994": "Logos/cdm1994.png",
    "Coupe du Monde 2002": "Logos/coupedumonde2002.png",
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
    "Euro 2024": "Logos/JO2024.png", # Ajusté selon ton historique GitHub
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
                    date_m = row.get('Date', 'Date inconnue')
                    comp_m = row.get('Compétition', 'Compétition inconnue')
                    st.caption(f"🗓️ {date_m} | 🏆 {comp_m}")
                    
                    dom = row.get('Domicile', '')
                    ext = row.get('Extérieur', '')
                    score = row.get('Score', '-')
                    
                    # RECHERCHE FLEXIBLE DES LOGOS D'EQUIPES
                    logo_dom = trouver_logo_equipe(dom)
                    logo_ext = trouver_logo_equipe(ext)
                    
                    c_dom, c_score, c_ext = st.columns([1, 2, 1])
                    with c_dom:
                        if logo_dom: st.image(logo_dom, use_column_width=True)
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:14px;'>{dom}</p>", unsafe_allow_html=True)
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{score}</h2>", unsafe_allow_html=True)
                    with c_ext:
                        if logo_ext: st.image(logo_ext, use_column_width=True)
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:14px;'>{ext}</p>", unsafe_allow_html=True)
                    
                    details = []
                    if 'Stade' in row and pd.notna(row['Stade']): details.append(f"🏟️ {row['Stade']}")
                    if 'Diffuseur' in row and pd.notna(row['Diffuseur']): details.append(f"📺 {row['Diffuseur']}")
                    if details:
                        st.markdown(f"<p style='text-align: center; color: gray; font-size:12px;'>{' | '.join(details)}</p>", unsafe_allow_html=True)

# --- NAVIGATION ---
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

# --- PAGES ---
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()
    
    aujourdhui = datetime.now()
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    st.write("---")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        if st.button(f"📅 Ça s'est joué aujourd'hui ({aujourdhui.day} {mois_fr[aujourdhui.month-1]})", use_container_width=True):
            st.session_state.page = 'ephemeride'; st.rerun()
    with col_date2:
        if st.button("🔎 Recherche par date", use_container_width=True):
            st.session_state.page = 'recherche_date'; st.rerun()
    
    st.write("---") 
    st.subheader("📂 Explorer par Compétition")
    c_n, c_c, c_d = st.columns(3)
    with c_n: 
        if st.button("🌍 NATIONS", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Nations']; st.rerun()
    with c_c: 
        if st.button("🏟️ CLUBS", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Clubs']; st.rerun()
    with c_d: 
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

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    auj = datetime.now()
    st.header(f"📅 Joués un {auj.day}/{auj.month}")
    motif = r'^0?' + str(auj.day) + r'/0?' + str(auj.month) + r'/'
    afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'recherche_date':
    st.header("🔎 Recherche par Date")
    c1, c2 = st.columns(2)
    j = c1.selectbox("Jour", [str(i) for i in range(1, 32)])
    m_nom = c2.selectbox("Mois", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
    m_num = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"].index(m_nom) + 1
    motif = r'^0?' + str(j) + r'/0?' + str(m_num) + r'/'
    afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Recherche par Équipe")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Sélectionne une équipe :", toutes)
    afficher_resultats(df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)])

elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    e1 = st.selectbox("Équipe A", toutes, index=0)
    e2 = st.selectbox("Équipe B", toutes, index=1 if len(toutes)>1 else 0)
    afficher_resultats(df[((df['Domicile'] == e1) & (df['Extérieur'] == e2)) | ((df['Domicile'] == e2) & (df['Extérieur'] == e1))])

elif st.session_state.page == 'statistiques':
    st.header("📊 Statistiques")
    st.bar_chart(df['Compétition'].value_counts().head(10))

elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    # Logique simplifiée pour l'exemple
    st.info("Utilisez les filtres ci-dessus pour affiner")
    afficher_resultats(df)

# ==========================================
# PAGE ARBORESCENCE (NAVIGATION)
# ==========================================
elif st.session_state.page == 'arborescence':
    noeud_actuel = MENU_ARBO
    for etape in st.session_state.chemin:
        if isinstance(noeud_actuel, dict): noeud_actuel = noeud_actuel[etape]

    st.caption(f"📂 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.edition_choisie: st.session_state.edition_choisie = None
        else:
            st.session_state.chemin.pop()
            if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()

    if isinstance(noeud_actuel, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud_actuel.keys()):
            with cols[i % 3]:
                if st.button(cle, use_container_width=True):
                    st.session_state.chemin.append(cle); st.rerun()

    elif isinstance(noeud_actuel, list) or (isinstance(noeud_actuel, str) and noeud_actuel.startswith("FILTER_")):
        if st.session_state.edition_choisie is None:
            if isinstance(noeud_actuel, list): mask = df['Compétition'].isin(noeud_actuel)
            else:
                if "CDM_FINALE" in noeud_actuel: mask = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
                elif "CDM_ELIM" in noeud_actuel: mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False, case=False)
                elif "EURO_FINALE" in noeud_actuel: mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
                elif "EURO_ELIM" in noeud_actuel: mask = df['Compétition'].str.contains("Eliminatoires Euro", na=False, case=False)
            
            eds = sorted(df[mask]['Compétition'].dropna().unique(), reverse=True)
            cols = st.columns(4)
            for i, ed in enumerate(eds):
                with cols[i % 4]:
                    if st.button(str(ed), use_container_width=True): st.session_state.edition_choisie = ed; st.rerun()
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(f"📍 {st.session_state.edition_choisie}")
            with c2:
                # Utilisation de ta liste LOGOS fixe
                path = LOGOS.get(st.session_state.edition_choisie)
                if path and os.path.exists(path): st.image(path, width=100)
            afficher_resultats(df[df['Compétition'] == st.session_state.edition_choisie])
    
    elif isinstance(noeud_actuel, str):
        c1, c2 = st.columns([4, 1])
        with c1: st.header(f"🏆 {noeud_actuel}")
        with c2:
            path = LOGOS.get(noeud_actuel)
            if path and os.path.exists(path): st.image(path, width=100)
        afficher_resultats(df[df['Compétition'].str.contains(noeud_actuel, na=False, case=False)])
