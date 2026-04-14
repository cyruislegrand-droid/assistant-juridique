import requests
import os

# ============================================================
# Ce script télécharge les 10 lois marocaines les plus
# consultées par les PME depuis leurs sources officielles.
# Tu n'as besoin de rien modifier — juste lancer le script.
# ============================================================

# Dossier où les PDFs seront sauvegardés
DOSSIER = "lois_pdf"

# Création du dossier si il n'existe pas encore
if not os.path.exists(DOSSIER):
    os.makedirs(DOSSIER)
    print(f"Dossier '{DOSSIER}' créé.")

# ============================================================
# Liste des 10 lois avec leur nom et leur lien de téléchargement
# ============================================================
LOIS = [
    {
        "nom": "01_code_travail_loi_65-99.pdf",
        "description": "Code du Travail (Loi 65-99)",
        "url": "https://www.emploi.gov.ma/index.php/fr/telechargements/send/4-textes-legislatifs/46-code-du-travail"
    },
    {
        "nom": "02_DOC_obligations_contrats.pdf",
        "description": "Code des Obligations et Contrats (DOC)",
        "url": "https://rnesm.justice.gov.ma/Documentation/MA/4_ONC_Law_fr-FR.pdf"
    },
    {
        "nom": "03_loi_5-96_SARL.pdf",
        "description": "Loi 5-96 sur la SARL",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/1997/BO_4478_fr.pdf"
    },
    {
        "nom": "04_code_commerce_loi_15-95.pdf",
        "description": "Code de Commerce (Loi 15-95)",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/1996/BO_4418_fr.pdf"
    },
    {
        "nom": "05_protection_consommateur_loi_31-08.pdf",
        "description": "Protection du Consommateur (Loi 31-08)",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/2011/BO_5932_fr.pdf"
    },
    {
        "nom": "06_echanges_electroniques_loi_53-05.pdf",
        "description": "Échanges Électroniques (Loi 53-05)",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/2007/BO_5584_fr.pdf"
    },
    {
        "nom": "07_protection_donnees_loi_09-08.pdf",
        "description": "Protection des Données Personnelles (Loi 09-08)",
        "url": "https://www.cndp.ma/images/loi-09-08-fr.pdf"
    },
    {
        "nom": "08_procedures_collectives_loi_73-17.pdf",
        "description": "Procédures Collectives (Loi 73-17)",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/2018/BO_6644_fr.pdf"
    },
    {
        "nom": "09_baux_commerciaux_loi_49-16.pdf",
        "description": "Baux Commerciaux (Loi 49-16)",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/2016/BO_6490_fr.pdf"
    },
    {
        "nom": "10_concurrence_prix_loi_104-12.pdf",
        "description": "Concurrence et Prix (Loi 104-12)",
        "url": "https://www.sgg.gov.ma/Portals/0/BO/2014/BO_6240_fr.pdf"
    },
]

# ============================================================
# Téléchargement de chaque loi
# ============================================================
print("\n--- Début du téléchargement des 10 lois ---\n")

for loi in LOIS:
    chemin = os.path.join(DOSSIER, loi["nom"])

    # Si le fichier existe déjà, on ne le re-télécharge pas
    if os.path.exists(chemin):
        print(f"[DÉJÀ PRÉSENT] {loi['description']}")
        continue

    print(f"[TÉLÉCHARGEMENT] {loi['description']}...")

    try:
        # Envoi de la requête avec un délai de 30 secondes
        reponse = requests.get(loi["url"], timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        # Si le téléchargement a réussi (code 200)
        if reponse.status_code == 200:
            with open(chemin, "wb") as fichier:
                fichier.write(reponse.content)
            taille = os.path.getsize(chemin) / 1024  # taille en Ko
            print(f"[OK] Sauvegardé : {loi['nom']} ({taille:.0f} Ko)")
        else:
            print(f"[ERREUR] Code {reponse.status_code} pour : {loi['description']}")

    except Exception as e:
        print(f"[ERREUR] Impossible de télécharger {loi['description']} : {e}")

print("\n--- Téléchargement terminé ---")
print(f"Tes PDFs sont dans le dossier : {os.path.abspath(DOSSIER)}")
print("\nÉtape suivante : lancer le script 'extraire_texte.py'")