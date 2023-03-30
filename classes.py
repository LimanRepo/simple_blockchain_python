import json
import time
from hashlib import sha256

PROOF_OF_WORK_DIFFICULTY = 2


class Block:
    """
    A class representing a block in a blockchain.

    Attributes:
        hash (str): The hash of the block.
        transactions (list): A list of transactions included in the block.
        timestamp (float): The timestamp of when the block was created.
        previous_hash (str): The hash of the previous block in the chain.
        nonce (int): A random number used in the proof-of-work algorithm.
    """

    def __init__(self, transactions, timestamp, previous_hash, nonce=0, hash=None):
        self.hash = hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        Computes the hash of the block using the SHA-256 hashing algorithm.

        Returns:
            The hash of the block.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def calculate_proof_of_work(self):
        """
        Calculates the proof of work for the block by repeatedly computing the hash of the block and
        incrementing the nonce until a hash with a certain number of leading zeros (as determined by
        the global constant PROOF_OF_WORK_DIFFICULTY) is found.

        Returns:
            None
        """
        while True:
            computed_hash = self.compute_hash()
            if computed_hash.startswith("0" * PROOF_OF_WORK_DIFFICULTY):
                self.hash = computed_hash
                break
            self.nonce += 1

    def is_proof_valid(self, proof):
        """
        Checks if a given proof is valid by checking if hash starts with a number of zeros equal to the difficulty,
        and if hash computed by current node is equal to hash announced by other node in network.

        Args:
            proof (str): The proof(hash) to be checked.

        Returns:
            True if the proof is valid, False otherwise.
        """
        return (
            proof.startswith("0" * PROOF_OF_WORK_DIFFICULTY)
            and proof == self.compute_hash()
        )

    @classmethod
    def from_dict(cls, block_dict, include_hash=True):
        """
        Create a new block instance from a dictionary.

        Args:
            block_dict (dict): A dictionary containing block data.
            include_hash (bool): A flag (default True) indicating whether to include the block hash in the new instance.

        Returns:
            A new instance of the Block class.

        """
        return cls(
            hash=block_dict["hash"] if include_hash else None,
            transactions=block_dict["transactions"],
            timestamp=block_dict["timestamp"],
            previous_hash=block_dict["previous_hash"],
            nonce=block_dict["nonce"],
        )


class Blockchain:
    """
    A class representing a blockchain.

    Attributes:
        unconfirmed_transactions (list): A list of unconfirmed transactions.
        chain (list): A list of blocks in the blockchain.
    """

    def __init__(self, chain=None, unconfirmed_transactions=None):
        self.unconfirmed_transactions = (
            [] if unconfirmed_transactions is None else unconfirmed_transactions
        )
        self.chain = chain
        if self.chain is None:
            self.chain = []
            self.create_genesis_block()

    def to_dict(self):
        """
        Converts the blockchain to a dictionary.

        Returns:
            A dictionary representation of the blockchain.
        """
        blocks = []
        for block in self.chain:
            blocks.append(block.__dict__)
        return {
            "unconfirmed_transactions": self.unconfirmed_transactions,
            "chain": blocks,
        }

    @classmethod
    def from_dict(cls, blockchain_dict):
        """
        Creates a new Blockchain instance from a dictionary.

        Args:
            blockchain_dict (dict): A dictionary containing the properties of the blockchain.

        Returns:
            A new Blockchain instance.
        """
        blocks = []
        for block in blockchain_dict["chain"]:
            blocks.append(Block.from_dict(block))
        return cls(
            chain=blocks,
            unconfirmed_transactions=blockchain_dict["unconfirmed_transactions"],
        )

    def create_genesis_block(self):
        """Creates genesis (first) block."""
        genesis_block = Block([], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_new_transaction(self, transaction):
        """
        Add a new transaction to the list of unconfirmed transactions.

        Args:
            transaction (dict): A dictionary containing transaction data

        Returns:
            None
        """
        self.unconfirmed_transactions.append(transaction)

    def mine_block(self):
        """
        Mines a new block adds it to the blockchain.

        Returns:
            The newly mined block.
        """
        last_block = self.last_block
        new_block = Block(
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash,
        )
        new_block.calculate_proof_of_work()

        self.chain.append(new_block)
        self.unconfirmed_transactions = []

        return new_block

    def verify_and_add_block(self, block_data):
        """
        Verifies the validity of a given block by comparing hash from last block in chain
        with previous hash in new block and checking correctness of proof.
        Adds verified block to the chain at the end.

        Args:
            block_data (dict): A dictionary containing the data for the block to be verified and added.

        Returns:
            None

        Raises:
            ValueError: If the previous hash of the given block does not match the hash of the last block in the chain.
            ValueError: If the proof of work of the given block is invalid.
        """
        block = Block.from_dict(block_data, include_hash=False)
        proof = block_data["hash"]
        if self.last_block.hash != block.previous_hash:
            raise ValueError("Previous hash incorrect")
        if not block.is_proof_valid(proof):
            raise ValueError("Block proof invalid")

        block.hash = proof
        self.chain.append(block)
