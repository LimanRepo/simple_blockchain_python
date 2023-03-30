import threading

from flask import Flask, jsonify, request

from p2p import (announce_new_block, populate_node, register_in_network,
                 start_server)

app = Flask(__name__)
server_thread = threading.Thread(target=start_server)
server_thread.start()


@app.route("/new_transaction", methods=["GET"])
def new_transaction():
    """Adds (dummy) transaction"""
    from p2p import blockchain

    blockchain.add_new_transaction({"test": "test"})
    return "Transaction added."


@app.route("/mine_block", methods=["GET"])
def mine_block():
    """
    Mines block

    The endpoint calls block mining, and later propagates it to all nodes in network"""
    from p2p import blockchain

    new_block = blockchain.mine_block()
    announce_new_block(new_block)
    return "Block was mined."


@app.route("/chain", methods=["GET"])
def get_chain():
    """Returns blockchain data"""
    from p2p import blockchain

    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify({"length": len(chain_data), "chain": chain_data})


@app.route("/nodes", methods=["GET"])
def get_nodes():
    """Returns list of nodes (host and port) in network (except calling node)"""
    from p2p import nodes

    return jsonify(nodes)


@app.route("/register", methods=["POST"])
def register():
    """Registers node in network"""
    node_http_address = request.get_json()["node_http_address"]
    register_in_network(node_http_address)
    return "Node was added to network"


@app.route("/populate_new_node", methods=["POST"])
def populate_new_node():
    """
    Propagates new node across network.

    The endpoint is called from inside by node which want to register in network,
    and returns current nodes in network as well as blockchain data to allow
    synchronization for new node.
    """
    new_node_host = request.get_json()["host"]
    new_node_port = request.get_json()["port"]
    current_nodes, blockchain_data = populate_node(new_node_host, new_node_port)
    return jsonify((current_nodes, blockchain_data))
