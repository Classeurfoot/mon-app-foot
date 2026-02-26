import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# ==========================================
# 🎨 TA BANQUE DE LOGOS LOCALE
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
    
    if st.button("📖 CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()
    
    # 📅 BOUTONS DE RECHERCHE PAR DATE
    aujourdhui = datetime.now()
    mois_francais = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    date_affichee = f"{aujourdhui.day} {mois_francais[aujourdhui.month - 1]}"
    
    st.write("---")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        if st.button(f"📅 Ça s'est joué aujourd'hui ({date_affichee})", use_container_width=True):
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
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Nations']
            st.rerun()
    with col_c:
        if st.button("🏟️ CLUBS", use_container_width=True):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Clubs']
            st.rerun()
    with col_d:
        if st.button("🎲 DIVERS", use_container_width=True):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Divers']
            st.rerun()

    st.write("---")
    st.subheader("🔍 Outils & Statistiques")

    col_outils1, col_outils2 = st.columns(2)
    with col_outils1:
        if st.button("🛡️ Par Équipe", use_container_width=True):
            st.session_state.page = 'recherche_equipe'
            st.rerun()
        if st.button("📊 Statistiques", use_container_width=True):
            st.session_state.page = 'statistiques'
            st.rerun()
    with col_outils2:
        if st.button("⚔️ Face-à-Face", use_container_width=True):
            st.session_state.page = 'face_a_face'
            st.rerun()
        if st.button("🕵️ Recherche Avancée", use_container_width=True):
            st.session_state.page = 'recherche_avancee'
            st.rerun()

# ==========================================
# PAGE CATALOGUE
# ==========================================
elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    st.dataframe(df[colonnes_presentes], use_container_width=True, height=800)

# ==========================================
# PAGE ÉPHÉMÉRIDE (Aujourd'hui)
# ==========================================
elif st.session_state.page == 'ephemeride':
    aujourdhui = datetime.now()
    mois_francais = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    date_texte = f"{aujourdhui.day} {mois_francais[aujourdhui.month - 1]}"
    
    st.header(f"📅 Ça s'est joué un {date_texte}")
    st.write("Voyage dans le temps ! Voici tous les matchs de vos archives qui se sont déroulés à cette même date.")
    
    if 'Date' in df.columns:
        motif_date = r'^0?' + str(aujourdhui.day) + r'/0?' + str(aujourdhui.month) + r'/'
        df_ephem = df[df['Date'].astype(str).str.contains(motif_date, na=False, regex=True)]
        
        if not df_ephem.empty:
            st.success(f"🎉 **{len(df_ephem)} matchs** ont été trouvés !")
            st.dataframe(df_ephem[colonnes_presentes], use_container_width=True, height=600)
        else:
            st.info(f"Aucun match dans vos archives ne s'est joué un {date_texte}.")
    else:
        st.warning("La colonne 'Date' n'est pas trouvée dans votre fichier.")

# ==========================================
# PAGE RECHERCHE PAR DATE (Manuel)
# ==========================================
elif st.session_state.page == 'recherche_date':
    st.header("🔎 Recherche par Date")
    st.write("Choisissez un jour et un mois pour voir ce qui s'est passé à cette date dans l'Histoire.")
    
    c1, c2 = st.columns(2)
    jours_possibles = [str(i) for i in range(1, 32)]
    mois_francais = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    with c1:
        jour_choisi = st.selectbox("Jour", jours_possibles)
    with c2:
        mois_choisi = st.selectbox("Mois", mois_francais)
        
    mois_num = mois_francais.index(mois_choisi) + 1
    
    if 'Date' in df.columns:
        motif_date = r'^0?' + str(jour_choisi) + r'/0?' + str(mois_num) + r'/'
        df_date = df[df['Date'].astype(str).str.contains(motif_date, na=False, regex=True)]
        
        st.write("---")
        if not df_date.empty:
            st.success(f"🎉 **{len(df_date)} matchs** trouvés pour un {jour_choisi} {mois_choisi} !")
            st.dataframe(df_date[colonnes_presentes], use_container_width=True, height=600)
        else:
            st.info(f"Aucun match dans vos archives ne s'est joué un {jour_choisi} {mois_choisi}.")

# ==========================================
# PAGE RECHERCHE PAR ÉQUIPE
# ==========================================
elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Recherche par Équipe")
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Sélectionne une équipe :", toutes_les_equipes)
    df_filtre = df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)]
    st.metric("Matchs trouvés", len(df_filtre))
    st.dataframe(df_filtre[colonnes_presentes], use_container_width=True, height=600)

# ==========================================
# PAGE FACE-À-FACE
# ==========================================
elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    colA, colB = st.columns(2)
    with colA: eq1 = st.selectbox("Équipe A", toutes_les_equipes, index=0)
    with colB: eq2 = st.selectbox("Équipe B", toutes_les_equipes, index=1 if len(toutes_les_equipes)>1 else 0)
    df_face = df[((df['Domicile'] == eq1) & (df['Extérieur'] == eq2)) | ((df['Domicile'] == eq2) & (df['Extérieur'] == eq1))]
    st.metric("Confrontations", len(df_face))
    st.dataframe(df_face[colonnes_presentes], use_container_width=True, height=600)

