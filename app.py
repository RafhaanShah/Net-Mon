"""Run nmap periodically to monitor for and notify when new devices are detected."""
import json
import os
import sys
import time

import apprise
import nmap3
import schedule

NOTIFICATION = os.getenv("NETMON_NOTIFICATION", "")
SUBNET = os.getenv("NETMON_SUBNET", "192.168.1.0/24")
MINUTES = os.getenv("NETMON_MINUTES", "15")
RESULTS = "results.json"


def main():
    """Run application."""
    print("Starting Net-Mon")

    apprise_client = get_apprise_client(NOTIFICATION)
    scan_and_process(apprise_client) # first run

    # then every x minutes
    schedule.every(int(MINUTES)).minutes.do(scan_and_process, apprise_client=apprise_client)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)

        except KeyboardInterrupt:
            sys.exit("\tStopping application, bye bye")


def scan_and_process(apprise_client):
    """Scans for new hosts and checks against existing hosts."""
    new_scan = scan()

    if is_first_run(RESULTS):
        print("First run, found " + str(len(new_scan)) + " hosts")
        write_json(new_scan)
        return

    old_scan = read_json()
    process_results(apprise_client, old_scan, new_scan)
    merged = merge_lists(old_scan, new_scan)
    write_json(merged)


def scan():
    """Do nmap scan and parse mac addresses."""
    nmap = nmap3.NmapScanTechniques()
    scan_result = nmap.nmap_ping_scan(SUBNET)
    scan_result.pop('stats', None)
    scan_result.pop('runtime', None)

    result = {}

    for ip_address in scan_result:
        host = scan_result[ip_address]
        if 'macaddress' in host:
            mcadr = host['macaddress']
            if mcadr and 'addr' in mcadr:
                mac = mcadr['addr']
                result[mac] = ip_address

    return result


def process_results(apprise_client, old_list, new_list):
    """Check for new hosts and notify."""
    for mac in new_list:
        if mac not in old_list:
            ip_address = new_list[mac]
            notify(apprise_client, mac, ip_address)


def read_json():
    """Read json to memory."""
    with open(RESULTS) as file:
        result = json.load(file)
        return result


def write_json(result):
    """Write result to json."""
    with open(RESULTS, 'w') as file:
        json.dump(result, file)


def merge_lists(old_list, new_list):
    """Merge two dictionaries."""
    for mac in new_list:
        old_list[mac] = new_list[mac]

    return old_list


def is_first_run(file):
    """Check if results file exists."""
    return not os.path.exists(file) or os.stat(file).st_size == 0


def notify(apprise_client, mac, ip_address):
    """Send apprise notification."""
    message = "New device " + mac + " on IP: " + ip_address
    print(message)
    apprise_client.notify(
        title="Net-Mon",
        body=message,
    )


def get_apprise_client(url):
    """Return Apprise instance."""
    apprise_client = apprise.Apprise()
    apprise_client.add(url)

    return apprise_client


if __name__ == "__main__":
    main()
