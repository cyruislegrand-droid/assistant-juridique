import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

# --------------------------------------------------
# REMPLACE CETTE VALEUR PAR TA CLE GROQ
# --------------------------------------------------
import streamlit as st
CLE_GROQ = st.secrets["GROQ_API_KEY"]

# --------------------------------------------------
# Configuration de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Assistant Juridique Maroc",
    page_icon="⚖",
    layout="centered"
)

st.title("Assistant Juridique Maroc")
st.caption("Posez vos questions sur le droit des affaires marocain")
st.divider()

# --------------------------------------------------
# Chargement des outils (une seule fois au demarrage)
# --------------------------------------------------
@st.cache_resource
def charger_outils():
    # Chargement du modele d'embedding
    modele = SentenceTransformer("intfloat/multilingual-e5-small")

    # Connexion a la base vectorielle
    client = chromadb.PersistentClient(path="lois_index")
    collection = client.get_collection("lois_maroc")

    # Connexion a Groq
    groq = Groq(api_key=CLE_GROQ)

    return modele, collection, groq

modele, collection, groq = charger_outils()

# --------------------------------------------------
# Historique de la conversation
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------------------------
# Zone de saisie de la question
# --------------------------------------------------
question = st.chat_input("Posez votre question juridique...")

if question:

    # Afficher la question
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Recherche dans la base vectorielle
    with st.spinner("Recherche dans les lois..."):

        # Transformer la question en vecteur
        vecteur = modele.encode(
            ["query: " + question],
            show_progress_bar=False
        ).tolist()

        # Trouver les 5 articles les plus pertinents
        resultats = collection.query(
            query_embeddings=vecteur,
            n_results=8
        )

        # Recuperer les textes trouves
        passages = resultats["documents"][0]
        sources = [m["loi"] for m in resultats["metadatas"][0]]

        # Construire le contexte pour l'IA
        contexte = ""
        for i, (passage, source) in enumerate(zip(passages, sources)):
            contexte += f"\n--- Source {i+1} : {source} ---\n{passage}\n"

    # Generer la reponse avec Groq
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

        reponse = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": prompt_utilisateur}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        texte_reponse = reponse.choices[0].message.content

    # Afficher la reponse
    with st.chat_message("assistant"):
        st.markdown(texte_reponse)

        # Afficher les sources utilisees
        sources_uniques = list(set(sources))
        st.caption(f"Sources consultees : {', '.join(sources_uniques)}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": texte_reponse
    })