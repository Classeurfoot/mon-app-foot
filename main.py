import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# ==========================================
# ⚙️ FONCTION MAGIQUE POUR LES NOMS D'ÉQUIPES
# ==========================================
def nettoyer_nom_equipe(nom):
    """Transforme 'Côte d'Ivoire' en 'cotedivoire' pour trouver l'image facilement"""
    if pd.isna(nom): return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

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

# --- OUTIL : FICHES DE MATCHS (VOTRE CODE EXACT) ---
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
                    
                    logo_dom = f"Logos/Equipes/{nettoyer_nom_equipe(dom)}.png"
                    logo_ext = f"Logos/Equipes/{nettoyer_nom_equipe(ext)}.png"
                    
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    
                    with c_dom:
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:15px; margin-bottom:2px;'>{dom}</p>", unsafe_allow_html=True)
                        if os.path.exists(logo_dom):
                            st.image(logo_dom, width=60)
                        
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{score}</h2>", unsafe_allow_html=True)
                        
                    with c_ext:
                        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:15px; margin-bottom:2px;'>{ext}</p>", unsafe_allow_html=True)
                        if os.path.exists(logo_ext):
                            st.image(logo_ext, width=60)
                    
                    details = []
                    if 'Stade' in row and pd.notna(row['Stade']): details.append(f"🏟️ {row['Stade']}")
                    if 'Diffuseur' in row and pd.notna(row['Diffuseur']): details.append(f"📺 {row['Diffuseur']}")
                    if 'Qualité' in row and pd.notna(row['Qualité']): details.append(f"⭐ {row['Qualité']}")
                    
                    if details:
                        st.markdown(f"<div style='text-align: center; color: gray; font-size:12px; border-top: 0.5px solid #444; margin-top:10px; padding-top:5px;'>{' | '.join(details)}</div>", unsafe_allow_html=True)

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
# PAGE D'ACCUEIL AVEC RECHERCHE ET ONGLETS
# ==========================================
if st.session_state.page == 'accueil':
    st.title("⚽ Archives Football")
    st.markdown(f"**Plongez dans l'histoire.** Retrouvez plus de **{len(df)}** matchs mythiques documentés et détaillés.")
    
    # --- 🔍 MOTEUR DE RECHERCHE GLOBAL ---
    st.write("")
    recherche_rapide = st.text_input("🔍 Recherche Rapide", placeholder="Tapez une équipe, une compétition, une année, un stade...")
    
    if recherche_rapide:
        mask = (
            df['Domicile'].astype(str).str.contains(recherche_rapide, case=False, na=False) |
            df['Extérieur'].astype(str).str.contains(recherche_rapide, case=False, na=False) |
            df['Compétition'].astype(str).str.contains(recherche_rapide, case=False, na=False)
        )
        for col in ['Phase', 'Stade', 'Saison', 'Date']:
            if col in df.columns:
                mask = mask | df[col].astype(str).str.contains(recherche_rapide, case=False, na=False)
                
        df_trouve = df[mask]
        st.write(f"**Résultats trouvés pour :** '{recherche_rapide}'")
        afficher_resultats(df_trouve)
        st.write("---")
    # -------------------------------------------------

    # --- 📑 LES ONGLETS D'INFORMATION (Inspirés de ta capture) ---
    st.write("### ℹ️ Informations Pratiques")
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Contenu", "💾 Formats & Organisation", "💶 Tarifs & Packs", "🤝 Échanges & Contact"])
    
    with tab1:
        st.info("""
        **Ce que vous trouverez dans cette collection :**
        * ✅ Des **matchs de clubs** et de **sélections nationales**.
        * ✅ Les grandes **compétitions internationales** : Coupe du Monde, Euro, Copa America, Jeux Olympiques...
        * ✅ Les **grands championnats** : Ligue 1, Serie A, Liga, Premier League...
        * ✅ Les **Coupes d'Europe** : Ligue des Champions, Coupe UEFA, etc.
        * ✅ Des matchs **amicaux, historiques et rares**.
        """)
        
    with tab2:
        col_org, col_form = st.columns(2)
        with col_org:
            st.success("""
            **🗂️ Organisation des matchs :**
            * 🗓️ Date et saison
            * 🏆 Compétition et phase
            * ⚽ Équipes et score final
            * 🏟️ Lieu et stade
            * 📺 Diffuseur d'origine (TF1, Canal+, etc.)
            * 🎙️ Langue et qualité du fichier
            * 📝 Remarques (qualité d'image, match incomplet...)
            """)
        with col_form:
            st.warning("""
            **📼 Formats disponibles :**
            * 💻 **Numérique :** formats courants (.mp4, .avi, .mkv) – parfaits pour ordi, tablette ou TV.
            * 💿 **DVD :** fichiers .VOB stockés sur disque dur pour un gain de place (plus besoin de stocker des boîtiers).
            * 📼 **VHS d'origine :** pour les collectionneurs et puristes, quelques exemplaires sont disponibles au format original.
            """)
            
    with tab3:
        st.success("""
        **💰 Grille Tarifaire :**
        * 💿 **1 match au format DVD** (indiqué dans le classeur) = **5 €**
        * 💻 **1 match autre format** (mp4, mkv...) = **3 €**
        
        **🎁 Offres & Réductions :**
        * 🆓 **1 match offert** tous les 10 (hors DVD).
        * 📉 **Réduc' dès 20 matchs achetés** (-10% sur le prix total).
        * 📦 **Packs thématiques dispos** (ex : France 98, campagne de clubs en Coupe d'Europe...).
        """)
        
    with tab4:
        st.info("""
        **🤝 Comment ça marche ?**
        * 🛒 Vous pouvez **acheter** un match à l'unité ou en **pack personnalisé**.
        * 🔄 **Échange possible :** Vous pouvez aussi proposer un échange si vous avez vos propres enregistrements !
        * 🚀 **Envoi numérique :** Les fichiers sont envoyés via Swisstransfer, WeTransfer ou Grosfichiers.
        * 📩 **Une question ou recherche précise ?** Contactez-moi directement, je me ferai un plaisir de vous répondre.
        """)
    # -------------------------------------------------

    st.write("---")
    
    if st.button("📖 PARCOURIR LE CATALOGUE COMPLET", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()
    
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
# PAGE CATALOGUE ET AUTRES
# ==========================================
elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    aujourdhui = datetime.now()
    mois_francais = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    date_texte = f"{aujourdhui.day} {mois_francais[aujourdhui.month - 1]}"
    st.header(f"📅 Ça s'est joué un {date_texte}")
    if 'Date' in df.columns:
        motif_date = r'^0?' + str(aujourdhui.day) + r'/0?' + str(aujourdhui.month) + r'/'
        df_ephem = df[df['Date'].astype(str).str.contains(motif_date, na=False, regex=True)]
        afficher_resultats(df_ephem)

elif st.session_state.page == 'recherche_date':
    st.header("🔎 Recherche par Date")
    c1, c2 = st.columns(2)
    jours_possibles = [str(i) for i in range(1, 32)]
    mois_francais = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    with c1: jour_choisi = st.selectbox("Jour", jours_possibles)
    with c2: mois_choisi = st.selectbox("Mois", mois_francais)
    mois_num = mois_francais.index(mois_choisi) + 1
    if 'Date' in df.columns:
        motif_date = r'^0?' + str(jour_choisi) + r'/0?' + str(mois_num) + r'/'
        df_date = df[df['Date'].astype(str).str.contains(motif_date, na=False, regex=True)]
        st.write("---")
        afficher_resultats(df_date)

elif st.session_state.page == 'recherche_equipe':
    st.header("🛡️ Recherche par Équipe")
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    choix = st.selectbox("Sélectionne une équipe :", toutes_les_equipes)
    df_filtre = df[(df['Domicile'] == choix) | (df['Extérieur'] == choix)]
    afficher_resultats(df_filtre)

elif st.session_state.page == 'face_a_face':
    st.header("⚔️ Face-à-Face")
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    colA, colB = st.columns(2)
    with colA: eq1 = st.selectbox("Équipe A", toutes_les_equipes, index=0)
    with colB: eq2 = st.selectbox("Équipe B", toutes_les_equipes, index=1 if len(toutes_les_equipes)>1 else 0)
    df_face = df[((df['Domicile'] == eq1) & (df['Extérieur'] == eq2)) | ((df['Domicile'] == eq2) & (df['Extérieur'] == eq1))]
    afficher_resultats(df_face)

elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    col1, col2, col3 = st.columns(3)
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().unique())
    competitions = sorted(df['Compétition'].dropna().unique())
    saisons = sorted(df['Saison'].dropna().unique(), reverse=True) if 'Saison' in df.columns else []
    with col1: f_equipes = st.multiselect("Équipes impliquées :", toutes_les_equipes)
    with col2: f_comps = st.multiselect("Compétitions :", competitions)
    with col3: f_saisons = st.multiselect("Saisons :", saisons) if saisons else []
    df_filtre = df.copy()
    if f_equipes: df_filtre = df_filtre[df_filtre['Domicile'].isin(f_equipes) | df_filtre['Extérieur'].isin(f_equipes)]
    if f_comps: df_filtre = df_filtre[df_filtre['Compétition'].isin(f_comps)]
    if f_saisons: df_filtre = df_filtre[df_filtre['Saison'].isin(f_saisons)]
    afficher_resultats(df_filtre)

