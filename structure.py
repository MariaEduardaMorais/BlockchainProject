import json
import requests
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import hashlib

class Blockchain:

    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        candidate_blocks = {}

        for node in neighbours:
            try:
                response = requests.get(f"{node}/chain", timeout=5)
                if response.status_code == 200:
                    chain = response.json()['chain']
                    if self.valid_chain(chain):
                        last_block = chain[-1]
                        last_block_hash = self.hash(last_block)
                        if last_block_hash not in candidate_blocks:
                            candidate_blocks[last_block_hash] = []
                        candidate_blocks[last_block_hash].append(chain)
            except requests.exceptions.RequestException:
                continue

        consensus_block = max(candidate_blocks, key=lambda x: len(candidate_blocks[x]), default=None)
        if consensus_block:
            valid_chains = [chain for chain in candidate_blocks[consensus_block]]
            longest_chain = max(valid_chains, key=len, default=None)
            if longest_chain and len(longest_chain) > len(self.chain):
                self.chain = longest_chain
                return True

        return False

    def sync_blockchain(self):
        """Synchronize the blockchain with other nodes after each block is mined."""
        self.resolve_conflicts()

# Flask Application
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    blockchain.sync_blockchain()  # Automatically synchronize and resolve conflicts after mining

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    return jsonify({'message': f'Transaction will be added to Block {index}'}), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.nodes.add(node.rstrip('/'))

    return jsonify({'message': 'New nodes have been added', 'total_nodes': list(blockchain.nodes)}), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        return jsonify({'message': 'Our chain was replaced', 'new_chain': blockchain.chain}), 200
    return jsonify({'message': 'Our chain is authoritative', 'chain': blockchain.chain}), 200

# GUI Application
def start_gui():
    def create_transaction():
        sender = sender_entry.get()
        recipient = recipient_entry.get()
        amount = amount_entry.get()
        try:
            amount = float(amount)
            response = requests.post(f'http://localhost:{port}/transactions/new',
                                     json={'sender': sender, 'recipient': recipient, 'amount': amount})
            messagebox.showinfo("Transaction", response.json()['message'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create transaction: {e}")

    def mine_block():
        try:
            response = requests.get(f'http://localhost:{port}/mine')
            messagebox.showinfo("Mining", response.json()['message'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mine block: {e}")

    def view_chain():
        try:
            response = requests.get(f'http://localhost:{port}/chain')
            chain = response.json()['chain']
            chain_details = json.dumps(chain, indent=4)
            chain_window = tk.Toplevel(root)
            chain_window.title("Blockchain Viewer")
            text = tk.Text(chain_window, wrap=tk.WORD, width=100, height=30)
            text.insert(tk.END, chain_details)
            text.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve chain: {e}")

    def resolve_chain():
        try:
            response = requests.get(f'http://localhost:{port}/nodes/resolve')
            messagebox.showinfo("Consensus", response.json()['message'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resolve conflicts: {e}")

    root = tk.Tk()
    root.title("Blockchain Interface")
    root.geometry("450x300")  # Adjusted size for better visibility

    tk.Label(root, text="Sender (origin of transaction):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    sender_entry = tk.Entry(root, width=30)
    sender_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Recipient (destination of transaction):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    recipient_entry = tk.Entry(root, width=30)
    recipient_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Amount (value to transfer):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    amount_entry = tk.Entry(root, width=30)
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Button(root, text="Create Transaction", command=create_transaction).grid(row=3, column=0, pady=10, padx=10)
    tk.Button(root, text="Mine Block", command=mine_block).grid(row=3, column=1, pady=10, padx=10)
    tk.Button(root, text="View Chain", command=view_chain).grid(row=4, column=0, pady=10, padx=10)

    root.mainloop()

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    Thread(target=start_gui).start()
    app.run(host='0.0.0.0', port=port)