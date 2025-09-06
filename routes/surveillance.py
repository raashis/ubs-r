from flask import Blueprint, request, jsonify
from collections import defaultdict

surveillance = Blueprint('surveillance', __name__)

def find_cycles(n, edges):
    graph = defaultdict(list)
    visited = set()
    parent = {}

    cycle_edges = set()

    def dfs(node, par):
        visited.add(node)
        for nei in graph[node]:
            if nei == par:
                continue
            if nei not in visited:
                parent[nei] = node
                dfs(nei, node)
            else:
                # back edge = cycle
                u, v = node, nei
                if (min(u, v), max(u, v)) not in cycle_edges:
                    cycle_edges.add((min(u, v), max(u, v)))

    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    for node in graph:
        if node not in visited:
            parent[node] = None
            dfs(node, None)

    return cycle_edges


@surveillance.route('/investigate', methods=['POST'])
def investigate():
    data = request.get_json()
    results = []

    for network_obj in data:
        network_id = network_obj["networkId"]
        connections = network_obj["network"]

        edges = [(edge["spy1"], edge["spy2"]) for edge in connections]

        # find all cycle edges
        cycle_edges = find_cycles(len(connections), edges)

        extra_channels = []
        for spy1, spy2 in edges:
            normalized_edge = {
                "spy1": min(spy1, spy2),
                "spy2": max(spy1, spy2)
            }
            if (normalized_edge["spy1"], normalized_edge["spy2"]) in cycle_edges:
                extra_channels.append(normalized_edge)

        # sort for determinism
        extra_channels.sort(key=lambda e: (e["spy1"], e["spy2"]))

        results.append({
            "networkId": network_id,
            "extraChannels": extra_channels
        })

    return jsonify({"networks": results})
