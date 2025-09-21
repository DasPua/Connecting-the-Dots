from Preprocessing import preprocess_documents
from KG import make_triplets,build_graph
import time

start_time = time.time()
chunks , vectors = preprocess_documents('./input/resume oc.pdf') 
temp = make_triplets(chunks)
# print(temp)

G = build_graph(chunks, temp)
print("time taken : ", time.time() - start_time)

import matplotlib.pyplot as plt
from pyvis.network import Network
import networkx as nx

def show_graph(G, output_file='graph.html'):
    # Ensure only serializable data is added
    clean_G = nx.Graph()

    for node, attrs in G.nodes(data=True):
        safe_attrs = {k: str(v) for k, v in attrs.items() if is_json_serializable(v)}
        clean_G.add_node(node, **safe_attrs)

    for u, v, attrs in G.edges(data=True):
        safe_attrs = {k: str(v) for k, v in attrs.items() if is_json_serializable(v)}
        clean_G.add_edge(u, v, **safe_attrs)

    net = Network(notebook=False)
    net.from_nx(clean_G)
    net.write_html(output_file)  # Saves without opening

def is_json_serializable(value):
    try:
        import json
        json.dumps(value)
        return True
    except:
        return False
show_graph(G)