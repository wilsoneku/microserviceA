import zmq
import json
import yfinance as yf
import pandas as pd

# validate incoming object, and return a JSON object read to send to the API
def validate_json(data):
   # check if incoming object is a string
    if not isinstance(data, str):
        return False, {"error": "Input must be a string"}
    try:
    # check if data can load into a JSON object
        json_data = json.loads(data)
        # handles submissions with all integers
        if not isinstance(json_data, dict):
            return True, {"stock": json_data, "call_type": "live"}
        return True, json_data
    except (json.JSONDecodeError, TypeError):
    # handle Strings
        if data.strip():
            return True, {"stock": data.strip(), "call_type": "live"}
        return False, {"error": "Empty input"}

# FETCH DATA VIA yFinance API
def fetch_yfinance(stock, call_type):
    try:
        dat = yf.Ticker(stock)

        # Set up metadata info to return
        info = dat.fast_info
        metadata = {
            "symbol": stock,
            "currency": info.currency,
            "exchange": info.exchange,
            "quote_type": info.quote_type,
            "market_cap": round(info.market_cap, 2)
        }

        if call_type == "live":
            # use the "info" object to get necessary information
            live_data = {
                "Date": pd.Timestamp.now().strftime('%Y-%m-%d'),
                "Last Found Price": round(info.last_price, 2),
                "High": round(info.day_high, 2),
                "Low": round(info.day_low, 2),
                "Open": round(info.open, 2),
                "Previous Close": round(info.previous_close, 2),
                "Volume": int(info.last_volume)
            }
            return {"metadata": metadata, "data": [live_data]}

        elif call_type == "daily":
            res = dat.history(period='1mo', interval='1d', rounding=True)
        elif call_type == "weekly":
            res = dat.history(period='1y', interval='1wk', rounding=True)
        elif call_type == "monthly":
            res = dat.history(period='5y', interval='1mo', rounding=True)
        else:
            return {
                "metadata": metadata,
                "error": f"Invalid call_type: {call_type}",
                "data": []
            }

        if res.empty:
            return {
                "metadata": metadata,
                "error": "No data available for this symbol",
                "data": []
            }

        # Convert returned data from Dataframe to JSON object
        df = pd.DataFrame(res)
        df.reset_index(inplace=True)
        df = df.rename(columns={'index': 'Date'})
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')   # format date
        data = json.loads(df.to_json(orient='records', date_format='iso'))

        return {"metadata": metadata, "data": data}

    except Exception as error:
        # When the stock cannot be found by the yFinance API
        return {
            "metadata": {"symbol": stock},
            "data": [],
            "error": f"Failed to find stock: {str(error)}",
        }

def main(address="tcp://*:8001"):
    # SETUP SOCKET
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(address)
    print(f"Server started on {address}")

    while True:
        # Set up socket
        data = socket.recv()
        received = data.decode('utf-8')
        print(f"Raw data: {received}")

        # Validate incoming JSON object
        is_valid, result = validate_json(received)
        if not is_valid:
            print(f"Error: {result['error']}")
            socket.send_json(result)

        # CHECK IF DATA IS JSON-esque string, or just a string
        else:
            print(f"Validated data: {result}")
            reply_data = fetch_yfinance(result['stock'], result['call_type'])
            # validated_reply = validate_reply(reply_data)
            socket.send_json(reply_data)


if __name__ == "__main__":
    main()