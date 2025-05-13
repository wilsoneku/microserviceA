# microserviceA
CS361 - Microservice project


### Required external python modules 
pyzmq
finnhub-python


SETUP INSTRUCTIONS --- WORK IN PROGRESS ---

1. install required python modules

2. GET ALPHA VANTAGE API KEY
3. Create .env file and add the following text (note: replace the appropriate text with your actual API key)
> ALPHA_VANTAGE_KEY=replace-with-key


### sample_request instructions
1. Run server.py

2. In a separate thread, run either string_example.py or json_example.py

**_sample_string.py_** will prompt you to enter a stock ticker symbol, and return 
data as if you passed a STRING to the microservice

**_sample_request.py_** will prompt you to enter a stock ticker symbol AND the type of data
you are looking for. It simulates sending a JSON object to the microservice