elif st.session_state.page == 'statistiques':
    st.header("📊 Tableau de Bord")
    st.metric("Total des matchs dans la base", len(df))
    st.write("---")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.subheader("🏆 Top 10 Compétitions")
        st.bar_chart(df['Compétition'].value_counts().head(10))
    with col_stat2:
        st.subheader("🛡️ Top 10 Équipes (Apparitions)")
        st.bar_chart(pd.concat([df['Domicile'], df['Extérieur']]).dropna().value_counts().head(10))

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
    
    if isinstance(noeud_actuel, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud_actuel.keys()):
            with cols[i % 3]:
                if st.button(cle, use_container_width=True):
                    st.session_state.chemin.append(cle)
                    st.rerun()

    elif isinstance(noeud_actuel, list):
        cols = st.columns(3)
        for i, element in enumerate(noeud_actuel):
            with cols[i % 3]:
                if st.button(element, use_container_width=True):
                    st.session_state.chemin.append(element)
                    st.rerun()

    elif isinstance(noeud_actuel, str):
        if noeud_actuel.startswith("FILTER_"):
            if noeud_actuel == "FILTER_CDM_FINALE": mask = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
            elif noeud_actuel == "FILTER_CDM_ELIM": mask = df['Compétition'].str.contains("Eliminatoires Coupe du Monde", na=False, case=False)
            elif noeud_actuel == "FILTER_EURO_FINALE": mask = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False, regex=True) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
            elif noeud_actuel == "FILTER_EURO_ELIM": mask = df['Compétition'].str.contains("Eliminatoires Euro|Eliminatoires Championnat d'Europe", na=False, case=False, regex=True)
            
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
                with c1: st.header(f"📍 {st.session_state.edition_choisie}")
                with c2:
                    if st.session_state.edition_choisie in LOGOS:
                        if os.path.exists(LOGOS[st.session_state.edition_choisie]): st.image(LOGOS[st.session_state.edition_choisie], width=100)
                df_final = df[df['Compétition'] == st.session_state.edition_choisie]
                afficher_resultats(df_final)
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(f"🏆 {noeud_actuel}")
            with c2:
                if noeud_actuel in LOGOS:
                    if os.path.exists(LOGOS[noeud_actuel]): st.image(LOGOS[noeud_actuel], width=100)
            mask = df['Compétition'].str.contains(noeud_actuel, na=False, case=False)
            df_final = df[mask]
            afficher_resultats(df_final)
