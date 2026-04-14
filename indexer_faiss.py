import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DOSSIER_TEXTE = "lois_texte"
DOSSIER_INDEX = "lois_index"

if not os.path.exists(DOSSIER_INDEX):
    os.makedirs(DOSSIER_INDEX)

print("\n=== Chargement du modele ===")
modele = SentenceTransformer("intfloat/multilingual-e5-small")
print("[OK] Modele charge\n")

TAILLE_CHUNK = 1500
CHEVAUCHEMENT = 200

tous_chunks = []
toutes_metadonnees = []

print("=== Decoupage des textes ===\n")

for nom_fichier in sorted(os.listdir(DOSSIER_TEXTE)):
    if not nom_fichier.endswith(".txt"):
        continue

    chemin = os.path.join(DOSSIER_TEXTE, nom_fichier)
    nom_loi = nom_fichier.replace(".txt", "")

    with open(chemin, "r", encoding="utf-8") as f:
        texte = f.read()

    debut = 0
    nb_chunks = 0
    while debut < len(texte):
        fin = debut + TAILLE_CHUNK
        chunk = texte[debut:fin]
        if len(chunk.strip()) > 100:
            tous_chunks.append(chunk)
            toutes_metadonnees.append({
                "texte": chunk,
                "loi": nom_loi
            })
            nb_chunks += 1
        debut += TAILLE_CHUNK - CHEVAUCHEMENT

    print(f"[OK] {nom_loi} — {nb_chunks} chunks")

print(f"\nTotal : {len(tous_chunks)} chunks\n")
print("=== Creation des embeddings ===")

TAILLE_LOT = 64
tous_embeddings = []

for i in range(0, len(tous_chunks), TAILLE_LOT):
    lot = tous_chunks[i:i + TAILLE_LOT]
    embeddings = modele.encode(
        ["passage: " + c for c in lot],
        show_progress_bar=False
    )
    tous_embeddings.extend(embeddings)
    print(f"   {min(i + TAILLE_LOT, len(tous_chunks))}/{len(tous_chunks)} chunks traites")

print("\n=== Sauvegarde index FAISS ===")

vecteurs = np.array(tous_embeddings).astype("float32")
dimension = vecteurs.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(vecteurs)

faiss.write_index(index, os.path.join(DOSSIER_INDEX, "index.faiss"))

with open(os.path.join(DOSSIER_INDEX, "chunks.json"), "w", encoding="utf-8") as f:
    json.dump(toutes_metadonnees, f, ensure_ascii=False, indent=2)

print(f"[OK] Index FAISS sauvegarde — {index.ntotal} vecteurs")
print(f"[OK] Chunks JSON sauvegarde")
print(f"\nDossier index : {os.path.abspath(DOSSIER_INDEX)}")
print("\nEtape suivante : copier index.faiss et chunks.json sur GitHub")