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
# ⚙️ FONCTION MAGIQUE POUR LES NOMS D'ÉQUIPES
# ==========================================
def nettoyer_nom_equipe(nom):
    if pd.isna(nom): return ""
    nom_sans_accents = ''.join(c for c in unicodedata.normalize('NFD', str(nom)) if unicodedata.category(c) != 'Mn')
    nom_propre = re.sub(r'[^a-z0-9]', '', nom_sans_accents.lower())
    return nom_propre

# ==========================================
# 🔍 SCANNER AUTOMATIQUE DE LOGOS
# ==========================================
@st.cache_data
def charger_dictionnaire_logos(dossier_racine="Logos"):
    dict_logos = {}
    if os.path.exists(dossier_racine):
        # On fouille dans tous les sous-dossiers
        for root, dirs, files in os.walk(dossier_racine):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # On nettoie le nom du fichier (sans l'extension)
                    nom_equipe = os.path.splitext(file)[0]
                    cle = nettoyer_nom_equipe(nom_equipe)
                    chemin_complet = os.path.join(root, file)
                    dict_logos[cle] = chemin_complet
    return dict_logos

# On lance le scanner
DICTIONNAIRE_LOGOS_EQUIPES = charger_dictionnaire_logos("Logos")

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
colonnes_possibles = ['Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Langue', 'Qualité']
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
        
        jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

        for i, (index, row) in enumerate(df_resultats.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    
                    # --- 1. FORMATTAGE DE LA DATE ---
                    date_brute = row.get('Date', '')
                    date_formatee = date_brute
                    if pd.notna(date_brute) and date_brute:
                        try:
                            dt = datetime.strptime(date_brute, "%d/%m/%Y")
                            date_formatee = f"{jours_fr[dt.weekday()]} {dt.day} {mois_fr[dt.month - 1]} {dt.year}"
                        except ValueError:
                            date_formatee = date_brute

                    # --- 2. EN-TÊTE ET FORMATTAGE SPECIFIQUE ---
                    stade = row.get('Stade', 'Stade inconnu')
                    if pd.isna(stade) or not str(stade).strip(): 
                        stade = "Stade inconnu"
                        
                    raw_journee = row.get('Journée', '')
                    val_journee = ""
                    if pd.notna(raw_journee) and str(raw_journee).strip():
                        try:
                            val_journee = str(int(float(raw_journee)))
                        except ValueError:
                            val_journee = str(raw_journee).strip()
                            
                    val_phase = str(row.get('Phase', '')).strip() if 'Phase' in row and pd.notna(row['Phase']) else ""
                    
                    comp_name = str(row.get('Compétition', ''))
                    comp_name_lower = comp_name.lower()
                    
                    # Logique de distinction des compétitions
                    mots_championnats = ['ligue 1', 'ligue 2', 'division 1', 'division 2', 'serie a', 'liga', 'premier league', 'bundesliga', 'championnat']
                    est_championnat = any(mot in comp_name_lower for mot in mots_championnats) and 'champions' not in comp_name_lower and 'nations' not in comp_name_lower and 'europe' not in comp_name_lower
                    
                    mots_nations = ['coupe du monde', 'euro', "championnat d'europe", 'copa america', 'ligue des nations', 'confédérations', 'olympiques']
                    est_nation = any(mot in comp_name_lower for mot in mots_nations) and 'clubs' not in comp_name_lower
                    
                    stade_str = stade
                    
                    # Affichage spécifique CLUBS vs NATIONS
                    if not est_nation: # On considère que ce sont des matchs de CLUBS
                        if est_championnat:
                            journee_str = ""
                            if val_journee:
                                if val_journee.isdigit() or not val_journee.lower().startswith(('j', 'journée')):
                                    journee_str = f"Journée {val_journee}"
                                else:
                                    journee_str = val_journee
                            elif val_phase:
                                journee_str = val_phase
                            
                            # Ajout: Compétition - Journée
                            if comp_name.strip():
                                stade_str += f" - {comp_name.strip()}"
                            if journee_str:
                                stade_str += f" - {journee_str}"
                                
                        else: # Coupes de clubs
                            # Ajout: Compétition - Phase
                            if comp_name.strip():
                                stade_str += f" - {comp_name.strip()}"
                            if val_phase:
                                stade_str += f" - {val_phase}"
                    else:
                        # Matchs de NATIONS : Conservation de l'affichage classique (Stade - Phase)
                        if val_phase:
                            stade_str += f" - {val_phase}"
                    
                    st.caption(f"🗓️ {date_formatee.capitalize()} | 🏟️ {stade_str}")
                    
                    dom = row.get('Domicile', '')
                    ext = row.get('Extérieur', '')
                    score = row.get('Score', '-')
                    
                    cle_dom = nettoyer_nom_equipe(dom)
                    cle_ext = nettoyer_nom_equipe(ext)
                    
                    logo_dom = DICTIONNAIRE_LOGOS_EQUIPES.get(cle_dom)
                    logo_ext = DICTIONNAIRE_LOGOS_EQUIPES.get(cle_ext)
                    
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    
                    # --- GESTION DOMICILE ---
                    with c_dom:
                        if logo_dom and os.path.exists(logo_dom):
                            try:
                                with open(logo_dom, "rb") as image_file:
                                    img_b64 = base64.b64encode(image_file.read()).decode()
                                html_dom = f"""
                                <div style='text-align:center;'>
                                    <p style='font-weight:bold; font-size:17px; margin-bottom:5px;'>{dom}</p>
                                    <img src='data:image/png;base64,{img_b64}' style='width:60px;'>
                                </div>
                                """
                                st.markdown(html_dom, unsafe_allow_html=True)
                            except Exception:
                                st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:17px; margin-bottom:2px;'>{dom}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:17px; margin-bottom:2px;'>{dom}</p>", unsafe_allow_html=True)
                        
                    # --- SCORE ---
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{score}</h2>", unsafe_allow_html=True)
                        
                    # --- GESTION EXTÉRIEUR ---
                    with c_ext:
                        if logo_ext and os.path.exists(logo_ext):
                            try:
                                with open(logo_ext, "rb") as image_file:
                                    img_b64 = base64.b64encode(image_file.read()).decode()
                                html_ext = f"""
                                <div style='text-align:center;'>
                                    <p style='font-weight:bold; font-size:17px; margin-bottom:5px;'>{ext}</p>
                                    <img src='data:image/png;base64,{img_b64}' style='width:60px;'>
                                </div>
                                """
                                st.markdown(html_ext, unsafe_allow_html=True)
                            except Exception:
                                st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:17px; margin-bottom:2px;'>{ext}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:17px; margin-bottom:2px;'>{ext}</p>", unsafe_allow_html=True)
                    
                    # --- 3. PIED DE FICHE ---
                    diffuseur = row.get('Diffuseur', '')
                    qualite = row.get('Qualité', '')
                    
                    has_diff = pd.notna(diffuseur) and str(diffuseur).strip() != ""
                    has_qual = pd.notna(qualite) and str(qualite).strip() != ""
                    
                    if has_diff or has_qual:
                        html_footer = "<div style='text-align: center; color: gray; border-top: 0.5px solid #444; margin-top:10px; padding-top:6px; padding-bottom:2px;'>"
                        parts = []
                        if has_diff:
                            parts.append(f"<span style='font-size: 16px; font-weight: 500;'>📺 {diffuseur}</span>")
                        if has_qual:
                            parts.append(f"<span style='font-size: 14px;'>💾 {qualite}</span>")
                        
                        html_footer += " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(parts)
                        html_footer += "</div>"
                        st.markdown(html_footer, unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'edition_choisie' not in st.session_state: st.session_state.edition_choisie = None

def go_home():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.edition_choisie = None

# ==========================================
# 🧭 BARRE LATÉRALE PERSISTANTE
# ==========================================
with st.sidebar:
    st.title("⚽ Menu Rapide")
    
    if st.button("🏠 Accueil", width="stretch"):
        go_home()
        st.rerun()
        
    st.divider()
    st.markdown("### 📂 Catégories")
    if st.button("🌍 Sélections Nationales", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Nations']
        st.session_state.edition_choisie = None
        st.rerun()
    if st.button("🏟️ Clubs", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Clubs']
        st.session_state.edition_choisie = None
        st.rerun()
    if st.button("🎲 Matchs de Gala", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Divers']
        st.session_state.edition_choisie = None
        st.rerun()
        
    st.divider()
    st.markdown("### 🔍 Outils")
    if st.button("📖 Catalogue Complet", width="stretch"):
        st.session_state.page = 'catalogue'
        st.rerun()
    if st.button("📊 Statistiques", width="stretch"):
        st.session_state.page = 'statistiques'
        st.rerun()
    if st.button("🛡️ Par Équipe", width="stretch"):
        st.session_state.page = 'recherche_equipe'
        st.rerun()
    if st.button("⚔️ Face-à-Face", width="stretch"):
        st.session_state.page = 'face_a_face'
        st.rerun()
    if st.button("🕵️ Recherche Avancée", width="stretch"):
        st.session_state.page = 'recherche_avancee'
        st.rerun()

# ==========================================
# PAGE D'ACCUEIL
# ==========================================
if st.session_state.page == 'accueil':
    st.markdown("<h1 style='text-align: center;'>⚽ Le Grenier du Foot</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #aaaaaa;'>Plongez dans l'histoire. Retrouvez plus de <b>4000</b> matchs en vidéo.</p>", unsafe_allow_html=True)
    st.write("")
    
    # --- 1. RECHERCHE ET INFOS ---
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

    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    with col_btn1:
        if st.button("📖 Contenu", width="stretch"): popup_contenu()
    with col_btn2:
        if st.button("💾 Formats", width="stretch"): popup_formats()
    with col_btn3:
        if st.button("💶 Tarifs", width="stretch"): popup_tarifs()
    with col_btn4:
        if st.button("✉️ Contact / Échanges", width="stretch"): popup_contact()
            
    st.write("---")
    
    # --- 2. LE CŒUR DE L'APP : EXPLORER PAR COMPÉTITION ---
    st.markdown("### 📂 Explorer le Classeur")
    st.markdown("<p style='color: gray; margin-bottom: 15px;'>Sélectionnez une catégorie pour naviguer dans l'arborescence des archives.</p>", unsafe_allow_html=True)
    
    col_n, col_c, col_d = st.columns(3)
    with col_n:
        st.markdown("<div style='text-align: center; color: #aaaaaa; font-size: 14px; margin-bottom: 5px;'>Coupes du Monde, Euros, Copa...</div>", unsafe_allow_html=True)
        if st.button("🌍 SÉLECTIONS NATIONALES", width="stretch", type="primary"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Nations']
            st.rerun()
    with col_c:
        st.markdown("<div style='text-align: center; color: #aaaaaa; font-size: 14px; margin-bottom: 5px;'>Ligue des Champions, Championnats...</div>", unsafe_allow_html=True)
        if st.button("🏟️ CLUBS", width="stretch", type="primary"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Clubs']
            st.rerun()
    with col_d:
        st.markdown("<div style='text-align: center; color: #aaaaaa; font-size: 14px; margin-bottom: 5px;'>Matchs amicaux, Jubilés...</div>", unsafe_allow_html=True)
        if st.button("🎲 MATCHS DE GALA", width="stretch", type="primary"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Divers']
            st.rerun()

    st.write("---")

    # --- 3. SECONDAIRE : CATALOGUE & ÉPHÉMÉRIDE CÔTE À CÔTE ---
    col_cat, col_eph = st.columns(2)
    
    with col_cat:
        st.markdown("### 📖 Tout voir d'un coup")
        st.markdown("<p style='color: gray;'>Vous préférez flâner ? Affichez la liste complète de tous les matchs disponibles.</p>", unsafe_allow_html=True)
        if st.button("Afficher le Catalogue Complet", width="stretch"):
            st.session_state.page = 'catalogue'
            st.rerun()
            
    with col_eph:
        st.markdown("### 📅 L'Éphéméride")
        aujourdhui = datetime.now()
        mois_francais = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        date_affichee = f"{aujourdhui.day} {mois_francais[aujourdhui.month - 1]}"
        
        nb_matchs_jour = 0
        if 'Date' in df.columns:
            motif_date = r'^0?' + str(aujourdhui.day) + r'/0?' + str(aujourdhui.month) + r'/'
            nb_matchs_jour = len(df[df['Date'].astype(str).str.contains(motif_date, na=False, regex=True)])

        if nb_matchs_jour > 0:
            st.success(f"🔥 **{nb_matchs_jour} matchs** se sont joués un {date_affichee} !")
        else:
            st.info(f"Que s'est-il passé un {date_affichee} ?")
            
        c_btn_e1, c_btn_e2 = st.columns(2)
        with c_btn_e1:
            if st.button("Voir les matchs du jour", width="stretch"):
                st.session_state.page = 'ephemeride'
                st.rerun()
        with c_btn_e2:
            if st.button("Chercher autre date", width="stretch"):
                st.session_state.page = 'recherche_date'
                st.rerun()

    st.write("---") 

    # --- 4. OUTILS & STATS ---
    st.markdown("### 🔍 Outils & Statistiques")
    col_outils1, col_outils2 = st.columns(2)
    with col_outils1:
        if st.button("🛡️ Par Équipe", width="stretch"):
            st.session_state.page = 'recherche_equipe'
            st.rerun()
        if st.button("📊 Statistiques", width="stretch"):
            st.session_state.page = 'statistiques'
            st.rerun()
    with col_outils2:
        if st.button("⚔️ Face-à-Face", width="stretch"):
            st.session_state.page = 'face_a_face'
            st.rerun()
        if st.button("🕵️ Recherche Avancée", width="stretch"):
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
                if st.button(cle, width="stretch"):
                    st.session_state.chemin.append(cle)
                    st.rerun()

    elif isinstance(noeud_actuel, list):
        cols = st.columns(3)
        for i, element in enumerate(noeud_actuel):
            with cols[i % 3]:
                if st.button(element, width="stretch"):
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
                            if st.button(str(ed), width="stretch"):
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

