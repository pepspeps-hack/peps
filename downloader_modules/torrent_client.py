import libtorrent as lt
import time
import os

class TorrentClient:
    def __init__(self, download_path='downloads/'):
        self.ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
        # Default settings for bandwidth, can be changed by methods
        self.ses.set_settings({'download_rate_limit': 0, 'upload_rate_limit': 0}) # 0 means unlimited
        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        self.handles = {} # To store torrent handles, mapping info_hash to handle

    def add_torrent_file(self, torrent_file_path):
        try:
            if not os.path.exists(torrent_file_path):
                raise FileNotFoundError(f"Torrent file not found: {torrent_file_path}")
            info = lt.torrent_info(torrent_file_path)
            params = {
                'save_path': self.download_path,
                'ti': info
            }
            handle = self.ses.add_torrent(params)
            if not handle.is_valid():
                # This check might be too early, as it might take time to be valid.
                # However, libtorrent might throw an exception earlier for totally invalid files.
                raise lt.error("Invalid torrent file or parameters.")
            self.handles[str(handle.info_hash())] = handle
            print(f"Added torrent: {handle.name() if handle.name() else str(handle.info_hash())}")
            return str(handle.info_hash())
        except lt.error as e: # Catch libtorrent specific errors
            raise RuntimeError(f"Libtorrent error adding torrent file: {e}")
        except FileNotFoundError as e:
            raise e # Re-raise specific file errors
        except Exception as e: # Catch other potential errors
            raise RuntimeError(f"Failed to add torrent file '{torrent_file_path}': {e}")

    def add_magnet_link(self, magnet_link):
        try:
            params = lt.parse_magnet_uri(magnet_link)
            params.save_path = self.download_path
            handle = self.ses.add_torrent(params)
            if not handle.is_valid():
                 # As with files, validity might take time. Magnet links are more prone to this.
                 # libtorrent usually handles malformed magnet URIs by throwing during parse_magnet_uri or add_torrent
                pass # We'll rely on status checks later if it doesn't become valid
            self.handles[str(handle.info_hash())] = handle
            print(f"Added magnet link. Info hash: {str(handle.info_hash())}")
            return str(handle.info_hash())
        except lt.error as e: # Catch libtorrent specific errors
            raise RuntimeError(f"Libtorrent error adding magnet link: {e}")
        except Exception as e: # Catch other potential errors
            raise RuntimeError(f"Failed to add magnet link '{magnet_link}': {e}")

    def get_torrent_status(self, info_hash_str):
        if info_hash_str not in self.handles:
            return "Torrent not found."

        handle = self.handles[info_hash_str]

        if not handle.is_valid():
            # This torrent might have been invalid from the start or encountered a fatal error.
            # Clean it up from our active handles if it's permanently invalid.
            # Note: Some torrents might be temporarily invalid (e.g. waiting for metadata).
            # A more robust solution would check specific error flags on the handle.
            s_error = handle.status().error
            if s_error:
                 del self.handles[info_hash_str]
                 return f"Torrent error: {s_error.message()}. Removed from tracking."

        s = handle.status()

        state_str = [
            'queued', 'checking', 'downloading metadata', 'downloading',
            'finished', 'seeding', 'allocating', 'checking resume data'
        ]

        current_state = s.state
        # Handle cases where state might be out of expected range, though unlikely with libtorrent
        if current_state >= len(state_str) or current_state < 0:
            state_display = f"unknown state ({current_state})"
        else:
            state_display = state_str[current_state]

        status_info = {
            "name": handle.name() if handle.name() else "Fetching name...",
            "state": state_display,
            "progress": s.progress * 100,
            "download_rate": s.download_rate / 1000,  # kB/s
            "upload_rate": s.upload_rate / 1000,      # kB/s
            "num_peers": s.num_peers,
            "total_download": s.total_done,
            "error": s.error.message() if s.error else None, # Add error message from status
            "eta": 0
        }

        if status_info["error"]:
            # If a torrent has an error, reflect it in its state for clarity
            status_info["state"] = f"error ({state_display})"

        if s.progress < 1 and s.download_rate > 0:
            try:
                status_info["eta"] = (s.total_wanted - s.total_done) / s.download_rate
            except ZeroDivisionError:
                 status_info["eta"] = float('inf')
        elif s.progress == 1:
            status_info["eta"] = 0

        return status_info

    def pause_torrent(self, info_hash_str):
        if info_hash_str in self.handles:
            handle = self.handles[info_hash_str]
            if not handle.is_valid() or handle.status().has_error:
                print(f"Cannot pause torrent {handle.name() or info_hash_str[:10]...}: It has an error or is invalid.")
                return False
            handle.pause()
            print(f"Paused torrent: {handle.name() or info_hash_str[:10]...}")
            return True
        return False

    def resume_torrent(self, info_hash_str):
        if info_hash_str in self.handles:
            handle = self.handles[info_hash_str]
            if not handle.is_valid() or handle.status().has_error:
                print(f"Cannot resume torrent {handle.name() or info_hash_str[:10]...}: It has an error or is invalid.")
                return False
            if handle.status().paused:
                handle.resume()
                print(f"Resumed torrent: {handle.name() or info_hash_str[:10]...}")
                return True
            else:
                print(f"Torrent {handle.name() or info_hash_str[:10]}... is not paused.")
                return False
        return False

    def cancel_torrent(self, info_hash_str, remove_files=False):
        if info_hash_str in self.handles:
            handle = self.handles[info_hash_str]
            handle_name = handle.name() or f"info_hash {info_hash_str[:10]}..." # Get name before removing

            # It's good practice to check if the handle is valid before trying to remove
            if not handle.is_valid():
                print(f"Attempting to cancel an already invalid torrent handle: {handle_name}. Removing from tracking.")
                del self.handles[info_hash_str]
                return True # Considered success as it's removed from our list

            try:
                flags = lt.session_handle.delete_files if remove_files else 0
                self.ses.remove_torrent(handle, flags)
                # Ensure it's removed from our dictionary even if remove_torrent fails silently for some reason
                if info_hash_str in self.handles: # check because alert might have removed it
                    del self.handles[info_hash_str]
                print(f"Cancelled torrent: {handle_name}")
            except lt.error as e:
                # This might happen if the handle is already invalid or session is shutting down
                print(f"Libtorrent error while cancelling torrent {handle_name}: {e}")
                if info_hash_str in self.handles:
                    del self.handles[info_hash_str] # Still remove from our list
                return False # Indicate cancellation wasn't clean
            return True
        return False

    def get_all_torrents_status(self):
        statuses = {}
        for info_hash, handle in list(self.handles.items()): # list() for safe deletion during iteration if needed
            statuses[info_hash] = self.get_torrent_status(info_hash)
        return statuses

    # --- Bandwidth Control ---
    def set_download_limit(self, rate_kbps):
        """Sets the global download rate limit in kilobytes per second. 0 for unlimited."""
        limit_bps = int(rate_kbps * 1000) if rate_kbps > 0 else 0
        self.ses.set_settings({'download_rate_limit': limit_bps})
        print(f"Global download limit set to {rate_kbps} kB/s.")

    def set_upload_limit(self, rate_kbps):
        """Sets the global upload rate limit in kilobytes per second. 0 for unlimited."""
        limit_bps = int(rate_kbps * 1000) if rate_kbps > 0 else 0
        self.ses.set_settings({'upload_rate_limit': limit_bps})
        print(f"Global upload limit set to {rate_kbps} kB/s.")

    def get_global_limits(self):
        """Returns the current global download and upload limits in kB/s."""
        settings = self.ses.settings()
        dl_limit_bps = settings.get('download_rate_limit', 0)
        ul_limit_bps = settings.get('upload_rate_limit', 0)
        return {
            "download_kbps": dl_limit_bps / 1000 if dl_limit_bps > 0 else 0,
            "upload_kbps": ul_limit_bps / 1000 if ul_limit_bps > 0 else 0
        }

    # --- Torrent Priority ---
    # libtorrent uses queue positions for simple prioritization.
    # Lower numbers are higher priority. -1 means don't auto-manage.
    # For more granular file priorities, one would iterate handle.file_priorities()

    def set_torrent_priority(self, info_hash_str, priority_up=True):
        """
        Moves a torrent up or down in the download queue.
        priority_up = True for higher priority (move up), False for lower (move down).
        Libtorrent's queue position 0 is highest.
        """
        if info_hash_str in self.handles:
            handle = self.handles[info_hash_str]
            if not handle.is_valid():
                print(f"Cannot set priority for invalid torrent {info_hash_str[:10]}...")
                return False

            if priority_up:
                handle.queue_position_up()
                print(f"Moved torrent {handle.name() or info_hash_str[:10]}... up in queue.")
            else:
                handle.queue_position_down()
                print(f"Moved torrent {handle.name() or info_hash_str[:10]}... down in queue.")
            return True
        print(f"Torrent {info_hash_str[:10]}... not found for priority change.")
        return False

    def set_torrent_top_priority(self, info_hash_str):
        if info_hash_str in self.handles:
            handle = self.handles[info_hash_str]
            if not handle.is_valid(): return False
            handle.queue_position_top()
            print(f"Set torrent {handle.name() or info_hash_str[:10]}... to top priority.")
            return True
        return False

    def set_torrent_bottom_priority(self, info_hash_str):
        if info_hash_str in self.handles:
            handle = self.handles[info_hash_str]
            if not handle.is_valid(): return False
            handle.queue_position_bottom()
            print(f"Set torrent {handle.name() or info_hash_str[:10]}... to bottom priority.")
            return True
        return False


