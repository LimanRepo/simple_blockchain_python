#!venv/bin/python
import json
import random
import subprocess
import time
import requests

FIRST_NODE_PORT = 8000
SECOND_NODE_PORT = 8001
THIRD_NODE_PORT = 8002
FOURTH_NODE_PORT = 8003

LOCALHOST = "http://127.0.0.1"


def get_chain(port):
    return requests.get(f"{LOCALHOST}:{port}/chain")


def get_nodes(port):
    return requests.get(f"{LOCALHOST}:{port}/nodes")


def mine_block(port):
    requests.get(f"{LOCALHOST}:{port}/mine_block")


def register_node(existing_node_port, new_node_port):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"node_http_address": f"{LOCALHOST}:{existing_node_port}"})
    requests.post(f"{LOCALHOST}:{new_node_port}/register", data=data, headers=headers)


def run_flask_instance_command(port):
    return f"flask --app main.py run --port {port}"


flask_app = subprocess.Popen(
    run_flask_instance_command(FIRST_NODE_PORT).split(), stdout=subprocess.PIPE
)
flask_app_2 = subprocess.Popen(
    run_flask_instance_command(SECOND_NODE_PORT).split(), stdout=subprocess.PIPE
)
flask_app_3 = subprocess.Popen(
    run_flask_instance_command(THIRD_NODE_PORT).split(), stdout=subprocess.PIPE
)
flask_app_4 = subprocess.Popen(
    run_flask_instance_command(FOURTH_NODE_PORT).split(), stdout=subprocess.PIPE
)


try:
    time.sleep(2)

    """
    Step 1:
    There is only one node in network. 
    Block is mined and there are two assertions, first checks that chain 
    has length of 2 (genesis block and one that was mined), second checks
    that node has no other nodes addresses saved.
    """
    mine_block(FIRST_NODE_PORT)
    chain = get_chain(FIRST_NODE_PORT).json()
    nodes = get_nodes(FIRST_NODE_PORT).json()

    assert chain["length"] == 2
    assert len(nodes) == 0

    """
    Step 2:
    There is still only one node in network. Second node was not yet registered.
    There are two assertion, first checks that chain from first node and second
    node are not the same (because they were not synchronised). Second assertion
    checks that second node also do not have any nodes addresses saved.
    """
    first_node_chain = get_chain(FIRST_NODE_PORT).json()
    second_node_chain = get_chain(SECOND_NODE_PORT).json()
    nodes = get_nodes(SECOND_NODE_PORT).json()

    assert first_node_chain != second_node_chain
    assert len(nodes) == 0

    """
    Step 3:
    Second node is registered to the network. There are three assertions that checks
    if node was properly synchronised. First assertion checks that both chains from 
    first and second nodes are the same. Second and third assertions checks that now
    both nodes have one node address saved (first node have address of second node
    and second node have address of first node).
    """
    register_node(FIRST_NODE_PORT, SECOND_NODE_PORT)
    first_node_chain = get_chain(FIRST_NODE_PORT).json()
    second_node_chain = get_chain(SECOND_NODE_PORT).json()
    first_node_nodes = get_nodes(FIRST_NODE_PORT).json()
    second_node_nodes = get_nodes(SECOND_NODE_PORT).json()

    assert first_node_chain == second_node_chain
    assert len(first_node_nodes) == 1
    assert len(second_node_nodes) == 1

    """
    Step 4:
    Two more nodes are registered to the network. New block is mined on randomly chosen node.
    There are five assertion, first checks that chains from all nodes are the same, next four
    checks that all nodes have exactly 3 addresses saved (each node have addresses of other nodes
    in network).
    
    """
    register_node(FIRST_NODE_PORT, THIRD_NODE_PORT)
    register_node(FIRST_NODE_PORT, FOURTH_NODE_PORT)
    random_node = [
        FIRST_NODE_PORT,
        SECOND_NODE_PORT,
        THIRD_NODE_PORT,
        FOURTH_NODE_PORT,
    ][random.randint(0, 3)]
    mine_block(random_node)
    first_node_chain = get_chain(FIRST_NODE_PORT).json()
    second_node_chain = get_chain(SECOND_NODE_PORT).json()
    third_node_chain = get_chain(THIRD_NODE_PORT).json()
    fourth_node_chain = get_chain(FOURTH_NODE_PORT).json()
    first_node_nodes = get_nodes(FIRST_NODE_PORT).json()
    second_node_nodes = get_nodes(SECOND_NODE_PORT).json()
    third_node_nodes = get_nodes(THIRD_NODE_PORT).json()
    fourth_node_nodes = get_nodes(FOURTH_NODE_PORT).json()

    assert (
        first_node_chain == second_node_chain == third_node_chain == fourth_node_chain
    )
    assert len(first_node_nodes) == 3
    assert len(second_node_nodes) == 3
    assert len(third_node_nodes) == 3
    assert len(fourth_node_nodes) == 3

finally:
    flask_app.kill()
    flask_app_2.kill()
    flask_app_3.kill()
    flask_app_4.kill()
