import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from textwrap import fill
from entity_extractor import extract_locations
import re
import os

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.unicode_minus"] = False

def _sanitize(text):
    return re.sub(r"[^\x00-\x7F]+", "", text) if text else text

def _short(text):
    text = _sanitize(text)
    wrapped = fill(text, 55)
    lines = wrapped.split("\n")
    return wrapped if len(lines) <= 4 else "\n".join(lines[:4]) + "\n..."

def _time(ts):
    try:
        if isinstance(ts, (int, float)):
            return datetime.utcfromtimestamp(ts).isoformat() + "Z"
        return ts or "UNKNOWN_TIME"
    except:
        return "UNKNOWN_TIME"

def build_semantic_knowledge_graph(posts, username, platform):
    G = nx.DiGraph()

    user = f"User:{username}"
    G.add_node(user, type="User", label=_sanitize(username))

    platform_node = f"Platform:{platform}"
    G.add_node(platform_node, type="Platform", label=platform.capitalize())
    G.add_edge(user, platform_node, relationship="ACTIVE_ON", confidence=1.0)

    for i, post in enumerate(posts, 1):
        if not post:
            continue

        post_node = f"Post:{i}"
        G.add_node(post_node, type="Post", label=f"Post {i}")
        G.add_edge(user, post_node, relationship="POSTED", confidence=1.0)

        text_node = f"Text:{i}"
        G.add_node(text_node, type="TextSignal", label=_short(post["text"]))
        G.add_edge(post_node, text_node, relationship="HAS_TEXT", confidence=1.0)

        time_node = f"Time:{i}"
        G.add_node(time_node, type="TemporalSignal", label=_time(post["timestamp"]))
        G.add_edge(post_node, time_node, relationship="HAS_TIME", confidence=0.85)

        if post["has_image"]:
            img_node = f"Image:{i}"
            G.add_node(img_node, type="ImageSignal", label="Image")
            G.add_edge(post_node, img_node, relationship="CONTAINS_IMAGE", confidence=1.0)

        if post["has_video"]:
            vid_node = f"Video:{i}"
            G.add_node(vid_node, type="VideoSignal", label="Video")
            G.add_edge(post_node, vid_node, relationship="CONTAINS_VIDEO", confidence=1.0)

        for loc in extract_locations(post["text"]):
            loc_node = f"Location:{loc}"
            G.add_node(loc_node, type="GeospatialData", label=loc)
            G.add_edge(text_node, loc_node, relationship="MENTIONS_LOCATION", confidence=0.75)

    return G

def visualize_semantic_graph(G, save_path):
    plt.figure(figsize=(40, 28), dpi=200)
    pos = nx.spring_layout(G, seed=42, k=3.0, iterations=250)

    colors = {
        "User": "#e63946",
        "Platform": "#6c757d",
        "Post": "#1d3557",
        "TextSignal": "#2a9d8f",
        "TemporalSignal": "#f4a261",
        "ImageSignal": "#7b2cbf",
        "VideoSignal": "#9d0208",
        "GeospatialData": "#00b4d8",
    }

    node_colors = [colors.get(G.nodes[n]["type"], "#000000") for n in G.nodes]

    nx.draw(G, pos, node_color=node_colors, node_size=3600,
            edge_color="#555", width=2.0, with_labels=False)

    labels = {n: G.nodes[n].get("label", "") for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight="bold")

    edge_labels = {(u, v): f'{d["relationship"]} ({d["confidence"]})'
                   for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=11)

    plt.title("Confidence-Weighted Semantic OSINT Graph", fontsize=18)
    plt.axis("off")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
