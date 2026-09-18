import csv
import re
import unicodedata
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

DOSSIER = Path(__file__).resolve().parent

SORTIE = DOSSIER / "captures_serie_a_2003-04.csv"

SAISON_DEFAUT = "2003-2004"
COMPETITION_DEFAUT = "Serie A"


# ============================================================
# CLUBS SERIE A 2003-04
# ============================================================

CLUBS = {
    "Ancona": [
        "ancona"
    ],

    "Bologna": [
        "bologna"
    ],

    "Brescia": [
        "brescia"
    ],

    "Chievo": [
        "chievo",
        "chievo verona"
    ],

    "Empoli": [
        "empoli"
    ],

    "Inter": [
        "inter",
        "internazionale"
    ],

    "Juventus": [
        "juventus",
        "juve"
    ],

    "Lazio": [
        "lazio"
    ],

    "Lecce": [
        "lecce"
    ],

    "Milan": [
        "milan",
        "ac milan"
    ],

    "Modena": [
        "modena"
    ],

    "Parma": [
        "parma"
    ],

    "Perugia": [
        "perugia"
    ],

    "Reggina": [
        "reggina"
    ],

    "Roma": [
        "roma",
        "as roma"
    ],

    "Sampdoria": [
        "sampdoria"
    ],

    "Siena": [
        "siena"
    ],

    "Udinese": [
        "udinese"
    ]
}


# ============================================================
# OUTILS TEXTE
# ============================================================

def sans_accents(texte):

    texte = unicodedata.normalize(
        "NFD",
        str(texte)
    )

    return "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )


def normaliser(texte):

    texte = sans_accents(texte).lower()

    # Les points, tirets, underscores etc. deviennent des espaces
    texte = re.sub(
        r"[^a-z0-9+]+",
        " ",
        texte
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte
    )

    return texte.strip()


def slug(texte):

    texte = normaliser(texte)

    texte = texte.replace(
        "+",
        "plus"
    )

    return texte.replace(
        " ",
        "-"
    )


# ============================================================
# SAISON
# ============================================================

def trouver_saison(nom):

    texte = normaliser(nom)

    # 2003-2004 / 2003.2004
    if re.search(
        r"\b2003\s+2004\b",
        texte
    ):
        return "2003-2004"

    # 03-04 / 03.04
    if re.search(
        r"\b03\s+04\b",
        texte
    ):
        return "2003-2004"

    return SAISON_DEFAUT


# ============================================================
# COMPETITION
# ============================================================

def trouver_competition(nom):

    texte = normaliser(nom)

    if re.search(
        r"\bserie\s+a\b",
        texte
    ):
        return "Serie A"

    if "champions league" in texte:
        return "Ligue des champions"

    if "champions" in texte:
        return "Ligue des champions"

    if "coppa italia" in texte:
        return "Coppa Italia"

    if "uefa" in texte:
        return "Coupe UEFA"

    return COMPETITION_DEFAUT


# ============================================================
# JOURNEE
# ============================================================

def trouver_journee(nom):

    # J22
    recherche = re.search(
        r"(?i)(?:^|[\s._\-\(\[])J\s*0?(\d{1,2})(?=$|[\s._\-\)\]])",
        nom
    )

    if recherche:

        return int(
            recherche.group(1)
        )

    return ""


# ============================================================
# DATE
# ============================================================

def date_valide(jour, mois, annee):

    try:

        date = datetime(
            int(annee),
            int(mois),
            int(jour)
        )

        return date.strftime(
            "%Y-%m-%d"
        )

    except ValueError:

        return ""


def trouver_date(nom):

    # --------------------------------------------------------
    # JJ.MM.AAAA / JJ-MM-AAAA / JJ_MM_AAAA
    # --------------------------------------------------------

    recherche = re.search(
        r"(?<!\d)"
        r"(\d{1,2})"
        r"[.\-_]"
        r"(\d{1,2})"
        r"[.\-_]"
        r"(\d{4})"
        r"(?!\d)",
        nom
    )

    if recherche:

        jour, mois, annee = recherche.groups()

        resultat = date_valide(
            jour,
            mois,
            annee
        )

        if resultat:
            return resultat


    # --------------------------------------------------------
    # JJ.MM.AA
    # Exemple : 01.02.04
    # --------------------------------------------------------

    recherche = re.search(
        r"(?<!\d)"
        r"(\d{1,2})"
        r"[.\-_]"
        r"(\d{1,2})"
        r"[.\-_]"
        r"(\d{2})"
        r"(?!\d)",
        nom
    )

    if recherche:

        jour, mois, annee = recherche.groups()

        annee = 2000 + int(annee)

        resultat = date_valide(
            jour,
            mois,
            annee
        )

        if resultat:
            return resultat


    # --------------------------------------------------------
    # AAAAMMJJ
    # Exemple : 20031129
    # --------------------------------------------------------

    recherche = re.search(
        r"(?<!\d)"
        r"(20\d{2})"
        r"(\d{2})"
        r"(\d{2})"
        r"(?!\d)",
        nom
    )

    if recherche:

        annee, mois, jour = recherche.groups()

        resultat = date_valide(
            jour,
            mois,
            annee
        )

        if resultat:
            return resultat


    return ""


# ============================================================
# DIFFUSEUR
# ============================================================

