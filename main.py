import streamlit as st
import pd
import os
from datetime import datetime
import unicodedata
import re
import base64

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# ==========================================
# ⚙️ FONCTIONS DES POP-UPS (INFORMATIONS)
# ==========================================
@st.dialog("📖 Contenu de la collection")
def popup_contenu():
    st.markdown("""
    **Ce que vous trouverez dans ce catalogue :**
    * 🌍 Des **matchs de clubs** et de **sélections nationales**.
    * 🏆 Les grandes **compétitions internationales** : Coupe du Monde, Euro, Copa America, Jeux Olympiques...
    * 🥇 Les **grands championnats** : Ligue 1, Serie A, Liga, Premier League...
    * ✨ Les **Coupes d'Europe** : Ligue des Champions, Coupe UEFA, Coupe des Coupes...
    * 🕰️ Des matchs **amicaux, historiques et rares**.
    """)

@st.dialog("💾 Formats & Organisation")
def popup_formats():
    st.markdown("### 🗂️ Données répertoriées")
    st.markdown("""
    * 🗓️ Date et saison du match
    * 🏆 Compétition et phase
    * 🏟️ Lieu et stade
    * 📺 Diffuseur d'origine (TF1, Canal+, etc.)
    * 🎙️ Langue des commentaires
    """)
    st.divider()
    st.markdown("### 📼 Formats disponibles")
    st.markdown("""
    * 💻 **Numérique :** formats courants (.mp4, .avi, .mkv) – parfaits pour ordinateur, tablette ou TV.
    * 💿 **DVD :** fichiers .VOB stockés sur disque dur.
    * 📼 **VHS :** pour les puristes, quelques exemplaires disponibles au format original.
    """)

@st.dialog("💶 Tarifs & Offres")
def popup_tarifs():
    st.markdown("### 💰 Grille Tarifaire")
    st.markdown("""
    * 💿 **1 match au format DVD** = **5 €**
    * 💻 **1 match au format Numérique** (mp4, mkv...) = **3 €**
    """)
    st.divider()
    st.markdown("### 🎁 Offres & Réductions")
    st.markdown("""
    * 🆓 **1 match offert** pour 10 matchs achetés (hors DVD).
    * 📉 **-10% de réduction** immédiate dès 20 matchs achetés.
    * 📦 **Packs thématiques** disponibles sur demande (ex : France 98, parcours européens...).
    """)

@st.dialog("🤝 Échanges & Contact")
def popup_contact():
    st.markdown("""
    **Comment obtenir un match ?**
    * 🛒 **Achat direct :** À l'unité ou en créant votre propre pack.
    * 🔄 **Échange :** Vous possédez vos propres archives ? Je suis toujours ouvert aux échanges de matchs rares !
    * 🚀 **Livraison :** Les fichiers numériques sont envoyés rapidement et de manière sécurisée via *Swisstransfer*, *WeTransfer* ou *Grosfichiers*.
    
    📩 **Me contacter :** N'hésitez pas à m'envoyer un message via mon bouton de contact pour toute demande ou recherche spécifique !
    """)

# ==========================================
# ⚙️ UTILITAIRES & SCANNER LOGOS
# ==========================================
def nettoyer_nom_equipe(nom):
    if pd.isna(nom): return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

@st.cache_data
def charger_dictionnaire_logos(dossier_racine="Logos"):
    dict_logos = {}
    if os.path.exists(dossier_racine):
        for root, dirs, files in os.walk(dossier_racine):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    nom_equipe = os.path.splitext(file)[0]
                    cle = nettoyer_nom_equipe(nom_equipe)
                    dict_logos[cle] = os.path.join(root, file)
    return dict_logos

DICTIONNAIRE_LOGOS_EQUIPES = charger_dictionnaire_logos("Logos")

LOGOS = {
    "Coupe du Monde 1998": "Logos/cdm1998.png",
    "Ligue 1": "Logos/ligue1.png",
    "Champions League": "Logos/championsleague.png"
}

