from flask import Blueprint, request, jsonify

surveillance = Blueprint('surveillance', __name__)

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX == rootY:
            return False
        self.parent[rootY] = rootX
        return True


@surveillance.route('/investigate', methods=['POST'])
def investigate():
    data = request.get_json()
    results = []

    for network_obj in data:
        network_id = network_obj["networkId"]
        connections = network_obj["network"]

        uf = UnionFind()
        nodes = set()
        for edge in connections:
            nodes.add(edge["spy1"])
            nodes.add(edge["spy2"])

        needed_edges = len(nodes) - 1
        kept_edges = []
        extra_channels = []

        for edge in connections:
            spy1, spy2 = edge["spy1"], edge["spy2"]

            normalized_edge = {
                "spy1": min(spy1, spy2),
                "spy2": max(spy1, spy2)
            }

            if len(kept_edges) < needed_edges and uf.union(spy1, spy2):
                kept_edges.append(normalized_edge)
            else:
                extra_channels.append(normalized_edge)

        # Sort output for determinism
        extra_channels.sort(key=lambda e: (e["spy1"], e["spy2"]))

        results.append({
            "networkId": network_id,
            "extraChannels": extra_channels
        })

    return jsonify({"networks": results})
