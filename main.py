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

# ==========================================
# 🥇 1. CONFIGURATION DE LA PAGE & STYLES
# ==========================================
st.set_page_config(
    page_title="Le Grenier du Football | Archives & Matchs de Foot Rétro en Vidéo", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection de styles globaux et sécurisation des boutons personnalisés
st.markdown("""
<style>
/* Alignement et styles mobiles */
@media (max-width: 768px) {
    h1 { flex-direction: column !important; gap: 10px; }
    h1 img { width: 80px !important; margin-right: 0 !important; }
    h1 span { font-size: 26px !important; text-align: center; white-space: normal !important; }
    div[style*="max-width: 850px"] { font-size: 14px !important; padding: 0 10px; }
}

/* Boutons de catégories de la barre latérale */
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

/* Boutons d'action ciblés pour l'accueil */
div.element-container:has(.btn-vert-cible) + div.element-container button {
    background-color: #2e7d32 !important; border-color: #2e7d32 !important; transition: all 0.3s ease;
}
div.element-container:has(.btn-vert-cible) + div.element-container button p { color: #ffffff !important; font-weight: 600 !important; }
div.element-container:has(.btn-vert-cible) + div.element-container button:hover {
    background-color: #1b5e20 !important; border-color: #1b5e20 !important; transform: scale(1.02);
}

div.element-container:has(.btn-bleu-cible) + div.element-container button {
    background-color: #1565c0 !important; border-color: #1565c0 !important; transition: all 0.3s ease;
}
div.element-container:has(.btn-bleu-cible) + div.element-container button p { color: #ffffff !important; font-weight: 600 !important; }
div.element-container:has(.btn-bleu-cible) + div.element-container button:hover {
    background-color: #0d47a1 !important; border-color: #0d47a1 !important; transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# --- ENCODAGE DU LOGO PRINCIPAL ---
@st.cache_data
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

logo_b64 = get_base64_image("logo.png")

# ==========================================
# ⚙️ 2. INITIALISATION DES ÉTATS (SESSION)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'chemin' not in st.session_state: st.session_state.chemin = []
if 'recherche_equipe_cible' not in st.session_state: st.session_state.recherche_equipe_cible = ""
if 'recherche_comp_cible' not in st.session_state: st.session_state.recherche_comp_cible = ""
if 'panier' not in st.session_state: st.session_state.panier = []

def go_home():
    st.session_state.page = 'accueil'
    st.session_state.chemin = []
    st.session_state.recherche_equipe_cible = ""
    st.session_state.recherche_comp_cible = ""

# ==========================================
# ⚙️ 3. POP-UPS INFORMATIVES (DIALOGS)
# ==========================================
@st.dialog("🧭 Guide & Contenu")
def popup_guide_contenu():
    st.markdown("""
    **Bienvenue dans l'antre du Grenier du Football !** Près de 5000 matchs au chaud : des classiques, des raretés, des “je l’avais oublié celui-là !”. Du foot vintage, numérisé à partir de VHS, aux saisons plus récentes… et on n’a pas fini de fouiller.
    
    ### 🛠️ Mode d'emploi : Comment fouiller les archives ?
    Pour explorer ce catalogue massif, deux affichages s'offrent à vous (sélectionnables juste au-dessus des listes de matchs) :
    * 📊 **Le Tableau classique :** Idéal pour une recherche rapide. C'est une vue condensée qui vous permet de trier facilement les colonnes (par année, compétition, etc.).
    * 📇 **Les Fiches détaillées :** La vue parfaite pour les puristes ! Plongez dans les détails de chaque match de manière beaucoup plus visuelle.
    
    💡 **L'astuce secrète :** Dans la vue "Fiches détaillées", **les petites étiquettes des clubs et compétitions sont interactives !** Cliquez simplement sur un club ou une compétition sur une fiche, et le site filtrera instantanément tout l'historique associé. Bonne fouille !
    """)

@st.dialog("💾 Formats & Organisation")
def popup_formats():
    st.markdown("""
    ### 🗂️ Données répertoriées
    * #️⃣ Numéro du match dans le grenier
    * 🗓️ Date et saison du match
    * 🏆 Compétition et phase
    * 🏟️ Lieu et stade
    * 📺 Diffuseur d'origine (TF1, Canal+, etc.)
    * 🎙️ Langue des commentaires
    * 📼 Qualité (DVD, MP4,...)
    
    ### 📼 Formats disponibles
    * 💻 **Numérique :** formats courants (.mp4, .avi, .mkv) – parfaits pour ordinateur, tablette ou TV.
    * 💿 **DVD :** fichiers .VOB stockés sur disque dur. *(⚠️ Note : Vous recevez les fichiers informatiques originaux, il n'y a pas d'envoi de DVD physique)*
    """)

@st.dialog("💶 Tarifs & Offres")
def popup_tarifs():
    st.markdown("""
    ### 💰 Grille Tarifaire
    * 💿 **1 match au format DVD** = **5 €**
    * 💻 **1 match au format Numérique** (mp4, mkv...) = **3 €**
    
    ### 🎁 Offres & Réductions
    * 🆓 **1 match offert** tous les 10 matchs achetés (le match le moins cher de votre sélection est automatiquement déduit à partir du 11ème match).
    * 🩹 **Remise "Archive Imparfaite" (-1 €) :** Si un match présente un défaut lié à l'usure du temps (qualité altérée, fichier incomplet...), une remise de 1€ est automatiquement appliquée.
    """)

@st.dialog("✉️ Contact & Commandes")
def popup_contact_commandes():
    st.markdown("""
    **Comment valider votre commande ?**
    * 🛒 **Le Panier :** Une fois votre sélection terminée, envoyez simplement le récapitulatif de votre panier par e-mail à **legrenierdufootball@hotmail.com** ou en Message Privé sur Instagram **[@legrenierdufootball](https://www.instagram.com/legrenierdufootball/)**.
    * 💳 **Le Paiement :** À réception de votre message, je vous répondrai avec les instructions pour procéder au paiement sécurisé via **PayPal**.
    * 🚀 **La Livraison :** Dès validation du paiement, vos matchs sont envoyés rapidement et en toute sécurité via des plateformes de téléchargement.
    """)

@st.dialog("🤝 Proposer un Échange")
def popup_echanges():
    st.markdown("""
    **Faisons grandir Le Grenier ensemble !** Je suis continuellement à la recherche de nouvelles archives pour sauvegarder le patrimoine footballistique. Si vous possédez vos propres enregistrements sur disques durs, DVD ou VHS, je suis très ouvert aux échanges !
    
    Consultez la section **"Mes Recherches"** dans le menu pour découvrir mes projets prioritaires actuels et contactez-moi par mail ou Instagram !
    """)

@st.dialog("📱 Le Grenier sur mobile")
def popup_raccourci_mobile():
    st.markdown("""
    ### Gardez le Grenier à portée de main !
    Vous pouvez ajouter un raccourci de ce site directement sur l'écran d'accueil de votre téléphone.
    
    🍎 **Sur iPhone (Safari) :** Appuyez sur **Partager** ➔ **Sur l'écran d'accueil** ➔ **Ajouter**.
    🤖 **Sur Android (Chrome) :** Appuyez sur les **3 petits points** ➔ **Ajouter à l'écran d'accueil**.
    """)

# ==========================================
# ⚙️ 4. UTILITAIRES DE RECHERCHE & LOGOS
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
                    chemin_complet = os.path.join(root, file)
                    try:
                        with open(chemin_complet, "rb") as img_file:
                            dict_logos[cle] = base64.b64encode(img_file.read()).decode()
                    except Exception:
                        pass
    return dict_logos

DICTIONNAIRE_LOGOS_EQUIPES = charger_dictionnaire_logos("Logos")

# Arborescence structurelle du catalogue
MENU_ARBO = {
    "Nations": {
        "Coupe du Monde": ["Coupe du Monde", "CM"],
        "Championnat d'Europe": ["Championnat d'Europe", "Euro", "EURO"],
        "Ligue des Nations": ["Ligue des Nations"],
        "Copa America": ["Copa America"],
        "Jeux Olympiques": ["Jeux Olympiques", "JO"]
    },
    "Coupes d'Europe": {
        "C1": ["Coupe d'Europe des clubs champions", "Champions League", "Ligue des Champions", "C1"],
        "C2": ["Coupe des Coupes", "C2"],
        "C3": ["Coupe Intertoto", "Coupe UEFA", "Europa League", "C3"],
        "C4": ["Europa Conference", "C4"],
        "Supercoupe d'Europe": ["Supercoupe d'Europe"]
    },
    "Championnats & Coupes": {
        "Championnat de France": ["Division 1", "Ligue 1", "Division 2", "Ligue 2"],
        "Coupe Nationale France": ["Coupe de France", "Coupe de la Ligue", "Trophée des Champions"],
        "Espagne": ["Liga", "Copa del Rey"],
        "Italie": ["Serie A", "Coppa Italia"],
        "Angleterre": ["Premier League", "FA Cup", "Carling Cup"],
        "Allemagne": ["Bundesliga"]
    },
    "Amicaux Internationaux": {
        "Matchs Amicaux": ["Amical", "Match amical"],
        "Tournois Divers": ["Tournoi Hassan II", "Kirin Cup", "Tournoi de France"]
    }
}

# ==========================================
# 📊 5. CHARGEMENT ET NETTOYAGE DES DONNÉES
# ==========================================
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
        
        if 'Date' in df.columns:
            dates_numeriques = pd.to_numeric(df['Date'], errors='coerce')
            masque_excel = dates_numeriques.notna()
            dates_converties = pd.to_datetime(dates_numeriques[masque_excel], unit='D', origin='1899-12-30')
            df.loc[masque_excel, 'Date'] = dates_converties.dt.strftime('%d/%m/%Y')
        return df
    except Exception as e:
        st.error(f"Erreur de lecture du fichier CSV : {e}")
        return pd.DataFrame()

df = load_data()
colonnes_possibles = ['Match', 'Saison', 'Date', 'Compétition', 'Phase', 'Journée', 'Domicile', 'Extérieur', 'Score', 'Stade', 'Diffuseur', 'Langue', 'Qualité', 'Commentaires sur fichier']
colonnes_presentes = [c for c in colonnes_possibles if c in df.columns]

# ==========================================
# 📇 6. MOTEUR D'AFFICHAGE OPTIMISÉ (PAGINÉ)
# ==========================================
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucune archive ne correspond à ces critères.")
        return
        
    st.metric("Matchs correspondants", len(df_resultats))
    mode = st.radio("Style de visualisation :", ["📊 Tableau compact", "🃏 Fiches illustrées"], horizontal=True, key=f"mode_{id(df_resultats)}")
    
    if mode == "📊 Tableau compact":
        df_display = df_resultats[colonnes_presentes].copy()
        df_display.insert(0, "Sélection", False)
        
        edited_df = st.data_editor(
            df_display,
            column_config={"Sélection": st.column_config.CheckboxColumn("🛒 Choisir", default=False)},
            disabled=colonnes_presentes,
            hide_index=True,
            use_container_width=True,
            height=450,
            key=f"editor_{id(df_resultats)}"
        )
        
        selected_rows = edited_df[edited_df["Sélection"] == True]
        if len(selected_rows) > 0:
            if st.button(f"🛒 Importer les {len(selected_rows)} sélection(s) au panier", type="primary", use_container_width=True):
                for _, row in selected_rows.iterrows():
                    match_dict = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items() if k != "Sélection"}
                    match_id = f"{match_dict.get('Date', '')}_{match_dict.get('Domicile', '')}_{match_dict.get('Extérieur', '')}"
                    if not any(f"{m.get('Date', '')}_{m.get('Domicile', '')}_{m.get('Extérieur', '')}" == match_id for m in st.session_state.panier):
                        q = str(match_dict.get('Qualité', '')).lower()
                        match_dict['format_choisi'] = 'DVD' if ('dvd' in q or 'vob' in q) else 'Numérique'
                        st.session_state.panier.append(match_dict)
                st.success("Sélection ajoutée au panier !")
                st.rerun()

    else:
        # PAGINATION TRÈS AGRESSIVE : 10 éléments max par vue
        taille_page = 10
        total_matchs = len(df_resultats)
        
        if total_matchs > taille_page:
            nb_pages = ((total_matchs - 1) // taille_page) + 1
            col_v, col_n = st.columns([3, 1])
            with col_n:
                page_sel = st.selectbox("Page active", range(1, nb_pages + 1), index=0, key=f"pag_{id(df_resultats)}")
            debut = (page_sel - 1) * taille_page
            fin = min(debut + taille_page, total_matchs)
            df_page = df_resultats.iloc[debut:fin]
            st.caption(f"Affichage index {debut + 1} à {fin} sur un total de {total_matchs}")
        else:
            df_page = df_resultats

        cols = st.columns(2)
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

        for idx, (original_idx, row) in enumerate(df_page.iterrows()):
            with cols[idx % 2]:
                with st.container(border=True):
                    date_b = row.get('Date', '')
                    date_f = date_b
                    if pd.notna(date_b) and date_b:
                        try:
                            dt = datetime.strptime(str(date_b).strip(), "%d/%m/%Y")
                            date_f = f"{jours[dt.weekday()]} {dt.day} {mois[dt.month - 1]} {dt.year}"
                        except: pass

                    stade = row.get('Stade', 'Stade inconnu')
                    phase = str(row.get('Phase', '')).strip() if pd.notna(row.get('Phase')) else ""
                    comp = str(row.get('Compétition', '')).strip()
                    
                    st.caption(f"🗓️ {date_f} | 🏟️ {stade} {f' - {phase}' if phase else ''}")
                    
                    if comp:
                        if st.button(f"🏆 {comp}", key=f"cp_{original_idx}_{idx}", use_container_width=True):
                            st.session_state.recherche_comp_cible = comp
                            st.session_state.page = 'recherche_avancee'
                            st.rerun()
                    
                    dom, ext, score = row.get('Domicile', ''), row.get('Extérieur', ''), row.get('Score', '-')
                    log_dom = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(dom))
                    log_ext = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(ext))
                    
                    c_d, c_s, c_e = st.columns([1, 1, 1])
                    with c_d:
                        if log_dom: st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{log_dom}' style='width:55px;height:55px;object-fit:contain;'></div>", unsafe_allow_html=True)
                        if st.button(dom, key=f"dm_{original_idx}_{idx}", use_container_width=True):
                            st.session_state.recherche_equipe_cible = dom
                            st.session_state.page = 'recherche_equipe'
                            st.rerun()
                    with c_s:
                        st.markdown(f"<h2 style='text-align:center; margin-top:10px;'>{score}</h2>", unsafe_allow_html=True)
                    with c_e:
                        if log_ext: st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{log_ext}' style='width:55px;height:55px;object-fit:contain;'></div>", unsafe_allow_html=True)
                        if st.button(ext, key=f"ex_{original_idx}_{idx}", use_container_width=True):
                            st.session_state.recherche_equipe_cible = ext
                            st.session_state.page = 'recherche_equipe'
                            st.rerun()
                    
                    diff, qual = row.get('Diffuseur', ''), row.get('Qualité', '')
                    if (pd.notna(diff) and str(diff).strip()) or (pd.notna(qual) and str(qual).strip()):
                        h_f = "<div style='text-align:center; margin-top:10px; border-top:0.5px solid #333; padding-top:5px;'>"
                        if pd.notna(diff) and str(diff).strip(): h_f += f"<span style='background-color:#1e3a8a; padding:3px 8px; border-radius:10px; font-size:11px; margin-right:5px;'>📺 {diff}</span>"
                        if pd.notna(qual) and str(qual).strip(): h_f += f"<span style='background-color:#374151; padding:3px 8px; border-radius:10px; font-size:11px;'>💾 {qual}</span>"
                        st.markdown(h_f + "</div>", unsafe_allow_html=True)
                    
                    m_id = f"{date_b}_{dom}_{ext}"
                    deja_dans_panier = any(f"{m.get('Date', '')}_{m.get('Domicile', '')}_{m.get('Extérieur', '')}" == m_id for m in st.session_state.panier)
                    
                    if deja_dans_panier:
                        if st.button("✅ Retirer du panier", key=f"rcrt_{original_idx}_{idx}", use_container_width=True):
                            st.session_state.panier = [m for m in st.session_state.panier if f"{m.get('Date', '')}_{m.get('Domicile', '')}_{m.get('Extérieur', '')}" != m_id]
                            st.rerun()
                    else:
                        if st.button("🛒 Sélectionner", key=f"acrt_{original_idx}_{idx}", type="primary", use_container_width=True):
                            m_dict = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items()}
                            q_low = str(m_dict.get('Qualité', '')).lower()
                            m_dict['format_choisi'] = 'DVD' if ('dvd' in q_low or 'vob' in q_low) else 'Numérique'
                            st.session_state.panier.append(m_dict)
                            st.rerun()

# ==========================================
# 🧭 7. RETOUR ET NAVIGATION LATÉRALE
# ==========================================
with st.sidebar:
    if logo_b64:
        st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{logo_b64}' style='width:100px;border-radius:50%; margin-bottom:10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🧭 Le Grenier</h2>", unsafe_allow_html=True)
    
    if st.button("🏠 Retour à l'Accueil", use_container_width=True): go_home(); st.rerun()
    if st.button("❓ Aide & FAQ", use_container_width=True): st.session_state.page = 'faq'; st.rerun()
    if st.button("📱 Installer l'App sur Mobile", use_container_width=True): popup_raccourci_mobile()
    
    st.divider()
    panier_taille = len(st.session_state.panier)
    if st.button(f"🛒 Mon Panier ({panier_taille})", use_container_width=True, type="primary" if panier_taille > 0 else "secondary"):
        st.session_state.page = 'panier'; st.rerun()
        
    st.divider()
    st.markdown("### 📂 Filtrage Thématique")
    
    st.markdown('<div class="css-nations"></div>', unsafe_allow_html=True)
    if st.button("🌍 Tournois des Nations", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Nations']; st.rerun()
    
    st.markdown('<div class="css-europe"></div>', unsafe_allow_html=True)
    if st.button("🏆 Coupes d'Europe (LDC...)", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ["Coupes d'Europe"]; st.rerun()
    
    st.markdown('<div class="css-champ"></div>', unsafe_allow_html=True)
    if st.button("🏟️ Championnats & Coupes", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Championnats & Coupes']; st.rerun()
    
    st.markdown('<div class="css-amicaux"></div>', unsafe_allow_html=True)
    if st.button("🤝 Amicaux & Divers", use_container_width=True): st.session_state.page = 'arborescence'; st.session_state.chemin = ['Amicaux Internationaux']; st.rerun()
    
    st.divider()
    st.markdown("### 🔍 Moteurs de Recherche")
    if st.button("📖 Tout le Catalogue", use_container_width=True): st.session_state.page = 'catalogue'; st.rerun()
    if st.button("🛡️ Par Équipe / Club", use_container_width=True): st.session_state.page = 'recherche_equipe'; st.rerun()
    if st.button("⚔️ Face-à-Face", use_container_width=True): st.session_state.page = 'face_a_face'; st.rerun()
    if st.button("🕵️ Filtres Avancés", use_container_width=True): st.session_state.page = 'recherche_avancee'; st.rerun()
    
    st.divider()
    st.markdown("### 🌟 Bonus & Échanges")
    if st.button("✨ Archives Dépoussiérées", use_container_width=True): st.session_state.page = 'pepites'; st.rerun()
    if st.button("🎯 Objectifs Collection", use_container_width=True): st.session_state.page = 'progression'; st.rerun()
    if st.button("🔎 Recherche Archives Rares", use_container_width=True): st.session_state.page = 'mes_recherches'; st.rerun()
    if st.button("📊 Statistiques Générales", use_container_width=True): st.session_state.page = 'statistiques'; st.rerun()

# ==========================================
# 🏠 8. LOGIQUE LOGICIELLE : ARCHITECTURE DES PAGES
# ==========================================

# --- PAGE : ACCUEIL ---
if st.session_state.page == 'accueil':
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 15px;'>
            <h1 style='display: flex; align-items: center; justify-content: center; line-height: 1.2;'>
                <span>Le Grenier du Football</span>
            </h1>
            <div style='max-width: 850px; margin: 0 auto; line-height: 1.6; font-size: 16px; color: #eaeaea; margin-top: 15px;'>
                Explorez un catalogue interactif de près de <b>5000 matchs classiques</b>, restaurés et numérisés à partir de véritables <b>cassettes VHS et fichiers DVD d'époque</b>.<br>
                Revivez l'histoire des plus grands chocs mondiaux, téléchargez vos archives favorites ou complétez la collection par échange.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Boutons d'appel à l'action rapides utilisant les marqueurs CSS sécurisés
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="btn-vert-cible"></div>', unsafe_allow_html=True)
        if st.button("🧭 Guide Complet", use_container_width=True): popup_guide_contenu()
    with c2:
        st.markdown('<div class="btn-bleu-cible"></div>', unsafe_allow_html=True)
        if st.button("💶 Grille Tarifaire", use_container_width=True): popup_tarifs()
    with c3:
        st.markdown('<div class="btn-vert-cible"></div>', unsafe_allow_html=True)
        if st.button("💾 Formats Fichiers", use_container_width=True): popup_formats()
    with c4:
        st.markdown('<div class="btn-bleu-cible"></div>', unsafe_allow_html=True)
        if st.button("✉️ Commander / Contacter", use_container_width=True): popup_contact_commandes()
        
    st.write("")
    
    recherche_rapide = st.text_input("🔍 Recherche Immédiate (Ex: France 1998, Marseille, Milan, Ligue des champions...)", placeholder="Saisissez un mot-clé...")
    if recherche_rapide:
        mask = (
            df['Domicile'].astype(str).str.contains(recherche_rapide, case=False, na=False) |
            df['Extérieur'].astype(str).str.contains(recherche_rapide, case=False, na=False) |
            df['Compétition'].astype(str).str.contains(recherche_rapide, case=False, na=False)
        )
        for col in ['Phase', 'Stade', 'Saison', 'Date']:
            if col in df.columns: mask = mask | df[col].astype(str).str.contains(recherche_rapide, case=False, na=False)
        afficher_resultats(df[mask])
    else:
        st.info("💡 Utilisez la barre latérale gauche pour naviguer de manière structurée à travers les époques et compétitions !")

# --- PAGE : ARBORESCENCE ---
elif st.session_state.page == 'arborescence':
    st.title("📁 Navigation Thématique")
    chemin = st.session_state.chemin
    
    # Fil d'Ariane
    st.markdown(f"**Position actuelle :** Accueil {' ➔ '.join(chemin)}")
    if st.button("⬅️ Revenir en arrière"):
        st.session_state.chemin.pop()
        if not st.session_state.chemin: go_home()
        st.rerun()
        
    # Exploration de la structure de données
    noeud_courant = MENU_ARBO
    for rep in chemin:
        if rep in noeud_courant: noeud_courant = noeud_courant[rep]
        
    if isinstance(noeud_courant, dict):
        cols = st.columns(3)
        for i, ss_cat in enumerate(noeud_courant.keys()):
            with cols[i % 3]:
                if st.button(ss_cat, use_container_width=True):
                    st.session_state.chemin.append(ss_cat)
                    st.rerun()
    else:
        # C'est une feuille (liste de mots-clés)
        mots_cles = noeud_courant
        masque = pd.Series(False, index=df.index)
        for mk in mots_cles:
            masque = masque | df['Compétition'].astype(str).str.contains(mk, case=False, na=False)
            
        st.write("---")
        afficher_resultats(df[masque])

# --- PAGE : CATALOGUE COMPLET ---
elif st.session_state.page == 'catalogue':
    st.title("📖 Registre Général des Archives")
    st.write("Retrouvez ici la totalité des éléments répertoriés dans le grenier.")
    afficher_resultats(df)

# --- PAGE : RECHERCHE PAR ÉQUIPE ---
elif st.session_state.page == 'recherche_equipe':
    st.title("🛡️ Exploration par Club ou Sélection")
    
    init_equipe = st.session_state.recherche_equipe_cible
    toutes_equipes = sorted(list(set(df['Domicile'].dropna().unique()) | set(df['Extérieur'].dropna().unique())))
    
    idx_defaut = 0
    if init_equipe in toutes_equipes:
        idx_defaut = toutes_equipes.index(init_equipe)
        
    equipe_choisie = st.selectbox("Sélectionnez l'équipe à analyser :", toutes_equipes, index=idx_defaut)
    
    if equipe_choisie:
        df_filtre = df[(df['Domicile'] == equipe_choisie) | (df['Extérieur'] == equipe_choisie)]
        afficher_resultats(df_filtre)

# --- PAGE : FACE-À-FACE ---
elif st.session_state.page == 'face_a_face':
    st.title("⚔️ Historique des Confrontations Directes")
    
    toutes_equipes = sorted(list(set(df['Domicile'].dropna().unique()) | set(df['Extérieur'].dropna().unique())))
    
    c1, c2 = st.columns(2)
    with c1: eqA = st.selectbox("Équipe locale / A :", toutes_equipes, index=0)
    with c2: eqB = st.selectbox("Équipe adverse / B :", toutes_equipes, index=min(1, len(toutes_equipes)-1))
    
    if eqA and eqB:
        df_confrontation = df[
            ((df['Domicile'] == eqA) & (df['Extérieur'] == eqB)) |
            ((df['Domicile'] == eqB) & (df['Extérieur'] == eqA))
        ]
        afficher_resultats(df_confrontation)

# --- PAGE : RECHERCHE AVANCÉE ---
elif st.session_state.page == 'recherche_avancee':
    st.title("🕵️ Filtres de Recherche Multi-Critères")
    
    init_comp = st.session_state.recherche_comp_cible
    toutes_comps = ["Toutes"] + sorted(df['Compétition'].dropna().unique().tolist())
    idx_c = toutes_comps.index(init_comp) if init_comp in toutes_comps else 0
    
    c1, c2, c3 = st.columns(3)
    with c1: comp_sel = st.selectbox("Compétition :", toutes_comps, index=idx_c)
    with c2: saison_sel = st.selectbox("Saison :", ["Toutes"] + sorted(df['Saison'].dropna().unique().tolist(), reverse=True))
    with c3: langue_sel = st.selectbox("Langue des commentaires :", ["Toutes"] + sorted(df['Langue'].dropna().unique().tolist())) if 'Langue' in df.columns else ("Toutes", ["Toutes"])
        
    df_f = df.copy()
    if comp_sel != "Toutes": df_f = df_f[df_f['Compétition'] == comp_sel]
    if saison_sel != "Toutes": df_f = df_f[df_f['Saison'] == saison_sel]
    if 'Langue' in df_f.columns and langue_sel != "Toutes": df_f = df_f[df_f['Langue'] == langue_sel]
        
    afficher_resultats(df_f)

# --- PAGE : LE PANIER ---
elif st.session_state.page == 'panier':
    st.title("🛒 Analyse et Validation de votre Sélection")
    
    if not st.session_state.panier:
        st.info("Votre panier est actuellement vide. Parcourez les archives pour ajouter des pièces !")
    else:
        items_a_conserver = []
        cout_total = 0.0
        recap_texte = "Bonjour Le Grenier du Football, voici ma sélection :\n\n"
        
        st.markdown("### 📋 Détails de la sélection")
        
        for i, match in enumerate(st.session_state.panier):
            with st.container(border=True):
                c_txt, c_fmt, c_sup = st.columns([2, 1, 0.5])
                
                with c_txt:
                    info_m = f"Match #{match.get('Match','?')} : {match.get('Domicile')} - {match.get('Extérieur')} ({match.get('Saison')})"
                    st.markdown(f"**{info_m}**")
                    st.caption(f"Compétition : {match.get('Compétition')} | Date : {match.get('Date')}")
                    
                with c_fmt:
                    fmt_choisi = st.radio("Format souhaité :", ["Numérique (3€)", "DVD / VOB (5€)"], 
                                          index=0 if match.get('format_choisi') == 'Numérique' else 1, 
                                          key=f"fmt_panier_{i}")
                    match['format_choisi'] = 'Numérique' if "Numérique" in fmt_choisi else 'DVD'
                    
                with c_sup:
                    if st.button("🗑️", key=f"del_{i}"):
                        continue
                        
                # Établissement du coût individuel de la ligne
                tarif_base = 5.0 if match['format_choisi'] == 'DVD' else 3.0
                qualite_m = str(match.get('Qualité', '')).lower()
                comm_m = str(match.get('Commentaires sur fichier', '')).lower()
                
                # Règle archive imparfaite (-1€)
                bonus_malus = 0.0
                if "imparfait" in qualite_m or "altere" in qualite_m or "defaut" in qualite_m or "incomplet" in comm_m:
                    bonus_malus = -1.0
                    st.caption("🩹 *Remise Archive Imparfaite automatique appliquée (-1€)*")
                    
                prix_final_ligne = max(0.0, tarif_base + bonus_malus)
                match['prix_calcule'] = prix_final_ligne
                items_a_conserver.append(match)
                cout_total += prix_final_ligne
                
        st.session_state.panier = items_a_conserver
        
        # Application de l'offre commerciale (1 gratuit tous les 10 achetés)
        nb_matchs = len(st.session_state.panier)
        nb_gratuits = nb_matchs // 11
        
        st.divider()
        st.markdown("### 💶 Facturation estimée")
        st.write(f"Nombre total de matchs sélectionnés : **{nb_matchs}**")
        
        if nb_gratuits > 0:
            # Tri des articles par prix pour offrir les moins chers
            prix_tous_matchs = sorted([m['prix_calcule'] for m in st.session_state.panier])
            remise_offerte = sum(prix_tous_matchs[:nb_gratuits])
            cout_total -= remise_offerte
            st.success(f"🎁 Offre de fidélité active : {nb_gratuits} match(s) offert(s) ! Réduction de -{remise_offerte}€")
            
        st.markdown(f"#### Montant Total de votre panier : <span style='color:#2e7d32; font-size:24px;'>{cout_total} €</span>", unsafe_allow_html=True)
        
        # Génération du bloc texte final pour commande simplifiée
        for m in st.session_state.panier:
            recap_texte += f"- Match #{m.get('Match','?')} : {m.get('Domicile')} vs {m.get('Extérieur')} | Format : {m['format_choisi']} ({m.get('Compétition')} - {m.get('Saison')})\n"
        recap_texte += f"\nTotal estimé : {cout_total} €"
        
        st.write("")
        st.markdown("### 📬 Comment valider cette sélection ?")
        st.info("Copiez le récapitulatif ci-dessous et transmettez-le directement par mail ou sur Instagram !")
        st.text_area("Texte de votre commande à copier :", recap_texte, height=180)

# --- PAGE : RESTE DES PAGES STATIQUES & BONUS ---
elif st.session_state.page == 'faq':
    st.title("❓ Aide, F.A.Q & Fonctionnement")
    st.markdown("""
    ### 🤝 Comment se passe la livraison des fichiers vidéo ?
    Une fois votre demande confirmée et le règlement PayPal effectué, vous recevrez des liens de téléchargement sécurisés via des plateformes d'échange de fichiers volumineux. Vous pourrez stocker et visionner les vidéos à vie sur l'appareil de votre choix.
    
    ### 📼 Quelle est la qualité visuelle des matchs rétro ?
    La qualité dépend directement de la source originale. Les rencontres des années 70 à 93 proviennent majoritairement de cassettes VHS d'époque, le rendu est donc d'époque (vintage). Les matchs plus récents bénéficient de numérisations de flux DVD ou TV numériques de haute clarté. Tout est spécifié dans la colonne *Qualité*.
    """)

elif st.session_state.page == 'pepites':
    st.title("✨ Les Archives Dépoussiérées")
    st.blockquote("Découvrez une sélection rigoureuse de matchs mythiques ou insolites qui ont marqué l'histoire du football mondial.")
    # On isole arbitrairement des matchs de légende d'avant 1986 pour l'exemple pépite
    df_p = df[df['Saison'].astype(str).str.contains("197|1980|1981|1982|1983|1984|1985", na=False)]
    afficher_resultats(df_p.head(20))

elif st.session_state.page == 'progression':
    st.title("🎯 Objectifs de la Collection")
    st.markdown("""
    Le Grenier du Football s'est donné pour mission de sauvegarder la mémoire du football télévisé francophone.
    - **Objectif Global 2026 :** Atteindre les 6000 archives indexées.
    - **Chantiers prioritaires :** Numérisation complète des saisons de Division 1 des années 1990-2000.
    """)

elif st.session_state.page == 'mes_recherches':
    st.title("🔎 Archives Rares Activement Recherchées")
    st.markdown("""
    Si vous possédez l'un des éléments suivants sur cassette VHS, DVD ou fichier brut, contactez-nous pour organiser un **échange standard avantageux** !
    
    1. 📼 **Multiplex de Division 1 (Canal+)** des années 1984 à 2002.
    2. ⚽ Tout match de Coupe d'Europe impliquant des clubs français (saisons antérieures à 1995).
    3. 🎙️ Enregistrements TV avec commentaires d'origine (TF1, France Télévisions, Canal+).
    """)

elif st.session_state.page == 'statistiques':
    st.title("📊 Statistiques Générales du Grenier")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top 10 des Compétitions représentées**")
            top_comp = df['Compétition'].value_counts().head(10).reset_index()
            fig1 = px.bar(top_comp, x='count', y='Compétition', orientation='h', template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            st.markdown("**Évolution chronologique des archives disponibles**")
            top_saisons = df['Saison'].value_counts().head(15).reset_index()
            fig2 = px.pie(top_saisons, values='count', names='Saison', template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Aucune donnée disponible pour éditer les graphiques.")
