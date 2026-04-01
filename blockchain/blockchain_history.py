from web3 import Web3
import json
import os
from datetime import datetime

# ==============================
# CONNECT TO GANACHE
# ==============================
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if w3.is_connected():
    print("✅ Blockchain Connected for History")
else:
    print("❌ Blockchain NOT Connected")

account = w3.eth.accounts[0]

# ==============================
# CONTRACT ADDRESS
# ==============================
contract_address = "0xCA0d7Bc513C7271C0Ab51AE04861020b36D2b777"

# ==============================
# LOAD ABI
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

abi_path = os.path.join(
    BASE_DIR,
    "build",
    "contracts",
    "DiseaseRecord.json"
)

with open(abi_path) as file:
    contract_json = json.load(file)
    abi = contract_json["abi"]

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

# ==============================
# STORE PREDICTION
# ==============================
def store_prediction(patient, disease, result):

    try:
        timestamp = int(datetime.now().timestamp())

        tx_hash = contract.functions.addRecord(
            patient,
            disease,
            result,
            timestamp
        ).transact({
            "from": account
        })

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print("✅ Prediction stored on blockchain")
        return receipt.transactionHash.hex()

    except Exception as e:
        print("❌ Blockchain Store Error:", e)
        return None


# ==============================
# FETCH ALL RECORDS
# ==============================
def get_all_records():

    records = []

    try:
        total = contract.functions.recordsLength().call()

        for i in range(total):

            data = contract.functions.getRecord(i).call()

            record = {
                "hash": f"Record-{i}",   # simple tx label
                "patient_hash": data[0],
                "disease": data[1],
                "model": data[2],
                "time": datetime.fromtimestamp(
                    data[3]
                ).strftime("%d-%m-%Y %H:%M:%S")
            }

            records.append(record)

        return records

    except Exception as e:
        print("❌ Fetch Error:", e)
        return []


# =====================================
# ADMIN BLOCKCHAIN LOGS
# =====================================
def get_blockchain_logs():
    try:
        return get_all_records()
    except Exception as e:
        print("❌ Log Fetch Error:", e)
        return []