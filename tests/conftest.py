import pytest

import p2p
from classes import Blockchain
from main import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def block():
    return Blockchain().mine_block()


@pytest.fixture
def set_blockchain():
    yield
    p2p.blockchain = Blockchain()


@pytest.fixture
def set_nodes():
    yield
    p2p.nodes = []
