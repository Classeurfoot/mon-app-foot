import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# --- STYLE CSS POUR LE CENTRAGE ET LES POLICES ---
st.markdown("""
    <style>
    /* Force le centrage des images dans les colonnes */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    /* Centrage du texte des clubs */
    .club-label {
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 5px;
        display: block;
    }
    /* Style pour le pied de fiche */
    .footer-diffuseur {
        font-size: 16px;
        font-weight: 500;
    }
    .footer-qualite {
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ FONCTIONS DE NETTOYAGE ET RECHERCHE
# ==========================================
def nettoyer_nom_equipe(nom):
    """Normalise le nom pour le comparer au nom du fichier image"""
    if pd.isna(nom): return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def trouver_logo_equipe(nom_equipe, dossier_racine="Logos"):
    """Fouille dans toute l'arborescence récursivement"""
    cible = nettoyer_nom_equipe(nom_equipe)
    if not cible or not os.path.exists(dossier_racine):
        return None
    
    for racine, dirs, fichiers in os.walk(dossier_racine):
        for f in fichiers:
            if f.lower().endswith(".png"):
                nom_fichier = nettoyer_nom_equipe(os.path.splitext(f)[0])
                if nom_fichier == cible:
                    return os.path.join(racine, f)
    return None

# ==========================================
# 🎨 BANQUE DE LOGOS (COMPÉTITIONS)
# ==========================================
LOGOS = {
    "Coupe du Monde 1998": "Logos/Monde/coupedumonde1998.png",
    "Euro 2024": "Logos/Compétitions/euro2024.png",
    "Ligue 1": "Logos/Ligue 1/logo.png",
    "Champions League": "Logos/Compétitions/championsleague.png"
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
                    # --- EN-TÊTE (Date | Stade) ---
                    date_m = row.get('Date', 'Date inconnue')
                    stade_m = row.get('Stade', 'Stade inconnu')
                    st.caption(f"🗓️ {date_m} | 🏟️ {stade_m}")
                    
                    dom = row.get('Domicile', '')
                    ext = row.get('Extérieur', '')
                    score = row.get('Score', '-')
                    
                    # Recherche des logos
                    path_dom = trouver_logo_equipe(dom)
                    path_ext = trouver_logo_equipe(ext)
                    
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    
                    with c_dom:
                        st.markdown(f"<span class='club-label'>{dom}</span>", unsafe_allow_html=True)
                        if path_dom: st.image(path_dom, width=65)
                        
                    with c_score:
                        st.markdown(f"<h1 style='text-align: center; margin-top: 15px;'>{score}</h1>", unsafe_allow_html=True)
                        
                    with c_ext:
                        st.markdown(f"<span class='club-label'>{ext}</span>", unsafe_allow_html=True)
                        if path_ext: st.image(path_ext, width=65)
                    
                    # --- PIED DE FICHE (Diffuseur | Qualité) ---
                    diff = f"📺 {row['Diffuseur']}" if 'Diffuseur' in row and pd.notna(row['Diffuseur']) else ""
                    qual = f"⭐ {row['Qualité']}" if 'Qualité' in row and pd.notna(row['Qualité']) else ""
                    
                    if diff or qual:
                        # Construction du HTML pour gérer les tailles de police différentes
                        diff_html = f"<span class='footer-diffuseur'>{diff}</span>" if diff else ""
                        qual_html = f"<span class='footer-qualite'>{qual}</span>" if qual else ""
                        separator = " &nbsp;&nbsp; | &nbsp;&nbsp; " if diff and qual else ""
                        
                        st.markdown(f"""
                            <div style='text-align: center; color: gray; border-top: 0.5px solid #444; margin-top:10px; padding-top:5px;'>
                                {diff_html}{separator}{qual_html}
                            </div>
                            """, unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION ---
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
# PAGE D'ACCUEIL ET AUTRES
# ==========================================
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

# (Les autres blocs elif catalogue, ephemeride, etc., suivent la même structure de navigation)
elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    auj = datetime.now()
    motif = r'^0?' + str(auj.day) + r'/0?' + str(auj.month) + r'/'
    afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'recherche_date':
    st.header("🔎 Recherche par Date")
    c1, c2 = st.columns(2)
    j = c1.selectbox("Jour", [str(x) for x in range(1, 32)])
    m_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    m_nom = c2.selectbox("Mois", m_list)
    m_num = m_list.index(m_nom) + 1
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
    colA, colB = st.columns(2)
    with colA: eq1 = st.selectbox("Équipe A", toutes, index=0)
    with colB: eq2 = st.selectbox("Équipe B", toutes, index=1 if len(toutes)>1 else 0)
    afficher_resultats(df[((df['Domicile'] == eq1) & (df['Extérieur'] == eq2)) | ((df['Domicile'] == eq2) & (df['Extérieur'] == eq1))])

elif st.session_state.page == 'arborescence':
    noeud = MENU_ARBO
    for etape in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[etape]
        elif isinstance(noeud, list): noeud = etape

    st.caption(f"📂 Chemin : {' > '.join(st.session_state.chemin)}")
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
        for el in noeud:
            if st.button(el, use_container_width=True): st.session_state.chemin.append(el); st.rerun()
    elif isinstance(noeud, str):
        # Logique de filtrage spécifique (CDM, EURO, etc.)
        mask = df['Compétition'].str.contains(noeud, na=False, case=False)
        if st.session_state.edition_choisie is None:
            eds = sorted(df[mask]['Compétition'].dropna().unique(), reverse=True)
            cols = st.columns(4)
            for i, ed in enumerate(eds):
                with cols[i % 4]:
                    if st.button(str(ed), use_container_width=True): st.session_state.edition_choisie = ed; st.rerun()
        else:
            afficher_resultats(df[df['Compétition'] == st.session_state.edition_choisie])
