import python_http_client

usd_quotes_url='http://api.nbp.pl' 
global_headers = {"Accept": "application/json"} # also available: xml

client = python_http_client.Client(host=usd_quotes_url, request_headers=global_headers)
response = client.api.exchangerates.rates.A.USD.last._(1).get() # /api/exchangerates/rates/A/USD/last/1

# print(response.status_code)
# print(response.headers)
print(response.body)