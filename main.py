import streamlit as st
import pandas as pd
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
# ⚙️ UTILITAIRES & LOGOS
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

LOGOS_COMPETITIONS = {
    "Coupe du Monde 1998": "Logos/cdm1998.png",
    "Ligue 1": "Logos/ligue1.png",
    "Champions League": "Logos/championsleague.png"
    # Ajoute les autres ici si besoin
}

# ==========================================
# 🧠 NAVIGATION & ARBORESCENCE
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
            "C3": ["Coupe Intertoto", "Coupe UEFA", "Europa League"]
        },
        "Championnat de France": ["Division 1", "Ligue 1", "Division 2", "Ligue 2"],
        "Championnats étrangers": {
            "Italie": ["Serie A", "Coppa Italia"],
            "Espagne": ["Liga", "Copa del Rey"],
            "Angleterre": ["Premier League", "FA Cup"]
        }
    },
    "Divers": {"Amical": ["Amical"], "Tournoi international": ["Kirin Cup"]}
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
        return df
    except Exception as e:
        st.error(f"Erreur : {e}"); return pd.DataFrame()

df = load_data()

# --- FONCTION : FICHES DE MATCHS ---
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucun match trouvé."); return
    st.metric("Matchs trouvés", len(df_resultats))
    
    mode = st.radio("Affichage :", ["📊 Tableau", "🃏 Fiches"], horizontal=True)
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
                    # Date
                    date_formatee = row.get('Date', '')
                    try:
                        dt = datetime.strptime(date_formatee, "%d/%m/%Y")
                        date_formatee = f"{jours_fr[dt.weekday()]} {dt.day} {mois_fr[dt.month - 1]} {dt.year}"
                    except: pass

                    # Logique En-tête (Club vs Nation)
                    stade = str(row.get('Stade', 'Stade inconnu'))
                    comp = str(row.get('Compétition', ''))
                    phase = str(row.get('Phase', '')).strip() if pd.notna(row.get('Phase')) else ""
                    
                    try: val_j = str(int(float(row.get('Journée', ''))))
                    except: val_j = str(row.get('Journée', ''))

                    mots_champ = ['ligue 1', 'ligue 2', 'serie a', 'liga', 'premier league', 'bundesliga', 'championnat']
                    est_champ = any(m in comp.lower() for m in mots_champ) and 'champions' not in comp.lower()
                    mots_nations = ['coupe du monde', 'euro', 'copa', 'nations']
                    est_nation = any(m in comp.lower() for m in mots_nations)

                    stade_str = stade
                    if not est_nation:
                        j_str = f"Journée {val_j}" if (val_j and (val_j.isdigit() or not val_j.lower().startswith('j'))) else val_j
                        suffixe = j_str if est_champ else phase
                        stade_str += f" - {comp}" + (f" - {suffixe}" if suffixe else "")
                    else:
                        stade_str += f" - {phase}" if phase else ""

                    st.caption(f"🗓️ {date_formatee.capitalize()} | 🏟️ {stade_str}")
                    
                    # Score & Logos
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    for side, col, team in [("dom", c_dom, row['Domicile']), ("ext", c_ext, row['Extérieur'])]:
                        with col:
                            logo = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(team))
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
                        st.markdown(f"<div style='text-align:center; color:gray; border-top:0.5px solid #444; padding-top:6px; font-size:15px;'>📺 {diff} &nbsp;&nbsp;|&nbsp;&nbsp; 💾 {qual}</div>", unsafe_allow_html=True)

# ==========================================
# 🧭 BARRE LATÉRALE (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("⚽ Navigation")
    if st.button("🏠 Accueil", width="stretch"):
        st.session_state.page = 'accueil'
        st.session_state.chemin = []
        st.rerun()
    
    st.divider()
    st.subheader("📂 Catégories")
    if st.button("🌍 Sélections Nationales", width="stretch"):
        st.session_state.page, st.session_state.chemin = 'arborescence', ['Nations']
        st.rerun()
    if st.button("🏟️ Clubs", width="stretch"):
        st.session_state.page, st.session_state.chemin = 'arborescence', ['Clubs']
        st.rerun()
    if st.button("🎲 Matchs de Gala", width="stretch"):
        st.session_state.page, st.session_state.chemin = 'arborescence', ['Divers']
        st.rerun()

    st.divider()
    st.subheader("📊 Outils")
    if st.button("📖 Catalogue Complet", width="stretch"):
        st.session_state.page = 'catalogue'; st.rerun()
    if st.button("📈 Statistiques", width="stretch"):
        st.session_state.page = 'statistiques'; st.rerun()
    if st.button("🕵️ Recherche Avancée", width="stretch"):
        st.session_state.page = 'recherche_avancee'; st.rerun()

# ==========================================
# 🚦 ROUTAGE DES PAGES
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'accueil'

if st.session_state.page == 'accueil':
    st.markdown("<h1 style='text-align: center;'>⚽ Archives Football</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #aaaaaa;'>Retrouvez plus de 4000 matchs mythiques.</p>", unsafe_allow_html=True)
    
    # Recherche interactive
    search = st.text_input("🔍 Recherche Rapide", placeholder="Équipe, année, stade...")
    if search:
        mask = df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        afficher_resultats(df[mask])
    else:
        # Boutons d'infos (Pop-ups)
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("📖 Contenu", width="stretch"): popup_contenu()
        with c2:
            if st.button("💾 Formats", width="stretch"): popup_formats()
        with c3:
            if st.button("💶 Tarifs", width="stretch"): popup_tarifs()
        with c4:
            if st.button("✉️ Contact", width="stretch"): popup_contact()
        
        st.info("Utilisez le menu à gauche pour naviguer par compétition ou consulter les statistiques.")

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet"); afficher_resultats(df)

elif st.session_state.page == 'statistiques':
    st.header("📈 Statistiques")
    st.metric("Total de matchs", len(df))
    st.subheader("Top 10 Compétitions")
    st.bar_chart(df['Compétition'].value_counts().head(10))

elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    # Filtres multiselect ici...
    afficher_resultats(df) # Version simplifiée pour le test

elif st.session_state.page == 'arborescence':
    # Logique de navigation dynamique (MENU_ARBO)
    st.header(f"📂 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        st.session_state.chemin.pop()
        if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()
    # ... (Reste de la logique arborescence)
    st.write("Sélectionnez une sous-catégorie ou une édition.")
