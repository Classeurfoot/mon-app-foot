import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re
import base64
import urllib.parse
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(page_title="Le Grenier du Football", layout="wide")

# --- LECTURE DU LOGO LGF ---
@st.cache_data   # <-- LA LIGNE MAGIQUE À AJOUTER ICI
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

logo_b64 = get_base64_image("logo.png")
# ---------------------------

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
@st.dialog("🧭 Guide & Contenu")
def popup_guide_contenu():
    st.markdown("""
    **Bienvenue dans l'antre du Grenier du Football !** Plus de 4000 matchs au chaud : des classiques, des raretés, des “je l’avais oublié celui-là !”. Du foot vintage, numérisé à partir de VHS, aux saisons plus récentes… et on n’a pas fini de fouiller.
    
    **Dans ce catalogue :**
    * 🌍 Des **matchs de clubs** et de **sélections nationales**.
    * 🏆 Les grandes **compétitions internationales** : Coupe du Monde, Euro, Copa America, Jeux Olympiques...
    * ✨ Les **Coupes d'Europe** : Ligue des Champions, Coupe UEFA, Coupe des Coupes...
    * 🥇 Les **grands championnats** : Ligue 1, Serie A, Liga, Premier League...
    * 🕰️ Des matchs **amicaux, historiques et rares**.
    ---
    ### 🛠️ Mode d'emploi : Comment fouiller les archives ?
    
    Pour explorer ce catalogue massif, deux affichages s'offrent à vous (sélectionnables juste au-dessus des listes de matchs) :
    
    * 📊 **Le Tableau classique :** Idéal pour une recherche rapide. C'est une vue condensée qui vous permet de trier facilement les colonnes (par année, compétition, etc.).
    * 📇 **Les Fiches détaillées :** La vue parfaite pour les puristes ! Plongez dans les détails de chaque match de manière beaucoup plus visuelle et aérée.
    
    💡 **L'astuce secrète :** Dans la vue "Fiches détaillées", **les petites étiquettes des clubs et compétitions sont interactives !** Cliquez simplement sur "Marseille" ou "Coupe du Monde" sur une fiche, et le site filtrera instantanément tout l'historique de cette équipe ou de ce tournoi. Bonne fouille !
    """)

@st.dialog("💾 Formats & Organisation")
def popup_formats():
    st.markdown("### 🗂️ Données répertoriées")
    st.markdown("""
    * #️⃣ Numéro du match dans le grenier
    * 🗓️ Date et saison du match
    * 🏆 Compétition et phase
    * 🏟️ Lieu et stade
    * 📺 Diffuseur d'origine (TF1, Canal+, etc.)
    * 🎙️ Langue des commentaires
    * 📼 Qualité (DVD, MP4,...)
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
    * 🩹 **Remise "Archive Imparfaite" (-1 €) :** Si un match présente un défaut lié à l'usure du temps (qualité altérée, fichier incomplet...), une remise de 1€ est automatiquement déduite dans votre panier. Le prix de l'authenticité !
    * 🔄 **Offre cumulable :** 2 matchs offerts pour 20 achetés, 3 pour 30, etc.
    * 📦 **Packs thématiques** disponibles sur demande (ex : France 98, parcours européens...).
    """)

@st.dialog("✉️ Contact & Commandes")
def popup_contact_commandes():
    st.markdown("""
    **Comment valider votre commande ?**
    * 🛒 **Le Panier :** Une fois votre sélection terminée, envoyez simplement le récapitulatif de votre panier par e-mail à **legrenierdufootball@hotmail.com** ou en Message Privé sur Instagram **[@legrenierdufootball](https://www.instagram.com/legrenierdufootball/)**.
    * 💳 **Le Paiement :** À réception de votre message, je vous répondrai avec les instructions pour procéder au paiement sécurisé via **PayPal**.
    * 🚀 **La Livraison :** Dès validation du paiement, vos matchs sont envoyés rapidement et en toute sécurité via des plateformes de téléchargement.
    
    ---
    **Une question spécifique ?** Vous cherchez un match qui n'est pas (encore) dans le catalogue ? N'hésitez pas à m'écrire par e-mail ou via Instagram, je vous répondrai avec plaisir !
    """)

@st.dialog("🤝 Proposer un Échange")
def popup_echanges():
    st.markdown("""
    **Faisons grandir Le Grenier ensemble !** Je suis continuellement à la recherche de nouvelles archives pour sauvegarder le patrimoine footballistique. Si vous possédez vos propres enregistrements sur disques durs, DVD ou VHS, je suis très ouvert aux échanges !
    
    **Comment procéder ?**
    * 🔎 Consultez la section **"Mes Recherches"** dans le menu pour découvrir mes projets prioritaires actuels.
    * 📋 Envoyez-moi votre liste de matchs ou vos propositions par e-mail à **legrenierdufootball@hotmail.com** ou sur Instagram **[@legrenierdufootball](https://www.instagram.com/legrenierdufootball/)**.
    * 🔄 Nous pourrons alors convenir d'un échange équitable de fichiers numériques.
    """)

