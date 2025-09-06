import json
import logging
import heapq
from collections import defaultdict
from routes import app  
from flask import request

logger = logging.getLogger(__name__)


def dijkstra(n, graph, src):
    dist = [float("inf")] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[v] > d + w:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return dist


def build_distance_matrix(subway):
    graph = defaultdict(list)
    stations = set()
    for route in subway:
        u, v = route["connection"]
        fee = route["fee"]
        graph[u].append((v, fee))
        graph[v].append((u, fee))
        stations.add(u)
        stations.add(v)

    n = max(stations) + 1
    return [dijkstra(n, graph, i) for i in range(n)]


def weighted_interval(tasks, dist_matrix, start_station):
    import bisect
    tasks = sorted(tasks, key=lambda t: t["end"])
    n = len(tasks)
    ends = [t["end"] for t in tasks]
    p = [bisect.bisect_right(ends, tasks[i]["start"]) - 1 for i in range(n)]
    dp = [(0, 0, [])] * (n + 1)

    for i in range(1, n + 1):
        task = tasks[i - 1]
        name, score, station = task["name"], task["score"], task["station"]
        best = dp[i - 1]

        prev_score, prev_fee, prev_schedule = dp[p[i - 1] + 1]

        if prev_score > 0 or p[i - 1] == -1:
            new_score = prev_score + score
            new_schedule = prev_schedule + [task]

            fee = 0
            if new_schedule:
                fee += dist_matrix[start_station][new_schedule[0]["station"]]
                for k in range(len(new_schedule) - 1):
                    fee += dist_matrix[new_schedule[k]["station"]][new_schedule[k + 1]["station"]]
                fee += dist_matrix[new_schedule[-1]["station"]][start_station]

            new_tuple = (new_score, fee, new_schedule)

            if new_tuple[0] > best[0]:
                best = new_tuple
            elif new_tuple[0] == best[0] and new_tuple[1] < best[1]:
                best = new_tuple

        dp[i] = best

    return dp[n]


@app.route('/princessDiaries', methods=['POST'])
def princess_diaries():
    data = request.get_json()
    tasks = data.get("tasks", [])
    subway = data.get("subway", [])
    start_station = data.get("starting_station", 0)

    logger.info(f"Received {len(tasks)} tasks")

    dist_matrix = build_distance_matrix(subway)

    max_score, min_fee, schedule = weighted_interval(tasks, dist_matrix, start_station)

    result = {
        "max_score": max_score,
        "min_fee": min_fee,
        "schedule": [t["name"] for t in schedule]
    }

    logger.info(f"Returning result: {result}")
    return json.dumps(result)
