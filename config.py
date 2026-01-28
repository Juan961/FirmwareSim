MQTT_CONFIG = {
    "CLIEND_ID": "firmware",
    "ENDPOINT": "a383zn5ixngw87-ats.iot.us-east-1.amazonaws.com",
    "PATH_TO_CERT": "./certificates/thing.cert.pem",
    "PATH_TO_PUBLIC_KEY": "./certificates/thing.public.key",
    "PATH_TO_PRIVATE_KEY": "./certificates/thing.private.key",

    "COMMAND_TOPIC_SUB": "device/thing/command",

    "TELEMETRY_TOPIC_PUB": "device/thing/telemetry",
    "HEARTBEAT_TOPIC_PUB": "device/thing/heartbeat",
    "ACK_TOPIC_PUB": "device/thing/ack",
    "STATUS_TOPIC_PUB": "device/thing/status",
}
