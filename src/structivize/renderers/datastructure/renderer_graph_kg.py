import graphviz
from graphviz import Digraph
import matplotlib.pyplot as plt
import networkx as nx
import rdflib
from rdflib.namespace import OWL, RDF, RDFS
import hashlib

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
            return {"shape": self.tool_config["shape_class"], "style": self.tool_config["style_class"], "color": self.tool_config["color_class"], "fillcolor": self.tool_config["color_class_fill"], "fontcolor": self.tool_config["color_class_font"]}
        if node in properties:
            return {"shape": self.tool_config["shape_prop"], "style": self.tool_config["style_propo"], "color": self.tool_config["color_prop"], "fillcolor": self.tool_config["color_prop_fill"], "fontcolor": self.tool_config["color_prop_font"]}
        if node in individuals:
            return {"shape": self.tool_config["shape_ind"], "style": self.tool_config["style_ind"], "color": self.tool_config["color_ind"], "fillcolor": self.tool_config["color_ind_fill"], "fontcolor": self.tool_config["color_ind_font"]}
        return {"shape": self.tool_config["shape_default"], "style": self.tool_config["style_default"], "color": self.tool_config["color_default"], "fillcolor": self.tool_config["color_default_fill"], "fontcolor": self.tool_config["color_default_font"]}


    def _edge_style(self, predicate):
        if predicate in {RDF.type}:
            return {"style": self.tool_config["line_type"], "color": self.tool_config["color_pred_type"]}
        if predicate in {RDFS.subClassOf, RDFS.subPropertyOf}:
            return {"style": self.tool_config["line_sub"], "color": self.tool_config["color_pred_sub"]}
        if predicate in {OWL.equivalentClass, OWL.sameAs}:
            return {"style": self.tool_config["line_eq"], "color": self.tool_config["color_pred_eq"]}
        return {"style": self.tool_config["line_default"], "color": self.tool_config["color_pred_default"]}


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
        "graphviz": {"direction": "TB", "shape_class": "box", "style_class": "rounded", "shape_prop": "diamond", "style_propo": "filled", "shape_ind": "ellipse", "style_ind": "filled", "shape_default": "ellipse", "style_default": "dashed", "color_class": "#1f77b4", "color_class_fill": "#ffffff", "color_class_font": "#1f77b4", "color_prop": "#9467bd", "color_prop_fill": "#f3e8ff", "color_prop_font": "#333333", "color_ind": "#2ca02c", "color_ind_fill": "#e6f4ea", "color_ind_font": "#333333", "color_default": "#7f7f7f", "color_default_fill": "#ffffff", "color_default_font": "#333333", "line_type": "solid", "color_pred_type": "#d62728", "line_sub": "dashed", "color_pred_sub": "#ff7f0e", "line_eq": "dotted", "color_pred_eq": "#8c564b", "line_default": "solid", "color_pred_default": "#555555"},
        # "graphviz": { "direction": "LR", "shape_class": "rect", "style_class": "filled", "shape_prop": "hexagon", "style_propo": "filled", "shape_ind": "circle", "style_ind": "filled", "shape_default": "egg", "style_default": "solid", "color_class": "#FFFFFF", "color_class_fill": "#1E1E1E", "color_class_font": "#00FFFF", "color_prop": "#FFFFFF", "color_prop_fill": "#2D2D2D", "color_prop_font": "#FF00FF", "color_ind": "#FFFFFF", "color_ind_fill": "#3C3C3C", "color_ind_font": "#00FF00", "color_default": "#AAAAAA", "color_default_fill": "#121212", "color_default_font": "#FFFFFF", "line_type": "bold", "color_pred_type": "#555555", "line_sub": "dashed", "color_pred_sub": "#AAAAAA", "line_eq": "dotted", "color_pred_eq": "#FFFFFF", "line_default": "solid", "color_pred_default": "#888888" },
        # "graphviz": { "direction": "TB", "shape_class": "box", "style_class": "rounded", "shape_prop": "underline", "style_propo": "", "shape_ind": "plaintext", "style_ind": "", "shape_default": "point", "style_default": "", "color_class": "#000000", "color_class_fill": "#FFFFFF", "color_class_font": "#000000", "color_prop": "#000000", "color_prop_fill": "#FFFFFF", "color_prop_font": "#333333", "color_ind": "#000000", "color_ind_fill": "#FFFFFF", "color_ind_font": "#000000", "color_default": "#000000", "color_default_fill": "#000000", "color_default_font": "#000000", "line_type": "solid", "color_pred_type": "#000000", "line_sub": "dashed", "color_pred_sub": "#000000", "line_eq": "dotted", "color_pred_eq": "#000000", "line_default": "solid", "color_pred_default": "#000000" },
        # "graphviz": { "direction": "BT", "shape_class": "component", "style_class": "filled", "shape_prop": "none", "style_propo": "", "shape_ind": "note", "style_ind": "filled", "shape_default": "ellipse", "style_default": "solid", "color_class": "#A80036", "color_class_fill": "#FFF8DC", "color_class_font": "#000000", "color_prop": "#000000", "color_prop_fill": "#FFFFFF", "color_prop_font": "#000000", "color_ind": "#808080", "color_ind_fill": "#E6E6E6", "color_ind_font": "#000000", "color_default": "#000000", "color_default_fill": "#FFFFFF", "color_default_font": "#000000", "line_type": "solid", "color_pred_type": "#000000", "line_sub": "bold", "color_pred_sub": "#A80036", "line_eq": "dotted", "color_pred_eq": "#000000", "line_default": "solid", "color_pred_default": "#000000" },
        # "graphviz": { "direction": "LR", "shape_class": "box", "style_class": "filled,rounded", "shape_prop": "ellipse", "style_propo": "filled", "shape_ind": "ellipse", "style_ind": "filled", "shape_default": "circle", "style_default": "filled", "color_class": "#4A90E2", "color_class_fill": "#D6EAF8", "color_class_font": "#2C3E50", "color_prop": "#F5B041", "color_prop_fill": "#FCF3CF", "color_prop_font": "#7D6608", "color_ind": "#58D68D", "color_ind_fill": "#D5F5E3", "color_ind_font": "#186A3B", "color_default": "#999999", "color_default_fill": "#EAECEE", "color_default_font": "#555555", "line_type": "solid", "color_pred_type": "#AAAAAA", "line_sub": "dashed", "color_pred_sub": "#555555", "line_eq": "bold", "color_pred_eq": "#2C3E50", "line_default": "solid", "color_pred_default": "#888888" },
        # "graphviz": { "direction": "TB", "shape_class": "tab", "style_class": "filled", "shape_prop": "diamond", "style_propo": "filled", "shape_ind": "box3d", "style_ind": "filled", "shape_default": "box", "style_default": "rounded", "color_class": "#000080", "color_class_fill": "#E0E0FF", "color_class_font": "#000000", "color_prop": "#800000", "color_prop_fill": "#FFE0E0", "color_prop_font": "#000000", "color_ind": "#008000", "color_ind_fill": "#E0FFE0", "color_ind_font": "#000000", "color_default": "#404040", "color_default_fill": "#F0F0F0", "color_default_font": "#000000", "line_type": "dashed", "color_pred_type": "#999999", "line_sub": "bold", "color_pred_sub": "#000000", "line_eq": "dotted", "color_pred_eq": "#FF0000", "line_default": "solid", "color_pred_default": "#555555" },
        # "graphviz": { "direction": "LR", "shape_class": "box", "style_class": "", "shape_prop": "parallelogram", "style_propo": "", "shape_ind": "circle", "style_ind": "", "shape_default": "box", "style_default": "dashed", "color_class": "#FFFFFF", "color_class_fill": "#003366", "color_class_font": "#FFFFFF", "color_prop": "#FFFFFF", "color_prop_fill": "#003366", "color_prop_font": "#FFFFFF", "color_ind": "#FFFFFF", "color_ind_fill": "#003366", "color_ind_font": "#FFFFFF", "color_default": "#FFFFFF", "color_default_fill": "#003366", "color_default_font": "#FFFFFF", "line_type": "dashed", "color_pred_type": "#AAAAAA", "line_sub": "bold", "color_pred_sub": "#FFFFFF", "line_eq": "dotted", "color_pred_eq": "#FFFFFF", "line_default": "solid", "color_pred_default": "#DDDDDD" },
        # "graphviz": { "direction": "LR", "shape_class": "record", "style_class": "filled", "shape_prop": "diamond", "style_propo": "filled", "shape_ind": "ellipse", "style_ind": "dashed", "shape_default": "point", "style_default": "", "color_class": "#333333", "color_class_fill": "#FFCC00", "color_class_font": "#000000", "color_prop": "#333333", "color_prop_fill": "#FF9999", "color_prop_font": "#000000", "color_ind": "#333333", "color_ind_fill": "#FFFFFF", "color_ind_font": "#555555", "color_default": "#000000", "color_default_fill": "#FFFFFF", "color_default_font": "#000000", "line_type": "dotted", "color_pred_type": "#888888", "line_sub": "solid", "color_pred_sub": "#000000", "line_eq": "bold", "color_pred_eq": "#0000FF", "line_default": "solid", "color_pred_default": "#333333" },
        # "graphviz": { "direction": "TB", "shape_class": "doublecircle", "style_class": "filled", "shape_prop": "plaintext", "style_propo": "", "shape_ind": "egg", "style_ind": "filled", "shape_default": "point", "style_default": "", "color_class": "#673AB7", "color_class_fill": "#D1C4E9", "color_class_font": "#311B92", "color_prop": "#009688", "color_prop_fill": "#B2DFDB", "color_prop_font": "#004D40", "color_ind": "#FF5722", "color_ind_fill": "#FFCCBC", "color_ind_font": "#BF360C", "color_default": "#9E9E9E", "color_default_fill": "#F5F5F5", "color_default_font": "#616161", "line_type": "solid", "color_pred_type": "#BDBDBD", "line_sub": "bold", "color_pred_sub": "#673AB7", "line_eq": "dashed", "color_pred_eq": "#FF5722", "line_default": "tapered", "color_pred_default": "#757575" },
        # "graphviz": { "direction": "BT", "shape_class": "box", "style_class": "rounded,filled", "shape_prop": "ellipse", "style_propo": "filled", "shape_ind": "box", "style_ind": "filled,dashed", "shape_default": "circle", "style_default": "", "color_class": "#2E86C1", "color_class_fill": "#D4E6F1", "color_class_font": "#154360", "color_prop": "#28B463", "color_prop_fill": "#D5F5E3", "color_prop_font": "#186A3B", "color_ind": "#D35400", "color_ind_fill": "#FAD7A0", "color_ind_font": "#6E2C00", "color_default": "#888888", "color_default_fill": "#FFFFFF", "color_default_font": "#333333", "line_type": "solid", "color_pred_type": "#888888", "line_sub": "solid", "color_pred_sub": "#154360", "line_eq": "bold", "color_pred_eq": "#D35400", "line_default": "solid", "color_pred_default": "#555555" },
        # "graphviz": { "direction": "LR", "shape_class": "invtrapezium", "style_class": "bold", "shape_prop": "star", "style_propo": "", "shape_ind": "Mcircle", "style_ind": "filled", "shape_default": "point", "style_default": "", "color_class": "#00FF00", "color_class_fill": "#000000", "color_class_font": "#00FF00", "color_prop": "#FF00FF", "color_prop_fill": "#000000", "color_prop_font": "#FF00FF", "color_ind": "#00FFFF", "color_ind_fill": "#003333", "color_ind_font": "#00FFFF", "color_default": "#FFFF00", "color_default_fill": "#000000", "color_default_font": "#FFFF00", "line_type": "solid", "color_pred_type": "#333333", "line_sub": "bold", "color_pred_sub": "#00FF00", "line_eq": "dashed", "color_pred_eq": "#00FFFF", "line_default": "dotted", "color_pred_default": "#FF00FF" },
        # "networkx": {},
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