def trouver_diffuseur(nom):

    texte = normaliser(nom)

    diffuseurs = [

        (
            "Rai International",
            [
                "rai international"
            ]
        ),

        (
            "Milan Channel",
            [
                "milan channel"
            ]
        ),

        (
            "Gioco Calcio",
            [
                "gioco calcio",
                "gc ita"
            ]
        ),

        (
            "FR Sport+",
            [
                "fr sport+",
                "fr sport plus"
            ]
        ),

        (
            "Sport+",
            [
                "sport+",
                "sport plus"
            ]
        ),

        (
            "Canal+",
            [
                "canal+",
                "canal plus"
            ]
        ),

        (
            "Foot+",
            [
                "foot+",
                "foot plus"
            ]
        ),

        (
            "Sky",
            [
                "sky tv",
                "sky"
            ]
        ),

        (
            "W9",
            [
                "w9"
            ]
        )
    ]

    for diffuseur, variantes in diffuseurs:

        for variante in variantes:

            if normaliser(variante) in texte:

                return diffuseur

    return ""


# ============================================================
# EQUIPES
# ============================================================

def trouver_equipes(nom):

    texte = normaliser(
        Path(nom).stem
    )

    trouves = []

    for club, variantes in CLUBS.items():

        meilleure_position = None

        for variante in variantes:

            variante_norm = normaliser(
                variante
            )

            recherche = re.search(
                r"\b" +
                re.escape(variante_norm) +
                r"\b",
                texte
            )

            if recherche:

                position = recherche.start()

                if (
                    meilleure_position is None
                    or position < meilleure_position
                ):

                    meilleure_position = position

        if meilleure_position is not None:

            trouves.append(
                (
                    meilleure_position,
                    club
                )
            )

    trouves.sort(
        key=lambda x: x[0]
    )

    # Supprimer éventuellement les doublons
    clubs_uniques = []

    for position, club in trouves:

        if club not in clubs_uniques:
            clubs_uniques.append(
                club
            )

    if len(clubs_uniques) >= 2:

        return (
            clubs_uniques[0],
            clubs_uniques[1]
        )

    if len(clubs_uniques) == 1:

        return (
            clubs_uniques[0],
            ""
        )

    return (
        "",
        ""
    )


# ============================================================
# NOM CIBLE
# ============================================================

def construire_nom(
    saison,
    competition,
    date,
    domicile,
    exterieur,
    diffuseur
):

    if not (
        saison
        and competition
        and date
        and domicile
        and exterieur
    ):

        return ""

    parties = [

        slug(saison),

        slug(competition),

        date,

        slug(domicile),

        slug(exterieur)
    ]

    # On conserve le diffuseur pour éviter les collisions
    # quand plusieurs versions du même match existent.

    if diffuseur:

        parties.append(
            slug(diffuseur)
        )

    return "__".join(
        parties
    ) + ".jpg"


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

extensions = {
    ".jpg",
    ".jpeg",
    ".png"
}

captures = sorted(
    fichier
    for fichier in DOSSIER.iterdir()
    if (
        fichier.is_file()
        and fichier.suffix.lower() in extensions
    )
)


resultats = []


for capture in captures:

    fichier = capture.name

    saison = trouver_saison(
        fichier
    )

    competition = trouver_competition(
        fichier
    )

    journee = trouver_journee(
        fichier
    )

    date = trouver_date(
        fichier
    )

    domicile, exterieur = trouver_equipes(
        fichier
    )

    diffuseur = trouver_diffuseur(
        fichier
    )


    # --------------------------------------------------------
    # Statut
    # --------------------------------------------------------

    if (
        domicile
        and exterieur
        and date
    ):

        statut = "OK"

    elif (
        domicile
        and exterieur
    ):

        statut = "PARTIEL"

    else:

        statut = "A VERIFIER"


    nom_cible = construire_nom(
        saison,
        competition,
        date,
        domicile,
        exterieur,
        diffuseur
    )


    resultats.append({

        "fichier": fichier,

        "saison": saison,

        "competition": competition,

        "journee": journee,

        "date": date,

        "domicile": domicile,

        "exterieur": exterieur,

        "diffuseur": diffuseur,

        "nom_cible": nom_cible,

        "statut": statut
    })


# ============================================================
# ECRITURE CSV
# ============================================================

colonnes = [

    "fichier",

    "saison",

    "competition",

    "journee",

    "date",

    "domicile",

    "exterieur",

    "diffuseur",

    "nom_cible",

    "statut"
]


with SORTIE.open(
    "w",
    encoding="utf-8-sig",
    newline=""
) as fichier_csv:

    writer = csv.DictWriter(
        fichier_csv,
        fieldnames=colonnes,
        delimiter=";"
    )

    writer.writeheader()

    writer.writerows(
        resultats
    )


# ============================================================
# RESUME
# ============================================================

ok = sum(
    1
    for ligne in resultats
    if ligne["statut"] == "OK"
)

partiels = sum(
    1
    for ligne in resultats
    if ligne["statut"] == "PARTIEL"
)

verifier = sum(
    1
    for ligne in resultats
    if ligne["statut"] == "A VERIFIER"
)


print()
print("=" * 70)
print("CSV TERMINE")
print("=" * 70)

print()
print(
    f"Captures analysées : {len(resultats)}"
)

print(
    f"OK                 : {ok}"
)

print(
    f"PARTIEL            : {partiels}"
)

print(
    f"A VERIFIER         : {verifier}"
)

print()
print(
    f"CSV : {SORTIE}"
)

print()