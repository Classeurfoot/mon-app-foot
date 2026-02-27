import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re
import base64
import plotly.express as px # Pour les graphiques

# 1. Configuration de la page
st.set_page_config(page_title="Classeur Foot", layout="wide")

# ==========================================
# ⚙️ FONCTION DE NETTOYAGE ET UTILITAIRES
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

def get_img_as_base64(file_path):
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==========================================
# 🧠 CHARGEMENT ET PRÉPARATION DES DONNÉES
# ==========================================
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
        
        # Préparation pour les stats par décennie
        if 'Saison' in df.columns:
            # Extrait l'année (ex: "1998" de "1998-1999" ou juste "1998")
            df['Annee'] = df['Saison'].str.extract(r'(\d{4})').astype(float)
            df['Decennie'] = (df['Annee'] // 10 * 10).fillna(0).astype(int).astype(str) + "s"
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 🧭 NAVIGATION PERSISTANTE (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("🧭 Navigation")
    
    if st.button("🏠 Accueil", width="stretch"):
        st.session_state.page = 'accueil'
        st.session_state.chemin = []
        st.session_state.edition_choisie = None
        st.rerun()

    st.divider()
    st.subheader("📂 Explorer")
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
    st.subheader("🔍 Outils")
    if st.button("📖 Catalogue Complet", width="stretch"):
        st.session_state.page = 'catalogue'
        st.rerun()
    if st.button("📊 Statistiques", width="stretch"):
        st.session_state.page = 'statistiques'
        st.rerun()
    if st.button("🕵️ Recherche Avancée", width="stretch"):
        st.session_state.page = 'recherche_avancee'
        st.rerun()

# ==========================================
# 🎬 FONCTION : MODE CINÉMA (FOCUS)
# ==========================================
def afficher_focus_match(row):
    st.button("⬅️ Quitter le mode focus", on_click=lambda: st.session_state.update({"page": "accueil"}))
    
    with st.container(border=True):
        st.markdown("<br>", unsafe_allow_html=True)
        # En-tête géant
        comp = row.get('Compétition', '')
        date_brute = row.get('Date', '')
        st.markdown(f"<h3 style='text-align: center; color: gray;'>{comp}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: gray;'>{date_brute} - {row.get('Stade', '')}</h4>", unsafe_allow_html=True)
        
        col1, col_score, col2 = st.columns([2, 1, 2])
        
        dom = row.get('Domicile', '')
        ext = row.get('Extérieur', '')
        logo_dom = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(dom))
        logo_ext = DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(ext))
        
        with col1:
            st.markdown(f"<h1 style='text-align: center;'>{dom}</h1>", unsafe_allow_html=True)
            img_dom = get_img_as_base64(logo_dom)
            if img_dom:
                st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_dom}' width='180'></div>", unsafe_allow_html=True)
        
        with col_score:
            st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin-top: 50px;'>{row.get('Score', '-')}</h1>", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"<h1 style='text-align: center;'>{ext}</h1>", unsafe_allow_html=True)
            img_ext = get_img_as_base64(logo_ext)
            if img_ext:
                st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_ext}' width='180'></div>", unsafe_allow_html=True)
        
        st.markdown("<br><hr>", unsafe_allow_html=True)
        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.subheader(f"📺 Diffuseur : {row.get('Diffuseur', 'Inconnu')}")
        with c_info2:
            st.subheader(f"💾 Qualité : {row.get('Qualité', 'Inconnue')}")

