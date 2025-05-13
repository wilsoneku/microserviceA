import zmq
import json
import requests
import os
import finnhub
from dotenv import load_dotenv

def validate_json(data):
    # validate incoming object, and return a JSON object read to send to the API
    if not isinstance(data, str):
        return False, {"error": "Input must be a string"}
    try:
        json_data = json.loads(data)
        # print(f"JSON data: {json_data}")
        if not isinstance(json_data, dict):
            return True, {"stock": json_data, "call_type": "live"}
        return True, json_data
    except (json.JSONDecodeError, TypeError):
        if data.strip():
            return True, {"stock": data.strip(), "call_type": "live"}
        return False, {"error": "Empty input"}

# FETCH DATA VIA ALPHA_VANTAGE API
def fetch_data(stock, call_type):
    # load API key from .env file
    load_dotenv()
    key = os.getenv('ALPHA_VANTAGE_KEY2')

    # dictionary to replace input with actual API call parameters
    functions = {
        'daily': 'TIME_SERIES_DAILY',
        'weekly': 'TIME_SERIES_WEEKLY',
        'monthly': 'TIME_SERIES_MONTHLY',
        'live': 'GLOBAL_QUOTE'
    }

    # Make API call
    if call_type == "all":
        all_data = {}
        for func_name, function in functions.items():
            url = f'https://www.alphavantage.co/query?function={function}&symbol={stock}&apikey={key}]'
            print(f"API call function: {function}, symbol: {stock}")
            response = requests.get(url)
            all_data[func_name] = response.json()
        return all_data
    else:
        if call_type.lower() not in functions:
            return {"error": f"Invalid call type. Must be one of: {', '.join(functions.keys())}"}
        function = functions[call_type]
        url = f'https://www.alphavantage.co/query?function={function}&symbol={stock}&apikey={key}]'
        print(f"API call function: {function}, symbol: {stock}")
        response = requests.get(url)
        return response.json()


def main(address="tcp://*:8001"):
    # SETUP SOCKET
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(address)
    print(f"Server started on {address}")

    while True:
        data = socket.recv()
        received = data.decode('utf-8')
        print(f"Raw data: {received}")

        is_valid, result = validate_json(received)

        if not is_valid:
            print(f"Error: {result['error']}")
            socket.send_json(result)

        # CHECK IF DATA IS JSON-esque string, or just a string
        else:
            print(f"Validated data: {result}")
            reply_data = fetch_data(result['stock'], result['call_type'])
            # validated_reply = validate_reply(reply_data)
            socket.send_json(reply_data)


if __name__ == "__main__":
    main()