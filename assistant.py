import streamlit as st
import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from groq import Groq

CLE_GROQ = st.secrets["GROQ_API_KEY"]
st.set_page_config(
    page_title="Assistant Juridique Maroc",
    page_icon="⚖",
    layout="centered"
)

st.title("Assistant Juridique Maroc")
st.caption("Posez vos questions sur le droit des affaires marocain")
st.divider()

@st.cache_resource
def charger_outils():
    modele = SentenceTransformer("intfloat/multilingual-e5-small")

    # Charger index FAISS
    index = faiss.read_index("lois_index/index.faiss")

    # Charger les textes et metadonnees
    with open("lois_index/chunks.json", "r", encoding="utf-8") as f:
        donnees = json.load(f)

    groq_client = Groq(api_key=CLE_GROQ)
    return modele, index, donnees, groq_client

modele, index, donnees, groq_client = charger_outils()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Posez votre question juridique...")

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("Recherche dans les lois..."):
        vecteur = modele.encode(
            ["query: " + question],
            show_progress_bar=False
        ).astype("float32")

        distances, indices = index.search(vecteur, 8)

        passages = []
        sources = []
        for idx in indices[0]:
            if idx < len(donnees):
                passages.append(donnees[idx]["texte"])
                sources.append(donnees[idx]["loi"])

        contexte = ""
        for i, (passage, source) in enumerate(zip(passages, sources)):
            contexte += f"\n--- Source {i+1} : {source} ---\n{passage}\n"

    with st.spinner("Redaction de la reponse..."):
        prompt_systeme = """Tu es un assistant juridique specialise dans le droit marocain des affaires.
Tu reponds aux questions en te basant UNIQUEMENT sur les textes de loi fournis.
Tu cites toujours la loi et l'article source de ta reponse.
Tu reponds en francais de maniere claire et structuree.
Si la reponse ne se trouve pas dans les textes fournis, dis-le clairement."""

        prompt_utilisateur = f"""Question : {question}

Textes de loi pertinents :
{contexte}

Reponds a la question en citant les articles et lois sources."""

        reponse = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": prompt_utilisateur}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        texte_reponse = reponse.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(texte_reponse)
        sources_uniques = list(set(sources))
        st.caption(f"Sources : {', '.join(sources_uniques)}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": texte_reponse
    })