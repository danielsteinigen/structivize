import graphviz
import matplotlib.pyplot as plt
import networkx as nx
import rdflib

from ...renderer import Renderer


class RendererKg(Renderer):

    def preprocess_code(self):
        self._clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml") and not self._code.startswith("@"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

    def _parse_kg(self, format):
        # Load RDF or OWL file
        g = rdflib.Graph()
        return g.parse(self._filepath_code, format=format)

    def _get_label(self, label):
        return str(label).split("#")[1] if "#" in str(label) else str(label).split("/")[-1]

    def _create_graph_graphviz(self, graph):
        # Create Graphviz Digraph
        dot = graphviz.Digraph()
        # Add triples
        for subj, pred, obj in graph:
            subj_ = self._get_label(subj)
            obj_ = self._get_label(obj)
            pred_ = self._get_label(pred)
            dot.node(subj_, subj_)
            dot.node(obj_, obj_)
            dot.edge(subj_, obj_, label=pred_)
        # Render graph
        dot.render(self.filepath_image, format="png", cleanup=True)

    def _create_graph_networkx(self, graph):
        # Create a NetworkX graph
        G = nx.DiGraph()
        # Add triples
        for subj, pred, obj in graph:
            subj_ = self._get_label(subj)
            obj_ = self._get_label(obj)
            pred_ = self._get_label(pred)
            G.add_edge(subj_, obj_, label=pred_)

        # Draw the graph
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, k=5, iterations=300, scale=2.0)  # Layout algorithm
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", edge_color="gray", font_size=8)

        # for u, v, d in G.edges(data=True):
        #     nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color="gray", style="--" if d["label"].lower() in ["type", "subclassof"] else "-", arrows=True)

        # Draw edge labels
        edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

        plt.savefig(f"{self.filepath_image}.png", dpi=300, bbox_inches="tight")
        plt.close()


@Renderer.register("kg_xml")
class RendererKgXml(RendererKg):
    DEFAULT_TOOL_CONFIGS = {
        "networkx": {},
        "graphviz": {},
    }

    def _render_graphviz(self):
        graph = self._parse_kg("xml")
        self._create_graph_graphviz(graph)

    def _render_networkx(self):
        graph = self._parse_kg("xml")
        self._create_graph_networkx(graph)


@Renderer.register("kg_turtle")
class RendererKgTurtle(RendererKg):
    DEFAULT_TOOL_CONFIGS = {
        "networkx": {},
        "graphviz": {},
    }

    def _render_graphviz(self):
        graph = self._parse_kg("turtle")
        self._create_graph_graphviz(graph)

    def _render_networkx(self):
        graph = self._parse_kg("turtle")
        self._create_graph_networkx(graph)
