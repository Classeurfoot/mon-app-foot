import streamlit as st
import pandas as pd

# 1. Configuration de base
st.set_page_config(page_title="App Foot", layout="wide")
st.title("⚽ Base de Données Football")

# 2. Fonction de chargement et de nettoyage
@st.cache_data
def load_data():
    df = pd.read_csv("matchs.csv", sep=None, engine="python")
    df = df.dropna(subset=['Domicile', 'Extérieur'])
    
    # --- CORRECTION DES DATES EXCEL ---
    if 'Date' in df.columns:
        dates_numeriques = pd.to_numeric(df['Date'], errors='coerce')
        masque_excel = dates_numeriques.notna()
        dates_converties = pd.to_datetime(dates_numeriques[masque_excel], unit='D', origin='1899-12-30')
        df.loc[masque_excel, 'Date'] = dates_converties.dt.strftime('%d/%m/%Y')
    
    return df

try:
    df = load_data()
    
    # Listes pour nos menus déroulants
    toutes_les_equipes = pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique()
    toutes_les_equipes.sort()
    
    toutes_les_competitions = df['Compétition'].dropna().unique()
    toutes_les_competitions.sort()

    # --- CRÉATION DES ONGLETS ---
    tab1, tab2, tab3 = st.tabs(["⚔️ Face-à-Face", "🛡️ Par Équipe", "🏆 Par Compétition"])

    # La liste des colonnes idéales qu'on veut afficher partout
    colonnes_ideales = ['Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Langue','Qualité']
    # On vérifie qu'elles existent bien dans le fichier pour éviter les erreurs
    colonnes_a_afficher = [c for c in colonnes_ideales if c in df.columns]

    # ==========================================
    # ONGLET 1 : FACE-A-FACE
    # ==========================================
    with tab1:
        st.subheader("🔍 Rechercher une confrontation directe")
        col1, col2 = st.columns(2)
        with col1:
            index_1 = list(toutes_les_equipes).index("PSG") if "PSG" in toutes_les_equipes else 0
            equipe1 = st.selectbox("Équipe 1 :", toutes_les_equipes, index=index_1, key="eq1")
        with col2:
            index_2 = list(toutes_les_equipes).index("Marseille") if "Marseille" in toutes_les_equipes else 1
            equipe2 = st.selectbox("Équipe 2 :", toutes_les_equipes, index=index_2, key="eq2")

        masque_faf = ((df['Domicile'] == equipe1) & (df['Extérieur'] == equipe2)) | \
                     ((df['Domicile'] == equipe2) & (df['Extérieur'] == equipe1))
        df_faf = df[masque_faf]

        if len(df_faf) > 0:
            st.success(f"✅ {len(df_faf)} matchs trouvés entre {equipe1} et {equipe2} !")
            st.dataframe(df_faf[colonnes_a_afficher], use_container_width=True)
        else:
            st.warning("Aucun match trouvé.")

    # ==========================================
    # ONGLET 2 : RECHERCHE PAR ÉQUIPE
    # ==========================================
    with tab2:
        st.subheader("🛡️ Historique d'une équipe")
        equipe_seule = st.selectbox("Sélectionne une équipe :", toutes_les_equipes, key="eq_seule")
        
        df_equipe = df[(df['Domicile'] == equipe_seule) | (df['Extérieur'] == equipe_seule)]
        
        st.success(f"✅ {len(df_equipe)} matchs trouvés pour {equipe_seule} dans la base de données.")
        st.dataframe(df_equipe[colonnes_a_afficher], use_container_width=True)

    # ==========================================
    # ONGLET 3 : RECHERCHE PAR COMPÉTITION
    # ==========================================
    with tab3:
        st.subheader("🏆 Historique d'une compétition")
        competition_seule = st.selectbox("Sélectionne une compétition :", toutes_les_competitions, key="comp_seule")
        
        df_comp = df[df['Compétition'] == competition_seule]
        
        st.success(f"✅ {len(df_comp)} matchs trouvés pour la compétition : {competition_seule}.")
        st.dataframe(df_comp[colonnes_a_afficher], use_container_width=True)

except FileNotFoundError:
    st.error("Le fichier 'matchs.csv' est introuvable.")