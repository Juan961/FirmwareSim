import uuid
import time
import json
import queue


from awscrt import mqtt5


from config import MQTT_CONFIG
from .mqtt_client import get_client


telemetry_queue = queue.Queue(maxsize=10)


ONE_HOUR_IN_SECONDS = 3600
SEND_TELEMETRY_INTERVAL = 0.5 # seconds


def telemetry_worker():
    from handlers import mission_control
    
    client = get_client()

    last_sent_time = time.time()

    while (time.time() - last_sent_time) < SEND_TELEMETRY_INTERVAL:
        now = int(time.time())

        ttl = now + ONE_HOUR_IN_SECONDS

        lat, lon, heading = mission_control.coords["lat"], mission_control.coords["lon"], mission_control.heading

        right_motor_speed, left_motor_speed = mission_control.get_motor_speeds()

        shoulder_angle, elbow_angle, wrist_angle = [1, 1, 1]

        telemetry = {
            "PK": "DEVICE#thing",
            "SK": f"TELEMETRY#{now}",
            "device_id": "thing",
            "message_id": str(uuid.uuid4()),
            "payload": {
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "heading": round(heading, 1),
                "battery": round(56, 1),
                "speedRight": round(right_motor_speed, 2),
                "speedLeft": round(left_motor_speed, 2),
                "signalStrength": round(-34, 1),
                "temperature": round(15, 1),
                "lidar": [],
                "shoulderAngle": round(shoulder_angle, 2),
                "elbowAngle": round(elbow_angle, 2),
                "wristAngle": round(wrist_angle, 2)
            },
            "created_at": now,
            "expires_at": ttl
        }

        publish_future = client.publish(mqtt5.PublishPacket(
            topic=MQTT_CONFIG["TELEMETRY_TOPIC_PUB"],
            payload=json.dumps(telemetry).encode("utf-8"),
            qos=mqtt5.QoS.AT_LEAST_ONCE
        ))

        publish_completion_data = publish_future.result(100)

        last_sent_time = time.time()

        print("Telemetry published to topic: '{}'".format(MQTT_CONFIG["TELEMETRY_TOPIC_PUB"]))
        print("PubAck received with {}\n".format(repr(publish_completion_data.puback.reason_code)))

        time.sleep(0.1)
