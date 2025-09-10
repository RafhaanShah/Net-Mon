# Net-Mon

Get notified for new devices on your network. This app runs [nmap](https://nmap.org/) periodically and saves found hosts, and send you a notification whenever a new device (mac-address) is found.

![](/assets/screenshot.jpg)

## Prerequisites
- A notification service supported by [Apprise](https://github.com/caronc/apprise#popular-notification-services) and the required API keys or other configuration for your chosen services
- Have `nmap` already installed on your system

## Building
Install Requirements:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Upgrade Dependencies:
```
pip install pipreqs
pip install --upgrade -r requirements.txt
pipreqs --force --ignore .venv
```

## Installation
- If you have Python installed, you can clone the repository and directly run the Python file
- You can download the latest release artifact from [GitHub Releases](https://github.com/RafhaanShah/Net-Mon/releases)
- If you have Docker installed, you can run the Docker image

## Configuration
You can configure Net-Mon using **environment variables** or **command-line arguments**.

### Environment Variables:
1. Apprise configuration url, for your chosen providers:
   - `NETMON_NOTIFICATION=tgram://bottoken/ChatID`
2. Subnet for scanning in CIDR form or range form:
   - `NETMON_SUBNET=192.168.1.0/24` or `NETMON_SUBNET=192.168.1.1-100`
3. Interval for scanning, in minutes:
   - `NETMON_MINUTES=15`
4. Results file path (optional, default is `results.json`):
   - `NETMON_RESULTS=results.json`

### Command-Line Arguments:
You can also pass these options directly when running the app:
- `--notification` Notification URL (e.g. `--notification tgram://bottoken/ChatID`)
- `--subnet` Subnet to scan (e.g. `--subnet 192.168.1.0/24`)
- `--minutes` Scan interval in minutes (e.g. `--minutes 15`)
- `--results` Results file path (default: `results.json`)

## Usage
- Python:
    `sudo python app.py --notification tgram://bottoken/ChatID`
- Executable:
    `sudo ./netmon --notification tgram://bottoken/ChatID`
- Docker:
    ```bash
    docker run -e \
        NETMON_NOTIFICATION=tgram://bottoken/ChatID \
        NETMON_SUBNET=192.168.1.0/24 \
        NETMON_MINUTES=15 \
        --net=host \
        ghcr.io/rafhaanshah/net-mon:latest
    ```
- Docker-Compose:
    ```yaml
    services:
        net-mon:
            container_name: net-mon
            image: ghcr.io/rafhaanshah/net-mon:latest
            restart: unless-stopped
            network_mode: host # needed for nmap to get mac addresses
            volumes:
            - ./results.json:/app/results.json # optional, if you want to keep found hosts persistent
                                               # create an empty results.json first
            environment:
            - NETMON_NOTIFICATION=tgram://bottoken/ChatID
            - NETMON_SUBNET=192.168.1.0/24
            - NETMON_MINUTES=60
    ```

## License
[MIT](https://choosealicense.com/licenses/mit/)
