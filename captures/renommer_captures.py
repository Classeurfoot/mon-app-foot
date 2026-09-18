import csv
import re
import unicodedata
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DOSSIER = Path(__file__).resolve().parent

CSV_PATH = DOSSIER / "captures_serie_a_2003-04.csv"


# ============================================================
# NORMALISATION
# ============================================================

def slug(texte):
    texte = str(texte or "").strip()

    texte = unicodedata.normalize("NFD", texte)

    texte = "".join(
        c for c in texte
        if unicodedata.category(c) != "Mn"
    )

    texte = texte.lower()

    texte = texte.replace("+", "plus")

    texte = re.sub(
        r"[^a-z0-9]+",
        "-",
        texte
    )

    texte = texte.strip("-")

    return texte


# ============================================================
# NOM DISPONIBLE
# ============================================================

def nom_disponible(nom_base, extension=".jpg"):

    cible = DOSSIER / f"{nom_base}{extension}"

    if not cible.exists():
        return cible

    numero = 2

    while True:

        cible = DOSSIER / f"{nom_base}__{numero}{extension}"

        if not cible.exists():
            return cible

        numero += 1


# ============================================================
# LECTURE CSV
# ============================================================

if not CSV_PATH.exists():

    print()
    print("ERREUR : CSV introuvable")
    print(CSV_PATH)

    input("\nAppuie sur ENTREE...")
    raise SystemExit


with CSV_PATH.open(
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    lecteur = csv.DictReader(
        f,
        delimiter=";"
    )

    lignes = list(lecteur)


# ============================================================
# RENOMMAGE
# ============================================================

renommes = 0
ignores = 0
erreurs = 0


for ligne in lignes:

    ancien = str(
        ligne.get("fichier", "")
    ).strip()

    saison = str(
        ligne.get("saison", "")
    ).strip()

    competition = str(
        ligne.get("competition", "")
    ).strip()

    domicile = str(
        ligne.get("domicile", "")
    ).strip()

    exterieur = str(
        ligne.get("exterieur", "")
    ).strip()


    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    if not (
        ancien
        and saison
        and competition
        and domicile
        and exterieur
    ):

        print(
            f"IGNORE - informations incomplètes : {ancien}"
        )

        ignores += 1
        continue


    ancien_path = DOSSIER / ancien


    if not ancien_path.exists():

        print(
            f"INTROUVABLE : {ancien}"
        )

        erreurs += 1
        continue


    # --------------------------------------------------------
    # Construire le nom
    # --------------------------------------------------------

    nom_base = (
        f"{slug(saison)}"
        f"__{slug(competition)}"
        f"__{slug(domicile)}"
        f"__{slug(exterieur)}"
    )


    extension = ancien_path.suffix.lower()

    if extension not in {
        ".jpg",
        ".jpeg",
        ".png"
    }:
        extension = ".jpg"


    nouveau_path = nom_disponible(
        nom_base,
        extension
    )


    # --------------------------------------------------------
    # Renommage
    # --------------------------------------------------------

    try:

        ancien_path.rename(
            nouveau_path
        )

        print()
        print("OK")
        print(f"  {ancien}")
        print(f"  -> {nouveau_path.name}")

        renommes += 1

    except Exception as e:

        print()
        print(f"ERREUR : {ancien}")
        print(e)

        erreurs += 1


# ============================================================
# RESUME
# ============================================================

print()
print("=" * 70)
print("TERMINE")
print("=" * 70)

print()
print(
    f"Renommées : {renommes}"
)

print(
    f"Ignorées  : {ignores}"
)

print(
    f"Erreurs   : {erreurs}"
)

print()

input(
    "Appuie sur ENTREE pour fermer..."
)