from flask import Blueprint, request, jsonify

surveillance = Blueprint('surveillance', __name__)  # ✅ This is the name you're using

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

@surveillance.route('/investigate', methods=['POST'])  # ✅ This is your endpoint
def investigate():
    data = request.get_json()
    results = []

    for network_obj in data:
        network_id = network_obj["networkId"]
        connections = network_obj["network"]

        uf = UnionFind()
        extra_channels = []

        for edge in connections:
            spy1 = edge["spy1"]
            spy2 = edge["spy2"]
            if not uf.union(spy1, spy2):
                extra_channels.append(edge)

        results.append({
            "networkId": network_id,
            "extraChannels": extra_channels
        })

    return jsonify({"networks": results})
