from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime
from web3 import Web3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app = Flask(__name__)

# 初始化 Web3 連接（使用 Infura 或 Alchemy URL）
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d6746aef3fb341ffa4b16483ec7b1ac2"))
contract_address = "0x33605d349ea88d687537a409817f9753b291f863"  # 智能合約地址
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "amount_to_store",
				"type": "uint256"
			}
		],
		"name": "store_m",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "payer",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "payee",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "TransferEvent",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "amount_to_transfer",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "payee_ad",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "payer_ad",
				"type": "address"
			}
		],
		"name": "weixin",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "amount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "check_tx",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "payee",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "payer",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "view_m",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
];  
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 連接資料庫
def connect_db():
    db_path = '/Users/zhen/Desktop/Dapp/dapp.db'
    if os.path.exists(db_path):
        print("Database found, connecting...")
        conn = sqlite3.connect(db_path)
    else:
        print("Database not found!")
        conn = None
    return conn

# 抓取鏈上歷史交易事件
def fetch_past_events():
    past_events = contract.events.TransferEvent.createFilter(fromBlock=0).get_all_entries()
    return past_events

@app.route('/view_database', methods=["GET"])
def view_database_page():
    return render_template('view_database.html')


# 同步鏈上歷史交易到 SQLite 資料庫
@app.route('/sync_blockchain', methods=["GET"])
def sync_blockchain():
    past_events = fetch_past_events()
    conn = connect_db()
    c = conn.cursor()

    for event in past_events:
        tx_hash = event['transactionHash'].hex()
        action = event['event']  
        user_id = event['args']['payer']  
        amount = event['args']['amount']  
        timestamp = datetime.datetime.now()  

        c.execute('''
            INSERT INTO transactions (tx_hash, action, user_id, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (tx_hash, action, user_id, amount, timestamp))

    conn.commit()
    c.close()
    conn.close()

    return jsonify({'message': 'Blockchain data synced successfully'})

# 其他功能與頁面邏輯
@app.route('/', methods=["GET"])
def index():
    return render_template('name_input.html')

@app.route('/main', methods=["POST"])
def main():
    name = request.form.get("name")
    current_time = datetime.datetime.now()

    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO user (name, timestamp) VALUES (?, ?)", (name, current_time))
    conn.commit()
    c.close()
    conn.close()

    return render_template('main.html', name=name)

@app.route('/store_money', methods=["GET"])
def store_money():
    return render_template('store_money.html')

@app.route('/store_money', methods=["POST"])
@app.route('/store_money', methods=["POST"])
def handle_store_money():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # 打印接收到的數據

        tx_hash = data['tx_hash']
        action = data['action']
        user_id = data['user_id']
        amount = data['amount']
        timestamp = data['timestamp']

        # 連接資料庫並執行插入操作
        conn = connect_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO transactions (tx_hash, action, user_id, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (tx_hash, action, user_id, amount, timestamp))

        conn.commit()
        c.close()
        conn.close()

        print("Transaction recorded successfully")  # 插入成功後打印
        return jsonify({'message': 'Transaction recorded successfully'})
    except Exception as e:
        print(f"Error recording transaction: {str(e)}")  # 如果發生錯誤，打印錯誤信息
        return jsonify({'error': 'Failed to record transaction'}), 500


@app.route('/transfer_money', methods=["GET"])
def transfer_money_page():
    return render_template('transfer_money.html')

@app.route('/transfer_money', methods=["POST"])
def handle_transfer_money():
    data = request.get_json()

    tx_hash = data['tx_hash']
    action = data['action']
    payer_id = data['user_id']
    receiver_id = data['receiver_id']
    amount = data['amount']
    timestamp = data['timestamp']

    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (tx_hash, action, user_id, receiver_id, amount, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tx_hash, action, payer_id, receiver_id, amount, timestamp))

    conn.commit()
    c.close()
    conn.close()

    return jsonify({'message': 'Transfer recorded successfully'})

# 提供資料庫內容的 API
@app.route('/view_database', methods=["GET"])
def view_database():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT tx_hash, action, user_id, receiver_id, amount, timestamp FROM transactions")
        transactions = cursor.fetchall()
        conn.close()
        return jsonify([{
            'tx_hash': tx[0],
            'action': tx[1],
            'user_id': tx[2],
            'receiver_id': tx[3],
            'amount': tx[4],
            'timestamp': tx[5]
        } for tx in transactions])
    except Exception as e:
        print(f"Error fetching database data: {str(e)}")
        return jsonify({"error": "Failed to fetch data"}), 500

# 刪除所有資料
@app.route('/delete_all_data', methods=["POST"])
def delete_all_data():
    conn = connect_db()
    c = conn.cursor()

    c.execute("DELETE FROM transactions")
    conn.commit()

    c.close()
    conn.close()

    return jsonify({'message': 'All data deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
