import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re

# 1. Configuration de la page
st.set_page_config(page_title="Archives Football", layout="wide")

# ==========================================
# ⚙️ FONCTIONS DE NETTOYAGE AUTOMATIQUE
# ==========================================
def nettoyer_nom(nom):
    """Transforme 'Euro 2024' en 'euro2024' ou 'Côte d'Ivoire' en 'cotedivoire'"""
    if pd.isna(nom): return ""
    # 1. Enlever les accents
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    # 2. Tout en minuscules et enlever les caractères spéciaux/espaces
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

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
    
    mode = st.radio("Mode d'affichage :", ["📊 Tableau", "🃏 Fiches"], horizontal=True)
    
    if mode == "📊 Tableau":
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
                    
                    # LOGOS AUTOMATIQUES
                    logo_dom = f"Logos/Equipes/{nettoyer_nom(dom)}.png"
                    logo_ext = f"Logos/Equipes/{nettoyer_nom(ext)}.png"
                    
                    c_dom, c_score, c_ext = st.columns([1, 1.5, 1])
                    
                    with c_dom:
                        if os.path.exists(logo_dom): st.image(logo_dom, use_column_width=True)
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:13px;'>{dom}</p>", unsafe_allow_html=True)
                        
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 10px;'>{score}</h2>", unsafe_allow_html=True)
                        if 'Phase' in row and pd.notna(row['Phase']):
                            st.markdown(f"<p style='text-align: center; color:gray; font-size:12px;'>{row['Phase']}</p>", unsafe_allow_html=True)
                        
                    with c_ext:
                        if os.path.exists(logo_ext): st.image(logo_ext, use_column_width=True)
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:13px;'>{ext}</p>", unsafe_allow_html=True)
                    
                    # Infos secondaires
                    details = []
                    if 'Stade' in row and pd.notna(row['Stade']): details.append(f"🏟️ {row['Stade']}")
                    if 'Diffuseur' in row and pd.notna(row['Diffuseur']): details.append(f"📺 {row['Diffuseur']}")
                    
                    if details:
                        st.markdown(f"<p style='text-align: center; color: gray; font-size:11px;'>{' | '.join(details)}</p>", unsafe_allow_html=True)

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

# ==========================================
# PAGES DE L'APPLICATION
# ==========================================
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()
    
    st.write("---")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        if st.button(f"📅 Ça s'est joué aujourd'hui", use_container_width=True):
            st.session_state.page = 'ephemeride'
            st.rerun()
    with col_date2:
        if st.button("🔎 Recherche par date", use_container_width=True):
            st.session_state.page = 'recherche_date'
            st.rerun()
    
    st.write("---") 
    st.subheader("📂 Explorer par Compétition")
    col_n, col_c, col_d = st.columns(3)
    with col_n:
        if st.button("🌍 NATIONS", use_container_width=True):
            st.session_state.page = 'arborescence'; st.session_state.chemin = ['Nations']; st.rerun()
    with col_c:
        if st.button("🏟️ CLUBS", use_container_width=True):
            st.session_state.page = 'arborescence'; st.session_state.chemin = ['Clubs']; st.rerun()
    with col_d:
        if st.button("🎲 DIVERS", use_container_width=True):
            st.session_state.page = 'arborescence'; st.session_state.chemin = ['Divers']; st.rerun()

    st.write("---")
    st.subheader("🔍 Outils & Statistiques")
    c_o1, c_o2 = st.columns(2)
    with c_o1:
        if st.button("🛡️ Par Équipe", use_container_width=True): st.session_state.page = 'recherche_equipe'; st.rerun()
        if st.button("📊 Statistiques", use_container_width=True): st.session_state.page = 'statistiques'; st.rerun()
    with c_o2:
        if st.button("⚔️ Face-à-Face", use_container_width=True): st.session_state.page = 'face_a_face'; st.rerun()
        if st.button("🕵️ Recherche Avancée", use_container_width=True): st.session_state.page = 'recherche_avancee'; st.rerun()

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    auj = datetime.now()
    st.header(f"📅 Ça s'est joué un {auj.day}/{auj.month}")
    motif = r'^0?' + str(auj.day) + r'/0?' + str(auj.month) + r'/'
    df_ephem = df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)]
    afficher_resultats(df_ephem)

elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Recherche par Équipe")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Équipe :", toutes)
    afficher_resultats(df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)])

elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    e1 = st.selectbox("Équipe A", toutes, index=0)
    e2 = st.selectbox("Équipe B", toutes, index=1 if len(toutes)>1 else 0)
    afficher_resultats(df[((df['Domicile']==e1)&(df['Extérieur']==e2))|((df['Domicile']==e2)&(df['Extérieur']==e1))])

elif st.session_state.page == 'statistiques':
    st.header("📊 Statistiques")
    st.bar_chart(df['Compétition'].value_counts().head(10))

# ==========================================
# PAGE ARBORESCENCE (LOGOS AUTO)
# ==========================================
elif st.session_state.page == 'arborescence':
    noeud = MENU_ARBO
    for etape in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[etape]
    
    st.caption(f"📂 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.edition_choisie: st.session_state.edition_choisie = None
        else:
            st.session_state.chemin.pop()
            if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()

    if isinstance(noeud, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud.keys()):
            with cols[i%3]:
                if st.button(cle, use_container_width=True): st.session_state.chemin.append(cle); st.rerun()
    elif isinstance(noeud, list) or (isinstance(noeud, str) and noeud.startswith("FILTER_")):
        # Gestion des listes et filtres (Phase Finale / Eliminatoires)
        if st.session_state.edition_choisie is None:
            if isinstance(noeud, list): mask = df['Compétition'].isin(noeud)
            else:
                if "CDM_FINALE" in noeud: mask = df['Compétition'].str.contains("Coupe du Monde", na=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False)
                elif "CDM_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False)
                elif "EURO_FINALE" in noeud: mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False)
                elif "EURO_ELIM" in noeud: mask = df['Compétition'].str.contains("Eliminatoires Euro", na=False)
            
            editions = sorted(df[mask]['Compétition'].dropna().unique(), reverse=True)
            cols = st.columns(4)
            for i, ed in enumerate(editions):
                with cols[i%4]:
                    if st.button(ed, use_container_width=True): st.session_state.edition_choisie = ed; st.rerun()
        else:
            # Affichage de l'édition avec son LOGO AUTOMATIQUE
            c1, c2 = st.columns([4, 1])
            with c1: st.header(f"📍 {st.session_state.edition_choisie}")
            with c2:
                # Cherche logos/euro2000.png par exemple
                path_logo = f"Logos/{nettoyer_nom(st.session_state.edition_choisie)}.png"
                if os.path.exists(path_logo): st.image(path_logo, width=100)
            afficher_resultats(df[df['Compétition'] == st.session_state.edition_choisie])
    else:
        # Cas des compétitions directes (ex: Ligue des Nations)
        c1, c2 = st.columns([4, 1])
        with c1: st.header(f"🏆 {noeud}")
        with c2:
            path_logo = f"Logos/{nettoyer_nom(noeud)}.png"
            if os.path.exists(path_logo): st.image(path_logo, width=100)
        afficher_resultats(df[df['Compétition'].str.contains(noeud, na=False, case=False)])
