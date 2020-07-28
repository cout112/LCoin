from django.shortcuts import render, redirect
from manager.models import Accounts
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from hashlib import sha256
import requests
import json
import datetime






CONNECTED_NODE_ADDRESS = "http://127.0.0.1:5000"
posts = []
peers = [] 


def fetch_my_posts(account_code):
	get_chain_address = f"{CONNECTED_NODE_ADDRESS}/mychain"

	data=json.dumps({"hash":account_code})
	headers = {"Content-Type":"application/json"}
	try:
		response = requests.post(get_chain_address, data=data, headers=headers)
	except:
		return "bad request"

	content=[]
	global posts
	posts = []
	
	if response.status_code == 200:
		chain = json.loads(response.content)
		global peers
		peers=[]
		peers=chain['peers']
	for tx in chain['chain']:
			tx['hour'] = timestamp_to_string(tx['timestamp'])
			content.append(tx)

	posts = sorted(content, 
					key=lambda k: k['timestamp'], 
					reverse = True)
	print(f"print posts - {posts}")



def fetch_posts():
	get_chain_address = f"{CONNECTED_NODE_ADDRESS}/chain"
	try:
		response = requests.get(get_chain_address)
	except:
		return
	content = []
	if response.status_code == 200:

		chain = json.loads(response.content)
		print(chain)
		global peers
		peers = []
		peers = chain['peers']
		for block in chain['chain']:
			for tx in block['transactions']:
				tx['index'] = block['index']
				tx['hash'] = block['hash']
				tx['previous_hash'] = block['previous_hash']
				tx['hour'] = timestamp_to_string(tx['timestamp'])
				content.append(tx)
	global posts

	posts = sorted(content, 
					key=lambda k: k['timestamp'], 
					reverse = True)

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')



def index(request):

	if not request.user.is_authenticated:
		return redirect("authenticated")

	if request.method == 'GET':
		accountname='Main'
		account=Accounts.objects.filter(name='Main').filter(user=request.user)[0]

	if request.method == 'POST':
		accountname=request.POST['accountname']
		account=Accounts.objects.filter(name=accountname).filter(user=request.user)[0]

	if request.user.username == 'admin':
		fetch_posts()
		accounts = ''
	else:

		
		accounts = Accounts.objects.filter(user=request.user)
		for a in accounts:
			fetch_my_posts(a.code)
			if not posts:
				a.amount = a.amount
			else:
				current_amount=0.00+float(a.amount)
				for post in posts:
					if post['origin'] == a.code:
						current_amount-=float(post['amount'])
	
					elif post['destination'] == a.code:
						current_amount+=float(post['amount'])

				a.amount = current_amount
		fetch_my_posts(account.code)
		current_amount=0.00+float(account.amount)
		# for post in posts:
			

		# 	if post['origin'] == account.code:
		# 		current_amount-=float(post['amount'])
		# 		post['total']=current_amount
		# 		post['destination_user'] = Accounts.objects.get(code=post['destination']).user.username
		# 		post['origin_account'] = account.name
		# 		print(f"transaction from {account.name} to {post['destination_user']}")
		# 	elif post['destination'] == account.code:
		# 		current_amount+=float(post['amount'])
		# 		post['total']=current_amount
		# 		post['origin_user'] = Accounts.objects.get(code=post['origin']).user.username
		# 		post['destination_account'] = account.name
		# 		print(f"transaction from {post['origin_user']} to {account.name}")

		for i in range(1,len(posts)+1):
			

			if posts[-i]['origin'] == account.code:
				current_amount-=float(posts[-i]['amount'])
				posts[-i]['total']=current_amount
				posts[-i]['destination_user'] = Accounts.objects.get(code=posts[-i]['destination']).user.username
				posts[-i]['origin_account'] = account.name
				print(f"transaction from {account.name} to {posts[-i]['destination_user']}")
			elif posts[-i]['destination'] == account.code:
				current_amount+=float(posts[-i]['amount'])
				posts[-i]['total']=current_amount
				posts[-i]['origin_user'] = Accounts.objects.get(code=posts[-i]['origin']).user.username
				posts[-i]['destination_account'] = account.name
				print(f"transaction from {posts[-i]['origin_user']} to {account.name}")

			print(f"{posts[-i]}")

	url=CONNECTED_NODE_ADDRESS+"/get_unconfirmed_transactions"
	try:
		response=requests.get(url)
	except:
		context={
				"message":f"The node {CONNECTED_NODE_ADDRESS} is not online"
		}
		return render(request, 'index.html', context)
	context = {
			"posts":posts,
			"node_address":CONNECTED_NODE_ADDRESS+'/',
			"peers":sorted(peers),
			"unconfirmed_transactions":json.loads(response.content)['unconfirmed_transactions'],
			"accounts":accounts,
			"current_account":Accounts.objects.filter(user=request.user).filter(name=accountname)[0],
	}
	return render(request, 'index.html', context)


