import json
import re
import sys

from PySpice.Spice.Parser import SpiceParser

from ....utils import load_text


def parse_spice_line(line):
    line = line.strip()
    if line.startswith(("*", ".", ";")) or not line:
        return None
    tokens = re.split(r"\s+", line)
    print(tokens)
    return tokens


def parse_pyspice(code):
    code = f"* X\n{code}"
    parser = SpiceParser(source=code)
    circuit = parser.build_circuit()
    elements = []
    for element in circuit.elements:
        name = element.name
        pins = element.node_names
        value = str(element.format_spice_parameters())
        elements.append([name] + pins + [value if value else ""])

    return elements


def convert_spice_to_yosys_json(spice_file, json_file):
    # with open(spice_file, 'r') as f:
    #     lines = f.readlines()

    cells = {}
    nets_found = set()

    spyce_parse = parse_pyspice(load_text(spice_file))
    for tokens in spyce_parse:
        # for line in lines:
        # tokens = parse_spice_line(line)
        if tokens is None:
            continue
        device = tokens[0]
        dev_type = device[0].upper()
        name = device

        if dev_type == "R":
            conns = {"A": tokens[1], "B": tokens[2]}
            cells[name] = {
                "type": "r_v",
                "connections": {},
                "port_directions": {"A": "input", "B": "output"},
                "attributes": {"value": tokens[3] if len(tokens) > 3 else ""},
            }
        elif dev_type == "C":
            conns = {"A": tokens[1], "B": tokens[2]}
            cells[name] = {
                "type": "c_v",
                "connections": {},
                "port_directions": {"A": "input", "B": "output"},
                "attributes": {"value": tokens[3] if len(tokens) > 3 else ""},
            }
        elif dev_type == "L" and tokens[0] != "LAMP":
            conns = {"A": tokens[1], "B": tokens[2]}
            cells[name] = {
                "type": "l_v",
                "connections": {},
                "port_directions": {"A": "input", "B": "output"},
                "attributes": {"value": tokens[3] if len(tokens) > 3 else ""},
            }
        elif dev_type == "D":
            conns = {"+": tokens[1], "-": tokens[2]}
            cells[name] = {
                "type": "d_v",
                "connections": {},
                "port_directions": {"+": "input", "-": "output"},
                "attributes": {"value": tokens[3] if len(tokens) > 3 else ""},
            }
        elif dev_type == "V":
            conns = {"+": tokens[1], "-": tokens[2]}
            cells[name] = {
                "type": "v",
                "connections": {},
                "attributes": {"value": f"{tokens[3] if len(tokens) > 3 else ''} {tokens[4] if len(tokens) > 4 else ''}"},
            }
        elif dev_type == "I":
            conns = {"+": tokens[1], "-": tokens[2]}
            cells[name] = {
                "type": "i",
                "connections": {},
                "attributes": {"value": f"{tokens[3] if len(tokens) > 3 else ''} {tokens[4] if len(tokens) > 4 else ''}"},
            }
        elif dev_type == "Q" or dev_type == "M":
            conns = {"C": tokens[1], "B": tokens[2], "E": tokens[3]}
            cells[name] = {"type": "q_npn", "connections": {}, "port_directions": {"C": "input", "B": "input", "E": "output"}}
        # TODO: add S

        else:
            # print(f"Type not found: {dev_type}")
            conns = {"in0": tokens[1], "out0": tokens[2]}  # in0, in1, out0, out1 TODO: check if this component has more pins
            cells[name] = {"type": "generic", "connections": {}, "port_directions": {"in0": "input", "out0": "output"}}

        for net in conns.values():
            nets_found.add(net)
        cells[name]["connections"] = conns

    nets_found = sorted(nets_found)
    net_to_id = {net: idx for idx, net in enumerate(nets_found)}

    for cell in cells.values():
        for pin, netname in cell["connections"].items():
            cell["connections"][pin] = [net_to_id[netname]]

    yosys_json = {"modules": {"top": {"cells": cells, "netnames": {net: {"bits": [idx]} for net, idx in net_to_id.items()}}}}

    with open(json_file, "w") as f:
        json.dump(yosys_json, f, indent=2)

    print(f"✅ JSON saved to {json_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python spice2yosysjson.py <input.spice> <output.json>")
        sys.exit(1)
    convert_spice_to_yosys_json(sys.argv[1], sys.argv[2])
