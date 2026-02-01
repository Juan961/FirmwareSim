import json
import time


from awsiot import mqtt5_client_builder


from config import MQTT_CONFIG
from .command_queue import commands_queue


TIMEOUT = 100


client = None
connection_established = False


def on_message(publish_received_data):
    try:
        print("\n=== MESSAGE RECEIVED ===")
        publish_packet = publish_received_data.publish_packet
        topic = publish_packet.topic
        payload = json.loads(publish_packet.payload)
        print("Topic: '{}'".format(topic))

        if payload.get("command"):
            commands_queue.add_command(payload)

    except Exception as e:
        print(f"Error processing incoming message: {e}")


def on_lifecycle_connection_success(lifecycle_event_data):
    global connection_established
    connection_established = True
    print("\n*** Connection established successfully ***\n")


def on_lifecycle_connection_failure(lifecycle_event_data):
    print(f"\n*** Connection failed: {lifecycle_event_data} ***\n")


def on_lifecycle_stopped(lifecycle_event_data):
    global connection_established
    connection_established = False
    print("\n*** Connection stopped ***\n")


def on_lifecycle_disconnection(lifecycle_event_data):
    global connection_established
    connection_established = False
    print("\n*** Connection disconnected ***\n")


def start_mqtt():
    global client

    print(f"Connecting to endpoint: {MQTT_CONFIG['ENDPOINT']}")
    print(f"Client ID: {MQTT_CONFIG['CLIENT_ID']}")
    print(f"Certificate path: {MQTT_CONFIG['PATH_TO_CERT']}")
    print(f"Private key path: {MQTT_CONFIG['PATH_TO_PRIVATE_KEY']}")

    # Verify certificate files exist
    import os
    if not os.path.exists(MQTT_CONFIG['PATH_TO_CERT']):
        raise FileNotFoundError(f"Certificate not found: {MQTT_CONFIG['PATH_TO_CERT']}")
    if not os.path.exists(MQTT_CONFIG['PATH_TO_PRIVATE_KEY']):
        raise FileNotFoundError(f"Private key not found: {MQTT_CONFIG['PATH_TO_PRIVATE_KEY']}")

    client = mqtt5_client_builder.mtls_from_path(
        endpoint=MQTT_CONFIG["ENDPOINT"],
        cert_filepath=MQTT_CONFIG["PATH_TO_CERT"],
        pri_key_filepath=MQTT_CONFIG["PATH_TO_PRIVATE_KEY"],
        client_id=MQTT_CONFIG["CLIENT_ID"],
        on_publish_received=on_message,
        on_lifecycle_connection_success=on_lifecycle_connection_success,
        on_lifecycle_stopped=on_lifecycle_stopped,
        on_lifecycle_disconnection=on_lifecycle_disconnection,
        on_lifecycle_connection_failure=on_lifecycle_connection_failure
    )

    print("Starting MQTT client...")
    client.start()

    print("Waiting for connection...")
    max_wait = 10
    waited = 0
    while not connection_established and waited < max_wait:
        time.sleep(0.5)
        waited += 0.5
    
    if not connection_established:
        raise Exception("Failed to establish connection within {} seconds".format(max_wait))
    
    print("MQTT client connected and ready!")


def get_client():
    global client

    if client is None:
        start_mqtt()

    return client
