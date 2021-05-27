
import json
import requests

# uses api from https://github.com/fawazahmed0/currency-api

def cad_conversion(usprice):

    urlpath="https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/cad.json"

    page = requests.get(urlpath, timeout=5)
    source = page.content

    data = json.loads(source)
    # print(json.dumps(data, indent=2))
    cad_conversion = (data['cad'])
    cdnprice = round(usprice * float(cad_conversion))
    
    return cdnprice


def usd_conversion(cdnprice):

    urlpath="https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/cad/usd.json"

    page = requests.get(urlpath, timeout=5)
    source = page.content

    data = json.loads(source)
    usd_conversion = (data['usd'])
    usdprice = round(cdnprice * float(usd_conversion))
    
    return usdprice
