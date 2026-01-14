from pyvis.network import Network

def render_graph_pyvis(G, output_html):
    net = Network(
        height="900px",
        width="100%",
        bgcolor="#0e1117",
        font_color="white",
        directed=True
    )

    color_map = {
        "User": "#e63946",
        "Platform": "#6c757d",
        "Post": "#1d3557",
        "TextSignal": "#2a9d8f",
        "TemporalSignal": "#f4a261",
        "ImageSignal": "#7b2cbf",
        "VideoSignal": "#9d0208",
        "GeospatialData": "#00b4d8",
    }

    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            label=data.get("label", node),
            title=data.get("type"),
            color=color_map.get(data.get("type"), "#ffffff"),
            size=30 if data.get("type") == "User" else 18
        )

    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, label=d.get("relationship"), width=2)

    net.toggle_physics(True)
    net.show_buttons(filter_=["physics"])
    net.save_graph(output_html)
