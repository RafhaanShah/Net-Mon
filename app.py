"""Run nmap periodically to monitor for and notify when new devices are detected."""

import argparse
import json
import os
import sys
import time

import apprise
import nmap3
import schedule


def parse_args():
    """Parse command-line arguments and fallback to environment variables."""
    parser = argparse.ArgumentParser(
        description="Run nmap periodically to monitor for new devices."
    )
    parser.add_argument(
        "--notification",
        default=os.getenv("NETMON_NOTIFICATION", ""),
        help="Notification URL",
    )
    parser.add_argument(
        "--subnet",
        default=os.getenv("NETMON_SUBNET", "192.168.1.0/241"),
        help="Subnet to scan",
    )
    parser.add_argument(
        "--minutes",
        default=os.getenv("NETMON_MINUTES", "15"),
        type=int,
        help="Scan interval in minutes",
    )
    parser.add_argument(
        "--results",
        default=os.getenv("NETMON_RESULTS", "resultsz.json"),
        help="Results file path",
    )
    return parser.parse_args()


def main():
    """Run application."""
    args = parse_args()
    print("Starting Net-Mon")
    service = args.notification.split("://")[0] if "://" in args.notification else ""
    print(f"Notification service: {service}")
    print(f"Subnet: {args.subnet}")
    print(f"Scan interval (minutes): {args.minutes}")

    apprise_client = get_apprise_client(args.notification)
    scan_and_process(apprise_client, args.results, args.subnet)  # first run

    # then every x minutes
    schedule.every(int(args.minutes)).minutes.do(
        scan_and_process,
        apprise_client=apprise_client,
        results=args.results,
        subnet=args.subnet,
    )

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)

        except KeyboardInterrupt:
            sys.exit("\tStopping application, bye bye")


def scan_and_process(apprise_client, results, subnet):
    """Scans for new hosts and checks against existing hosts."""
    new_scan = scan(subnet)

    if is_first_run(results):
        print("First run, found " + str(len(new_scan)) + " hosts")
        write_json(new_scan, results)
        return

    old_scan = read_json(results)
    process_results(apprise_client, old_scan, new_scan)
    merged = merge_lists(old_scan, new_scan)
    write_json(merged, results)


def scan(subnet):
    """Do nmap scan and parse mac addresses."""
    nmap = nmap3.NmapScanTechniques()
    scan_result = nmap.nmap_ping_scan(subnet)
    scan_result.pop("stats", None)
    scan_result.pop("runtime", None)

    result = {}

    for ip_address, host in scan_result.items():
        if "macaddress" in host:
            mcadr = host["macaddress"]
            if mcadr and "addr" in mcadr:
                mac = mcadr["addr"]
                result[mac] = ip_address

    return result


def process_results(apprise_client, old_list, new_list):
    """Check for new hosts and notify."""
    for mac in new_list:
        if mac not in old_list:
            ip_address = new_list[mac]
            notify(apprise_client, mac, ip_address)


def read_json(results):
    """Read json to memory."""
    with open(results, encoding="utf-8") as file:
        result = json.load(file)
        return result


def write_json(result, results):
    """Write result to json."""
    with open(results, "w", encoding="utf-8") as file:
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
