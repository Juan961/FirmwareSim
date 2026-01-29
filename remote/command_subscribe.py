from awscrt import mqtt5


from .mqtt_client import get_client
from config import MQTT_CONFIG


def on_message(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))


def mqtt_init_sub():
    print("===== Initializing MQTT subscriber... =====")

    client = get_client()

    subscribe_future = client.subscribe(subscribe_packet=mqtt5.SubscribePacket(
        subscriptions=[
            mqtt5.Subscription(
                topic_filter=MQTT_CONFIG["COMMAND_TOPIC_SUB"],
                qos=mqtt5.QoS.AT_LEAST_ONCE
            )
        ]
    ))

    suback = subscribe_future.result(100)

    print("Suback received with reason codes: {}".format(suback.reason_codes))
    print("✓ Successfully subscribed to both topics")
    print("Listening for messages...\n")
