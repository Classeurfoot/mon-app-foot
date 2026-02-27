import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re
import base64

# 1. Configuration de la page
st.set_page_config(page_title="Le Grenier du Football", layout="wide")

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
# ⚙️ FONCTIONS UTILES
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

# ==========================================
# 🎨 LOGOS COMPÉTITIONS
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
# 🧠 ARBORESCENCE
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
colonnes_presentes = [c for c in ['Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Langue', 'Qualité'] if c in df.columns]

# --- OUTIL : FICHES DE MATCHS ---
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucun match trouvé.")
        return
    st.metric("Matchs trouvés", len(df_resultats))
    mode = st.radio("Mode d'affichage :", ["📊 Tableau classique", "🃏 Fiches détaillées"], horizontal=True, key=f"mode_{len(df_resultats)}")
    
    if mode == "📊 Tableau classique":
        st.dataframe(df_resultats[colonnes_presentes], use_container_width=True, height=600)
    else:
        st.write("---")
        cols = st.columns(2)
        jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

        for i, (index, row) in enumerate(df_resultats.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    # --- DATE ---
                    date_brute = row.get('Date', '')
                    date_formatee = date_brute
                    if pd.notna(date_brute) and date_brute:
                        try:
                            dt = datetime.strptime(date_brute, "%d/%m/%Y")
                            date_formatee = f"{jours_fr[dt.weekday()]} {dt.day} {mois_fr[dt.month - 1]} {dt.year}"
                        except: pass

                    # --- INFOS COMPLEMENTAIRES ---
                    stade = row.get('Stade', 'Stade inconnu')
                    val_phase = str(row.get('Phase', '')).strip() if pd.notna(row.get('Phase')) else ""
                    st.caption(f"🗓️ {date_formatee.capitalize()} | 🏟️ {stade} {f'- {val_phase}' if val_phase else ''}")

                    # --- LOGOS ET SCORE ---
                    dom, ext, score = row.get('Domicile', ''), row.get('Extérieur', ''), row.get('Score', '-')
                    logo_dom = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(dom))
                    logo_ext = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(ext))

                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    with c_dom:
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>{dom}</p>", unsafe_allow_html=True)
                        if logo_dom: st.image(logo_dom, width=60)
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{score}</h2>", unsafe_allow_html=True)
                    with c_ext:
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>{ext}</p>", unsafe_allow_html=True)
                        if logo_ext: st.image(logo_ext, width=60)

                    # --- BADGES COULEUR (Qualité) ---
                    diffuseur = row.get('Diffuseur', '')
                    qualite = str(row.get('Qualité', '')).strip()
                    if pd.notna(diffuseur) or (qualite and qualite.lower() != "nan"):
                        html_f = "<div style='text-align: center; color: gray; border-top: 0.5px solid #444; margin-top:10px; padding-top:8px;'>"
                        if pd.notna(diffuseur): html_f += f"<span>📺 {diffuseur}</span> &nbsp;&nbsp;|&nbsp;&nbsp; "
                        if qualite and qualite.lower() != "nan":
                            q_low = qualite.lower()
                            color = "#2e7d32" if any(x in q_low for x in ['hd', 'mp4', 'mkv', 'numérique']) else "#e65100" if 'dvd' in q_low else "#424242" if 'vhs' in q_low else "#1976d2"
                            html_f += f"<span style='background:{color}; color:white; padding:2px 8px; border-radius:10px; font-size:11px;'>💾 {qualite}</span>"
                        st.markdown(html_f + "</div>", unsafe_allow_html=True)

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'edition_choisie' not in st.session_state: st.session_state.edition_choisie = None

def go_home():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.edition_choisie = None

# ==========================================
# 🧭 BARRE LATÉRALE
# ==========================================
with st.sidebar:
    st.title("⚽ Menu Rapide")
    if st.button("🏠 Accueil", width="stretch"): go_home(); st.rerun()
    st.divider()
    st.markdown("### 🌟 Nouveautés")
    if st.button("✨ Dernières Pépites", width="stretch"): st.session_state.page = 'dernieres_pepites'; st.rerun()
    if st.button("🎯 Progression", width="stretch"): st.session_state.page = 'progression'; st.rerun()
    st.divider()
    st.markdown("### 🔍 Outils")
    if st.button("📖 Catalogue", width="stretch"): st.session_state.page = 'catalogue'; st.rerun()
    if st.button("📊 Stats", width="stretch"): st.session_state.page = 'statistiques'; st.rerun()
    if st.button("🕵️ Avancé", width="stretch"): st.session_state.page = 'recherche_avancee'; st.rerun()

