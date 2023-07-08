import requests
import time

providers_testnet = [
    {
        "name": "Infura",
        "url": "https://goerli.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc"
    },
    {
        "name": "test",
        "url": "https://goerli.blockpi.network/v1/rpc/public"
    },
    {
        "name": "test2",
        "url": "https://eth-goerli.public.blastapi.io"
    },
    {
        "name": "test3",
        "url": "https://goerli.gateway.tenderly.co"
    }
    ]

providers = [
    {
        "name": "rsync-builder",
        "url": "https://rsync-builder.xyz/"
    },
    {
        "name": "Infura",
        "url": "https://mainnet.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc"
    },
    {
        "name": "QuickNode",
        "url": "https://frequent-flashy-theorem.discover.quiknode.pro/7e58b0a32c49c77019714bded2cb0d88420fb393/"
    },
    {
        "name": "Alchemy",
        "url": "https://eth-mainnet.g.alchemy.com/v2/ANUgbxXb5fRwPxLlAZ9fGcKGYdcoaik5"
    },
    {
        "name": "pokt",
        "url": "https://eth-mainnet.gateway.pokt.network/v1/lb/d518f45b2a8952940ec35399"
    },
    {
        "name": "pokt",
        "url": "https://eth-mainnet.gateway.pokt.network/v1/lb/d518f45b2a8952940ec35399"
    }
    ]

def find_key(dictionary_list, value):
    for dictionary in dictionary_list:
        for key, val in dictionary.items():
            if val == value:
                return dictionary['url']
    return None

def check_provider_speed(provider):
    try:
        start_time = time.time()
        response = requests.get(provider["url"])
        end_time = time.time()
        response_time = end_time - start_time
        print(f"{provider['name']}: {response_time} seconds")
        return response_time
    except requests.exceptions.RequestException as e:
        print(f"{provider['name']}: Error - {e}")
        return None
    
def sort_provide(prov):
    response_times = {}
    for provider in prov:
        response_time = check_provider_speed(provider)
        if response_time is not None:
            response_times[provider["name"]] = response_time
    fastest_provider = min(response_times, key=response_times.get)
    
    print(f"Самый быстрый провайдер: {fastest_provider}")
    return fastest_provider

if __name__ == "__main__":
    res = sort_provide(providers_testnet)
    key = find_key(providers_testnet, res)
    print(key)