if __name__ == '__main__':
    # Example Usage (requires a .torrent file or magnet link to test)
    client = TorrentClient()

    # To test with a .torrent file (replace 'test.torrent' with an actual file path)
    # try:
    #     torrent_id_file = client.add_torrent_file('path/to/your/test.torrent')
    #     if torrent_id_file:
    #         print(f"Added torrent file with ID: {torrent_id_file}")
    # except Exception as e:
    #     print(f"Error adding .torrent file: {e}")

    # To test with a magnet link (replace with an actual magnet link)
    # magnet_uri = "magnet:?xt=urn:btih:...."
    # try:
    #     torrent_id_magnet = client.add_magnet_link(magnet_uri)
    #     if torrent_id_magnet:
    #         print(f"Added magnet link with ID: {torrent_id_magnet}")
    # except Exception as e:
    #     print(f"Error adding magnet link: {e}")


    print("\nMonitoring downloads (Ctrl+C to stop)...")
    try:
        while True:
            all_statuses = client.get_all_torrents_status()
            if not all_statuses:
                print("No active torrents.")
            else:
                os.system('clear' if os.name == 'posix' else 'cls') # Clear console
                for info_hash, status in all_statuses.items():
                    if isinstance(status, str): # Torrent not found message
                        print(f"Info Hash: {info_hash} - Status: {status}")
                        continue

                    print(f"--- Torrent: {status['name']} (Hash: {info_hash[:10]}...) ---")
                    print(f"  State: {status['state']}, Progress: {status['progress']:.2f}%")
                    print(f"  Down: {status['download_rate']:.2f} kB/s, Up: {status['upload_rate']:.2f} kB/s, Peers: {status['num_peers']}")
                    if status['state'] == 'downloading':
                        eta_seconds = status.get('eta', 0)
                        if eta_seconds == float('inf'):
                            eta_str = "Unknown"
                        elif eta_seconds > 0 :
                            eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
                        else:
                            eta_str = "N/A"
                        print(f"  ETA: {eta_str}")
                    print("-" * 30)

            if not client.handles: # Exit if no torrents are being managed
                # Check if any torrents ever started, or if they were all invalid
                if not any(s['progress'] > 0 for s in all_statuses.values() if isinstance(s, dict)):
                     print("No torrents were successfully started or all are complete/invalid.")
                break # Exit loop if no torrents or all completed/failed early

            time.sleep(2) # Update status every 2 seconds

            # Example: Auto-pause a torrent after some condition (e.g., 10 seconds for testing)
            # if torrent_id_file and time.time() - client.handles[torrent_id_file].status().added_time > 10:
            #    if client.handles[torrent_id_file].status().state == lt.torrent_status.state_t.downloading:
            #        client.pause_torrent(torrent_id_file)

            # Example: Resume after another 5 seconds
            # if torrent_id_file and client.handles[torrent_id_file].is_paused() and \
            #    time.time() - client.handles[torrent_id_file].status().added_time > 15: # Simplistic timer
            #     client.resume_torrent(torrent_id_file)

            # Example: Cancel a torrent (e.g., after 20 seconds for testing)
            # if torrent_id_file and time.time() - client.handles[torrent_id_file].status().added_time > 20:
            #    client.cancel_torrent(torrent_id_file, remove_files=True)
            #    torrent_id_file = None # So we don't try to operate on it again

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Shutting down session...")
        # You might want to save resume data here before exiting
        # for handle_info_hash, handle in client.handles.items():
        #     if handle.is_valid() and handle.has_metadata():
        #         handle.save_resume_data()
        # client.ses.post_torrent_updates() # Process save_resume_data
        # print("Resume data saved for active torrents.")
        pass # Session will be destroyed when client object is garbage collected or explicitly
    print("Done.")
