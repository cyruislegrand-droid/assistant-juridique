import pdfplumber
import os

# --------------------------------------------------
# Ce script lit chaque PDF et extrait le texte
# Il sauvegarde le texte dans un dossier "lois_texte"
# --------------------------------------------------

DOSSIER_PDF = "lois_pdf"
DOSSIER_TEXTE = "lois_texte"

# Création du dossier texte s'il n'existe pas
if not os.path.exists(DOSSIER_TEXTE):
    os.makedirs(DOSSIER_TEXTE)
    print(f"Dossier '{DOSSIER_TEXTE}' créé.")

print("\n=== Extraction du texte des PDFs ===\n")

succes = 0
echecs = []

# On parcourt tous les PDFs du dossier
for nom_fichier in sorted(os.listdir(DOSSIER_PDF)):

    # On ne traite que les fichiers PDF
    if not nom_fichier.endswith(".pdf"):
        continue

    chemin_pdf = os.path.join(DOSSIER_PDF, nom_fichier)
    nom_texte = nom_fichier.replace(".pdf", ".txt")
    chemin_texte = os.path.join(DOSSIER_TEXTE, nom_texte)

    # Si déjà extrait, on passe
    if os.path.exists(chemin_texte):
        print(f"[DEJA FAIT]  {nom_fichier}")
        succes += 1
        continue

    print(f"[EXTRACTION] {nom_fichier}...")

    try:
        texte_total = ""

        with pdfplumber.open(chemin_pdf) as pdf:
            nb_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                texte_page = page.extract_text()
                if texte_page:
                    texte_total += texte_page + "\n"

                # Afficher la progression toutes les 50 pages
                if (i + 1) % 50 == 0:
                    print(f"   ... {i+1}/{nb_pages} pages traitées")

        # Vérifier qu'on a bien extrait du texte
        if len(texte_total.strip()) < 100:
            print(f"[ATTENTION]  Peu de texte extrait pour {nom_fichier} — PDF peut-être scanné")
            echecs.append(nom_fichier)
            continue

        # Sauvegarder le texte
        with open(chemin_texte, "w", encoding="utf-8") as f:
            f.write(texte_total)

        taille = len(texte_total)
        print(f"[OK]  {nom_texte} — {nb_pages} pages — {taille:,} caractères")
        succes += 1

    except Exception as e:
        print(f"[ERREUR]  {nom_fichier} : {e}")
        echecs.append(nom_fichier)

# --------------------------------------------------
# Résumé
# --------------------------------------------------
print(f"\n=== TERMINE : {succes}/10 fichiers extraits ===")

if echecs:
    print("\nFichiers avec problèmes :")
    for e in echecs:
        print(f"  - {e}")
    print("\nNote : les PDFs scannés (images) ne peuvent pas être lus")
    print("       directement. Dis-le moi et on trouvera une solution.")

print(f"\nTes textes sont ici : {os.path.abspath(DOSSIER_TEXTE)}")
print("\nEtape suivante : lancer indexer_lois.py")