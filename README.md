# Wayback Machine Snapshot Downloader

A Python tool to efficiently download and track changes in website snapshots from the Internet Archive's Wayback Machine. This tool helps you archive and monitor historical versions of websites by downloading unique snapshots and avoiding duplicates.

## Features

- Fetches all available snapshots for given URLs from the Wayback Machine
- Downloads only unique snapshots based on content hash
- Supports both HTTP and HTTPS connections
- Automatically detects and assigns appropriate file extensions
- Maintains a log of downloaded URLs to prevent redundant downloads
- Shows progress bars for better visibility during downloads
- Handles connection errors and timeouts gracefully

## Requirements

```
python >= 3.6
requests
tqdm
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/wayback-snapshot-downloader.git
cd wayback-snapshot-downloader
```

2. Install required packages:
```bash
pip install requests tqdm
```

## Usage

1. Create a file named `url.txt` containing the URLs you want to archive (one URL per line):
```
https://example.com
https://example.org
```

2. Run the script:
```bash
python wayback_downloader.py
```

The script will:
- Create a `downloads` directory for storing snapshots
- Create a `downloaded_urls.log` to track processed URLs
- Download unique snapshots for each URL
- Show progress and status information during execution

### File Structure

```
├── wayback_downloader.py
├── url.txt
├── downloaded_urls.log
└── downloads/
    └── [timestamp]_[hash].[extension]
```

### Configuration

You can modify these variables in the script:
- `input_file`: Path to the file containing URLs (default: "url.txt")
- `output_dir`: Directory for downloaded snapshots (default: "downloads")
- `log_file`: Path to the download log file (default: "downloaded_urls.log")

## Functions

### `fetch_all_wayback_snapshots(url)`
Retrieves all available snapshots for a given URL from the Wayback Machine.

### `calculate_hash(content)`
Generates a SHA256 hash of the content to identify unique snapshots.

### `extract_extension(snapshot_url, content_type)`
Determines the appropriate file extension based on URL or content type.

### `download_snapshot(snapshot_url, output_dir, timestamp, seen_hashes, log_file)`
Downloads a snapshot and saves it with a unique filename based on timestamp and content hash.

## Error Handling

The script includes comprehensive error handling for:
- Connection failures (both HTTPS and HTTP)
- Request timeouts
- Invalid responses
- File system operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Internet Archive's Wayback Machine for providing the snapshot API
- Requests library for handling HTTP operations
- TQDM library for progress bar functionality