# ==========================================
# PAGE RECHERCHE AVANCÉE
# ==========================================
elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    st.write("Cumulez les filtres pour trouver des matchs précis.")

    col1, col2, col3 = st.columns(3)
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    competitions = sorted(df['Compétition'].dropna().unique())
    saisons = sorted(df['Saison'].dropna().unique(), reverse=True) if 'Saison' in df.columns else []

    with col1:
        f_equipes = st.multiselect("Équipes impliquées :", toutes_les_equipes)
    with col2:
        f_comps = st.multiselect("Compétitions :", competitions)
    with col3:
        if saisons: f_saisons = st.multiselect("Saisons :", saisons)
        else: f_saisons = []

    df_filtre = df.copy()
    if f_equipes:
        df_filtre = df_filtre[df_filtre['Domicile'].isin(f_equipes) | df_filtre['Extérieur'].isin(f_equipes)]
    if f_comps:
        df_filtre = df_filtre[df_filtre['Compétition'].isin(f_comps)]
    if f_saisons:
        df_filtre = df_filtre[df_filtre['Saison'].isin(f_saisons)]

    st.metric("Matchs trouvés", len(df_filtre))
    st.dataframe(df_filtre[colonnes_presentes], use_container_width=True, height=600)

# ==========================================
# PAGE STATISTIQUES
# ==========================================
elif st.session_state.page == 'statistiques':
    st.header("📊 Tableau de Bord")
    st.metric("Total des matchs dans la base", len(df))
    st.write("---")

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.subheader("🏆 Top 10 Compétitions")
        top_comp = df['Compétition'].value_counts().head(10)
        st.bar_chart(top_comp)
    with col_stat2:
        st.subheader("🛡️ Top 10 Équipes (Apparitions)")
        toutes_equipes = pd.concat([df['Domicile'], df['Extérieur']]).dropna()
        top_equipes = toutes_equipes.value_counts().head(10)
        st.bar_chart(top_equipes)

    if 'Diffuseur' in df.columns:
        st.write("---")
        st.subheader("📺 Répartition par Diffuseur (Top 10)")
        top_diffuseurs = df['Diffuseur'].dropna().value_counts().head(10)
        st.bar_chart(top_diffuseurs)

# ==========================================
# PAGE ARBORESCENCE (NAVIGATION DYNAMIQUE)
# ==========================================
elif st.session_state.page == 'arborescence':
    
    noeud_actuel = MENU_ARBO
    for etape in st.session_state.chemin:
        if isinstance(noeud_actuel, dict): noeud_actuel = noeud_actuel[etape]
        elif isinstance(noeud_actuel, list): noeud_actuel = etape

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
    
    # --- SOUS-MENUS ---
    if isinstance(noeud_actuel, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud_actuel.keys()):
            with cols[i % 3]:
                if st.button(cle, use_container_width=True):
                    st.session_state.chemin.append(cle)
                    st.rerun()

    # --- LISTE DE COMPÉTITIONS ---
    elif isinstance(noeud_actuel, list):
        cols = st.columns(3)
        for i, element in enumerate(noeud_actuel):
            with cols[i % 3]:
                if st.button(element, use_container_width=True):
                    st.session_state.chemin.append(element)
                    st.rerun()

    # --- RÉSULTATS FINAUX (AVEC LOGO) ---
    elif isinstance(noeud_actuel, str):
        
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
                    cols = st.columns(4)
                    for i, ed in enumerate(editions):
                        with cols[i % 4]:
                            if st.button(str(ed), use_container_width=True):
                                st.session_state.edition_choisie = ed
                                st.rerun()
                else:
                    st.warning("Aucune édition trouvée pour ce choix.")
            
            else:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.header(f"📍 {st.session_state.edition_choisie}")
                with c2:
                    if st.session_state.edition_choisie in LOGOS:
                        chemin_image = LOGOS[st.session_state.edition_choisie]
                        if os.path.exists(chemin_image):
                            st.image(chemin_image, width=100)
                        else:
                            st.caption("(Logo introuvable)")

                df_final = df[df['Compétition'] == st.session_state.edition_choisie]
                st.metric("Matchs trouvés", len(df_final))
                st.dataframe(df_final[colonnes_presentes], use_container_width=True, height=600)
        
        else:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.header(f"🏆 {noeud_actuel}")
            with c2:
                if noeud_actuel in LOGOS:
                    chemin_image = LOGOS[noeud_actuel]
                    if os.path.exists(chemin_image):
                        st.image(chemin_image, width=100)
                    else:
                        st.caption("(Logo introuvable)")

            mask = df['Compétition'].str.contains(noeud_actuel, na=False, case=False)
            df_final = df[mask]
            st.metric("Matchs trouvés", len(df_final))
            st.dataframe(df_final[colonnes_presentes], use_container_width=True, height=600)
