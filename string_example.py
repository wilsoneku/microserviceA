import json
import zmq

def send_message(stock):
    server_address = "tcp://localhost:8001"

    # Connect to socket
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(server_address)

    # pass stock ticker (string) to microservice
    socket.send_string(stock)

    print(f"Sending request: {stock}")

    # Handle reply data
    reply = socket.recv()
    reply_data = json.loads(reply.decode('utf-8'))

    # Cleanup resources
    socket.close()
    context.term()

    return reply_data

def main():
    server_address = "tcp://localhost:8001"

    # Get input and set all received text to upper case
    stock = input("Enter stock symbol (e.g., IBM, AAPL): ").upper()

    api_reply = send_message(stock)

    # Save data to a local file (just an example of how to handle the incoming data)
    with open('reply_data.json', 'w') as f:
        json.dump(api_reply, f, indent=4)

if __name__ == "__main__":
    main()
