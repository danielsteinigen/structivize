import hashlib

import graphviz
import matplotlib.pyplot as plt
import networkx as nx
import rdflib
from graphviz import Digraph
from rdflib.namespace import OWL, RDF, RDFS

from ...renderer import Renderer, StatisticResponse


class RendererKg(Renderer):

    def preprocess_code(self):
        self._clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml") and not self._code.startswith("@"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

    def _parse_kg(self, format) -> rdflib.Graph:
        g = rdflib.Graph()
        return g.parse(self._filepath_code, format=format)

    def _get_label(self, label) -> str:
        return str(label).split("#")[1] if "#" in str(label) else str(label).split("/")[-1]

    def _qname_label(self, g: rdflib.Graph, term) -> str:
        label = g.value(term, RDFS.label)
        if label is not None:
            return str(label)
        label_text = self._get_label(term)
        return label_text[1:] if label_text.startswith(":") else label_text

    def _is_literal(self, node) -> bool:
        return isinstance(node, rdflib.term.Literal)

    def _build_type_sets(self, g: rdflib.Graph):
        classes = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class))
        classes |= set(g.subjects(RDFS.subClassOf, None))
        classes |= set(g.objects(None, RDFS.subClassOf))
        classes |= set(o for _, _, o in g.triples((None, RDF.type, None)) if isinstance(o, rdflib.term.URIRef))

        properties = (
            set(g.subjects(RDF.type, RDF.Property))
            | set(g.subjects(RDF.type, OWL.ObjectProperty))
            | set(g.subjects(RDF.type, OWL.DatatypeProperty))
            | set(g.subjects(RDF.type, OWL.AnnotationProperty))
        )
        properties |= set(g.subjects(RDFS.subPropertyOf, None))
        properties |= set(g.objects(None, RDFS.subPropertyOf))
        properties |= set(p for _, p, _ in g)

        individuals = set(g.subjects(RDF.type, OWL.NamedIndividual))
        for s, _, o in g.triples((None, RDF.type, None)):
            if o in classes:
                individuals.add(s)
        for s, _, _ in g:
            if s not in classes and s not in properties:
                individuals.add(s)
        return classes, properties, individuals

    def _node_style(self, node, classes, properties, individuals):
        if node in classes:
            return {
                "shape": self.tool_config["shape_class"],
                "style": self.tool_config["style_class"],
                "color": self.tool_config["color_class"],
                "fillcolor": self.tool_config["color_class_fill"],
                "fontcolor": self.tool_config["color_class_font"],
            }
        if node in properties:
            return {
                "shape": self.tool_config["shape_prop"],
                "style": self.tool_config["style_prop"],
                "color": self.tool_config["color_prop"],
                "fillcolor": self.tool_config["color_prop_fill"],
                "fontcolor": self.tool_config["color_prop_font"],
            }
        if node in individuals:
            return {
                "shape": self.tool_config["shape_ind"],
                "style": self.tool_config["style_ind"],
                "color": self.tool_config["color_ind"],
                "fillcolor": self.tool_config["color_ind_fill"],
                "fontcolor": self.tool_config["color_ind_font"],
            }
        return {
            "shape": self.tool_config["shape_default"],
            "style": self.tool_config["style_default"],
            "color": self.tool_config["color_default"],
            "fillcolor": self.tool_config["color_default_fill"],
            "fontcolor": self.tool_config["color_default_font"],
        }

    def _edge_style(self, predicate):
        if predicate in {RDF.type}:
            return {
                "style": self.tool_config["line_type"],
                "color": self.tool_config["color_pred_type"],
                "fontcolor": self.tool_config.get("color_edge_font", "#000000"),
            }
        if predicate in {RDFS.subClassOf, RDFS.subPropertyOf}:
            return {
                "style": self.tool_config["line_sub"],
                "color": self.tool_config["color_pred_sub"],
                "fontcolor": self.tool_config.get("color_edge_font", "#000000"),
            }
        if predicate in {OWL.equivalentClass, OWL.sameAs}:
            return {
                "style": self.tool_config["line_eq"],
                "color": self.tool_config["color_pred_eq"],
                "fontcolor": self.tool_config.get("color_edge_font", "#000000"),
            }
        return {
            "style": self.tool_config["line_default"],
            "color": self.tool_config["color_pred_default"],
            "fontcolor": self.tool_config.get("color_edge_font", "#000000"),
        }

    def _create_graph_graphviz(self, g):
        classes, properties, individuals = self._build_type_sets(g)
        suppress_type_targets = {
            OWL.Class,
            OWL.ObjectProperty,
            OWL.NamedIndividual,
            OWL.Ontology,
            RDFS.Class,
            RDF.Property,
            RDFS.Resource,
            RDFS.Literal,
        }

        dot = Digraph()
        bg_color = self.tool_config.get("bgcolor", "#FFFFFF")
        dot.attr("graph", bgcolor=bg_color)
        dot.attr("graph", rankdir=self.tool_config["direction"], fontsize="10")
        dot.attr("node", fontsize="10")
        dot.attr("edge", fontsize="9")

        nodes = set()
        for s, p, o in g:
            if self._is_literal(o):
                continue
            if p == RDF.type and o in suppress_type_targets:
                continue
            nodes.add(s)
            nodes.add(o)

        node_ids = {}
        for n in nodes:
            nid = node_ids.get(n)
            if nid is None:
                nid = f"n_{hashlib.md5(str(n).encode('utf-8')).hexdigest()}"
                node_ids[n] = nid
            label = self._qname_label(g, n)
            style = self._node_style(n, classes, properties, individuals)
            dot.node(nid, label=label, **style)

        for s, p, o in g:
            if self._is_literal(o):
                continue
            if p == RDF.type and o in suppress_type_targets:
                continue
            label = self._qname_label(g, p)
            style = self._edge_style(p)
            dot.edge(node_ids[s], node_ids[o], label=label, **style)

        dot.render(self.filepath_image, format="png", cleanup=True)
        self._png_save(self.filepath_image)

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
        self._png_save(self.filepath_image)


