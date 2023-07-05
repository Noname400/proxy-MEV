import requests
import time

websites = [
    ("flashbots", "https://relay.flashbots.net/"),
    ("builder0x69", "http://builder0x69.io/"),
    ("edennetwork", "https://api.edennetwork.io/v1/bundle"),
    ("beaverbuild", "https://rpc.beaverbuild.org/"),
    ("lightspeedbuilder", "https://rpc.lightspeedbuilder.info/"),
    ("eth-builder", "https://eth-builder.com/"),
    ("ultrasound", "https://relay.ultrasound.1money/"),
    ("agnostic-relay", "https://agnostic-relay.net/"),
    ("relayoor-wtf", "https://relayooor.wtf/"),
    ("rsync-builder", "https://rsync-builder.xyz/")
]

response_times = []

for website in websites:
    name, url = website
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        response_time = end_time - start_time
        response_times.append((name, response_time))
        print(f"{name}: {response_time} seconds")
    except requests.exceptions.RequestException as e:
        print(f"{name}: Error - {e}")

response_times.sort(key=lambda x: x[1])  # Сортировка по времени отклика

print(f"Отсортированные результаты: {response_times[0]}")
for result in response_times:
    name, response_time = result
    print(f"{name}: {response_time} seconds")
