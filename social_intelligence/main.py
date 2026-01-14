from apify_fetcher import fetch_instagram, fetch_facebook
from normalizer import normalize_post
from graph_builder import build_semantic_knowledge_graph, visualize_semantic_graph

def main():
    print("\nSOCIAL INTELLIGENCE SYSTEM (CLI MODE)\n")
    print("1. Instagram\n2. Facebook")

    choice = input("Select platform (1–2): ").strip()

    if choice == "1":
        user = input("Instagram username: ")
        raw = fetch_instagram(user)
        platform = "instagram"
    elif choice == "2":
        user = input("Facebook page username: ")
        raw = fetch_facebook(user)
        platform = "facebook"
    else:
        print("Invalid choice.")
        return

    if not raw:
        print("No public posts found.")
        return

    posts = [
        normalize_post(p, platform, i)
        for i, p in enumerate(raw[:5], 1)
        if p
    ]

    graph = build_semantic_knowledge_graph(posts, user, platform)
    print(f"Nodes: {graph.number_of_nodes()} | Edges: {graph.number_of_edges()}")

    visualize_semantic_graph(graph, "graph.png")

if __name__ == "__main__":
    main()