@st.dialog("📱 Le Grenier sur mobile")
def popup_raccourci_mobile():
    st.markdown("""
    ### Gardez le Grenier à portée de main !
    Vous pouvez ajouter un raccourci de ce site directement sur l'écran d'accueil de votre téléphone. Cela créera une icône pour y accéder en un clic.
    
    🍎 **Sur iPhone (Safari) :**
    1. Appuyez sur l'icône **Partager** (le carré avec une flèche vers le haut, en bas de l'écran).
    2. Faites défiler vers le bas et appuyez sur **Sur l'écran d'accueil**.
    3. Confirmez en appuyant sur **Ajouter**.

    🤖 **Sur Android (Chrome) :**
    1. Appuyez sur les **trois petits points** (en haut à droite).
    2. Appuyez sur **Ajouter à l'écran d'accueil**.
    3. Confirmez en appuyant sur **Ajouter**.
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
    "Coupes d'Europe": {
        "C1": ["Coupe d'Europe des clubs champions", "Champions League"],
        "C2": ["Coupe des Coupes"],
        "C3": ["Coupe Intertoto", "Coupe UEFA", "Europa League"],
        "C4": ["Europa Conference"],
        "Supercoupe d'Europe": "Supercoupe d'Europe"
    },
    "Championnats & Coupes": {
        "Tournois internationaux clubs": {
            "Coupe Intercontinentale": "Coupe intercontinentale",
            "Coupe du Monde des clubs de la FIFA": "Coupe du Monde des clubs de la FIFA",
            "Coupe du Monde des Clubs 2025": "Coupe du Monde des Clubs 2025"
        },
        "Championnat de France": ["Division 1", "Ligue 1", "Division 2", "Ligue 2"],
        "Coupe Nationale": ["Coupe de France", "Coupe de la Ligue", "Trophée des Champions"],
        "Championnats étrangers": {
            "Italie": ["Serie A", "Coppa Italia"],
            "Espagne": ["Liga", "Copa del Rey"],
            "Angleterre": ["Premier League", "FA Cup"],
            "Allemagne": ["Bundesliga"]
        }
    },
    "Amicaux Internationaux": {
        "Amical": ["Amical", "Opel Master Cup"],
        "Tournoi international": ["Tournoi Hassan II", "Kirin Cup"]
    }
}

# 3. Chargement des données
@st.cache_data
def load_data():
    try:
        # 1. Lecture avec le bon séparateur (;) et formatage du score en texte
        df = pd.read_csv("matchs.csv", sep=";", encoding="utf-8-sig", dtype={'Score': str})
        df.columns = df.columns.str.strip()

        # 2. CHASSE AUX FANTÔMES : On supprime les lignes 100% vides d'Excel
        df = df.dropna(subset=['Saison', 'Compétition'], how='all')
# --- NOUVEAU : SAUVETAGE DES MULTIPLEX ---
# On remplace les cases vides (NaN) par du texte pour que l'application ne les supprime pas
        df['Domicile'] = df['Domicile'].fillna("Multiplex / Divers")
        df['Extérieur'] = df['Extérieur'].fillna("-")
        df['Score'] = df['Score'].fillna("-")
        df['Stade'] = df['Stade'].fillna("Plusieurs stades")
# --- LIGNE DE DÉBOGAGE À AJOUTER ---
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
colonnes_possibles = ['Match','Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Langue', 'Qualité', 'Commentaires sur fichier']
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
    # On utilise une balise HTML (h2) pour centrer le texte et l'emoji
    st.markdown("<h2 style='text-align: center;'>📺 Menu Rapide</h2>", unsafe_allow_html=True)
    st.write("") # Ajoute un petit espace invisible pour bien aérer avant le bouton Accueil
    
    if st.button("🏠 Accueil", width="stretch"):
        go_home()
        st.rerun()
                
    # --- BOUTON F.A.Q ---
    if st.button("❓ F.A.Q & Infos", width="stretch"):
        st.session_state.page = 'faq'
        st.rerun()

        # --- BOUTON : Le Grenier sur mobile ---
    if st.button("📱 Le Grenier sur mobile", width="stretch"):
        popup_raccourci_mobile() # <-- LE BON NOM

    # --- NOUVEAU BOUTON INSTAGRAM (AVEC LE VRAI LOGO) ---
    st.markdown("""
        <a href="https://www.instagram.com/legrenierdufootball/" target="_blank" style="
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: transparent;
            border: 1px solid #555;
            border-radius: 8px;
            color: #fafafa;
            padding: 10px;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 10px;
            transition: 0.2s;
        " onmouseover="this.style.borderColor='#E1306C'; this.style.color='#E1306C';" onmouseout="this.style.borderColor='#555'; this.style.color='#fafafa';">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
            </svg>
            Rejoignez le Grenier
        </a>
    """, unsafe_allow_html=True)
        
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
    st.markdown("""
    <h3 style='margin-bottom: -10px;'>📂 Catégories</h3>
    
    <style>
    /* 1. NATIONS (Or Vieilli) */
    div.element-container:has(.css-nations) + div.element-container button {
        background-color: #b8860b !important; border-color: #b8860b !important;
    }
    div.element-container:has(.css-nations) + div.element-container button:hover {
        background-color: #8b6508 !important; border-color: #8b6508 !important;
    }
    div.element-container:has(.css-nations) + div.element-container button p { color: white !important; font-weight: 500;}

    /* 2. COUPES D'EUROPE (Bleu Nuit) */
    div.element-container:has(.css-europe) + div.element-container button {
        background-color: #1a2b4c !important; border-color: #1a2b4c !important;
    }
    div.element-container:has(.css-europe) + div.element-container button:hover {
        background-color: #101a2e !important; border-color: #101a2e !important;
    }
    div.element-container:has(.css-europe) + div.element-container button p { color: white !important; font-weight: 500;}

    /* 3. CHAMPIONNATS (Bordeaux) */
    div.element-container:has(.css-champ) + div.element-container button {
        background-color: #722f37 !important; border-color: #722f37 !important;
    }
    div.element-container:has(.css-champ) + div.element-container button:hover {
        background-color: #4a1e23 !important; border-color: #4a1e23 !important;
    }
    div.element-container:has(.css-champ) + div.element-container button p { color: white !important; font-weight: 500;}

    /* 4. AMICAUX (Vert Sauge) */
    div.element-container:has(.css-amicaux) + div.element-container button {
        background-color: #5b7c6c !important; border-color: #5b7c6c !important;
    }
    div.element-container:has(.css-amicaux) + div.element-container button:hover {
        background-color: #435b4f !important; border-color: #435b4f !important;
    }
    div.element-container:has(.css-amicaux) + div.element-container button p { color: white !important; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

    # --- 🔘 LES BOUTONS (AVEC LEURS MARQUEURS INVISIBLES) ---
    st.markdown('<div class="css-nations" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🌍 Nations (Mondial, Euro...)", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Nations']
        st.rerun()
        
    st.markdown('<div class="css-europe" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🏆 Coupes d'Europe (LDC...)", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ["Coupes d'Europe"]
        st.rerun()
        
    st.markdown('<div class="css-champ" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🏟️ Championnats & Coupes", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Championnats & Coupes']
        st.rerun()
        
    st.markdown('<div class="css-amicaux" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🤝 Amicaux Internationaux", width="stretch"):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Amicaux Internationaux']
        st.rerun()
        
    st.divider()
    st.markdown("### 🌟 Nouveautés")
    # --- ON RENOMME DANS LE THÈME DU GRENIER ---
    if st.button("✨ Archives Dépoussiérées", width="stretch"):
        st.session_state.page = 'pepites'
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
# PAGE : ACCUEIL
# ==========================================
if st.session_state.page == 'accueil':
    
    # 1. Préparation du Logo (Espace réduit à 10px)
    if logo_b64:
        logo_html = f"<img src='data:image/png;base64,{logo_b64}' style='width: 120px; vertical-align: middle; margin-right: 0px; border-radius: 80%;'>"
    else:
        logo_html = "⚽ "

    # 2. Affichage du bloc (Titre + Texte SEO fusionnés)
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 10px;'>
            <h1 style='margin-bottom: 0px; display: flex; align-items: center; justify-content: center; line-height: 1;'>
                {logo_html}
                <span>Le Grenier du Football</span>
            </h1>
            <div style='max-width: 850px; margin: 0 auto; line-height: 1.5; font-size: 16px; color: #fafafa;'>
                Découvrez un catalogue interactif de plus de <b>4000 matchs de foot rétro</b> en formats numérique et DVD.<br>
                Retrouvez les émotions de la <i>Coupe du Monde</i>, de la <i>Ligue des Champions</i> et des championnats historiques.<br>
                <b>Parcourez le classeur, commandez vos matchs vintage préférés ou proposez des échanges entre collectionneurs.</b>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # La suite de ton code (colonnes d'images...)
    col1, col2, col3 = st.columns(3)
    
    # La suite de ton code (colonnes d'images...)
    col1, col2, col3 = st.columns(3)
    
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

    # --- ASTUCE CSS POUR COLORER LES BOUTONS SPECIFIQUES ---
    st.markdown("""
    <style>
    /* 🟢 BOUTON COMMANDES (4ème colonne) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
        background-color: #2e7d32 !important;
        border-color: #2e7d32 !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover {
        background-color: #1b5e20 !important;
        border-color: #1b5e20 !important;
        transform: scale(1.02);
    }

    /* 🔵 BOUTON ÉCHANGES (5ème colonne) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {
        background-color: #1565c0 !important;
        border-color: #1565c0 !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button:hover {
        background-color: #0d47a1 !important;
        border-color: #0d47a1 !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

    # Rangée des 5 boutons d'informations
    col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
    with col_btn1:
        if st.button("🧭 Guide & Contenu", use_container_width=True):
            popup_guide_contenu()
    with col_btn2:
        if st.button("💾 Formats", use_container_width=True): popup_formats()
    with col_btn3:
        if st.button("💶 Tarifs", use_container_width=True): popup_tarifs()
    with col_btn4:
        # Pas besoin de mettre type="primary", le CSS s'en occupe !
        if st.button("✉️ Commandes", use_container_width=True): popup_contact_commandes()
    with col_btn5:
        if st.button("🤝 Échanges", use_container_width=True): popup_echanges()
            
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
    
    st.markdown("### 📂 Explorer le Grenier")
    
    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        # Marqueur invisible pour "Nations"
        st.markdown('<div class="css-nations" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
        if st.button("🌍 Nations (Mondial, Euro...)", use_container_width=True, key="btn_acc_nat"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Nations']
            st.rerun()
            
        # Marqueur invisible pour "Coupes d'Europe"
        st.markdown('<div class="css-europe" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
        if st.button("🏆 Coupes d'Europe (LDC...)", use_container_width=True, key="btn_acc_eur"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ["Coupes d'Europe"]
            st.rerun()

    with col_cat2:
        # Marqueur invisible pour "Championnats"
        st.markdown('<div class="css-champ" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
        if st.button("🏟️ Championnats & Coupes", use_container_width=True, key="btn_acc_champ"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Championnats & Coupes']
            st.rerun()
            
        # Marqueur invisible pour "Amicaux"
        st.markdown('<div class="css-amicaux" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
        if st.button("🤝 Amicaux Internationaux", use_container_width=True, key="btn_acc_ami"):
            st.session_state.page = 'arborescence'
            st.session_state.chemin = ['Amicaux Internationaux']
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
    # 🌟 NOUVEAU BLOC : LE COURRIER DES PASSIONNÉS
    # ==========================================
    st.write("---")
    st.markdown("### 🖋️ Le Courrier des Passionnés")
    st.markdown("<p style='color: gray; font-size: 15px;'>Quelques retours de collectionneurs qui ont déjà fouillé dans le Grenier...</p>", unsafe_allow_html=True)
    
    col_avis1, col_avis2, col_avis3 = st.columns(3)
    
    with col_avis1:
        st.info("⭐⭐⭐⭐⭐\n\n*« Échange parfait ! J'ai pu récupérer des vieux matchs de l'AC Milan introuvables ailleurs. Les fichiers VOB sont impeccables. Merci l'Archiviste ! »*\n\n**— Julien T. (Via Instagram)**")
        
    with col_avis2:
        st.success("⭐⭐⭐⭐⭐\n\n*« Site super sérieux. J'ai commandé 3 matchs de Coupe du Monde 98 en format MP4, lien reçu dans la journée. Qualité VHS au top pour la nostalgie. »*\n\n**— Marc94 (Via E-mail)**")
        
    with col_avis3:
        st.warning("⭐⭐⭐⭐⭐\n\n*« Une vraie mine d'or. J'ai proposé un échange avec mes propres archives, super contact et très pro. Je recommande les yeux fermés ! »*\n\n**— Seb_Collection (Via Facebook)**")

# ==========================================
# PAGE : LE PANIER MAGIQUE (PRIX & CHOIX)
# ==========================================
elif st.session_state.page == 'panier':
    st.header("🛒 Mon Panier")
    
    if len(st.session_state.panier) == 0:
        st.info("Votre panier est vide pour le moment. Naviguez dans le catalogue pour ajouter des matchs !")
        if st.button("Retourner à l'accueil"):
            st.session_state.page = 'accueil' # Correction mineure ici : go_home() n'était pas défini partout
            st.rerun()
    else:
        st.markdown(f"**Vous avez sélectionné {len(st.session_state.panier)} match(s).**")
        st.write("---")
        
        total_prix_base = 0
        total_remise_defauts = 0
        liste_prix = []
        items_a_supprimer = []
        
        for i, match in enumerate(st.session_state.panier):
            col_info, col_fmt, col_btn = st.columns([5, 2, 1])
            
            date_m = match.get('Date', '?')
            comp_m = match.get('Compétition', '?')
            dom_m = match.get('Domicile', '')
            ext_m = match.get('Extérieur', '')
            
            # --- ANALYSE DES FORMATS DISPONIBLES ---
            qual_m = str(match.get('Qualité', '')).lower()
            # On détecte s'il y a du format physique
            has_dvd = 'dvd' in qual_m or 'vob' in qual_m
            # On détecte s'il y a du format numérique (ajoute d'autres extensions si besoin)
            has_num = any(ext in qual_m for ext in ['mp4', 'mkv', 'avi', 'ts', 'numérique', 'mpeg', 'wmv', 'divx'])
            
            # Si la case est vide ou non reconnue, on force en numérique par défaut
            if not has_dvd and not has_num:
                has_num = True
            
            # --- DÉTECTION DU DÉFAUT (-1€) ---
            commentaire = str(match.get('Commentaires sur fichier', '')).strip()
            a_defaut = bool(commentaire and commentaire.lower() not in ['nan', 'none', ''])
            
            with col_info:
                st.markdown(f"🗓️ **{date_m}** | 🏆 {comp_m}<br>⚔️ **{dom_m} - {ext_m}**", unsafe_allow_html=True)
                if a_defaut:
                    st.markdown(f"<span style='color: #d97706; font-size: 13px;'>🩹 <i>Archive imparfaite : {commentaire}</i></span>", unsafe_allow_html=True)
            
            with col_fmt:
                # Étiquettes de prix adaptées
                p_dvd = 4 if a_defaut else 5
                p_num = 2 if a_defaut else 3
                lbl_dvd = f"💿 DVD ({p_dvd}€ au lieu de 5€)" if a_defaut else "💿 DVD (5€)"
                lbl_num = f"💻 Numérique ({p_num}€ au lieu de 3€)" if a_defaut else "💻 Numérique (3€)"

                # === LA NOUVELLE LOGIQUE D'AFFICHAGE ===
                if has_dvd and has_num:
                    # CAS 1 : Les deux formats sont détectés -> On offre le choix
                    idx_actuel = 0 if match.get('format_choisi') == 'DVD' else 1
                    choix_fmt = st.selectbox(
                        "Format :", 
                        [lbl_dvd, lbl_num], 
                        key=f"fmt_sel_{i}",
                        index=idx_actuel
                    )
                    match['format_choisi'] = 'DVD' if 'DVD' in choix_fmt else 'Numérique'
                    
                elif has_dvd and not has_num:
                    # CAS 2 : Uniquement DVD -> Texte figé
                    st.markdown(f"<div style='margin-top: 30px; font-weight: 500; font-size: 15px;'>{lbl_dvd}</div>", unsafe_allow_html=True)
                    match['format_choisi'] = 'DVD'
                    
                else:
                    # CAS 3 : Uniquement Numérique -> Texte figé
                    st.markdown(f"<div style='margin-top: 30px; font-weight: 500; font-size: 15px;'>{lbl_num}</div>", unsafe_allow_html=True)
                    match['format_choisi'] = 'Numérique'
                    
            with col_btn:
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                if st.button("❌ Retirer", key=f"del_cart_{i}"):
                    items_a_supprimer.append(i)
            
            st.divider()
            
            # --- CALCULS POUR CE MATCH ---
            prix_base = 5 if match['format_choisi'] == 'DVD' else 3
            prix_final_match = prix_base - 1 if a_defaut else prix_base
            
            total_prix_base += prix_base
            if a_defaut:
                total_remise_defauts += 1
                
            liste_prix.append(prix_final_match)
                
        # Exécution de la suppression si demandée
        if items_a_supprimer:
            for idx in sorted(items_a_supprimer, reverse=True):
                st.session_state.panier.pop(idx)
            st.rerun()
            
        # ==================================
        # CALCUL DE LA RÉDUCTION (Matchs Gratuits)
        # ==================================
        nb_articles = len(st.session_state.panier)
        nb_gratuits = nb_articles // 11
        reduction_gratuits = 0
        
        if nb_gratuits > 0:
            # On trie la liste des prix FINAUX du moins cher au plus cher
            liste_prix.sort()
            reduction_gratuits = sum(liste_prix[:nb_gratuits])
            
        total_final = total_prix_base - total_remise_defauts - reduction_gratuits
        
        # ==================================
        # AFFICHAGE DU RÉCAPITULATIF
        # ==================================
        st.subheader("💳 Récapitulatif")
        st.markdown(f"**Sous-total brut :** {total_prix_base} €")
        
        # Le fameux bloc Info Bleu pour les défauts
        if total_remise_defauts > 0:
            st.info(f"🩹 **Archive Imparfaite :** Une remise a été appliquée pour compenser l'usure du temps (qualité altérée, fichier incomplet...) sur vos bandes. (-{total_remise_defauts} €)")
            
        # Le bloc Vert pour la promo 10 = 1 offert
        if reduction_gratuits > 0:
            st.success(f"🎁 **Offre Spéciale :** La valeur de vos {nb_gratuits} match(s) offert(s) a été déduite ! (-{reduction_gratuits} €)")
            
        st.markdown(f"### **Total à payer : {total_final} €**")
        st.write("---")
        
        st.write("---")
        st.subheader("📩 Valider ma commande")
        st.markdown("Choisissez votre méthode préférée pour m'envoyer votre sélection :")
        
        # ==================================
        # GÉNÉRATION DE L'E-MAIL ET DU TEXTE DE COPIE
        # ==================================
        texte_recap = "Bonjour, je souhaite commander ces matchs vus dans Le Grenier :\n\n"
        for match in st.session_state.panier:
            fmt_r = match.get('format_choisi', 'Numérique')
            
            # Précision pour ton suivi perso dans le mail
            commentaire_mail = str(match.get('Commentaires sur fichier', '')).strip()
            a_defaut_mail = bool(commentaire_mail and commentaire_mail.lower() not in ['nan', 'none', ''])
            txt_defaut = " [Archive Imparfaite]" if a_defaut_mail else ""
            
            texte_recap += f"- [{fmt_r}]{txt_defaut} {match.get('Date', '?')} | {match.get('Domicile', '')} vs {match.get('Extérieur', '')} ({match.get('Compétition', '?')})\n"
        
        texte_recap += f"\nTotal d'articles : {nb_articles}"
        if total_remise_defauts > 0:
            texte_recap += f"\nRemise Archive Imparfaite : -{total_remise_defauts}€"
        if reduction_gratuits > 0:
            texte_recap += f"\nRéduction appliquée (11ème offert) : -{reduction_gratuits}€"
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
# PAGE : F.A.Q (FOIRE AUX QUESTIONS)
# ==========================================
elif st.session_state.page == 'faq':
    st.header("❓ Foire Aux Questions & Informations")
    st.markdown("<p style='color: gray; font-size:16px;'>Vous trouverez ici toutes les réponses concernant le fonctionnement du Grenier, la qualité des vidéos et les modalités de commande.</p>", unsafe_allow_html=True)
    st.write("---")

    with st.expander("📺 D'où proviennent toutes ces archives ?"):
        st.markdown("""
        Ces matchs sont le fruit de plusieurs années de passion, de numérisations personnelles (anciennes cassettes VHS, enregistrements TV d'époque) et d'échanges avec d'autres collectionneurs à travers le monde. Le Grenier du Football est avant tout un véritable travail de sauvegarde du patrimoine footballistique !
        """)

    with st.expander("🎞️ Quelle est la qualité vidéo des matchs ? Sont-ils en HD ?"):
        st.markdown("""
        L'honnêteté avant tout : la grande majorité des matchs d'avant 2005-2010 conservent le charme et le "grain" typique de leur époque. Il s'agit de diffusions standard (SD), de numérisations VHS ou de premiers DVD. Ce n'est pas de la 4K, c'est de l'Histoire pure dans son jus d'origine ! Les matchs plus récents sont, bien entendu, dans des résolutions supérieures.
        
        💡 **À savoir (DVD vs Numérique) :** Lorsqu'un match vous est proposé à la fois en format DVD et en format Numérique, **le format DVD offrira toujours la meilleure qualité d'image brute**, même pour les archives les plus anciennes. Le format numérique (mp4, mkv...) implique une compression vidéo pour réduire le poids du fichier, ce qui n'est pas le cas du format DVD (.VOB) qui conserve le flux vidéo intact.
        """)

    with st.expander("🎙️ Un match a plusieurs diffuseurs ou langues. Comment faire le bon choix ?"):
        st.markdown("""
        Il est fréquent qu'un match mythique soit disponible avec plusieurs choix de diffuseurs (TF1, Canal+, RAI...) et de langues de commentaires. 
        
        ⚠️ **Attention : ces versions ne sont pas toujours de la même qualité !** L'une peut provenir d'un DVD irréprochable avec des commentaires étrangers, tandis que l'autre peut être une numérisation VHS avec une image plus modeste, conservée uniquement pour la nostalgie des commentaires français d'époque.
        
        ✉️ **Mon conseil :** Pour éviter toute méprise, n'hésitez pas à me contacter par message avant de valider votre commande. Je pourrai vous renseigner précisément sur le trio **Diffuseur - Qualité - Langue** pour chaque version !
        """)

    with st.expander("🤝 Comment fonctionne un échange de matchs ?"):
        st.markdown("""
        C'est très simple ! Si vous avez des archives qui pourraient m'intéresser (jetez un œil à la rubrique **Mes Recherches**), envoyez-moi votre liste. Nous comparons nos catalogues, nous nous mettons d'accord sur un échange équitable (1 match contre 1 match, par exemple), et nous nous transmettons les fichiers numériques via des plateformes sécurisées.
        """)

    with st.expander("💳 Comment se passe le paiement pour une commande directe ? Est-ce sécurisé ?"):
        st.markdown("""
        Absolument. Une fois votre sélection faite via le panier, vous m'envoyez le récapitulatif. Je vous confirme rapidement la disponibilité de vos fichiers. Le règlement s'effectue ensuite de manière 100% sécurisée via **PayPal**. 
        """)

    with st.expander("⏳ Dans quel délai vais-je recevoir mes matchs après le paiement ?"):
        st.markdown("""
        Le Grenier du Football est géré par un passionné, il n'y a pas de robot d'envoi automatisé ! Une fois votre paiement validé, je prépare vos fichiers manuellement et vous envoie votre lien de téléchargement privé dans un délai très rapide, généralement **entre 24h et 48h maximum**.
        """)

    with st.expander("🔗 Combien de temps mes liens de téléchargement sont-ils valables ?"):
        st.markdown("""
        Les transferts se font via des plateformes sécurisées (*SwissTransfer, WeTransfer, GrosFichiers...*). Ces plateformes suppriment automatiquement les fichiers au bout d'un certain temps (généralement **entre 7 et 30 jours**). Il est donc indispensable de télécharger vos matchs rapidement à réception du lien et de les sauvegarder précieusement sur votre propre disque dur !
        """)
        
    st.write("---")
    st.info("💡 **Vous n'avez pas trouvé votre réponse ?** N'hésitez pas à me contacter directement par e-mail ou sur Instagram !")

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
# PAGE : ARCHIVES DÉPOUSSIÉRÉES (Anciennement Dernières Pépites)
# ==========================================
elif st.session_state.page == 'pepites':
    st.header("✨ Les Archives Dépoussiérées")
    st.markdown("<p style='color: gray; font-size:16px;'>Voici les 30 derniers matchs fraîchement exhumés des cartons et ajoutés au catalogue !</p>", unsafe_allow_html=True)
    st.write("---")
    
    # --- TRI INFAILLIBLE PAR ID DE MATCH ---
    # On trie simplement par le numéro d'ID (Match) du plus grand (récent) au plus petit (ancien)
    if 'Match' in df.columns:
        df_pepites = df.sort_values(by='Match', ascending=False).head(30)
    else:
        # Sécurité au cas où la colonne 'Match' serait renommée un jour
        df_pepites = df.tail(30).iloc[::-1]
        
    # On affiche les résultats
    afficher_resultats(df_pepites)
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

        mask_euro = df['Compétition'].str.contains(r"\bEuro\b|Championnat d'Europe", na=False, case=False, regex=True) & ~df['Compétition'].str.contains("Eliminatoires|Europa|Coupe d'Europe", na=False, case=False, regex=True)
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
# PAGE : CATALOGUE COMPLET
# ==========================================
elif st.session_state.page == 'catalogue':
    st.header("📚 Le Catalogue Complet")
    
    # --- PRÉPARATION DU TRI ---
    df_tri = df.copy()
    
    # On convertit temporairement la colonne Date en format date Python pour un tri réel
    # dayfirst=True est crucial car tes dates sont au format FR (JJ/MM/AAAA)
    df_tri['Date_Sort'] = pd.to_datetime(df_tri['Date'], dayfirst=True, errors='coerce')
    
    # --- LE TRI MULTI-CRITÈRES ---
    # 1. Saison (du plus récent au plus ancien)
    # 2. Compétition (ordre alphabétique)
    # 3. Date_Sort (chronologique au sein de la compétition)
    df_tri = df_tri.sort_values(
        by=['Saison', 'Compétition', 'Date_Sort'], 
        ascending=[True, True, True]
    )
    
    # On supprime la colonne temporaire avant l'affichage
    df_tri = df_tri.drop(columns=['Date_Sort'])
    
    afficher_resultats(df_tri)

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
    st.header("📊 Le Bilan de l'Inventaire")
    st.markdown("<p style='color: gray; font-size:16px;'>Plongez dans les archives du Grenier à travers ces infographies.</p>", unsafe_allow_html=True)
    st.write("---")

    # --- LIGNE 1 : ÉVOLUTION ET COMPÉTITIONS ---
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### ⏳ Les Époques Traversées")
        st.caption("L'évolution chronologique du catalogue, saison par saison.")
        # Compte le nombre de matchs par saison (trié chronologiquement)
        df_saisons = df['Saison'].dropna().value_counts().reset_index()
        df_saisons.columns = ['Saison', 'Nombre']
        df_saisons = df_saisons.sort_values('Saison')
        
        fig_saisons = px.line(df_saisons, x='Saison', y='Nombre', markers=True, 
                              color_discrete_sequence=['#8b5a2b']) # Marron vintage
        fig_saisons.update_layout(xaxis_title="", yaxis_title="Nombre de matchs")
        st.plotly_chart(fig_saisons, use_container_width=True)

    with c2:
        st.markdown("### 🌍 Le Profil des Compétitions")
        st.caption("La répartition entre clubs, nations et tournois.")
        # Répartition par Type de Compétition (Coupe du Monde, Amical, etc.)
        if 'Type Compétition' in df.columns:
            df_type = df['Type Compétition'].dropna().value_counts().reset_index()
            df_type.columns = ['Type', 'Nombre']
            
            fig_type = px.pie(df_type, values='Nombre', names='Type', hole=0.4,
                              color_discrete_sequence=px.colors.sequential.Oranges)
            fig_type.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_type, use_container_width=True)

    st.write("---")

    # --- LIGNE 2 : LES ÉQUIPES ET LES AFFICHES ---
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("### 🛡️ Les Locataires du Grenier")
        st.caption("Les 10 équipes les plus archivées.")
        # Combine Domicile et Extérieur
        equipes = pd.concat([df['Domicile'], df['Extérieur']])
        equipes = equipes[~equipes.isin(["Multiplex / Divers", "-"])]
        df_equipes = equipes.value_counts().head(10).reset_index()
        df_equipes.columns = ['Équipe', 'Apparitions']
        
        fig_equipes = px.bar(df_equipes, x='Apparitions', y='Équipe', orientation='h',
                             color='Apparitions', color_continuous_scale='Oranges')
        fig_equipes.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title="")
        st.plotly_chart(fig_equipes, use_container_width=True)

    with c4:
        st.markdown("### ⚔️ Les Classiques du Grenier")
        st.caption("Les 10 affiches les plus répertoriées.")
        # Astuce : On trie alphabétiquement "Dom" et "Ext" pour que "Milan - Inter" 
        # soit compté pareil que "Inter - Milan"
        def generer_affiche(row):
            dom = str(row.get('Domicile', '')).strip()
            ext = str(row.get('Extérieur', '')).strip()
            if dom in ["Multiplex / Divers", "-", ""] or ext in ["Multiplex / Divers", "-", ""]:
                return None
            equipes_triees = sorted([dom, ext])
            return f"{equipes_triees[0]} - {equipes_triees[1]}"
            
        df['Affiche'] = df.apply(generer_affiche, axis=1)
        df_affiches = df['Affiche'].dropna().value_counts().head(10).reset_index()
        df_affiches.columns = ['Affiche', 'Rencontres']
        
        fig_affiches = px.bar(df_affiches, x='Rencontres', y='Affiche', orientation='h',
                              color='Rencontres', color_continuous_scale='Reds')
        fig_affiches.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title="")
        st.plotly_chart(fig_affiches, use_container_width=True)

    st.write("---")

    # --- LIGNE 3 : DIFFUSEURS ET QUALITÉ ---
    c5, c6 = st.columns(2)

    with c5:
        st.markdown("### 📻 L'Audimat d'Époque")
        st.caption("Les chaînes de télévision d'origine les plus représentées.")
        # Les 10 diffuseurs les plus présents
        df_diff = df['Diffuseur'].dropna().value_counts().head(10).reset_index()
        df_diff.columns = ['Diffuseur', 'Matchs']
        
        fig_diff = px.pie(df_diff, values='Matchs', names='Diffuseur',
                          color_discrete_sequence=px.colors.sequential.RdBu)
        fig_diff.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_diff, use_container_width=True)

    with c6:
        st.markdown("### 📼 L'Inventaire Technique")
        st.caption("La répartition des supports et formats de conservation.")
        # La répartition des qualités techniques
        df_qual = df['Qualité'].dropna().value_counts().head(8).reset_index()
        df_qual.columns = ['Format', 'Quantité']
        
        fig_qual = px.bar(df_qual, x='Format', y='Quantité', text='Quantité',
                          color='Quantité', color_continuous_scale='gray')
        fig_qual.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_qual, use_container_width=True)
# ==========================================
# PAGE ARBORESCENCE (NAVIGATION DYNAMIQUE)
# ==========================================
elif st.session_state.page == 'arborescence':
    
    # --- 🎨 AJOUT DU CSS DYNAMIQUE POUR LES SOUS-MENUS ---
    if len(st.session_state.chemin) > 0:
        cat_principale = st.session_state.chemin[0]
        
        # Couleurs par défaut
        couleur_fond = "#333333" 
        couleur_survol = "#222222"
        
        # On repère la catégorie et on charge la bonne couleur
        if cat_principale == "Nations":
            couleur_fond, couleur_survol = "#b8860b", "#8b6508"
        elif cat_principale == "Coupes d'Europe":
            couleur_fond, couleur_survol = "#1a2b4c", "#101a2e"
        elif cat_principale == "Championnats & Coupes":
            couleur_fond, couleur_survol = "#722f37", "#4a1e23"
        elif cat_principale == "Amicaux Internationaux":
            couleur_fond, couleur_survol = "#5b7c6c", "#435b4f"

        # On applique le style à tous les boutons du sous-menu
        st.markdown(f"""
        <style>
        /* Cible les boutons situés dans la grille (les sous-menus) */
        div[data-testid="column"] div.stButton > button {{
            background-color: {couleur_fond} !important;
            border-color: {couleur_fond} !important;
            transition: all 0.2s ease;
        }}
        div[data-testid="column"] div.stButton > button p {{
            color: #ffffff !important;
            font-weight: 500;
        }}
        div[data-testid="column"] div.stButton > button:hover {{
            background-color: {couleur_survol} !important;
            border-color: {couleur_survol} !important;
            transform: scale(1.02); /* Petit effet de zoom élégant au survol */
        }}
        </style>
        """, unsafe_allow_html=True)
    
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
            elif noeud_actuel == "FILTER_EURO_FINALE": mask = df['Compétition'].str.contains(r"\bEuro\b|Championnat d'Europe", na=False, case=False, regex=True) & ~df['Compétition'].str.contains("Eliminatoires|Europa|Coupe d'Europe", na=False, case=False, regex=True)
            elif noeud_actuel == "FILTER_EURO_ELIM": mask = df['Compétition'].str.contains(r"Eliminatoires \bEuro\b|Eliminatoires Championnat d'Europe", na=False, case=False, regex=True)
            
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
                    # --- NOUVEAU : RECHERCHE DYNAMIQUE DU LOGO DE LA COMPÉTITION ---
                    cle_logo = nettoyer_nom_equipe(st.session_state.edition_choisie)
                    chemin_logo = DICTIONNAIRE_LOGOS_EQUIPES.get(cle_logo)
                    if chemin_logo and os.path.exists(chemin_logo):
                        st.image(chemin_logo, width=100)
                        
                df_final = df[df['Compétition'] == st.session_state.edition_choisie]
                afficher_resultats(df_final)
        else:
            c1, c2 = st.columns([4, 1])
            with c1: st.header(f"🏆 {noeud_actuel}")
            with c2:
                # --- NOUVEAU : RECHERCHE DYNAMIQUE DU LOGO DE LA COMPÉTITION ---
                cle_logo = nettoyer_nom_equipe(noeud_actuel)
                chemin_logo = DICTIONNAIRE_LOGOS_EQUIPES.get(cle_logo)
                if chemin_logo and os.path.exists(chemin_logo):
                    st.image(chemin_logo, width=100)
                    
            mask = df['Compétition'].str.contains(noeud_actuel, na=False, case=False)
            df_final = df[mask]
            afficher_resultats(df_final)

# ==========================================
# 🛑 PIED DE PAGE (FOOTER GLOBAL)
# ==========================================
st.write("---")

foot_a, foot_b = st.columns([1, 1])

with foot_a:
    st.markdown("<br><p style='color: gray; font-size: 14px;'>© 2026 - Le Grenier du Football<br><i>Archives pour passionnés.</i></p>", unsafe_allow_html=True)

with foot_b:
    st.markdown("**Le Bureau de l'Archiviste**")
    st.markdown("✉️ [legrenierdufootball@hotmail.com](mailto:legrenierdufootball@hotmail.com)")
    
    # Intégration des logos Instagram et Facebook
    st.markdown("""
        <div style="display: flex; gap: 15px; margin-top: 10px; align-items: center;">
            <a href="https://www.instagram.com/legrenierdufootball/" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="30" alt="Instagram">
            </a>
            <a href="https://www.facebook.com/profile.php?id=61584405236853" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="30" alt="Facebook">
            </a>
        </div>
    """, unsafe_allow_html=True)
















































