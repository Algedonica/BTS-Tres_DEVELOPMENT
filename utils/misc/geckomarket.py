from pycoingecko import CoinGeckoAPI
import json

def getCryptoData(n):
    cg = CoinGeckoAPI()
    x=cg.get_price(ids=n, vs_currencies=['usd', 'rub'],  include_24hr_change='true')

    data=json.dumps(x)
    a=json.loads(data)
    returning = [a[n]['usd'],a[n]['rub'],a[n]['usd_24h_change']]
    return returning

    