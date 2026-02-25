import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# 2. Le Cerveau de l'application (Dictionnaire de l'arborescence)
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
        st.error(f"Erreur de lecture du fichier : {e}")
        return pd.DataFrame()

df = load_data()
colonnes_possibles = ['Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur']
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
    
    # Bouton principal
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()
    
    st.write("---") 
    st.subheader("📂 Explorer par Compétition")
    
    # Ligne 1 : Arborescence
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌍 NATIONS", use_container_width=True):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Nations']
            st.rerun()
    with col2:
        if st.button("🏟️ CLUBS", use_container_width=True):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Clubs']
            st.rerun()
    with col3:
        if st.button("🎲 DIVERS", use_container_width=True):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Divers']
            st.rerun()

    st.write("---")
    st.subheader("🔍 Outils de Recherche")

    # Ligne 2 : Outils Spécifiques
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("🛡️ Par Équipe", use_container_width=True):
            st.session_state.page = 'recherche_equipe'
            st.rerun()
    with col5:
        if st.button("⚔️ Face-à-Face", use_container_width=True):
            st.session_state.page = 'face_a_face'
            st.rerun()
    with col6:
        if 'Stade' in df.columns:
            if st.button("📍 Par Stade", use_container_width=True):
                st.session_state.page = 'recherche_stade'
                st.rerun()

# ==========================================
# PAGE CATALOGUE
# ==========================================
elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    st.dataframe(df[colonnes_presentes], use_container_width=True, height=800)

# ==========================================
# PAGES DE RECHERCHE SPÉCIFIQUE
# ==========================================
elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Recherche par Équipe")
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Sélectionne une équipe :", toutes_les_equipes)
    df_filtre = df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)]
    st.metric("Matchs trouvés", len(df_filtre))
    st.dataframe(df_filtre[colonnes_presentes], use_container_width=True, height=600)

elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    c1, c2 = st.columns(2)
    with c1: eq1 = st.selectbox("Équipe A", toutes_les_equipes, index=0)
    with c2: eq2 = st.selectbox("Équipe B", toutes_les_equipes, index=1 if len(toutes_les_equipes)>1 else 0)
    
    df_face = df[((df['Domicile'] == eq1) & (df['Extérieur'] == eq2)) | 
                 ((df['Domicile'] == eq2) & (df['Extérieur'] == eq1))]
    st.metric("Confrontations trouvées", len(df_face))
    st.dataframe(df_face[colonnes_presentes], use_container_width=True, height=600)

elif st.session_state.page == 'recherche_stade':
    st.header("📍 Recherche par Stade")
    tous_les_stades = sorted(df['Stade'].dropna().unique())
    stade_choisi = st.selectbox("Sélectionne un stade :", tous_les_stades)
    df_stade = df[df['Stade'] == stade_choisi]
    st.metric("Matchs joués dans ce stade", len(df_stade))
    st.dataframe(df_stade[colonnes_presentes], use_container_width=True, height=600)

# ==========================================
# PAGE ARBORESCENCE (NAVIGATION DYNAMIQUE)
# ==========================================
elif st.session_state.page == 'arborescence':
    
    # 1. On trouve le dossier actuel
    noeud_actuel = MENU_ARBO
    for etape in st.session_state.chemin:
        if isinstance(noeud_actuel, dict):
            noeud_actuel = noeud_actuel[etape]
        elif isinstance(noeud_actuel, list):
            noeud_actuel = etape

    # 2. Fil d'Ariane
    fil_ariane = " > ".join(st.session_state.chemin)
    st.caption(f"📂 Chemin : {fil_ariane}")
    
    if st.button("⬅️ Retour"):
        if st.session_state.edition_choisie is not None:
            st.session_state.edition_choisie = None
        else:
            st.session_state.chemin.pop()
            if len(st.session_state.chemin) == 0:
                st.session_state.page = 'accueil'
        st.rerun()
        
    st.divider()
    
    # CAS 1 : C'est un Dictionnaire (Sous-menus)
    if isinstance(noeud_actuel, dict):
        st.subheader("Choisissez une catégorie :")
        cols = st.columns(2)
        for i, cle in enumerate(noeud_actuel.keys()):
            if cols[i % 2].button(cle, use_container_width=True):
                st.session_state.chemin.append(cle)
                st.rerun()

    # CAS 2 : C'est une Liste (Liste de compétitions)
    elif isinstance(noeud_actuel, list):
        st.subheader("Choisissez une compétition :")
        cols = st.columns(2)
        for i, element in enumerate(noeud_actuel):
            if cols[i % 2].button(element, use_container_width=True):
                st.session_state.chemin.append(element)
                st.rerun()

    # CAS 3 : C'est un Texte (Tableau final ou Choix d'Édition)
    elif isinstance(noeud_actuel, str):
        
        # Filtres Spéciaux (Phase finale vs Éliminatoires)
        if noeud_actuel.startswith("FILTER_"):
            if noeud_actuel == "FILTER_CDM_FINALE":
                mask = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
            elif noeud_actuel == "FILTER_CDM_ELIM":
                mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False, case=False)
            elif noeud_actuel == "FILTER_EURO_FINALE":
                mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False, regex=True) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
            elif noeud_actuel == "FILTER_EURO_ELIM":
                mask = df['Compétition'].str.contains("Eliminatoires Euro|Eliminatoires Championnat d'Europe", na=False, case=False, regex=True)
            
            if st.session_state.edition_choisie is None:
                editions = sorted(df[mask]['Compétition'].dropna().unique(), reverse=True)
                if editions:
                    st.subheader("🗓️ Choisissez l'édition :")
                    cols = st.columns(3)
                    for i, ed in enumerate(editions):
                        if cols[i % 3].button(str(ed), use_container_width=True):
                            st.session_state.edition_choisie = ed
                            st.rerun()
                else:
                    st.warning("Aucune édition trouvée pour ce choix.")
            else:
                st.header(f"📍 {st.session_state.edition_choisie}")
                df_final = df[df['Compétition'] == st.session_state.edition_choisie]
                st.metric("Matchs trouvés", len(df_final))
                st.dataframe(df_final[colonnes_presentes], use_container_width=True, height=600)
        
        # Filtre Standard
        else:
            st.header(f"🏆 {noeud_actuel}")
            mask = df['Compétition'].str.contains(noeud_actuel, na=False, case=False)
            df_final = df[mask]
            
            if not df_final.empty:
                st.metric("Matchs trouvés", len(df_final))
                st.dataframe(df_final[colonnes_presentes], use_container_width=True, height=600)
            else:
                st.warning(f"Aucun match trouvé pour : {noeud_actuel}")