@Renderer.register("kg_xml")
class RendererKgXml(RendererKg):
    DEFAULT_TOOL_CONFIGS = {
        "graphviz": {
            "bgcolor": "#FFFFFF",
            "direction": "TB",
            "shape_class": "box",
            "style_class": "rounded,filled",
            "color_class": "#F37021",
            "color_class_fill": "#FFF0E0",
            "color_class_font": "#B34000",
            "shape_prop": "hexagon",
            "style_propo": "",
            "color_prop": "#005A9C",
            "color_prop_fill": "#FFFFFF",
            "color_prop_font": "#005A9C",
            "shape_ind": "ellipse",
            "style_ind": "filled",
            "color_ind": "#005A9C",
            "color_ind_fill": "#E6F2FF",
            "color_ind_font": "#003366",
            "shape_default": "circle",
            "style_default": "",
            "color_default": "#808080",
            "color_default_fill": "#FFFFFF",
            "color_default_font": "#333333",
            "line_type": "solid",
            "color_pred_type": "#F37021",
            "line_sub": "dashed",
            "color_pred_sub": "#005A9C",
            "line_eq": "dotted",
            "color_pred_eq": "#333333",
            "line_default": "solid",
            "color_pred_default": "#666666",
        },
        "networkx": {},
    }
    FILE_EXT = "xml"

    def _render_graphviz(self):
        graph = self._parse_kg("xml")
        self._create_graph_graphviz(graph)

    def _render_networkx(self):
        graph = self._parse_kg("xml")
        self._create_graph_networkx(graph)

    def statistics(self) -> StatisticResponse:
        g = self._parse_kg("xml")
        nodes = set()
        for s, p, o in g:
            nodes.update([s, p, o])
        resources = set()
        for s, p, o in g:
            resources.update([s, o])
        # G = nx.DiGraph()
        # for subj, pred, obj in g:
        #     G.add_edge(str(subj), str(obj), label=str(pred))
        # nodes_nx = G.number_of_nodes()
        # return {"nodes": len(nodes), "resources": len(resources), "triples": len(g)}

        return StatisticResponse(node_types={"nodes": len(resources)})


@Renderer.register("kg_turtle")
class RendererKgTurtle(RendererKg):
    DEFAULT_TOOL_CONFIGS = {
        "graphviz": {},
        "networkx": {},
    }
    FILE_EXT = "ttl"

    def _render_graphviz(self):
        graph = self._parse_kg("turtle")
        self._create_graph_graphviz(graph)

    def _render_networkx(self):
        graph = self._parse_kg("turtle")
        self._create_graph_networkx(graph)
