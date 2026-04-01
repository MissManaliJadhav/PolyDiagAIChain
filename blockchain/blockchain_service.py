from web3 import Web3
import json
import os
from datetime import datetime

# =====================================
# CONNECT TO GANACHE BLOCKCHAIN
# =====================================
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if w3.is_connected():
    print("✅ Blockchain Connected Successfully")
else:
    print("❌ Blockchain NOT Connected")

# =====================================
# USE FIRST GANACHE ACCOUNT
# =====================================
account = w3.eth.accounts[0]

# =====================================
# CONTRACT ADDRESS (PASTE YOUR DEPLOYED ADDRESS)
# =====================================
contract_address = "0xCA0d7Bc513C7271C0Ab51AE04861020b36D2b777"

# =====================================
# LOAD CONTRACT ABI
# =====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

abi_path = os.path.join(
    BASE_DIR,
    "build",
    "contracts",
    "DiseaseRecord.json"
)

with open(abi_path, encoding="utf-8") as file:
    contract_json = json.load(file)
    abi = contract_json["abi"]

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

# =====================================
# STORE PREDICTION INTO BLOCKCHAIN
# =====================================
def store_prediction(patient_name, disease, result):
    try:
        print("📦 Sending Data To Blockchain...")
        print(patient_name, disease, result)

        tx_hash = contract.functions.addRecord(
            patient_name,
            disease,
            result
        ).transact({
            "from": account
        })

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        tx_id = receipt.transactionHash.hex()

        print("✅ Stored Successfully")
        print("Transaction ID:", tx_id)

        return tx_id

    except Exception as e:
        print("❌ Blockchain Error:", e)
        return None


# =====================================
# GET ALL RECORDS FROM BLOCKCHAIN
# =====================================
def get_all_records():

    records = []

    try:
        total = contract.functions.recordsLength().call()

        for i in range(total):

            data = contract.functions.getRecord(i).call()
            record_result = data[2]
            if "Trust:" in record_result:
                trust_value = record_result.split("Trust:")[-1]
            else:
                trust_value = "N/A"
                record = {"hash": f"Record-{i}","patient": data[0],"disease": data[1],"result": record_result,"trust": trust_value,
    "timestamp": datetime.fromtimestamp(data[3]
    ).strftime("%d-%m-%Y %H:%M:%S")
} 
            records.append(record)

        return records

    except Exception as e:
        print("❌ Fetch Error:", e)
        return []

# =====================================
# GET RECORDS FOR SPECIFIC PATIENT
# =====================================
def get_patient_records(patient_name):
    try:
        all_records = get_all_records()

        patient_records = [
            r for r in all_records
            if r["patient"] == patient_name
        ]

        return patient_records

    except Exception as e:
        print("❌ Patient Fetch Error:", e)
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