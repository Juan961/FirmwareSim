import time


from awsiot import mqtt5_client_builder


from config import MQTT_CONFIG


TIMEOUT = 100


client = None
connection_established = False


def on_message(publish_received_data):
    publish_packet = publish_received_data.publish_packet
    topic = publish_packet.topic
    payload = publish_packet.payload
    print("\n=== MESSAGE RECEIVED ===")
    print("Topic: '{}'".format(topic))
    print("Payload: {}".format(payload.decode('utf-8')))
    print("========================\n")


def on_lifecycle_connection_success(lifecycle_event_data):
    global connection_established
    connection_established = True
    print("\n*** Connection established successfully ***\n")


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

    client = mqtt5_client_builder.mtls_from_path(
        endpoint=MQTT_CONFIG["ENDPOINT"],
        cert_filepath=MQTT_CONFIG["PATH_TO_CERT"],
        pri_key_filepath=MQTT_CONFIG["PATH_TO_PRIVATE_KEY"],
        client_id=MQTT_CONFIG["CLIENT_ID"],
        on_publish_received=on_message,
        on_lifecycle_connection_success=on_lifecycle_connection_success,
        on_lifecycle_stopped=on_lifecycle_stopped,
        on_lifecycle_disconnection=on_lifecycle_disconnection,
    )

    print("Starting MQTT client...")
    client.start()
    
    # Wait for connection to be established
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
