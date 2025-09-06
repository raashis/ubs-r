import logging
from collections import defaultdict, Counter, deque
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)


def would_create_cycle(keep_adj, u, v):
    """
    If we add u->v, does it create a directed cycle?
    Check if there's already a path v -> ... -> u in the kept graph.
    """
    if u == v:
        return True
    # BFS/DFS from v to see if we can reach u
    q = deque([v])
    seen = {v}
    while q:
        x = q.popleft()
        if x == u:
            return True
        for nxt in keep_adj[x]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return False


@app.route('/investigate', methods=['POST'])
def investigate():
    payload = request.get_json(silent=True) or {}
    networks = payload.get("networks", [])
    out = {"networks": []}

    for net in networks:
        net_id = net.get("networkId")
        edges = net.get("network", [])

        # Normalize edges as (u, v)
        E = [(e.get("spy1"), e.get("spy2")) for e in edges if e.get("spy1") and e.get("spy2")]

        # Stats to guide greedy keep/cut
        # Prefer keeping edges whose target is rare (helps preserve unique connections).
        target_freq = Counter(v for _, v in E)

        # Sort edges: 1) ascending target frequency, 2) source name, 3) target name
        # (So we keep edges to rare targets first; ties are stable & deterministic.)
        E_sorted = sorted(E, key=lambda ev: (target_freq[ev[1]], ev[0], ev[1]))

        # Degree constraints and kept graph
        indeg = defaultdict(int)
        outdeg = defaultdict(int)
        keep_adj = defaultdict(list)

        extras = []

        for (u, v) in E_sorted:
            # Rule 1: one outgoing per spy
            if outdeg[u] >= 1:
                extras.append({"spy1": u, "spy2": v})
                continue
            # Rule 2: one incoming per spy
            if indeg[v] >= 1:
                extras.append({"spy1": u, "spy2": v})
                continue
            # Rule 3: no cycles
            if would_create_cycle(keep_adj, u, v):
                extras.append({"spy1": u, "spy2": v})
                continue

            # Safe to keep
            keep_adj[u].append(v)
            outdeg[u] += 1
            indeg[v] += 1

        out["networks"].append({
            "networkId": net_id,
            "extraChannels": extras
        })

    return jsonify(out)
