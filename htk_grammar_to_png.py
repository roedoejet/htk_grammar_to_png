import argparse
import re
import networkx as nx


class Grammar:
    def __init__(self, path: str):
        self.path = path
        with open(self.path) as f:
            self.data = f.read()
        self.version_pattern = r"VERSION=(\d\.\d)"
        self.meta_pattern = r"N=(\d+)\s+L=(\d+)"
        self.state_pattern = r"I=(\d+)\s+W=([a-zA-Z!]+)"
        self.arc_pattern = r"J=\d+\s+S=(\d+)\s+E=(\d+)"

    def parse(self):
        meta_match = re.search(self.meta_pattern, self.data)
        self.meta = {
            "version": re.search(self.version_pattern, self.data).group(),
            "no_of_states": meta_match.group(1),
            "no_of_arcs": meta_match.group(2),
        }
        self.nodes = {x[0]: x[1] for x in re.findall(self.state_pattern, self.data)}
        self.arcs = re.findall(self.arc_pattern, self.data)

    def create_graph(self, ftype, null):
        G = nx.DiGraph()
        nodes = self.nodes.keys()
        if not null:
            null_nodes = [x == '!NULL' for x in self.nodes.values()]
            nodes = [x for i, x in enumerate(nodes) if not null_nodes[i]]
        G.add_nodes_from(nodes)
        nx.set_node_attributes(G, self.nodes, "label")
        G.nodes(data=True)
        for arc in self.arcs:
            if arc[0] in nodes and arc[1] in nodes:
                G.add_edge(arc[0], arc[1])
        pdot = nx.drawing.nx_pydot.to_pydot(G)
        if ftype == "png":
            pdot.write_png(f"{self.path}multi.png")
        elif ftype == "svg":
            pdot.write_svg(f"{self.path}multi.svg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A basic parser to turn HTK grammar networks into rendered images."
    )
    parser.add_argument(
        "--filetype",
        "-f",
        action="store",
        default="svg",
        choices=["svg", "png"],
        help="Type of file to render",
    )
    parser.add_argument(
        "--null",
        "-n",
        action="store_true",
        default=False,
        help="Show null nodes",
    )
    parser.add_argument("grammar", nargs="?", help="The grammar to be rendered")
    args = parser.parse_args()
    grammar = Grammar(args.grammar)
    grammar.parse()
    grammar.create_graph(args.filetype, null=args.null)