def authenticated(request):
	if request.user.is_authenticated:
		return redirect("index")
	return render(request, "authenticated.html")

def signup(request):
	if request.method != 'POST':
		return render(request, 'authenticated')
	username = request.POST['username']
	password = request.POST['password']
	email = request.POST['email']
	check_email = User.objects.filter(email=email)
	check_user = User.objects.filter(username=username)
	if check_email:
		return render(request, 'authenticated.html', {"message":"email already exists"})
	if check_user:
		return render(request, 'authenticated.html', {"message":"user already exists"})
	user = User.objects.create_user(username, email=email, password=password)
	user.save()
	forhash=json.dumps({"user":username,
			 "email":email,
			 "account":"Main"})
	account_hash=sha256(forhash.encode()).hexdigest()
	accounts=Accounts(user=user, name='Main', code=account_hash)
	accounts.save()

	return redirect("index")

def login_authenticate(request):
	print("login request")
	if request.method != 'POST':
		return redirect("index")

	username = request.POST['usernamelogin']
	password = request.POST['passwordlogin']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)	
		return redirect("index")
	else:
		return redirect("authenticated")

def logout_user(request):
	if request.method == 'POST':
		logout(request)
		return redirect("authenticated")
	return redirect("index")

def change_node(request):
	if request.method != 'POST':
		return "Bad request"
	global CONNECTED_NODE_ADDRESS
	node_address=request.POST['node_address']
	if node_address[-1] == '/':
		CONNECTED_NODE_ADDRESS = node_address[:-1]
	else:
		CONNECTED_NODE_ADDRESS = node_address
	return redirect("index")

def check_transaction(request):
	amount = request.POST['amount']
	origin = request.POST['origin']
	destination = request.POST['destination']
	destination_account = Accounts.objects.filter(code=destination)
	fetch_my_posts(origin)
	origin_account = Accounts.objects.filter(code=origin)[0]
	current_amount=0.00+float(origin_account.amount)
	for post in posts:
		if post['origin'] == origin:
			current_amount-=float(post['amount'])
		elif post['destination'] == origin:
			current_amount+=float(post['amount'])
	if float(amount) > current_amount and destination_account:
		context = {
				"message":"You don't have enough Lcoins in this account, go back to reenter amount",
				"origin":origin,
				"destination":destination_account[0],
				"amount":amount,
				"accounts":origin_account,			
		}
		return render(request, 'confirm_transaction.html', context)
	if destination_account:
		context = {
				"origin":origin,
				"destination":destination_account[0],
				"amount":amount,
				"accounts":origin_account,
				"node":CONNECTED_NODE_ADDRESS,
		}
		return render(request, 'confirm_transaction.html', context)
	context = {
			"message":"We detected the destination user doesn't exist, go back to reenter the user",
			"origin":origin,
			"destination":destination,
			"amount":amount,
			"accounts":origin_account,
	}
	return render(request, 'confirm_transaction.html', context)
	


def send_transaction(request):
	amount = request.POST['amount']
	origin_code = request.POST['origin']
	destination_code = request.POST['destination']
	origin = Accounts.objects.get(code=origin_code)
	destination = Accounts.objects.get(code=destination_code)
	

	new_tx_address = f"{CONNECTED_NODE_ADDRESS}/new_transaction"
	post_object = {
			'origin':origin_code,
			'destination':destination_code,
			'amount':amount,
	}
	response = requests.post(new_tx_address, json=post_object, headers={'Content-type': 'application/json'})
	
	return redirect("index")



def mine_request(request):
	node_address= F"{CONNECTED_NODE_ADDRESS}/mine"
	response = requests.get(node_address)
	if response.content == "No transactions to mine":
		print("No transactions to mine")
	else:
		print("mined")
	return redirect("index")

def new_account(request):
	if request.method != 'POST':
		return redirect("index")
	account_name=request.POST['account_name']
	user=request.user
	username=user.username
	email=user.email
	forhash=json.dumps({"user":username,
			 "email":email,
			 "account":account_name})
	account_hash=sha256(forhash.encode()).hexdigest()
	accounts=Accounts(user=user, name=account_name, code=account_hash)
	accounts.save()
	return redirect("index")











