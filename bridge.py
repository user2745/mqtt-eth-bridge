import paho.mqtt.client as mqtt
import requests
import json
from web3 import Web3
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_REQUEST, MQTT_TOPIC_RESPONSE, ETH_RPC_URL

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# Callback when an MQTT message is received
def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        
        if payload.get("method") == "eth_sendTransaction":
            response = handle_transaction(payload)
        else:
            response = requests.post(ETH_RPC_URL, json=payload).json()
        
        # Publish response to MQTT
        client.publish(MQTT_TOPIC_RESPONSE, json.dumps(response))

    except Exception as e:
        client.publish(MQTT_TOPIC_RESPONSE, json.dumps({"error": str(e)}))

def handle_transaction(payload):
    """Handles sending transactions via web3.py"""
    try:
        tx = payload["params"][0]
        signed_tx = w3.eth.account.sign_transaction(tx, private_key="your-private-key")  # Secure this in production!
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return {"tx_hash": tx_hash.hex()}
    except Exception as e:
        return {"error": str(e)}

# MQTT Setup
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC_REQUEST)
client.loop_forever()