# ==========================================
# 🃏 FONCTION : FICHES DE MATCHS (CLUBS/NATIONS)
# ==========================================
def afficher_resultats(df_resultats):
    if df_resultats.empty:
        st.warning("Aucun match trouvé.")
        return
        
    st.metric("Matchs trouvés", len(df_resultats))
    
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

                # En-tête dynamique
                stade = row.get('Stade', 'Stade inconnu')
                comp = str(row.get('Compétition', ''))
                phase = str(row.get('Phase', '')).strip() if pd.notna(row.get('Phase')) else ""
                
                # Nettoyage Journée (int)
                raw_j = row.get('Journée', '')
                val_j = ""
                if pd.notna(raw_j):
                    try: val_j = f"Journée {int(float(raw_j))}"
                    except: val_j = str(raw_j)

                # Logique d'affichage demandée
                mots_champ = ['ligue 1', 'ligue 2', 'serie a', 'liga', 'premier league', 'bundesliga', 'championnat']
                est_champ = any(m in comp.lower() for m in mots_champ) and 'champions' not in comp.lower()
                
                # Détection CLUBS vs NATIONS
                mots_nations = ['coupe du monde', 'euro', 'copa america', 'nations']
                est_nation = any(m in comp.lower() for m in mots_nations)

                if est_nation:
                    header_str = f"{stade} - {phase}" if phase else stade
                else: # Clubs
                    suffixe = val_j if est_champ else phase
                    header_str = f"{stade} - {comp} - {suffixe}" if suffixe else f"{stade} - {comp}"

                st.caption(f"🗓️ {date_formatee.capitalize()} | 🏟️ {header_str}")
                
                # Teams & Logos
                c_dom, c_score, c_ext = st.columns([2, 1, 2])
                dom, ext = row['Domicile'], row['Extérieur']
                img_dom = get_img_as_base64(DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(dom)))
                img_ext = get_img_as_base64(DICTIONNAIRE_LOGOS_EQUIPES.get(nettoyer_nom_equipe(ext)))

                with c_dom:
                    st.markdown(f"<div style='text-align:center;'><p style='font-weight:bold; font-size:17px; margin-bottom:5px;'>{dom}</p>" + (f"<img src='data:image/png;base64,{img_dom}' width='60'>" if img_dom else "") + "</div>", unsafe_allow_html=True)
                with c_score:
                    st.markdown(f"<h2 style='text-align: center; margin-top: 15px;'>{row['Score']}</h2>", unsafe_allow_html=True)
                with c_ext:
                    st.markdown(f"<div style='text-align:center;'><p style='font-weight:bold; font-size:17px; margin-bottom:5px;'>{ext}</p>" + (f"<img src='data:image/png;base64,{img_ext}' width='60'>" if img_ext else "") + "</div>", unsafe_allow_html=True)
                
                # Footer + Bouton Cinema
                f_col1, f_col2 = st.columns([4, 1])
                with f_col1:
                    parts = []
                    if pd.notna(row.get('Diffuseur')): parts.append(f"📺 {row['Diffuseur']}")
                    if pd.notna(row.get('Qualité')): parts.append(f"💾 {row['Qualité']}")
                    st.markdown(f"<div style='text-align:center; color:gray; font-size:14px; border-top:0.5px solid #444; padding-top:5px;'>{' | '.join(parts)}</div>", unsafe_allow_html=True)
                with f_col2:
                    if st.button("🎬 Focus", key=f"btn_cin_{index}"):
                        st.session_state.cinema_match = row
                        st.session_state.page = 'cinema'
                        st.rerun()

# ==========================================
# 📊 PAGE : STATISTIQUES VISUELLES
# ==========================================
def afficher_stats_visuelles():
    st.header("📊 Statistiques de la Collection")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⏳ Répartition par décennies")
        fig_dec = px.pie(df, names='Decennie', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_dec, use_container_width=True)
        
    with c2:
        st.subheader("💾 Qualité des fichiers")
        # On nettoie un peu les noms de qualité pour le graph
        df_qual = df['Qualité'].fillna('Inconnue').value_counts().reset_index()
        fig_qual = px.bar(df_qual, x='Qualité', y='count', color='Qualité', text_auto=True)
        st.plotly_chart(fig_qual, use_container_width=True)

    st.subheader("🏆 Top 10 des Compétitions les plus présentes")
    df_comp = df['Compétition'].value_counts().head(10).reset_index()
    st.plotly_chart(px.bar(df_comp, x='count', y='Compétition', orientation='h', color='count'), use_container_width=True)

# ==========================================
# 🚦 GESTIONNAIRE DE PAGES
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'accueil'
if 'cinema_match' not in st.session_state: st.session_state.cinema_match = None

if st.session_state.page == 'accueil':
    st.markdown("<h1 style='text-align: center;'>⚽ Archives Football</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #aaaaaa;'>Retrouvez plus de <b>{len(df)}</b> matchs mythiques.</p>", unsafe_allow_html=True)
    
    # Recherche Rapide Interactive
    recherche = st.text_input("🔍 Recherche Rapide", placeholder="Une équipe, un stade, une année...")
    if recherche:
        mask = df.apply(lambda row: row.astype(str).str.contains(recherche, case=False).any(), axis=1)
        afficher_resultats(df[mask])
    else:
        # Layout d'accueil classique (Éphéméride, etc.)
        st.info("Utilisez la barre latérale à gauche pour naviguer dans les catégories !")

elif st.session_state.page == 'cinema':
    afficher_focus_match(st.session_state.cinema_match)

elif st.session_state.page == 'statistiques':
    afficher_stats_visuelles()

elif st.session_state.page == 'catalogue':
    st.header("📖 Catalogue Complet")
    afficher_resultats(df)

elif st.session_state.page == 'arborescence':
    # (Ici on garde ta logique de MENU_ARBO précédente pour la navigation par clics)
    st.write("Navigation par compétition en cours...")
    # ... (Le code de l'arborescence peut être réinséré ici)
