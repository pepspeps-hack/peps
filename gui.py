import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from downloader_modules.torrent_client import TorrentClient
import threading
import time
import os

class TorrentApp:
    def __init__(self, root):
        self.client = TorrentClient(download_path="downloads_gui/") # Separate download folder for GUI
        self.root = root
        self.root.title("Torrent Downloader")
        self.root.geometry("800x600")

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam') # Using a theme that looks a bit more modern

        # Frames
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(fill=tk.X)

        self.progress_frame = ttk.Frame(root, padding="10")
        self.progress_frame.pack(fill=tk.BOTH, expand=True)

        # Controls
        ttk.Label(control_frame, text="Torrent File or Magnet Link:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_entry = ttk.Entry(control_frame, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.browse_button = ttk.Button(control_frame, text="Browse .torrent", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        self.add_button = ttk.Button(control_frame, text="Add Torrent", command=self.add_torrent)
        self.add_button.grid(row=0, column=3, padx=5, pady=5)

        control_frame.columnconfigure(1, weight=1) # Make entry field expandable

        # Torrents display area (Treeview)
        columns = ("name", "size", "progress", "status", "down_speed", "up_speed", "eta", "peers")
        self.tree = ttk.Treeview(self.progress_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("name", text="Name")
        self.tree.column("name", width=250)
        self.tree.heading("size", text="Size (MB)")
        self.tree.column("size", width=80, anchor="e")
        self.tree.heading("progress", text="Progress")
        self.tree.column("progress", width=100, anchor="center") # Progress bar will be here
        self.tree.heading("status", text="Status")
        self.tree.column("status", width=100)
        self.tree.heading("down_speed", text="Down (kB/s)")
        self.tree.column("down_speed", width=80, anchor="e")
        self.tree.heading("up_speed", text="Up (kB/s)")
        self.tree.column("up_speed", width=80, anchor="e")
        self.tree.heading("eta", text="ETA")
        self.tree.column("eta", width=70, anchor="center")
        self.tree.heading("peers", text="Peers")
        self.tree.column("peers", width=50, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(self.progress_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons for selected torrent
        action_button_frame = ttk.Frame(root, padding="10")
        action_button_frame.pack(fill=tk.X)

        self.pause_button = ttk.Button(action_button_frame, text="Pause", command=self.pause_selected_torrent)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.resume_button = ttk.Button(action_button_frame, text="Resume", command=self.resume_selected_torrent)
        self.resume_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(action_button_frame, text="Cancel", command=self.cancel_selected_torrent)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        self.cancel_delete_button = ttk.Button(action_button_frame, text="Cancel & Delete Files", command=lambda: self.cancel_selected_torrent(delete_files=True))
        self.cancel_delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Priority buttons
        self.priority_up_button = ttk.Button(action_button_frame, text="Priority Up", command=lambda: self.change_selected_priority(priority_up=True))
        self.priority_up_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.priority_down_button = ttk.Button(action_button_frame, text="Priority Down", command=lambda: self.change_selected_priority(priority_up=False))
        self.priority_down_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.priority_top_button = ttk.Button(action_button_frame, text="Priority Top", command=self.set_selected_top_priority)
        self.priority_top_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.priority_bottom_button = ttk.Button(action_button_frame, text="Priority Bottom", command=self.set_selected_bottom_priority)
        self.priority_bottom_button.pack(side=tk.LEFT, padx=5, pady=5)


        # Global Bandwidth Limits Frame
        bandwidth_frame = ttk.LabelFrame(root, text="Global Bandwidth Limits (kB/s - 0 for unlimited)", padding="10")
        bandwidth_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(bandwidth_frame, text="Download:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.download_limit_entry = ttk.Entry(bandwidth_frame, width=8)
        self.download_limit_entry.grid(row=0, column=1, padx=5, pady=2)
        self.download_limit_entry.insert(0, "0") # Default unlimited

        ttk.Label(bandwidth_frame, text="Upload:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.upload_limit_entry = ttk.Entry(bandwidth_frame, width=8)
        self.upload_limit_entry.grid(row=0, column=3, padx=5, pady=2)
        self.upload_limit_entry.insert(0, "0") # Default unlimited

        self.apply_limits_button = ttk.Button(bandwidth_frame, text="Apply Limits", command=self.apply_global_limits)
        self.apply_limits_button.grid(row=0, column=4, padx=10, pady=2)

        # Status bar for messages or current limits
        self.status_bar = ttk.Label(root, text="Limits: DL - Unlimited, UL - Unlimited", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status_bar_limits()


        # Store torrent info_hash against treeview item id
        self.tree_item_to_info_hash = {}
        self.info_hash_to_tree_item = {}

        # Start update loop
        self.update_running = True
        self.update_thread = threading.Thread(target=self.periodic_update_torrents, daemon=True)
        self.update_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a .torrent file",
            filetypes=(("Torrent files", "*.torrent"), ("All files", "*.*"))
        )
        if filepath:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, filepath)

    def add_torrent(self):
        source = self.url_entry.get()
        if not source:
            messagebox.showerror("Error", "No torrent file or magnet link provided.")
            return

        try:
            info_hash = None
            if source.startswith("magnet:") or source.startswith("magnet:?xt=urn:btih:"):
                info_hash = self.client.add_magnet_link(source)
                print(f"GUI: Adding magnet link {info_hash}")
            elif os.path.exists(source) and source.endswith(".torrent"):
                info_hash = self.client.add_torrent_file(source)
                print(f"GUI: Adding torrent file {info_hash}")
            else:
                messagebox.showerror("Error", "Invalid source. Please provide a valid .torrent file path or a magnet link.")
                return

            if info_hash:
                # Add to treeview (initially, some data might be missing)
                # Name might take a moment to resolve, especially for magnets
                status = self.client.get_torrent_status(info_hash)
                if isinstance(status, dict):
                    name = status.get("name", "Fetching name...")
                    item_id = self.tree.insert("", tk.END, values=(name, "N/A", 0, "starting", 0, 0, "N/A", 0))
                    self.tree_item_to_info_hash[item_id] = info_hash
                    self.info_hash_to_tree_item[info_hash] = item_id
                else: # Error string from get_torrent_status
                     messagebox.showerror("Error Adding Torrent", f"Could not add torrent: {status}")
                self.url_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to add torrent. The client returned no info_hash.")

        except Exception as e:
            messagebox.showerror("Error Adding Torrent", str(e))
            print(f"GUI: Error adding torrent: {e}")

    def get_selected_info_hash(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "No torrent selected.")
            return None
        return self.tree_item_to_info_hash.get(selected_item[0])

    def pause_selected_torrent(self):
        info_hash = self.get_selected_info_hash()
        if info_hash:
            if self.client.pause_torrent(info_hash):
                print(f"GUI: Paused {info_hash}")
            else:
                messagebox.showerror("Error", f"Could not pause torrent {info_hash[:10]}...")


    def resume_selected_torrent(self):
        info_hash = self.get_selected_info_hash()
        if info_hash:
            if self.client.resume_torrent(info_hash):
                print(f"GUI: Resumed {info_hash}")
            else:
                messagebox.showerror("Error", f"Could not resume torrent {info_hash[:10]}...")


    def cancel_selected_torrent(self, delete_files=False):
        info_hash = self.get_selected_info_hash()
        if info_hash:
            confirm_msg = f"Are you sure you want to cancel torrent {info_hash[:10]}...?"
            if delete_files:
                confirm_msg += " This will also delete its downloaded files."

            if messagebox.askyesno("Confirm Cancel", confirm_msg):
                if self.client.cancel_torrent(info_hash, remove_files=delete_files):
                    print(f"GUI: Cancelled {info_hash}, delete_files={delete_files}")
                    # Remove from treeview - this will be handled by periodic_update_torrents
                    # as the torrent will no longer be in client.handles
                else:
                    messagebox.showerror("Error", f"Could not cancel torrent {info_hash[:10]}...")


    def periodic_update_torrents(self):
        while self.update_running:
            try:
                all_statuses = self.client.get_all_torrents_status()

                # Schedule the GUI update to run in the main thread
                self.root.after(0, self.update_gui_with_statuses, all_statuses)

            except Exception as e:
                print(f"Error in periodic_update_torrents: {e}")
            time.sleep(1) # Update interval

    def update_gui_with_statuses(self, all_statuses):
        if not self.update_running: # Check if we are shutting down
            return

        current_tree_hashes = set(self.info_hash_to_tree_item.keys())
        active_torrent_hashes = set(all_statuses.keys())

        # Add new torrents or update existing ones
        for info_hash, status in all_statuses.items():
            if isinstance(status, str): # Error string like "Torrent not found" or "Torrent error..."
                # If it was an error that caused removal, it won't be in active_torrent_hashes
                # If it's "Torrent not found", it means it was removed by client logic.
                # This case should be handled by the removal logic below.
                print(f"GUI Update: Status for {info_hash[:10]} is string: {status}")
                continue

            name = status.get("name", "Fetching...")
            total_size_bytes = status.get("total_download", 0) # This is total_done, should be total_wanted for size
            # For actual total size, we might need to store it when torrent is added or get it from handle.torrent_file().total_size()
            # For now, using total_done as a placeholder if total_wanted isn't easily available in status dict.
            # A better way: store total_wanted when torrent is added if possible, or calculate from torrent_info

            # Try to get total_wanted for size display
            handle = self.client.handles.get(info_hash)
            if handle and handle.is_valid() and handle.has_metadata():
                tf = handle.torrent_file()
                if tf:
                    total_size_bytes = tf.total_size()

            size_mb = f"{total_size_bytes / (1024 * 1024):.2f}" if total_size_bytes else "N/A"

            progress_val = status.get("progress", 0)
            state = status.get("state", "N/A")
            down_speed = f"{status.get('download_rate', 0):.2f}"
            up_speed = f"{status.get('upload_rate', 0):.2f}"

            eta_seconds = status.get('eta', 0)
            if status.get('error'):
                eta_str = "ERR"
                state = f"Error: {status.get('error', '')[:20]}" # Show part of error in state
            elif state in ['finished', 'seeding']:
                eta_str = "Done"
            elif eta_seconds == float('inf') or eta_seconds == 0 and state == 'downloading': # eta can be 0 if calc fails or not started
                eta_str = "---" if state == 'downloading metadata' or status.get('download_rate', 0) == 0 else "Inf"
            elif eta_seconds > 0 :
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
            else:
                eta_str = "N/A"

            peers = status.get("num_peers", 0)

            values = (name, size_mb, progress_val, state, down_speed, up_speed, eta_str, peers)

            if info_hash in self.info_hash_to_tree_item:
                item_id = self.info_hash_to_tree_item[info_hash]
                try:
                    self.tree.item(item_id, values=values)
                    # Update progress bar (custom widget would be better, but simple text for now)
                    self.tree.set(item_id, "progress", f"{progress_val:.2f}%")
                except tk.TclError: # Item might have been deleted if GUI is slow to update
                    print(f"GUI Update: TclError updating item for {info_hash[:10]}. It might have been removed.")
                    # Clean up if item_id is no longer valid
                    if info_hash in self.info_hash_to_tree_item: del self.info_hash_to_tree_item[info_hash]
                    # self.tree_item_to_info_hash might still have old item_id, needs cleanup too
                    # This part needs more robust handling for item deletion synchronization
            else:
                # This case should ideally be handled by add_torrent, but as a fallback:
                item_id = self.tree.insert("", tk.END, values=values)
                self.tree_item_to_info_hash[item_id] = info_hash
                self.info_hash_to_tree_item[info_hash] = item_id
                self.tree.set(item_id, "progress", f"{progress_val:.2f}%")

        # Remove torrents from Treeview that are no longer active
        hashes_to_remove_from_tree = current_tree_hashes - active_torrent_hashes
        for info_hash_to_remove in hashes_to_remove_from_tree:
            if info_hash_to_remove in self.info_hash_to_tree_item:
                item_id = self.info_hash_to_tree_item[info_hash_to_remove]
                try:
                    if self.tree.exists(item_id): # Check if item exists before deleting
                         self.tree.delete(item_id)
                except tk.TclError:
                    print(f"GUI Update: TclError deleting item for {info_hash_to_remove[:10]}. Already gone?")

                del self.info_hash_to_tree_item[info_hash_to_remove]
                # Also remove from the reverse mapping
                # Need to find the key (item_id) for the value (info_hash_to_remove)
                item_id_to_del_from_rev_map = None
                for tid, ih_map_val in list(self.tree_item_to_info_hash.items()): # Use list for safe iteration if modifying
                    if ih_map_val == info_hash_to_remove:
                        item_id_to_del_from_rev_map = tid
                        break
                if item_id_to_del_from_rev_map and item_id_to_del_from_rev_map in self.tree_item_to_info_hash:
                    del self.tree_item_to_info_hash[item_id_to_del_from_rev_map]

    def apply_global_limits(self):
        try:
            dl_limit_str = self.download_limit_entry.get()
            ul_limit_str = self.upload_limit_entry.get()

            dl_limit = int(dl_limit_str) if dl_limit_str else 0
            ul_limit = int(ul_limit_str) if ul_limit_str else 0

            if dl_limit < 0 or ul_limit < 0:
                messagebox.showerror("Error", "Limits must be non-negative.")
                return

            self.client.set_download_limit(dl_limit)
            self.client.set_upload_limit(ul_limit)
            self.update_status_bar_limits()
            messagebox.showinfo("Limits Applied", f"Download limit set to {dl_limit if dl_limit > 0 else 'Unlimited'} kB/s.\nUpload limit set to {ul_limit if ul_limit > 0 else 'Unlimited'} kB/s.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input for limits. Please enter numbers only.")
        except Exception as e:
            messagebox.showerror("Error Applying Limits", str(e))

    def update_status_bar_limits(self):
        limits = self.client.get_global_limits()
        dl_text = f"{limits['download_kbps']:.0f} kB/s" if limits['download_kbps'] > 0 else "Unlimited"
        ul_text = f"{limits['upload_kbps']:.0f} kB/s" if limits['upload_kbps'] > 0 else "Unlimited"
        self.status_bar.config(text=f"Limits: DL - {dl_text}, UL - {ul_text}")

    def change_selected_priority(self, priority_up=True):
        info_hash = self.get_selected_info_hash()
        if info_hash:
            if self.client.set_torrent_priority(info_hash, priority_up=priority_up):
                direction = "up" if priority_up else "down"
                # No direct feedback in GUI for queue position, user relies on client print
                messagebox.showinfo("Priority", f"Moved torrent {info_hash[:10]}... {direction} in queue.")
            else:
                messagebox.showerror("Priority Error", f"Could not change priority for {info_hash[:10]}...")

    def set_selected_top_priority(self):
        info_hash = self.get_selected_info_hash()
        if info_hash:
            if self.client.set_torrent_top_priority(info_hash):
                messagebox.showinfo("Priority", f"Moved torrent {info_hash[:10]}... to top of queue.")
            else:
                messagebox.showerror("Priority Error", f"Could not set top priority for {info_hash[:10]}...")

    def set_selected_bottom_priority(self):
        info_hash = self.get_selected_info_hash()
        if info_hash:
            if self.client.set_torrent_bottom_priority(info_hash):
                messagebox.showinfo("Priority", f"Moved torrent {info_hash[:10]}... to bottom of queue.")
            else:
                messagebox.showerror("Priority Error", f"Could not set bottom priority for {info_hash[:10]}...")


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? This will stop all active torrents."):
            self.update_running = False
            # Give the update thread a moment to see the flag
            # No need to explicitly join if daemon=True, but good practice to signal client
            print("GUI: Shutting down...")

            # Cancel all torrents gracefully (optional, session destruction might handle it)
            # for info_hash in list(self.client.handles.keys()):
            #     self.client.cancel_torrent(info_hash, remove_files=False) # Don't delete files on quit

            # libtorrent session is managed by TorrentClient.
            # It will be cleaned up when TorrentClient instance is garbage collected.
            # Or, add an explicit client.shutdown() method if needed for saving resume data etc.

            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TorrentApp(root)
    root.mainloop()
