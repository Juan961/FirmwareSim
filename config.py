import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MQTT_CONFIG = {
    "CLIENT_ID": "thing",
    "ENDPOINT": "a383zn5ixngw87-ats.iot.us-east-1.amazonaws.com",
    "PATH_TO_CERT": os.path.join(_SCRIPT_DIR, "certificates", "thing.cert.pem"),
    "PATH_TO_PUBLIC_KEY": os.path.join(_SCRIPT_DIR, "certificates", "thing.public.key"),
    "PATH_TO_PRIVATE_KEY": os.path.join(_SCRIPT_DIR, "certificates", "thing.private.key"),

    "COMMAND_TOPIC_SUB": "device/thing/command",

    "TELEMETRY_TOPIC_PUB": "device/thing/telemetry",
    "HEARTBEAT_TOPIC_PUB": "device/thing/heartbeat",
    "ACK_TOPIC_PUB": "device/thing/ack",
    "STATUS_TOPIC_PUB": "device/thing/status",
}
