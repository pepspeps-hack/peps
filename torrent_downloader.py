# Main application file for the Torrent Downloader
import argparse
import time
import os
from downloader_modules.torrent_client import TorrentClient

def display_status(client):
    """Displays the status of all torrents."""
    all_statuses = client.get_all_torrents_status()
    if not all_statuses:
        print("No active torrents.")
        return

    os.system('clear' if os.name == 'posix' else 'cls')
    print("--- Torrent Status ---")
    for info_hash, status_data in all_statuses.items():
        if isinstance(status_data, str): # Error message like "Torrent not found"
            print(f"Info Hash: {info_hash[:10]}... - Status: {status_data}")
            continue

        print(f"\nTorrent: {status_data['name']} (Hash: {info_hash[:10]}...)")
        print(f"  State: {status_data['state']}, Progress: {status_data['progress']:.2f}%")
        print(f"  Down: {status_data['download_rate']:.2f} kB/s, Up: {status_data['upload_rate']:.2f} kB/s, Peers: {status_data['num_peers']}")
        if status_data['state'] == 'downloading':
            eta_seconds = status_data.get('eta', 0)
            if eta_seconds == float('inf'):
                eta_str = "Unknown"
            elif eta_seconds > 0:
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
            else:
                eta_str = "N/A"
            print(f"  ETA: {eta_str}")
    print("-" * 20)

def main():
    parser = argparse.ArgumentParser(description="Command-line Torrent Downloader")
    parser.add_argument("--download_dir", type=str, default="downloads/", help="Directory to save downloaded files.")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add torrent command
    add_parser = subparsers.add_parser("add", help="Add a new torrent.")
    add_group = add_parser.add_mutually_exclusive_group(required=True)
    add_group.add_argument("-f", "--file", type=str, help="Path to the .torrent file.")
    add_group.add_argument("-m", "--magnet", type=str, help="Magnet link.")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show status of torrents.")
    status_parser.add_argument("--id", type=str, help="Info hash of a specific torrent to view.")
    status_parser.add_argument("-i", "--interactive", action="store_true", help="Continuously display status.")


    # Pause command
    pause_parser = subparsers.add_parser("pause", help="Pause a torrent.")
    pause_parser.add_argument("id", type=str, help="Info hash of the torrent to pause.")

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a torrent.")
    resume_parser.add_argument("id", type=str, help="Info hash of the torrent to resume.")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a torrent.")
    cancel_parser.add_argument("id", type=str, help="Info hash of the torrent to cancel.")
    cancel_parser.add_argument("--delete_files", action="store_true", help="Delete downloaded files along with the torrent.")

    args = parser.parse_args()

    client = TorrentClient(download_path=args.download_dir)

    if args.command == "add":
        torrent_id = None
        try:
            if args.file:
                torrent_id = client.add_torrent_file(args.file)
                print(f"Attempting to add torrent from file. Info Hash (on success): {torrent_id}")
            elif args.magnet:
                torrent_id = client.add_magnet_link(args.magnet)
                print(f"Attempting to add torrent from magnet link. Info Hash (on success): {torrent_id}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except RuntimeError as e: # Catching generic runtime errors from TorrentClient
            print(f"Error: {e}")
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")

        if torrent_id:
            # Automatically start monitoring if a torrent is added
            print("Monitoring download (Ctrl+C to stop)...")
            try:
                while True:
                    if torrent_id not in client.handles: # Torrent was removed or completed very fast
                        print(f"Torrent {torrent_id[:10]}... no longer active or completed.")
                        break
                    display_status(client)
                    s = client.get_torrent_status(torrent_id)
                    if isinstance(s, dict) and (s['state'] == 'finished' or s['state'] == 'seeding'):
                        print(f"\nTorrent {s['name']} finished downloading.")
                        break
                    if not client.handles: # No torrents left
                        break
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\nStopped monitoring.")


    elif args.command == "status":
        if args.interactive:
            print("Continuously displaying status (Ctrl+C to stop)...")
            try:
                while True:
                    display_status(client)
                    if not client.handles:
                        print("No torrents to monitor. Exiting interactive status.")
                        break
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\nStopped interactive status display.")
        elif args.id:
            status = client.get_torrent_status(args.id)
            if isinstance(status, str):
                print(status)
            else:
                print(f"--- Status for {status['name']} (Hash: {args.id[:10]}...) ---")
                print(f"  State: {status['state']}, Progress: {status['progress']:.2f}%")
                print(f"  Down: {status['download_rate']:.2f} kB/s, Up: {status['upload_rate']:.2f} kB/s, Peers: {status['num_peers']}")
                if status['state'] == 'downloading':
                    eta_seconds = status.get('eta', 0)
                    if eta_seconds == float('inf') :
                         eta_str = "Unknown"
                    elif eta_seconds > 0:
                        eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
                    else:
                        eta_str = "N/A"
                    print(f"  ETA: {eta_str}")
        else:
            display_status(client)

    elif args.command == "pause":
        if client.pause_torrent(args.id):
            print(f"Torrent {args.id[:10]}... paused.")
        else:
            print(f"Could not pause torrent {args.id[:10]}.... It might not exist.")
        display_status(client)


    elif args.command == "resume":
        if client.resume_torrent(args.id):
            print(f"Torrent {args.id[:10]}... resumed.")
        else:
            print(f"Could not resume torrent {args.id[:10]}.... It might not exist or is not paused.")
        display_status(client)

    elif args.command == "cancel":
        if client.cancel_torrent(args.id, remove_files=args.delete_files):
            print(f"Torrent {args.id[:10]}... cancelled.")
            if args.delete_files:
                print("Associated files will be deleted.")
        else:
            print(f"Could not cancel torrent {args.id[:10]}.... It might not exist.")
        display_status(client)

    else:
        # This part is theoretically unreachable if a command is always given,
        # but good for a default message or if subparsers are not required.
        # If no command is given and subparsers are required, argparse handles it.
        if not client.handles:
            parser.print_help()
        else:
            # Default to interactive status if there are existing torrents from a previous session (not implemented yet)
            # For now, just show status once.
            print("No command specified. Showing current status (if any):")
            display_status(client)


if __name__ == "__main__":
    main()