# ==========================================
# 🧠 STRUCTURE DE NAVIGATION
# ==========================================
MENU_ARBO = {
    "Nations": {
        "Coupe du Monde": {"Phase finale": "FILTER_CDM_FINALE", "Eliminatoires": "FILTER_CDM_ELIM"},
        "Championnat d'Europe": {"Phase finale": "FILTER_EURO_FINALE", "Eliminatoires": "FILTER_EURO_ELIM"},
        "Ligue des Nations": "Ligue des Nations",
        "Copa America": "Copa America",
        "Jeux Olympiques": "Jeux Olympiques"
    },
    "Clubs": {
        "Coupe d'Europe": {
            "C1": ["Coupe d'Europe des clubs champions", "Champions League"],
            "C2": ["Coupe des Coupes"],
            "C3": ["Coupe Intertoto", "Coupe UEFA", "Europa League"],
            "C4": ["Conference League"]
        },
        "Championnat de France": ["Division 1", "Ligue 1", "Division 2", "Ligue 2"],
        "Championnats étrangers": {
            "Italie": ["Serie A", "Coppa Italia"],
            "Espagne": ["Liga", "Copa del Rey"],
            "Angleterre": ["Premier League", "FA Cup"]
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
        st.error(f"Erreur : {e}"); return pd.DataFrame()

df = load_data()

# --- OUTIL : FICHES DE MATCHS ---
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucun match trouvé."); return
    
    st.metric("Matchs trouvés", len(df_resultats))
    mode = st.radio("Mode d'affichage :", ["📊 Tableau", "🃏 Fiches"], horizontal=True)
    
    if mode == "📊 Tableau":
        st.dataframe(df_resultats, use_container_width=True, height=600)
    else:
        st.write("---")
        cols = st.columns(2)
        jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

        for i, (index, row) in enumerate(df_resultats.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    # Format Date
                    date_brute = row.get('Date', '')
                    date_formatee = date_brute
                    try:
                        dt = datetime.strptime(date_brute, "%d/%m/%Y")
                        date_formatee = f"{jours_fr[dt.weekday()]} {dt.day} {mois_fr[dt.month - 1]} {dt.year}"
                    except: pass

                    # En-tête (Logique Club/Nation)
                    stade = row.get('Stade', 'Stade inconnu')
                    comp = str(row.get('Compétition', ''))
                    val_phase = str(row.get('Phase', '')).strip() if pd.notna(row.get('Phase')) else ""
                    try: val_j = str(int(float(row.get('Journée', ''))))
                    except: val_j = str(row.get('Journée', ''))

                    mots_champ = ['ligue 1', 'ligue 2', 'serie a', 'liga', 'premier league', 'bundesliga', 'championnat']
                    est_champ = any(m in comp.lower() for m in mots_champ) and 'champions' not in comp.lower()
                    mots_nations = ['coupe du monde', 'euro', 'copa america', 'nations']
                    est_nation = any(m in comp.lower() for m in mots_nations)

                    stade_str = stade
                    if not est_nation:
                        j_label = f"Journée {val_j}" if (val_j and val_j.isdigit()) else val_j
                        suffixe = j_label if est_champ else val_phase
                        stade_str += f" - {comp}" + (f" - {suffixe}" if suffixe else "")
                    else:
                        stade_str += f" - {val_phase}" if val_phase else ""

                    st.caption(f"🗓️ {date_formatee.capitalize()} | 🏟️ {stade_str}")
                    
                    # Teams & Logos
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    for col, team in [(c_dom, row['Domicile']), (c_ext, row['Extérieur'])]:
                        with col:
                            cle = nettoyer_nom_equipe(team)
                            logo = DICTIONNAIRE_LOGOS_EQUIPES.get(cle)
                            html = f"<div style='text-align:center;'><p style='font-weight:bold; font-size:17px; margin-bottom:5px;'>{team}</p>"
                            if logo and os.path.exists(logo):
                                b64 = base64.b64encode(open(logo, "rb").read()).decode()
                                html += f"<img src='data:image/png;base64,{b64}' style='width:60px;'>"
                            st.markdown(html + "</div>", unsafe_allow_html=True)
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{row['Score']}</h2>", unsafe_allow_html=True)

                    # Footer
                    diff, qual = row.get('Diffuseur', ''), row.get('Qualité', '')
                    if pd.notna(diff) or pd.notna(qual):
                        st.markdown(f"<div style='text-align: center; color: gray; border-top: 0.5px solid #444; margin-top:10px; padding-top:6px; font-size:15px;'>📺 {diff} &nbsp;|&nbsp; 💾 {qual}</div>", unsafe_allow_html=True)

# ==========================================
# 🚦 GESTIONNAIRE DE NAVIGATION (SIDEBAR + ACCUEIL)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'edition_choisie' not in st.session_state: st.session_state.edition_choisie = None

def naviguer(page, chemin=None):
    st.session_state.page = page
    st.session_state.chemin = chemin if chemin else []
    st.session_state.edition_choisie = None
    st.rerun()

# --- BARRE LATÉRALE PERSISTANTE ---
with st.sidebar:
    st.title("⚽ Navigation")
    if st.button("🏠 Accueil", width="stretch"): naviguer('accueil')
    st.divider()
    st.subheader("📂 Explorer")
    if st.button("🌍 SÉLECTIONS NATIONALES", width="stretch"): naviguer('arborescence', ['Nations'])
    if st.button("🏟️ CLUBS", width="stretch"): naviguer('arborescence', ['Clubs'])
    if st.button("🎲 MATCHS DE GALA", width="stretch"): naviguer('arborescence', ['Divers'])
    st.divider()
    st.subheader("🔍 Outils")
    if st.button("📊 Statistiques", width="stretch"): naviguer('statistiques')
    if st.button("🕵️ Recherche Avancée", width="stretch"): naviguer('recherche_avancee')

# --- LOGIQUE DES PAGES ---
if st.session_state.page == 'accueil':
    st.markdown("<h1 style='text-align: center;'>⚽ Archives Football</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #aaaaaa;'>Retrouvez plus de <b>{len(df)}</b> matchs mythiques.</p>", unsafe_allow_html=True)
    
    # Recherche Rapide
    recherche = st.text_input("🔍 Recherche Rapide", placeholder="Équipe, compétition, année...")
    if recherche:
        mask = df.apply(lambda r: r.astype(str).str.contains(recherche, case=False).any(), axis=1)
        afficher_resultats(df[mask])
    else:
        # Boutons Info
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("📖 Contenu", width="stretch"): popup_contenu()
        with c2: 
            if st.button("💾 Formats", width="stretch"): popup_formats()
        with c3: 
            if st.button("💶 Tarifs", width="stretch"): popup_tarifs()
        with c4: 
            if st.button("✉️ Contact", width="stretch"): popup_contact()
        
        st.write("---")
        # Gros boutons de navigation Accueil
        st.markdown("### 📂 Accès Rapide")
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            if st.button("🌍 SÉLECTIONS NATIONALES", width="stretch", type="primary"): naviguer('arborescence', ['Nations'])
        with ca2:
            if st.button("🏟️ CLUBS", width="stretch", type="primary"): naviguer('arborescence', ['Clubs'])
        with ca3:
            if st.button("🎲 MATCHS DE GALA", width="stretch", type="primary"): naviguer('arborescence', ['Divers'])

elif st.session_state.page == 'arborescence':
    noeud = MENU_ARBO
    for etape in st.session_state.chemin:
        noeud = noeud[etape]

    st.caption(f"📂 Chemin : {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.edition_choisie: st.session_state.edition_choisie = None
        else: st.session_state.chemin.pop()
        if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()

    if st.session_state.edition_choisie:
        afficher_resultats(df[df['Compétition'] == st.session_state.edition_choisie])
    elif isinstance(noeud, dict):
        cols = st.columns(3)
        for i, cle in enumerate(noeud.keys()):
            with cols[i % 3]:
                if st.button(cle, width="stretch"):
                    st.session_state.chemin.append(cle); st.rerun()
    elif isinstance(noeud, list):
        cols = st.columns(3)
        for i, item in enumerate(noeud):
            with cols[i % 3]:
                if st.button(item, width="stretch"):
                    st.session_state.edition_choisie = item; st.rerun()
    elif isinstance(noeud, str) and noeud.startswith("FILTER_"):
        # Logique des filtres CDM/EURO
        terme = "Coupe du Monde" if "CDM" in noeud else "Euro"
        eds = sorted(df[df['Compétition'].str.contains(terme, case=False, na=False)]['Compétition'].unique(), reverse=True)
        cols = st.columns(4)
        for i, ed in enumerate(eds):
            with cols[i % 4]:
                if st.button(ed, width="stretch"):
                    st.session_state.edition_choisie = ed; st.rerun()

elif st.session_state.page == 'statistiques':
    st.header("📊 Statistiques")
    st.bar_chart(df['Compétition'].value_counts().head(10))

elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    # Filtres multiselect ici si tu veux...
    afficher_resultats(df)
