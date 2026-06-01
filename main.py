import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re
import base64
import urllib.parse
import plotly.express as px
import smtplib
from email.mime.text import MIMEText

# 1. Configuration de la page (Optimisée SEO)
st.set_page_config(page_title="Le Grenier du Football | Archives & Matchs de Foot Rétro en Vidéo", layout="wide")

# --- LECTURE DU LOGO LGF ---
@st.cache_data
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
    **Bienvenue dans l'antre du Grenier du Football !** Près de 5000 matchs au chaud : des classiques, des raretés, des “je l’avais oublié celui-là !”. Du foot vintage, numérisé à partir de VHS, aux saisons plus récentes… et on n’a pas fini de fouiller.
    
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
    * 🩹 **Remise "Archive Imparfaite" (-1 €) :** Si un match présente un défaut lié à l'usure du temps (qualité altérée, fichier incomplet...), une remise de 1€ est automatiquement déduite dans votre panier.
    * 🔄 **Offre cumulable :** 2 matchs offerts pour 20 achetés, 3 pour 30, etc.
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
            "Coupe Intercontinentalale": "Coupe intercontinentale",
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
        df = pd.read_csv("matchs.csv", sep=";", encoding="utf-8-sig", dtype={'Score': str})
        df.columns = df.columns.str.strip()

        df = df.dropna(subset=['Saison', 'Compétition'], how='all')
        
        df['Domicile'] = df['Domicile'].fillna("Multiplex / Divers")
        df['Extérieur'] = df['Extérieur'].fillna("-")
        df['Score'] = df['Score'].fillna("-")
        df['Stade'] = df['Stade'].fillna("Plusieurs stades")
        
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
        
        df_display = df_resultats[colonnes_presentes].copy()
        df_display.insert(0, "Sélection", False)
        
        edited_df = st.data_editor(
            df_display,
            column_config={
                "Sélection": st.column_config.CheckboxColumn("🛒 Ajouter", default=False)
            },
            disabled=colonnes_presentes,
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
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
                    
                    # --- TAGS VISUELS ---
                    if has_diff or has_qual:
                        html_footer = "<div style='text-align: center; margin-top:12px; border-top: 0.5px solid #444; padding-top:8px;'>"
                        if has_diff:
                            html_footer += f"<span style='background-color:#1E3A8A; color:white; padding: 4px 10px; border-radius: 12px; font-size:12px; margin-right:8px; font-weight:500;'>📺 {diffuseur}</span>"
                        if has_qual:
                            couleur_q = "#8B5A2B" if "dvd" in qualite.lower() or "vob" in qualite.lower() else "#4B5563"
                            html_footer += f"<span style='background-color:{couleur_q}; color:white; padding: 4px 10px; border-radius: 12px; font-size:12px; font-weight:500;'>💾 {qualite}</span>"
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
    st.markdown("<h2 style='text-align: center;'>📺 Menu Rapide</h2>", unsafe_allow_html=True)
    st.write("")
    
    if st.button("🏠 Accueil", use_container_width=True):
        go_home()
        st.rerun()
                
    if st.button("❓ F.A.Q & Infos", use_container_width=True):
        st.session_state.page = 'faq'
        st.rerun()

    if st.button("📱 Le Grenier sur mobile", use_container_width=True):
        popup_raccourci_mobile() 

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
        
    # --- GESTION DU PANIER & JAUGE DE PROGRESSION ---
    nb_articles = len(st.session_state.panier)
    if nb_articles > 0:
        if st.button(f"🛒 Mon Panier ({nb_articles})", use_container_width=True, type="primary"):
            st.session_state.page = 'panier'
            st.rerun()
            
        # Logique de calcul de l'offre commerciale (10 payants + 1 offert = cycles de 11)
        nb_cadeaux_inclus = nb_articles // 11
        matchs_dans_cycle_actuel = nb_articles % 11
        st.write("") 
        
        if matchs_dans_cycle_actuel == 10:
            st.markdown("🎁 **Pack Complété !** Le prochain match ajouté à votre panier sera **100% GRATUIT** !")
            st.progress(1.0)
        elif nb_cadeaux_inclus > 0 and matchs_dans_cycle_actuel == 0:
            st.success(f"🎉 **Offre Activée !** Votre panier inclut déjà **{nb_cadeaux_inclus} match(s) gratuit(s)** !")
            st.progress(0.0)
            st.caption("Ajoutez 10 matchs de plus pour débloquer un autre cadeau !")
        else:
            matchs_restants = 10 - matchs_dans_cycle_actuel
            pourcentage_jauge = matchs_dans_cycle_actuel / 10
            st.markdown(f"🔥 Plus que **{matchs_restants}** match(s) avant votre **match offert** !")
            st.progress(pourcentage_jauge)
            if nb_cadeaux_inclus > 0:
                st.caption(f"✨ Vous profitez déjà de {nb_cadeaux_inclus} match(s) offert(s) dans cette commande.")
    else:
        if st.button("🛒 Mon Panier (0)", use_container_width=True):
            st.session_state.page = 'panier'
            st.rerun()
        st.write("")
        st.info("💡 **Profitez de l'offre !** Ajoutez 10 matchs pour repartir avec **1 match gratuit**.")
            
    st.divider()
    st.markdown("""
    <h3 style='margin-bottom: -10px;'>📂 Catégories</h3>
    
    <style>
    div.element-container:has(.css-nations) + div.element-container button {
        background-color: #b8860b !important; border-color: #b8860b !important;
    }
    div.element-container:has(.css-nations) + div.element-container button:hover {
        background-color: #8b6508 !important; border-color: #8b6508 !important;
    }
    div.element-container:has(.css-nations) + div.element-container button p { color: white !important; font-weight: 500;}

    div.element-container:has(.css-europe) + div.element-container button {
        background-color: #1a2b4c !important; border-color: #1a2b4c !important;
    }
    div.element-container:has(.css-europe) + div.element-container button:hover {
        background-color: #101a2e !important; border-color: #101a2e !important;
    }
    div.element-container:has(.css-europe) + div.element-container button p { color: white !important; font-weight: 500;}

    div.element-container:has(.css-champ) + div.element-container button {
        background-color: #722f37 !important; border-color: #722f37 !important;
    }
    div.element-container:has(.css-champ) + div.element-container button:hover {
        background-color: #4a1e23 !important; border-color: #4a1e23 !important;
    }
    div.element-container:has(.css-champ) + div.element-container button p { color: white !important; font-weight: 500;}

    div.element-container:has(.css-amicaux) + div.element-container button {
        background-color: #5b7c6c !important; border-color: #5b7c6c !important;
    }
    div.element-container:has(.css-amicaux) + div.element-container button:hover {
        background-color: #435b4f !important; border-color: #435b4f !important;
    }
    div.element-container:has(.css-amicaux) + div.element-container button p { color: white !important; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="css-nations" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🌍 Nations (Mondial, Euro...)", use_container_width=True):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Nations']
        st.rerun()
        
    st.markdown('<div class="css-europe" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🏆 Coupes d'Europe (LDC...)", use_container_width=True):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ["Coupes d'Europe"]
        st.rerun()
        
    st.markdown('<div class="css-champ" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🏟️ Championnats & Coupes", use_container_width=True):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Championnats & Coupes']
        st.rerun()
        
    st.markdown('<div class="css-amicaux" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)
    if st.button("🤝 Amicaux Internationaux", use_container_width=True):
        st.session_state.page = 'arborescence'
        st.session_state.chemin = ['Amicaux Internationaux']
        st.rerun()
        
    st.divider()
    st.markdown("### 🌟 Nouveautés")
    if st.button("✨ Archives Dépoussiérées", use_container_width=True):
        st.session_state.page = 'pepites'
        st.rerun()
    if st.button("🎯 Progression Collection", use_container_width=True):
        st.session_state.page = 'progression'
        st.rerun()
        
    st.divider()
    st.markdown("### 🤝 Échanges & Requêtes")
    if st.button("🔎 Mes Recherches", use_container_width=True):
        st.session_state.page = 'mes_recherches'
        st.rerun()
        
    st.divider()
    st.markdown("### 🔍 Outils")
    if st.button("📖 Catalogue Complet", use_container_width=True):
        st.session_state.page = 'catalogue'
        st.rerun()
    if st.button("📊 Statistiques", use_container_width=True):
        st.session_state.page = 'statistiques'
        st.rerun()
    if st.button("🛡️ Par Équipe", use_container_width=True):
        st.session_state.page = 'recherche_equipe'
        st.rerun()
    if st.button("⚔️ Face-à-Face", use_container_width=True):
        st.session_state.page = 'face_a_face'
        st.rerun()
    if st.button("🕵️ Recherche Avancée", use_container_width=True):
        st.session_state.page = 'recherche_avancee'
        st.rerun()

# ==========================================
# PAGE : ACCUEIL
# ==========================================
if st.session_state.page == 'accueil':

    st.markdown("""
    <style>
    @media (max-width: 768px) {
        h1 { 
            flex-direction: column !important; 
            gap: 10px; 
        }
        h1 img { 
            width: 80px !important; 
            margin-right: 0 !important; 
        }
        h1 span { 
            font-size: 26px !important; 
            text-align: center; 
            white-space: normal !important;
        }
        div[style*="max-width: 850px"] { 
            font-size: 14px !important; 
            padding: 0 10px; 
        }
        div[data-testid="stVerticalBlock"] > div:has(button) {
            padding-bottom: 0px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    if logo_b64:
        logo_html = f"<img src='data:image/png;base64,{logo_b64}' style='width: 120px; vertical-align: middle; margin-right: 0px; border-radius: 80%;'>"
    else:
        logo_html = "⚽ "

    # --- TEXTE OPTIMISÉ SEO ---
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 10px;'>
            <h1 style='margin-bottom: 0px; display: flex; align-items: center; justify-content: center; line-height: 1;'>
                {logo_html}
                <span>Le Grenier du Football</span>
            </h1>
            <div style='max-width: 850px; margin: 0 auto; line-height: 1.6; font-size: 16px; color: #fafafa; margin-top: 15px;'>
                Découvrez un grand choix d'<b>archives de matchs de football rétro</b>. Explorez un catalogue interactif de près de <b>5000 matchs classiques</b>, numérisés à partir de véritables <b>cassettes VHS et DVD</b>.<br><br>
                Revivez en vidéo les rencontres historiques de la <i>Coupe du Monde</i>, de la <i>Ligue des Champions</i> et des grands championnats européens. De l'Équipe de France aux clubs de légende, l'Histoire du foot est ici.<br><br>
                <b>Téléchargez vos matchs vintage préférés, complétez votre collection, ou proposez vos propres vidéos pour un échange entre passionnés.</b>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
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

    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
        background-color: #2e7d32 !important; border-color: #2e7d32 !important; transition: all 0.3s ease;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button p { color: #ffffff !important; font-weight: 600 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button:hover {
        background-color: #1b5e20 !important; border-color: #1b5e20 !important; transform: scale(1.02);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {
        background-color: #1565c0 !important; border-color: #1565c0 !important; transition: all 0.3s ease;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button p { color: #ffffff !important; font-weight: 600 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button:hover {
        background-color: #0d47a1 !important; border-color: #0d47a1 !important; transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)
