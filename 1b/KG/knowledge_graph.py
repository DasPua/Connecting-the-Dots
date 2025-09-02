import networkx as nx 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings,ChatOllama
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel, Field
from typing import List

class Triplet(BaseModel):
    subject: str = Field(..., description="The entity or concept being described.")
    relation: str = Field(..., description="The relationship between the subject and the object.")
    object: str = Field(..., description="The target entity or value connected to the subject.")
    
class python_triplets(BaseModel):
    triplet : List[Triplet] = Field(..., description = "A list of extracted knowledge triplets.")
    
llm = ChatOllama(model = "tinyllama:1.1b", temperature=0.0,
    top_p=0.7,
    top_k=40,
    repetition_penalty=1.1,
    presence_penalty=0.0,
    frequency_penalty=0.1,
    max_tokens=512,).with_structured_output(python_triplets)

def graph_details(chunks):
    messages = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a factual information extractor.\n"
        "Input text: 'Barack Obama was born in Hawaii in 1961.'\n"
        "Valid triplets:\n"
        "[{\"subject\": \"Barack Obama\", \"relation\": \"was born in\", \"object\": \"Hawaii\"},\n"
        " {\"subject\": \"Barack Obama\", \"relation\": \"was born in year\", \"object\": \"1961\"}]\n\n"
        "Input text: 'He might have worked at Google.'\n"
        "Valid triplets:\n"
        "[] (Don't include uncertain facts)\n\n"
        "Follow this format exactly. Do not invent anything not present in the text.\n"),
        HumanMessage(content=f"Input text : {chunks.page_content}")
    ])
    messages = messages.format_messages(text=chunks.page_content)
    response = llm.invoke(
        messages
    )
    return [(t.subject, t.relation, t.object) for t in response.triplet]

def make_triplets(chunks):
    all_triplets = []
    for chunk in chunks:
        try:
            triplets = graph_details(chunk)
            all_triplets.append(triplets)
        except Exception as e:
            print("Failed to extract from chunk:", chunk.page_content[:100], "\nError:", e)
    return all_triplets

def combine_duplicates(triplets, th = 0.85):
    for chunk in triplets:
        subjects = [item[0] for item in chunk]
        embeddings = OllamaEmbeddings(model = "tinyllama:1.1b")
        vectors =[embeddings.embed_query(subject) for subject in subjects]
        merged = {}
        used = set()
        
        for i in range(len(subjects)):
            if i in used:continue
            used.add(i)
            for j in range(i+1, len(subjects)) :
                if j in used : continue
                sim = cosine_similarity([vectors[i]], [vectors[j]])[0][0]
                if sim>th:
                    used.add(j)
                    merged[subjects[j]] = subjects[i]
    return merged

def build_graph(chunks, triplets):
    G = nx.Graph()
    used = set()
    merged = combine_duplicates(triplets)
    for i, (chunk, chunk_triplets) in enumerate(zip(chunks, triplets)):
        G.add_node(i, text=chunk, type="chunk")
        for triplet in chunk_triplets:
            (subject, relation, object) = triplet
            print(triplet)
            s = merged.get(subject, subject)
            if s not in used:
                G.add_node(s, type="subject")
                used.add(s)
            G.add_node(object, type="object")
            G.add_edge(i, s, relation=relation)
            G.add_edge(i, object, relation=relation)
    return G


