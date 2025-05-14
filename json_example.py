import json
import zmq

def send_message(stock, selected_type):
    server_address = "tcp://localhost:8001"

    # Connect to socket
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(server_address)

    # set up JSON object and pass to microservice
    data = {'stock': stock, 'call_type': selected_type}
    socket.send_json(data)

    print(f"Sending request: {data}")

    # Handle reply data
    reply = socket.recv()
    reply_data = json.loads(reply.decode('utf-8'))

    # Clean up resources
    if socket:
        socket.close()
    if context:
        context.term()

    return reply_data

def main():
    stock = input("Enter stock symbol (e.g., IBM, AAPL): ").upper()

    print("\nSelect data type:")
    print("1. Live")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")
    # print("5. All Data")

    choice = input("\nEnter your choice (1-4): ")

    type_map = {
        "1": "live",
        "2": "daily",
        "3": "weekly",
        "4": "monthly",
        # "5": "all"
    }

    selected_type = type_map.get(choice)

    print(f"\nFetching {selected_type} for {stock}...")
    api_reply = send_message(stock, selected_type)

    with open('reply_data.json', 'w') as f:
        json.dump(api_reply, f, indent=4)

if __name__ == "__main__":
    main()

# # # EITHER Send data via string
# # socket.send_string(stock)
# # print(f"Sent: {stock}")
#
# # OR, send data vis JSON object
# data = {'stock': stock, 'type': 'live'}
# socket.send_json(data)
# print(data)