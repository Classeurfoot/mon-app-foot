import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re
import base64
import urllib.parse

# 1. Configuration de la page
st.set_page_config(page_title="Le Grenier du Football", layout="wide")

# ==========================================
# ⚙️ GESTION DE LA NAVIGATION & PANIER
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'edition_choisie' not in st.session_state: st.session_state.edition_choisie = None
if 'recherche_equipe_cible' not in st.session_state: st.session_state.recherche_equipe_cible = None
if 'recherche_comp_cible' not in st.session_state: st.session_state.recherche_comp_cible = None
if 'panier' not in st.session_state: st.session_state.panier = []

def go_home():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.edition_choisie = None
    st.session_state.recherche_equipe_cible = None
    st.session_state.recherche_comp_cible = None

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

# --- MISE À JOUR : POPUP DES TARIFS ---
@st.dialog("💶 Tarifs & Offres")
def popup_tarifs():
    st.markdown("### 💰 Grille Tarifaire")
    st.markdown("""
    * 💿 **1 match au format DVD** = **5 €**
      *(⚠️ Note : Pour les formats DVD, vous recevez les fichiers informatiques originaux (.VOB), il n'y a pas d'envoi de DVD physique)*
    * 💻 **1 match au format Numérique** (mp4, mkv...) = **3 €**
    """)
    st.divider()
    st.markdown("### 🎁 Offres & Réductions")
    st.markdown("""
    * 🆓 **1 match offert** tous les 10 matchs achetés (le match le moins cher de votre sélection est automatiquement déduit à partir du 11ème match).
    * 🔄 **Offre cumulable :** 2 matchs offerts pour 20 achetés, 3 pour 30, etc.
    * 📦 **Packs thématiques** disponibles sur demande (ex : France 98, parcours européens...).
    """)

