import json
import pickle
import socket
import threading

import requests

from classes import Blockchain

ADD_NODE_PREFIX = b"1"
ADD_BLOCK_PREFIX = b"2"
LOCALHOST = "127.0.0.1"

host = None
port = None
nodes = []
blockchain = Blockchain()


def register_in_network(node_http_address):
    """
     Registers the current node in network.

    The function calls another node, so it can propagate new node host and port across network,
    also synchronises new node blockchain data as well as its list of nodes.

     Args:
         node_http_address (string): A string representing the HTTP address of a node in the network.

     Returns:
         None
    """
    url = f"{node_http_address}/populate_new_node"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"host": host, "port": port})
    response = requests.post(url, data=data, headers=headers)

    global nodes
    nodes, blockchain_data = json.loads(response.content)
    global blockchain
    blockchain = Blockchain.from_dict(blockchain_data)


def populate_node(new_node_host, new_node_port):
    """
    Contains logic for new node propagation.

    The function sends new node host and port using socket for communication with other nodes in network.

    Args:
        new_node_host (string): A string representing the hostname of the new node to be populated.
        new_node_port (int): An integer representing the port number on which the new node socket will be listening.

    Returns:
        A tuple containing two items:
            1. A list of dictionaries representing the current network nodes.
            2. A dictionary representing the current state of the blockchain.
    """
    serialized_node = pickle.dumps(
        json.dumps({"host": new_node_host, "port": new_node_port})
    )
    for node in nodes:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((node["host"], node["port"]))
            msg = ADD_NODE_PREFIX + serialized_node
            s.sendall(msg)

    current_nodes = nodes.copy()
    current_nodes.append({"host": host, "port": port})
    nodes.append({"host": new_node_host, "port": new_node_port})

    return current_nodes, blockchain.to_dict()


def announce_new_block(block):
    """
    Contains logic for new block propagation.

    The function sends new block data using socket for communicating with other nodes in network.

    Args:
        block (Block): A Block object representing the new block to be announced.

    Returns:
        None
    """
    serialized_block_data = pickle.dumps(json.dumps(block.__dict__, sort_keys=True))
    for node in nodes:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((node["host"], node["port"]))
            msg = ADD_BLOCK_PREFIX + serialized_block_data
            s.sendall(msg)


def connection_handler(conn):
    """
    Handles incoming connections from socket.

    The function checks prefix of message and based on it handles properly adding new node or new block actions.

    Args:
        conn (socket): A socket object representing a connection.

    Returns:
    None
    """
    data = conn.recv(1024)
    prefix = data[:1]
    body = data[1:]

    if prefix == ADD_NODE_PREFIX:
        new_node = json.loads(pickle.loads(body))
        nodes.append({"host": new_node["host"], "port": new_node["port"]})
    elif prefix == ADD_BLOCK_PREFIX:
        block_data = json.loads(pickle.loads(body))
        blockchain.verify_and_add_block(block_data)

    conn.close()


def start_server():
    """Creates a  socket and listens for incoming connections.

    The function binds the socket to a random port on the local host and listens for incoming connections. Once a
    connection is established, the function spawns a new thread to handle the connection.

    Returns:
        None
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LOCALHOST, 0))
        global host
        global port
        host, port = s.getsockname()
        s.listen()

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=connection_handler, args=(conn,))
            thread.start()
