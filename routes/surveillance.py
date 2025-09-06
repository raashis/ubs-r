from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

class UnionFind:
    def __init__(self, spies):
        # Create a parent map for each spy
        self.parent = {spy: spy for spy in spies}
        # Create a rank map to optimize union
        self.rank = {spy: 0 for spy in spies}
    
    def find(self, spy):
        # Path compression
        if self.parent[spy] != spy:
            self.parent[spy] = self.find(self.parent[spy])
        return self.parent[spy]
    
    def union(self, spy1, spy2):
        # Union by rank
        root1 = self.find(spy1)
        root2 = self.find(spy2)
        
        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1
            return False  # No cycle formed
        return True  # Cycle detected

@app.route('/investigate', methods=['POST'])
def investigate():
    data = request.json
    
    result = {"networks": []}
    
    for network_data in data:
        network_id = network_data["networkId"]
        network = network_data["network"]
        
        spies = set()
        for connection in network:
            spies.add(connection["spy1"])
            spies.add(connection["spy2"])
        
        uf = UnionFind(spies)
        extra_channels = []
        
        for connection in network:
            spy1 = connection["spy1"]
            spy2 = connection["spy2"]
            
            if uf.union(spy1, spy2):
                extra_channels.append(connection)
        
        result["networks"].append({
            "networkId": network_id,
            "extraChannels": extra_channels
        })
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
