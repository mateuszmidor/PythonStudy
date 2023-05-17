import requests

def GetUsdToPlnRate(date):
    # Construct the API URL
    url = f'https://api.frankfurter.app/{date}?from=USD&to=PLN'

    # Send a GET request to the API and parse the JSON response
    response = requests.get(url)
    data = response.json()

    # Extract the exchange rate from the response and return it
    rate = data['rates']['PLN']
    return rate

rate = GetUsdToPlnRate('2023-03-20')
print(rate) # Output: 4.3185
