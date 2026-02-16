import time

import requests

# code source: https://realpython.com/python-concurrency/


def main():
    sites = [
        "https://www.jython.org",
        "http://olympus.realpython.org/dice",
    ] * 80
    start_time = time.perf_counter()
    download_all_sites(sites)
    duration = time.perf_counter() - start_time
    print(f"Downloaded {len(sites)} sites in {duration} seconds")


def download_all_sites(sites):
    with requests.Session() as session:
        for url in sites:
            download_site(url, session)


def download_site(url, session):
    with session.get(url) as response:
        print(f"Read {len(response.content)} bytes from {url}")


if __name__ == "__main__":
    main()


# Downloaded 160 sites in 15.839770364000287 seconds
