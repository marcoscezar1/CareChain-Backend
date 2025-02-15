from os import environ
import logging
import requests
import generate_results

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def hex2str(hex):
    """
    Decodes a hex string into a regular string
    """
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    """
    Encodes a string as a hex string
    """
    return "0x" + str.encode("utf-8").hex()

def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    try:
        input = hex2str(data["payload"])
        logger.info(f"Received input: '{input}' and starting results")

        care_results = generate_results.generate_results(input)
        logger.info(f"Data={input}, Generated: {care_results}")
        response = requests.post(rollup_server + "/notice", json={"payload": str2hex(str(data))})
        logger.info(f"Received notice status {response.status_code} body {response.content}")
        return "accept"
    
    except Exception as e:
        msg = f"An unexpected error ocurred processing data {data}"
        logger.error(e)
        logger.error(msg)
        response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})
        logger.info(f"Received report status {response.status_code} body {response.content}")
        return "reject"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    notice_payload = {"payload": data["payload"]}
    response = requests.post(rollup_server + "/notice", json=notice_payload)
    logger.info(f"Received notice status {response.status_code} body {response.content}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
