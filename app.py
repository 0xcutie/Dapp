from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)

# 連接資料庫
def connect_db():
    conn = sqlite3.connect('/content/drive/MyDrive/Colab Notebooks/2024 SC6113 T1/dapp.db')
    return conn

# 第一步：輸入名字的頁面
@app.route('/', methods=["GET"])
def index():
    return render_template('name_input.html')

# 第二步：接收名字並顯示 "Hi, [名字]"
@app.route('/main', methods=["POST"])
def main():
    name = request.form.get("name")  # 從表單中取得名字
    current_time = datetime.datetime.now()

    # 將名字記錄到資料庫
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO user (name, timestamp) VALUES (?, ?)", (name, current_time))
    conn.commit()
    c.close()
    conn.close()

    return render_template('main.html', name=name)  # 將名字傳遞到 main.html 顯示

# 顯示 Store Money 頁面
@app.route('/store_money', methods=["GET"])
def store_money():
    return render_template('store_money.html')

# 處理前端的 Store Money 操作，並記錄到資料庫
@app.route('/store_money', methods=["POST"])
def handle_store_money():
    data = request.get_json()  # 從前端獲取 JSON 數據

    # 從 JSON 數據中提取值
    tx_hash = data['tx_hash']
    action = data['action']
    user_id = data['user_id']
    amount = data['amount']
    timestamp = data['timestamp']

    # 將交易記錄寫入 SQLite 資料庫
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (tx_hash, action, user_id, amount, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (tx_hash, action, user_id, amount, timestamp))

    conn.commit()
    c.close()
    conn.close()

    return jsonify({'message': 'Transaction recorded successfully'})

# 顯示 Transfer Money 頁面
@app.route('/transfer_money', methods=["GET"])
def transfer_money_page():
    return render_template('transfer_money.html')

# 處理前端的 Transfer Money 操作，並記錄到資料庫
@app.route('/transfer_money', methods=["POST"])
def handle_transfer_money():
    data = request.get_json()  # 從前端獲取 JSON 數據

    # 從 JSON 數據中提取值
    tx_hash = data['tx_hash']
    action = data['action']
    payer_id = data['user_id']  # 這是付款方的地址
    receiver_id = data['receiver_id']  # 這是收款方的地址
    amount = data['amount']
    timestamp = data['timestamp']

    # 將交易記錄寫入 SQLite 資料庫
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

# View Database API: 提供資料庫中的數據
@app.route('/view_database', methods=["GET"])
def view_database():
    conn = connect_db()
    c = conn.cursor()

    # 獲取所有交易記錄
    c.execute("SELECT tx_hash, action, user_id, receiver_id, amount, timestamp FROM transactions")
    rows = c.fetchall()

    # 將資料轉換為 JSON 格式返回
    data = [
        {
            'tx_hash': row[0],
            'action': row[1],
            'user_id': row[2],
            'receiver_id': row[3],
            'amount': row[4],
            'timestamp': row[5]
        }
        for row in rows
    ]

    c.close()
    conn.close()
    return jsonify(data)

# 刪除所有資料的 API
@app.route('/delete_all_data', methods=["POST"])
def delete_all_data():
    conn = connect_db()
    c = conn.cursor()

    # 刪除 transactions 表中的所有記錄
    c.execute("DELETE FROM transactions")
    conn.commit()

    c.close()
    conn.close()

    return jsonify({'message': 'All data deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
