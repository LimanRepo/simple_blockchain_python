import json
from unittest.mock import patch

from p2p import blockchain, nodes


def test_new_transaction(client, set_blockchain):
    response = client.get("/new_transaction")

    assert blockchain.unconfirmed_transactions == [{"test": "test"}]
    assert "Transaction added." == response.text


@patch("main.announce_new_block")
@patch("classes.Blockchain.mine_block")
def test_mine_block(
    mock_mine_block, mock_announce_new_block, client, block, set_blockchain
):
    mock_mine_block.return_value = block
    response = client.get("/mine_block")

    mock_announce_new_block.assert_called_once_with(block)
    assert "Block was mined." == response.text


def test_get_chain(client, set_blockchain):
    response = client.get("/chain")
    chain_data = [blockchain.last_block.__dict__]

    assert json.loads(response.data.decode("utf-8")) == {
        "length": len(chain_data),
        "chain": chain_data,
    }


def test_get_nodes(client, set_nodes):
    nodes.append("127.0.0.1")
    response = client.get("/nodes")

    assert json.loads(response.data.decode("utf-8")) == ["127.0.0.1"]


@patch("main.register_in_network")
def test_register(mock_register_in_network, client):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"node_http_address": "127.0.0.1"})
    response = client.post("/register", data=data, headers=headers)

    mock_register_in_network.assert_called_once_with("127.0.0.1")
    assert "Node was added to network" == response.text


@patch("main.populate_node")
def test_populate_new_node(mock_populate_node, client, set_blockchain):
    mock_populate_node.return_value = (["127.0.0.1"], blockchain.to_dict())
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"host": "127.0.0.1", "port": "1234"})
    response = client.post("/populate_new_node", data=data, headers=headers)

    mock_populate_node.assert_called_once_with("127.0.0.1", "1234")
    assert json.loads(response.data.decode("utf-8")) == [
        ["127.0.0.1"],
        blockchain.to_dict(),
    ]
