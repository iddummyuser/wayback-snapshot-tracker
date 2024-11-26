import os
import requests
import hashlib
import urllib.parse
import mimetypes
from tqdm import tqdm

def fetch_all_wayback_snapshots(url):
    """
    Fetch all available Wayback Machine snapshots for a given URL.
    """
    api_url_https = f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(url)}&output=json&fl=timestamp,original&filter=statuscode:200"
    api_url_http = f"http://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(url)}&output=json&fl=timestamp,original&filter=statuscode:200"

    try:
        response = requests.get(api_url_https, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        print(f"HTTPS connection failed: {e}. Retrying with HTTP...")
        try:
            response = requests.get(api_url_http, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch snapshots using both HTTPS and HTTP: {e}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching snapshots: {e}")
        return []

    if response.status_code == 200:
        data = response.json()
        return [(snapshot[0], f"https://web.archive.org/web/{snapshot[0]}/{snapshot[1]}") for snapshot in data[1:]]
    return []

def calculate_hash(content):
    """
    Calculate the SHA256 hash of the given content.
    """
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()

def extract_extension(snapshot_url, content_type):
    """
    Extract the file extension from the URL or infer from the content type.
    """
    parsed_url = urllib.parse.urlparse(snapshot_url)
    extension = os.path.splitext(parsed_url.path)[1]

    # If no extension in the URL, infer from the Content-Type header
    if not extension and content_type:
        extension = mimetypes.guess_extension(content_type.split(';')[0]) or ".html"

    return extension

def load_downloaded_urls(log_file):
    """
    Load previously downloaded URLs from the log file.
    """
    if not os.path.exists(log_file):
        return set()
    with open(log_file, 'r') as file:
        return set(line.strip() for line in file)

def save_downloaded_url(log_file, url):
    """
    Append a downloaded URL to the log file.
    """
    with open(log_file, 'a') as file:
        file.write(url + '\n')

def download_snapshot(snapshot_url, output_dir, timestamp, seen_hashes, log_file):
    """
    Download the content of a snapshot and return its hash and extension.
    """
    try:
        response = requests.get(snapshot_url, stream=True, timeout=10)
        response.raise_for_status()

        content = response.content
        file_hash = calculate_hash(content)

        if file_hash in seen_hashes:
            print(f"File already downloaded (by hash), skipping: {snapshot_url}")
            return None  # Skip duplicate downloads

        file_extension = extract_extension(snapshot_url, response.headers.get("Content-Type"))
        filename = f"{timestamp}_{file_hash[:8]}{file_extension}"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, 'wb') as file:
            file.write(content)

        save_downloaded_url(log_file, snapshot_url)
        print(f"Downloaded: {file_path}")
        return file_hash
    except requests.RequestException as e:
        print(f"Error downloading {snapshot_url}: {e}")
        return None

def main(input_file, output_dir, log_file):
    """
    Main function to download all unique snapshots for URLs and track hash changes.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    downloaded_urls = load_downloaded_urls(log_file)

    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    print(f"Total URLs to process: {len(urls)}\n")

    for index, url in enumerate(urls, 1):
        print(f"\nProcessing URL ({index}/{len(urls)}): {url}")
        snapshots = fetch_all_wayback_snapshots(url)
        if not snapshots:
            print(f"No snapshots found for URL: {url}")
            continue

        print(f"Found {len(snapshots)} snapshots for URL: {url}")

        # Track hashes to detect changes
        seen_hashes = set()
        completed = 0

        for timestamp, snapshot_url in tqdm(snapshots, desc=f"Processing snapshots for {url}"):
            if snapshot_url in downloaded_urls:
                print(f"Snapshot already downloaded, skipping: {snapshot_url}")
                continue
            file_hash = download_snapshot(snapshot_url, output_dir, timestamp, seen_hashes, log_file)
            if file_hash:
                seen_hashes.add(file_hash)
            completed += 1

        print(f"Completed snapshots for {url}: {completed}/{len(snapshots)}")

if __name__ == "__main__":
    input_file = "url.txt"  # File containing list of URLs
    output_dir = "downloads"  # Directory to save downloaded files
    log_file = "downloaded_urls.log"  # Log file to track downloaded URLs
    main(input_file, output_dir, log_file)