# ==========================================
# PAGE D'ACCUEIL
# ==========================================
if st.session_state.page == 'accueil':
    st.markdown("<h1 style='text-align: center;'>⚽ Le Grenier du Football</h1>", unsafe_allow_html=True)
    st.write("")

    # --- RECHERCHE ---
    recherche = st.text_input("🔍 Recherche Rapide", placeholder="Équipe, année, compétition...")
    if recherche:
        mask = df.astype(str).apply(lambda x: x.str.contains(recherche, case=False)).any(axis=1)
        afficher_resultats(df[mask])
        st.divider()

    # --- ÉPHÉMÉRIDE DIRECT ---
    aujourdhui = datetime.now()
    motif = f"^{aujourdhui.day:02d}/{aujourdhui.month:02d}/"
    df_jour = df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)]
    if not df_jour.empty:
        st.info(f"📅 **Aujourd'hui ({aujourdhui.day}/{aujourdhui.month}) :** {len(df_jour)} matchs historiques dans la base !")
        if st.button("Voir les matchs du jour"): st.session_state.page = 'ephemeride'; st.rerun()

    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        if st.button("📖 Contenu", use_container_width=True): popup_contenu()
    with col2:
        if st.button("💾 Formats", use_container_width=True): popup_formats()
    with col3:
        if st.button("💶 Tarifs", use_container_width=True): popup_tarifs()
    with col4:
        if st.button("✉️ Contact", use_container_width=True): popup_contact()

    st.divider()
    st.markdown("### 📂 Explorer le Classeur")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌍 SÉLECTIONS", type="primary", use_container_width=True):
            st.session_state.page, st.session_state.chemin = 'arborescence', ['Nations']; st.rerun()
    with c2:
        if st.button("🏟️ CLUBS", type="primary", use_container_width=True):
            st.session_state.page, st.session_state.chemin = 'arborescence', ['Clubs']; st.rerun()
    with c3:
        if st.button("🎲 GALA / AMICAL", type="primary", use_container_width=True):
            st.session_state.page, st.session_state.chemin = 'arborescence', ['Divers']; st.rerun()

# ==========================================
# PAGES SECONDAIRES
# ==========================================
elif st.session_state.page == 'dernieres_pepites':
    st.header("✨ Dernières Pépites")
    afficher_resultats(df.tail(10).iloc[::-1])

elif st.session_state.page == 'progression':
    st.header("🎯 Progression de la Collection")
    if 'Phase' in df.columns:
        m_fin = df['Phase'].astype(str).str.lower().str.contains('finale')
        # Stats CDM
        m_cdm = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Elim", na=False)
        nb_cdm = df[m_cdm & m_fin]['Compétition'].nunique()
        st.write(f"🏆 **Finales CDM :** {nb_cdm}/22")
        st.progress(nb_cdm/22.0)
        # Stats Euro
        m_euro = df['Compétition'].str.contains("Euro", na=False, case=False) & ~df['Compétition'].str.contains("Elim", na=False)
        nb_euro = df[m_euro & m_fin]['Compétition'].nunique()
        st.write(f"🇪🇺 **Finales Euro :** {nb_euro}/17")
        st.progress(nb_euro/17.0)
    else: st.warning("Colonne 'Phase' absente.")

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'ephemeride':
    aujourdhui = datetime.now()
    st.header(f"📅 Matchs du {aujourdhui.day}/{aujourdhui.month}")
    motif = f"^{aujourdhui.day:02d}/{aujourdhui.month:02d}/"
    afficher_resultats(df[df['Date'].astype(str).str.contains(motif, na=False, regex=True)])

elif st.session_state.page == 'statistiques':
    st.header("📊 Statistiques")
    st.metric("Total Matchs", len(df))
    st.subheader("Top Compétitions")
    st.bar_chart(df['Compétition'].value_counts().head(10))

elif st.session_state.page == 'recherche_avancee':
    st.header("🕵️ Recherche Avancée")
    c1, c2 = st.columns(2)
    with c1: comp_f = st.multiselect("Compétition", sorted(df['Compétition'].unique()))
    with c2: sais_f = st.multiselect("Saison", sorted(df['Saison'].unique(), reverse=True)) if 'Saison' in df.columns else []
    df_f = df.copy()
    if comp_f: df_f = df_f[df_f['Compétition'].isin(comp_f)]
    if sais_f: df_f = df_f[df_f['Saison'].isin(sais_f)]
    afficher_resultats(df_f)

elif st.session_state.page == 'arborescence':
    # (Logique d'arborescence conservée de ta version précédente)
    noeud = MENU_ARBO
    for e in st.session_state.chemin:
        if isinstance(noeud, dict): noeud = noeud[e]
    
    st.caption(f"📂 {' > '.join(st.session_state.chemin)}")
    if st.button("⬅️ Retour"):
        if st.session_state.edition_choisie: st.session_state.edition_choisie = None
        else: st.session_state.chemin.pop()
        if not st.session_state.chemin: st.session_state.page = 'accueil'
        st.rerun()

    if isinstance(noeud, dict):
        cols = st.columns(3)
        for i, k in enumerate(noeud.keys()):
            with cols[i%3]:
                if st.button(k, use_container_width=True): st.session_state.chemin.append(k); st.rerun()
    elif isinstance(noeud, (list, str)):
        st.header(f"🏆 {st.session_state.chemin[-1]}")
        # Simplification pour l'exemple : affiche les matchs contenant le nom de la catégorie
        mask = df['Compétition'].str.contains(st.session_state.chemin[-1], case=False, na=False)
        afficher_resultats(df[mask])
