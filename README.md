# 🏗️ Blockchain Demo Project

## 📋 Overview

This project is based on the tutorial "Build Your Own Blockchain in Python: A Practical Guide" available at this link. It demonstrates a simple blockchain implementation using Python and Flask, and includes functionalities for:
This project demonstrates a simple blockchain implementation using Python and Flask. It includes functionalities for:

🔨 Mining new blocks.

🔄 Adding transactions.

🧠 Achieving consensus across a distributed network of nodes.

## ✨ Features

🛠️ Create and mine new blocks.

💸 Add new transactions.

🌐 Register and resolve conflicts with other nodes.

🧩 Simple Proof of Work algorithm.

## 💻 Requirements

Python 3.x

Flask

Requests

## ⚙️ Installation

### Clone the repository
    git clone <repository-url>
    cd <repository-folder>

### Install dependencies
    pip install -r requirements.txt

## 🚀 Usage

## Run the application
    python blockchain.py -p <port>

Replace <port> with the desired port number (default is 5000).

## 📡 API Endpoints

1. ⛏️ Mine a New Block

GET /mine

Response:

    {
      "message": "New Block Forged",
      "index": <block_index>,
      "transactions": [...],
      "proof": <proof>,
      "previous_hash": "<previous_hash>"
    }

2. ➕ Add a New Transaction

POST /transactions/new

Request Body:

    {
      "sender": "<sender_address>",
      "recipient": "<recipient_address>",
      "amount": <amount>
    }

Response:

    {
      "message": "Transaction will be added to Block <block_index>"
    }

3. 🔗 View the Full Blockchain

GET /chain

Response:

    {
      "chain": [...],
      "length": <chain_length>
    }

4. 🌐 Register New Nodes

POST /nodes/register

Request Body:

    {
      "nodes": ["<node_url>", "<node_url>"]
    }

Response:

    {
      "message": "New nodes have been added",
      "total_nodes": ["<node_url>", "<node_url>"]
    }

5. 🤝 Consensus Algorithm (Resolve Conflicts)

GET /nodes/resolve

Response (if replaced):

    {
      "message": "Our chain was replaced",
      "new_chain": [...]
    }

Response (if authoritative):

    {
      "message": "Our chain is authoritative",
      "chain": [...]
    }

## ⚙️ How It Works

🔐 Hashing: Each block contains a SHA-256 hash of its contents.

🏋️ Proof of Work: A simple PoW algorithm ensures the integrity of the blockchain.

🌍 Consensus: Nodes resolve conflicts by selecting the longest valid chain.
