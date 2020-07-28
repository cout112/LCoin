from hashlib import sha256
import datetime
import json
import time
from flask import Flask, request, render_template, redirect
import requests





		

class Block:

	def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):

		self.index = index
		self.transactions = transactions
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.nonce = nonce

	def compute_hash(self):
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()

class BlockChain:

	difficulty = 5


	def __init__(self):


		self.unconfirmed_transactions = []
		self.chain = []


	def create_genesis_block(self):

		genesis_block = Block(0, [], 0, 0, 0)
		genesis_block.hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)


	@property
	def last_block(self):

		return self.chain[-1]

	@staticmethod
	def proof_of_work(block):

		block.nonce = 0

		computed_hash = block.compute_hash()
		while not computed_hash.startswith('0' * BlockChain.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash()
			print (f"{block.nonce} - {computed_hash[:10]}")
		return computed_hash

	def add_block(self, block, proof):
		previous_hash = self.last_block.hash
		if previous_hash != block.previous_hash:
			return False
		if not self.is_valid_proof(block, proof):
			return False

		block.hash = proof
		self.chain.append(block)
		return True

	def is_valid_proof(self, block, block_hash):
		if block.index == 0:
			return (block_hash == block.compute_hash())
		return (block_hash.startswith('0' * BlockChain.difficulty)) and (block_hash == block.compute_hash())
	


	def add_new_transaction(self, transaction):

		self.unconfirmed_transactions.append(transaction)

	def mine(self):

		if not self.unconfirmed_transactions:
			return False
		last_block = self.last_block

		new_block = Block(index = last_block.index + 1, 
						transactions = self.unconfirmed_transactions,
						timestamp = time.time(),
						previous_hash = last_block.hash)
		proof = self.proof_of_work(new_block)
		block_added = self.add_block(new_block, proof)
		if block_added:
			self.unconfirmed_transactions = []
			return f"Mined {new_block.index} block"
		return False

	@classmethod
	def check_chain_validity(cls, chain):
		result = True
		previous_hash = '0'
		for block in chain:
			block_hash = block.hash
			delattr(block, 'hash')

			if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
				result = False
				break
			block.hash, previous_hash = block_hash, block_hash
		return result





app = Flask(__name__)
blockchain = BlockChain()
blockchain.create_genesis_block()
peers = set()
address = None







@app.route("/")
def index():
	global address
	global peers
	print(f"main page called with {peers}")
	address = request.base_url
	peers.add(request.host_url)
	connected = False
	if len(peers) > 1:
		connected = True
	return render_template("node_page.html", peers=peers, address=address, connected=connected)



@app.route("/new_transaction", methods=['POST'])
def new_transaction():
	tx_data = request.get_json()

	required_fields = ['origin', 'destination', 'amount']

	for field in required_fields:
		if not tx_data.get(field):
			return "Invalid transaction data", 404

	tx_data["timestamp"] = time.time()

	blockchain.add_new_transaction(tx_data)
	return "Success", 201



@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transactions():
	result = blockchain.mine()
	print("blockchain mined")
	if not result:
		return "No transactions to mine"
	else:
		chain_length=len(blockchain.chain)
		print(f"chain length = {chain_length}")
		consensus()
		if chain_length == len(blockchain.chain):
			print (f"announce new block for {blockchain.last_block.__dict__}")
			announce_new_block(blockchain.last_block)
			return f"Block {blockchain.last_block.index} is mined"
		else:
			return "Block not mined, current chain invalid"


@app.route("/pending_tx")
def get_pending_tx():
	return json.dumps(blockchain.unconfirmed_transactions)

@app.route("/register_node", methods=['POST'])
def register_new_peers():

	node_address = request.get_json()["node_address"]
	print (f"new node request from {node_address}")
	if not node_address:
		return "Invalid data", 400
	for node in node_address:
		peers.update(node_address)
	print (peers)
	shout_new_node()
	return get_chain()

@app.route("/chain", methods=['GET'])
def get_chain():
	chain_data = []
	for block in blockchain.chain:
		print (block.__dict__)
		chain_data.append(block.__dict__)
	length=len(chain_data)
	return json.dumps({"length":length, 
						"chain":chain_data, 
						"peers":list(peers)})


@app.route("/mychain", methods=['POST'])
def mychain():

	if request.method != 'POST':
		return "Bad request", 400
	print("mychain function called")
	chain_data=[]
	hashtofetch=request.get_json()
	print(f"return chainblocks with the hash {hashtofetch['hash']}")
	for block in blockchain.chain:
		for i in block.transactions:
			if i['origin'] == hashtofetch['hash'] or i['destination'] == hashtofetch['hash']:
				chain_data.append(i)
	length=len(chain_data)
	print(f"length of chain {length}")
	return json.dumps({"length":length, 
						"chain":chain_data, 
						"peers":list(peers)})



@app.route("/register_with", methods=['POST'])
def register_with_existing_node():
	global peers
	node_address = request.form.get("node_address")
	if not node_address:
		return "Invalid data", 400
	data = {"node_address":list(peers)}
	headers = {"Content-Type":"application/json"}
	try:
		response = requests.post(node_address + "/register_node", data=json.dumps(data), headers=headers)
	except:
		return "node doesn't exist"
	if response.status_code == 200:
		global blockchain
		
		chain_dump = response.json()['chain']
		blockchain = create_chain_from_dump(chain_dump)
		#peers.update(response.json()['peers'])
		return redirect("/")
	else:
		return response.content, response.status_code

@app.route("/add_block", methods=['POST'])
def verify_and_add_block():
	if request.method == 'POST':
		block_data=request.get_json()
		block = Block(block_data['index'], 
					block_data['transactions'], 
					block_data['timestamp'],
					block_data['previous_hash'],
					block_data['nonce'])
		proof = block_data['hash']
		added = blockchain.add_block(block, proof)

		if not added:
			return "The block was discarded by the block", 400

		return "Block added to the chain", 201
	else:
		return "Bad request", 400

@app.route("/listen_new_node", methods=['POST'])
def listen_new_node():
	global peers
	peers_listened=set()
	peers_listened.update(request.get_json()['peers'])

	peers=peers_listened
	return redirect("/")

@app.route("/check_availability")
def check_availability():
	return "available"

@app.route("/refresh_nodes")
def refresh_nodes():
	shout_new_node()
	return redirect("/")

@app.route("/get_unconfirmed_transactions")
def get_unconfirmed_transactions():

	return json.dumps({"unconfirmed_transactions":blockchain.unconfirmed_transactions})

# @app.route("/test", methods = ['POST'])
# def test():
# 	print("testing post method")
# 	dictionary = request.get_json()
# 	print(dictionary['name'])
# 	return "dictionary"












def create_chain_from_dump(chain_dump):
	generated_blockchain=BlockChain()
	generated_blockchain.create_genesis_block()
	for idx, block_data in enumerate(chain_dump):
		if idx == 0:
			continue
		block = Block(block_data['index'],
					block_data['transactions'],
					block_data['timestamp'],
					block_data['previous_hash'],
					block_data['nonce'])
		proof = block_data['hash']
		
		added = generated_blockchain.add_block(block, proof)
		if not added:
			raise Exception("The chain is tampered!!")
		
	return generated_blockchain

def consensus():
	global blockchain
	longest_chain = None
	current_len = len(blockchain.chain)		

	for peer in peers:
		response = requests.get(f'{peer}chain')	
		length = response.json()['length']
		chain = response.json()['chain']

		if length > current_len	and blockchain.check_chain_validity(chain):
			current_len =length
			longest_chain = chain

	if longest_chain:
		blockchain = longest_chain
		return True
	return False


def announce_new_block(block):
	for peer in peers:
		if peer != address:
			url = f"{peer}add_block"
			headers = {'Content-Type': "application/json"}
			response = requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)


def fetch_posts():
	get_chain_address=f"{CONNECTED_NODE_ADDRESS}/chain"
	response = requests.get(get_chain_address)
	if response.status_code == 200:
		content = []
		chain = json.loads(response.content)

		for block in chain['chain']:
			for tx in block['transactions']:
				tx['index'] = block['index']
				tx['hash'] = block['previous_hash']
				content.append(tx)

		global posts
		posts = sorted(content, key=lambda k: k['timestamp'], reverse=True)

def check_nodes():
	return "1"


def shout_new_node():
	global peers
	nodes=set()
	for peer in peers:
		try:	
			response = requests.get(peer + "check_availability")
			if response.status_code == 200:
				nodes.add(peer)
		except:
			print (f"node {peer} disconected")
	peers = nodes
	data={"peers":list(peers)}
	headers = {"Content-Type":"application/json"}
	for peer in peers:
		try:	
			response = requests.post(peer + "listen_new_node", data=json.dumps(data), headers=headers)
			if response.status_code == 200:
				nodes.add(peer)
		except:
			print (f"node {peer} disconected")
	peers = nodes
















