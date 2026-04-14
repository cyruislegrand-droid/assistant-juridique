import os
import chromadb
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Ce script découpe les textes en morceaux (chunks)
# et les indexe dans une base vectorielle Chroma
# C'est le "cerveau" de l'assistant
# --------------------------------------------------

DOSSIER_TEXTE = "lois_texte"
DOSSIER_INDEX = "lois_index"

# Taille de chaque morceau en caractères (~400 tokens)
TAILLE_CHUNK = 1500
# Chevauchement entre morceaux pour ne pas perdre le contexte
CHEVAUCHEMENT = 200

print("\n=== Chargement du modele d'embedding ===")
print("(premiere fois : telechargement ~500 Mo, patiente...)\n")

# Chargement du modele multilingue (arabe + francais + anglais)
modele = SentenceTransformer("intfloat/multilingual-e5-small")
print("[OK] Modele charge\n")

# Connexion a la base vectorielle Chroma
client = chromadb.PersistentClient(path=DOSSIER_INDEX)

# Supprime la collection si elle existe deja (pour repartir propre)
try:
    client.delete_collection("lois_maroc")
    print("[INFO] Ancienne collection supprimee")
except:
    pass

# Cree une nouvelle collection
collection = client.create_collection(
    name="lois_maroc",
    metadata={"description": "Lois marocaines PME"}
)

print("=== Debut de l'indexation ===\n")

total_chunks = 0
fichiers_traites = 0

for nom_fichier in sorted(os.listdir(DOSSIER_TEXTE)):

    if not nom_fichier.endswith(".txt"):
        continue

    chemin = os.path.join(DOSSIER_TEXTE, nom_fichier)
    nom_loi = nom_fichier.replace(".txt", "")

    print(f"[INDEXATION] {nom_loi}...")

    # Lecture du texte
    with open(chemin, "r", encoding="utf-8") as f:
        texte = f.read()

    # Decoupage en chunks avec chevauchement
    chunks = []
    debut = 0
    while debut < len(texte):
        fin = debut + TAILLE_CHUNK
        chunk = texte[debut:fin]
        if len(chunk.strip()) > 100:  # ignorer les chunks trop courts
            chunks.append(chunk)
        debut += TAILLE_CHUNK - CHEVAUCHEMENT

    if not chunks:
        print(f"[ATTENTION] Aucun chunk pour {nom_loi}")
        continue

    print(f"   {len(chunks)} chunks crees...")

    # Traitement par lots de 50 pour eviter les surcharges memoire
    TAILLE_LOT = 50
    for i in range(0, len(chunks), TAILLE_LOT):
        lot = chunks[i:i + TAILLE_LOT]

        # Creation des embeddings (adresses GPS)
        embeddings = modele.encode(
            ["passage: " + c for c in lot],
            show_progress_bar=False
        ).tolist()

        # Identifiants uniques pour chaque chunk
        ids = [f"{nom_loi}_chunk_{i + j}" for j in range(len(lot))]

        # Metadonnees pour chaque chunk
        metadonnees = [
            {
                "loi": nom_loi,
                "chunk_numero": i + j,
                "source": "Lois marocaines PME"
            }
            for j in range(len(lot))
        ]

        # Ajout dans la base vectorielle
        collection.add(
            documents=lot,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadonnees
        )

        total_chunks += len(lot)

    print(f"[OK] {nom_loi} — {len(chunks)} chunks indexes")
    fichiers_traites += 1

# --------------------------------------------------
# Resume final
# --------------------------------------------------
print(f"\n=== INDEXATION TERMINEE ===")
print(f"Fichiers traites : {fichiers_traites}/10")
print(f"Total chunks indexes : {total_chunks}")
print(f"Index sauvegarde dans : {os.path.abspath(DOSSIER_INDEX)}")
print("\nEtape suivante : lancer assistant.py")