@st.dialog("🤝 Échanges & Contact")
def popup_contact():
    st.markdown("""
    **Comment obtenir un match ?**
    * 🛒 **Achat direct :** Faites votre sélection en l'ajoutant à votre panier, puis envoyez-moi le récapitulatif.
    * 🔄 **Échange :** Vous possédez vos propres archives ? Je suis toujours ouvert aux échanges de matchs rares !
    * 🚀 **Livraison :** Les fichiers numériques sont envoyés rapidement et de manière sécurisée via *Swisstransfer*, *WeTransfer* ou *Grosfichiers*.
    
    📩 **Me contacter :** N'hésitez pas à m'envoyer un message en privé pour finaliser votre commande !
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
        st.markdown("<p style='color: gray; font-size:14px;'>☑️ Cochez les matchs dans la première colonne, puis cliquez sur le bouton en dessous pour les ajouter au panier.</p>", unsafe_allow_html=True)
        
        # Création d'une copie du dataframe pour l'affichage interactif
        df_display = df_resultats[colonnes_presentes].copy()
        df_display.insert(0, "Sélection", False)
        
        # Affichage du tableau éditable
        edited_df = st.data_editor(
            df_display,
            column_config={
                "Sélection": st.column_config.CheckboxColumn("🛒 Ajouter", default=False)
            },
            disabled=colonnes_presentes, # Empêche de modifier les vraies données
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        # Récupérer les lignes cochées
        selected_rows = edited_df[edited_df["Sélection"] == True]
        
        if len(selected_rows) > 0:
            if st.button(f"🛒 Ajouter les {len(selected_rows)} match(s) sélectionné(s) au panier", type="primary", use_container_width=True):
                nb_ajouts = 0
                for _, row in selected_rows.iterrows():
                    match_dict = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items() if k != "Sélection"}
                    match_id = f"{match_dict.get('Date', '')}_{match_dict.get('Domicile', '')}_{match_dict.get('Extérieur', '')}"
                    in_cart = any(f"{m.get('Date', '')}_{m.get('Domicile', '')}_{m.get('Extérieur', '')}" == match_id for m in st.session_state.panier)
                    
                    if not in_cart:
                        q = str(match_dict.get('Qualité', '')).lower()
                        match_dict['format_choisi'] = 'DVD' if 'dvd' in q or 'vob' in q else 'Numérique'
                        st.session_state.panier.append(match_dict)
                        nb_ajouts += 1
                
                # Relance l'application pour mettre à jour le compteur du panier
                st.rerun()

    else:
        st.write("---")
        cols = st.columns(2)
        
        jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

        for i, (index, row) in enumerate(df_resultats.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    
                    date_brute = row.get('Date', '')
                    date_formatee = date_brute
                    if pd.notna(date_brute) and date_brute:
                        try:
                            dt = datetime.strptime(date_brute, "%d/%m/%Y")
                            date_formatee = f"{jours_fr[dt.weekday()]} {dt.day} {mois_fr[dt.month - 1]} {dt.year}"
                        except ValueError:
                            pass

                    stade = row.get('Stade', 'Stade inconnu')
                    if pd.isna(stade) or not str(stade).strip(): stade = "Stade inconnu"
                    val_phase = str(row.get('Phase', '')).strip() if pd.notna(row.get('Phase')) else ""
                    comp_name = str(row.get('Compétition', '')).strip()
                    
                    stade_str = stade
                    if val_phase: stade_str += f" - {val_phase}"
                    
                    st.caption(f"🗓️ {date_formatee.capitalize()} | 🏟️ {stade_str}")
                    
                    if comp_name:
                        if st.button(f"🏆 {comp_name}", key=f"btn_comp_{index}_{i}", use_container_width=True):
                            st.session_state.recherche_comp_cible = comp_name
                            st.session_state.page = 'recherche_avancee'
                            st.rerun()
                    
                    dom = row.get('Domicile', '')
                    ext = row.get('Extérieur', '')
                    score = row.get('Score', '-')
                    
                    logo_dom = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(dom))
                    logo_ext = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(ext))
                    
                    c_dom, c_score, c_ext = st.columns([1, 1, 1])
                    
                    with c_dom:
                        if logo_dom and os.path.exists(logo_dom):
                            try:
                                with open(logo_dom, "rb") as image_file:
                                    img_b64 = base64.b64encode(image_file.read()).decode()
                                html_dom = f"<div style='text-align:center;'><img src='data:image/png;base64,{img_b64}' style='width:60px; margin-bottom:5px;'></div>"
                                st.markdown(html_dom, unsafe_allow_html=True)
                            except Exception: pass
                        if st.button(dom, key=f"btn_dom_{index}_{i}", use_container_width=True):
                            st.session_state.recherche_equipe_cible = dom
                            st.session_state.page = 'recherche_equipe'
                            st.rerun()
                        
                    with c_score:
                        st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{score}</h2>", unsafe_allow_html=True)
                        
                    with c_ext:
                        if logo_ext and os.path.exists(logo_ext):
                            try:
                                with open(logo_ext, "rb") as image_file:
                                    img_b64 = base64.b64encode(image_file.read()).decode()
                                html_ext = f"<div style='text-align:center;'><img src='data:image/png;base64,{img_b64}' style='width:60px; margin-bottom:5px;'></div>"
                                st.markdown(html_ext, unsafe_allow_html=True)
                            except Exception: pass
                        if st.button(ext, key=f"btn_ext_{index}_{i}", use_container_width=True):
                            st.session_state.recherche_equipe_cible = ext
                            st.session_state.page = 'recherche_equipe'
                            st.rerun()
                    
                    diffuseur = row.get('Diffuseur', '')
                    qualite = row.get('Qualité', '')
                    has_diff = pd.notna(diffuseur) and str(diffuseur).strip() != ""
                    has_qual = pd.notna(qualite) and str(qualite).strip() != ""
                    
                    if has_diff or has_qual:
                        html_footer = "<div style='text-align: center; color: gray; border-top: 0.5px solid #444; margin-top:10px; padding-top:6px; padding-bottom:2px;'>"
                        parts = []
                        if has_diff: parts.append(f"<span style='font-size: 16px; font-weight: 500;'>📺 {diffuseur}</span>")
                        if has_qual: parts.append(f"<span style='font-size: 14px;'>💾 {qualite}</span>")
                        html_footer += " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(parts)
                        html_footer += "</div>"
                        st.markdown(html_footer, unsafe_allow_html=True)
                        
                    st.write("") 
                    
                    match_id = f"{date_brute}_{dom}_{ext}"
                    in_cart = any(f"{m.get('Date', '')}_{m.get('Domicile', '')}_{m.get('Extérieur', '')}" == match_id for m in st.session_state.panier)
                    
                    if in_cart:
                        if st.button("✅ Ajouté (Retirer)", key=f"cart_{index}_{i}", use_container_width=True):
                            st.session_state.panier = [m for m in st.session_state.panier if f"{m.get('Date', '')}_{m.get('Domicile', '')}_{m.get('Extérieur', '')}" != match_id]
                            st.rerun()
                    else:
                        if st.button("🛒 Ajouter au panier", key=f"cart_{index}_{i}", type="primary", use_container_width=True):
                            match_dict = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items()}
                            q = str(match_dict.get('Qualité', '')).lower()
                            if 'dvd' in q or 'vob' in q:
                                match_dict['format_choisi'] = 'DVD'
                            else:
                                match_dict['format_choisi'] = 'Numérique'
                                
                            st.session_state.panier.append(match_dict)
                            st.rerun()

# ==========================================
# 🧭 BARRE LATÉRALE PERSISTANTE
# ==========================================
with st.sidebar:
    st.title("⚽ Menu Rapide")
    
    if st.button("🏠 Accueil", width="stretch"):
        go_home()
        st.rerun()
        
    st.divider()
    
    nb_articles = len(st.session_state.panier)
    if nb_articles > 0:
        if st.button(f"🛒 Mon Panier ({nb_articles})", width="stretch", type="primary"):
            st.session_state.page = 'panier'
            st.rerun()
    else:
        if st.button("🛒 Mon Panier (0)", width="stretch"):
            st.session_state.page = 'panier'
            st.rerun()
            
    st.divider()
    st.markdown("### 📂 Catégories")
    if st.button("🌍 Sélections Nationales", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Nations']
        st.rerun()
    if st.button("🏟️ Clubs", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Clubs']
        st.rerun()
    if st.button("🎲 Matchs de Gala", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Divers']
        st.rerun()
        
    st.divider()
    st.markdown("### 🌟 Nouveautés & Objectifs")
    if st.button("✨ Dernières Pépites", width="stretch"):
        st.session_state.page = 'dernieres_pepites'
        st.rerun()
    if st.button("🎯 Progression Collection", width="stretch"):
        st.session_state.page = 'progression'
        st.rerun()
        
    st.divider()
    st.markdown("### 🤝 Échanges & Requêtes")
    if st.button("🔎 Mes Recherches", width="stretch"):
        st.session_state.page = 'mes_recherches'
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
    st.markdown("<h1 style='text-align: center;'>⚽ Le Grenier du Football</h1>", unsafe_allow_html=True)
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
    
    with st.container(border=True):
        c_txt, c_btn = st.columns([3, 1])
        with c_txt:
            st.markdown("<h4 style='margin-top:0px; margin-bottom:5px;'>🚨 Vous possédez vos propres archives ?</h4>", unsafe_allow_html=True)
            st.markdown("Je suis constamment à la recherche de nouveaux matchs pour compléter le Grenier. Découvrez ma liste de recherches et proposons-nous des échanges !")
        with c_btn:
            st.write("") 
            if st.button("🔎 Voir mes recherches", use_container_width=True, type="primary"):
                st.session_state.page = 'mes_recherches'
                st.rerun()
                
    st.write("---")
    
    st.markdown("### 📂 Explorer le Classeur")
    st.markdown("<p style='color: gray; margin-bottom: 15px;'>Sélectionnez une catégorie pour naviguer dans l'arborescence des archives.</p>", unsafe_allow_html=True)
    
    col_n, col_c, col_d = st.columns(3)
    with col_n:
        if st.button("🌍 SÉLECTIONS NATIONALES", width="stretch", type="primary"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Nations']
            st.rerun()
    with col_c:
        if st.button("🏟️ CLUBS", width="stretch", type="primary"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Clubs']
            st.rerun()
    with col_d:
        if st.button("🎲 MATCHS DE GALA", width="stretch", type="primary"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Divers']
            st.rerun()

    st.write("---")

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
            if st.button("Voir les matchs du jour", width="stretch"):
                st.session_state.page = 'ephemeride'
                st.rerun()
        else:
            st.info(f"Que s'est-il passé un {date_affichee} ?")
            if st.button("Chercher autre date", width="stretch"):
                st.session_state.page = 'recherche_date'
                st.rerun()

# ==========================================
# PAGE : LE PANIER MAGIQUE (PRIX & CHOIX)
# ==========================================
elif st.session_state.page == 'panier':
    st.header("🛒 Mon Panier")
    
    if len(st.session_state.panier) == 0:
        st.info("Votre panier est vide pour le moment. Naviguez dans le catalogue pour ajouter des matchs !")
        if st.button("Retourner à l'accueil"):
            go_home()
            st.rerun()
    else:
        st.markdown(f"**Vous avez sélectionné {len(st.session_state.panier)} match(s).**")
        st.write("---")
        
        total_prix = 0
        liste_prix = []
        items_a_supprimer = []
        
        for i, match in enumerate(st.session_state.panier):
            col_info, col_fmt, col_btn = st.columns([5, 2, 1])
            
            date_m = match.get('Date', '?')
            comp_m = match.get('Compétition', '?')
            dom_m = match.get('Domicile', '')
            ext_m = match.get('Extérieur', '')
            qual_m = str(match.get('Qualité', '')).lower()
            
            with col_info:
                st.markdown(f"🗓️ **{date_m}** | 🏆 {comp_m}<br>⚔️ **{dom_m} - {ext_m}**", unsafe_allow_html=True)
            
            with col_fmt:
                if 'dvd' in qual_m or 'vob' in qual_m:
                    idx_actuel = 0 if match.get('format_choisi') == 'DVD' else 1
                    choix_fmt = st.selectbox(
                        "Format :", 
                        ["💿 DVD (5€)", "💻 Numérique (3€)"], 
                        key=f"fmt_sel_{i}",
                        index=idx_actuel
                    )
                    match['format_choisi'] = 'DVD' if 'DVD' in choix_fmt else 'Numérique'
                else:
                    st.markdown("<div style='margin-top: 30px; color: gray; font-size: 15px;'>💻 Numérique (3€)</div>", unsafe_allow_html=True)
                    match['format_choisi'] = 'Numérique'
                    
            with col_btn:
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                if st.button("❌ Retirer", key=f"del_cart_{i}"):
                    items_a_supprimer.append(i)
            
            st.divider()
            
            # Récupération des prix pour le calcul global
            prix_match = 5 if match['format_choisi'] == 'DVD' else 3
            total_prix += prix_match
            liste_prix.append(prix_match)
                
        # Exécution de la suppression si demandée
        if items_a_supprimer:
            for idx in sorted(items_a_supprimer, reverse=True):
                st.session_state.panier.pop(idx)
            st.rerun()
            
        # ==================================
        # CALCUL DE LA RÉDUCTION (Idée B)
        # ==================================
        nb_articles = len(st.session_state.panier)
        nb_gratuits = nb_articles // 11
        reduction = 0
        
        if nb_gratuits > 0:
            # On trie la liste des prix du moins cher au plus cher
            liste_prix.sort()
            # La réduction = la somme des 'x' matchs les moins chers
            reduction = sum(liste_prix[:nb_gratuits])
            
        total_final = total_prix - reduction
        
        st.subheader("💳 Récapitulatif")
        st.markdown(f"**Sous-total :** {total_prix} €")
        
        if reduction > 0:
            st.success(f"🎁 **Offre Spéciale :** La valeur de vos {nb_gratuits} match(s) offert(s) a été déduite ! (-{reduction} €)")
            
        st.markdown(f"### **Total à payer : {total_final} €**")
        st.write("---")
        
        st.write("---")
        st.subheader("📩 Valider ma commande")
        st.markdown("Choisissez votre méthode préférée pour m'envoyer votre sélection :")
        
        # Génération du texte récapitulatif
        texte_recap = "Bonjour, je souhaite commander ces matchs vus dans Le Grenier :\n\n"
        for match in st.session_state.panier:
            fmt_r = match.get('format_choisi', 'Numérique')
            texte_recap += f"- [{fmt_r}] {match.get('Date', '?')} | {match.get('Domicile', '')} vs {match.get('Extérieur', '')} ({match.get('Compétition', '?')})\n"
        
        texte_recap += f"\nTotal d'articles : {nb_articles}"
        if reduction > 0:
            texte_recap += f"\nRéduction appliquée : -{reduction}€ (Règle du moins cher offert)"
        texte_recap += f"\nMontant Total : {total_final}€"
        texte_recap += "\n\nMerci de me donner les détails pour le paiement !"

        # --- LES DEUX COLONNES D'ENVOI ---
        col_mail, col_copy = st.columns(2)
        
        with col_mail:
            with st.container(border=True):
                st.markdown("<h4 style='text-align: center;'>📧 Option 1 : Par E-mail</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Votre application d'e-mail va s'ouvrir automatiquement avec le récapitulatif.</p>", unsafe_allow_html=True)
                
                # Encodage du mail pour le bouton
                sujet_mail = "Nouvelle commande - Le Grenier du Football"
                lien_mailto = f"mailto:legrenierdufootball@hotmail.com?subject={urllib.parse.quote(sujet_mail)}&body={urllib.parse.quote(texte_recap)}"
                
                st.link_button("🚀 Envoyer ma commande par E-mail", lien_mailto, use_container_width=True)

        with col_copy:
            with st.container(border=True):
                st.markdown("<h4 style='text-align: center;'>💬 Option 2 : Par Message Privé</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Copiez le texte ci-dessous et envoyez-le moi sur les réseaux sociaux.</p>", unsafe_allow_html=True)
                st.code(texte_recap, language="text")
                
        st.write("")
        if st.button("🗑️ Vider tout le panier", type="secondary"):
            st.session_state.panier = []
            st.rerun()

# ==========================================
# PAGE : MES RECHERCHES (WANTED)
# ==========================================
elif st.session_state.page == 'mes_recherches':
    st.header("🔎 Mes Recherches Actuelles")
    st.markdown("<p style='color: gray; font-size:16px;'>Vous avez ces trésors dans vos disques durs ou vos cartons ? Contactez-moi pour un échange !</p>", unsafe_allow_html=True)
    st.divider()

    col_milan, col_france = st.columns(2)

    with col_milan:
        st.markdown("""
        <div style='background-color: #2b1111; padding: 25px; border-radius: 15px; border: 2px solid #e32221; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);'>
            <div style='text-align: center;'>
                <h2 style='color: #ffffff; margin-bottom: 5px; font-weight: 800;'>🔴⚫ AC Milan</h2>
            </div>
            <hr style='border-color: #e32221; margin-top: 15px; margin-bottom: 20px;'>
            <div style='color: white; line-height: 1.8; font-size: 15px;'>
                <p><b>🔴⚫ Tifoso du Milan</b> (plus de 600 matchs dans ma collection)</p>
                <p>Je cherche en continu de nouvelles vidéos pour étoffer ma collection : matchs complets toutes compétitions confondues (versions française ou italienne uniquement).</p>
                <p>🎥 Si vous possédez des enregistrements du Milan, je suis preneur.</p>
                <p>📩 Contactez-moi en DM pour proposer un échange ou une vente.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_france:
        st.markdown("""
        <div style='background-color: #0b2340; padding: 25px; border-radius: 15px; border: 2px solid #1a5fb4; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);'>
            <div style='text-align: center;'>
                <h2 style='color: #ffffff; margin-bottom: 5px; font-weight: 800;'>Mondial 1998 (France 98)</h2>
            </div>
            <hr style='border-color: #1a5fb4; margin-top: 15px; margin-bottom: 20px;'>
            <div style='color: white; line-height: 1.8; font-size: 15px;'>
                <p><b>✨ Projet France 98 :</b> construire l’archive idéale.</p>
                <p>Mon but : je cherche à réunir les 64 matchs du tournoi en meilleure qualité possible, avec toutes les versions TV françaises (TF1, France TV, Canal+, Eurosport...). Il m'en manque encore !!!</p>
                <p>🎞️ Matchs complets, résumés, magazines : tout m’intéresse.</p>
                <p>🗂️ Je recherche aussi les avant/après-match et émissions spéciales.</p>
                <p>📩 Contactez-moi en DM pour proposer un échange ou une vente.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE : DERNIÈRES PÉPITES
# ==========================================
elif st.session_state.page == 'dernieres_pepites':
    st.header("✨ Les Dernières Pépites")
    st.markdown("<p style='color: gray; font-size:16px;'>Voici les 10 derniers matchs tout fraîchement ajoutés au Grenier.</p>", unsafe_allow_html=True)
    df_derniers = df.tail(10).iloc[::-1]
    afficher_resultats(df_derniers)

# ==========================================
# PAGE : PROGRESSION DE LA COLLECTION
# ==========================================
elif st.session_state.page == 'progression':
    st.header("🎯 Progression de la Collection")
    st.divider()

    if 'Phase' in df.columns:
        mask_finale = df['Phase'].astype(str).str.strip().str.lower().isin(['finale', 'final'])
        mask_cdm = df['Compétition'].str.contains("Coupe du Monde", na=False, case=False) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
        cdm_possedees = df[mask_cdm & mask_finale]['Compétition'].nunique()
        total_cdm = 22
        pct_cdm = min(100, int((cdm_possedees / total_cdm) * 100))

        mask_euro = df['Compétition'].str.contains("Euro|Championnat d'Europe", na=False, case=False, regex=True) & ~df['Compétition'].str.contains("Eliminatoires", na=False, case=False)
        euro_possedees = df[mask_euro & mask_finale]['Compétition'].nunique()
        total_euro = 17
        pct_euro = min(100, int((euro_possedees / total_euro) * 100))

        mask_c1 = df['Compétition'].str.contains("Champions League|Coupe d'Europe des clubs champions", na=False, case=False)
        c1_possedees = df[mask_c1 & mask_finale]['Saison'].nunique() if 'Saison' in df.columns else len(df[mask_c1 & mask_finale])
        total_c1 = 69
        pct_c1 = min(100, int((c1_possedees / total_c1) * 100))

        col_prog1, col_prog2, col_prog3 = st.columns(3)
        with col_prog1:
            st.markdown(f"**Coupe du Monde** ({cdm_possedees}/{total_cdm})")
            st.progress(pct_cdm / 100.0, text=f"{pct_cdm}% des Finales")
        with col_prog2:
            st.markdown(f"**Euro** ({euro_possedees}/{total_euro})")
            st.progress(pct_euro / 100.0, text=f"{pct_euro}% des Finales")
        with col_prog3:
            st.markdown(f"**Ligue des Champions** ({c1_possedees}/{total_c1})")
            st.progress(pct_c1 / 100.0, text=f"{pct_c1}% des Finales")
            
        st.write("---")
        eds_cdm = df[mask_cdm]['Compétition'].nunique()
        eds_euro = df[mask_euro]['Compétition'].nunique()
        
        st.markdown(f"**Éditions de Coupe du Monde :** {eds_cdm}/{total_cdm}")
        st.progress(min(1.0, eds_cdm/total_cdm))
        st.write("")
        st.markdown(f"**Éditions d'Euro :** {eds_euro}/{total_euro}")
        st.progress(min(1.0, eds_euro/total_euro))
    else:
        st.warning("La colonne 'Phase' n'est pas présente dans votre fichier pour calculer les finales.")

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
    
    idx_defaut = 0
    cible = st.session_state.get('recherche_equipe_cible')
    if cible and cible in toutes_les_equipes:
        idx_defaut = toutes_les_equipes.index(cible)
        
    choix = st.selectbox("Sélectionne une équipe :", toutes_les_equipes, index=idx_defaut)
    st.session_state.recherche_equipe_cible = choix 
    
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
    
    toutes_les_equipes = sorted(pd.concat([df['Domicile'], df['Extérieur']]).dropna().astype(str).unique())
    competitions = sorted(df['Compétition'].dropna().astype(str).unique()) if 'Compétition' in df.columns else []
    phases = sorted(df['Phase'].dropna().astype(str).unique()) if 'Phase' in df.columns else []
    stades = sorted(df['Stade'].dropna().astype(str).unique()) if 'Stade' in df.columns else []
    saisons = sorted(df['Saison'].dropna().astype(str).unique(), reverse=True) if 'Saison' in df.columns else []
    
    def_comp = []
    cible_comp = st.session_state.get('recherche_comp_cible')
    if cible_comp and cible_comp in competitions:
        def_comp = [cible_comp]
    
    col1, col2 = st.columns(2)
    with col1:
        f_equipes = st.multiselect("🛡️ Équipes impliquées :", toutes_les_equipes)
    with col2:
        f_comps = st.multiselect("🏆 Compétitions :", competitions, default=def_comp)
        
    col3, col4, col5 = st.columns(3)
    with col3:
        f_phases = st.multiselect("⏱️ Phase (ex: Finale, 1/8) :", phases) if phases else []
    with col4:
        f_stades = st.multiselect("🏟️ Stade :", stades) if stades else []
    with col5:
        f_saisons = st.multiselect("🗓️ Saisons :", saisons) if saisons else []
        
    df_filtre = df.copy()
    if f_equipes: df_filtre = df_filtre[df_filtre['Domicile'].isin(f_equipes) | df_filtre['Extérieur'].isin(f_equipes)]
    if f_comps: df_filtre = df_filtre[df_filtre['Compétition'].isin(f_comps)]
    if f_phases: df_filtre = df_filtre[df_filtre['Phase'].isin(f_phases)]
    if f_stades: df_filtre = df_filtre[df_filtre['Stade'].isin(f_stades)]
    if f_saisons: df_filtre = df_filtre[df_filtre['Saison'].isin(f_saisons)]
        
    st.write("---")
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

