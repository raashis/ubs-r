import logging
from collections import defaultdict, Counter, deque
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def would_create_cycle(keep_adj, u, v):
    """
    Returns True if adding u->v creates a cycle in the kept graph.
    BFS from v to see if we can reach u.
    """
    if u == v:
        return True
    q = deque([v])
    seen = {v}
    while q:
        x = q.popleft()
        for nxt in keep_adj.get(x, []):
            if nxt == u:
                return True
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return False


@app.route('/investigate', methods=['POST'])
def investigate():
    try:
        payload = request.get_json(force=True)
        if not payload or "networks" not in payload:
            return jsonify({"error": "Missing 'networks' field in request"}), 400

        networks_input = payload.get("networks", [])
        output = {"networks": []}

        for net in networks_input:
            net_id = net.get("networkId", "unknown")
            edges = net.get("network", [])

            # Normalize edges to (spy1, spy2) strings
            E = []
            for e in edges:
                spy1 = e.get("spy1")
                spy2 = e.get("spy2")
                if spy1 is None or spy2 is None:
                    logger.warning(f"Skipping invalid edge in {net_id}: {e}")
                    continue
                E.append((str(spy1), str(spy2)))

            # Sort edges: keep edges to rare targets first for deterministic output
            target_freq = Counter(v for _, v in E)
            E_sorted = sorted(E, key=lambda ev: (target_freq[ev[1]], ev[0], ev[1]))

            indeg = defaultdict(int)
            outdeg = defaultdict(int)
            keep_adj = defaultdict(list)
            extras = []

            for u, v in E_sorted:
                if outdeg[u] >= 1:
                    extras.append({"spy1": u, "spy2": v})
                    continue
                if indeg[v] >= 1:
                    extras.append({"spy1": u, "spy2": v})
                    continue
                if would_create_cycle(keep_adj, u, v):
                    extras.append({"spy1": u, "spy2": v})
                    continue

                keep_adj[u].append(v)
                outdeg[u] += 1
                indeg[v] += 1

            output["networks"].append({
                "networkId": net_id,
                "extraChannels": extras
            })

        return jsonify(output)

    except Exception as e:
        logger.exception("Error processing /investigate request")
        return jsonify({"error": str(e)}), 500
