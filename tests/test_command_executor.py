# tests/test_command_executor.py

import unittest
from unittest.mock import patch, mock_open
import os
from utils.command_executor import CommandExecutor

class TestCommandExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = CommandExecutor()

    @patch('builtins.print') # Mock print to check output
    def test_execute_search(self, mock_print):
        query = "test query"
        result = self.executor.execute_search(query)
        self.assertEqual(result, f"Search initiated for '{query}'.")
        mock_print.assert_called_with(f"Executing search for: '{query}'")

    @patch('builtins.print')
    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('os.path.abspath')
    @patch('os.path.isfile') # Added mock for os.path.isfile
    def test_execute_sort_files_success(self, mock_isfile, mock_abspath, mock_listdir, mock_isdir, mock_print): # Added mock_isfile
        mock_abspath.return_value = "/fake/dir"
        mock_isdir.return_value = True
        mock_listdir.return_value = ["b.txt", "a.txt", "c.doc"]
        mock_isfile.return_value = True # Assume all items from listdir are files for this test

        result = self.executor.execute_sort_files("/fake/dir")

        self.assertEqual(result, "Files in '/fake/dir' have been conceptually sorted.")
        mock_print.assert_any_call("Attempting to sort files in: '/fake/dir'")
        # Check if the sorted list was printed (order matters here)
        # The actual sorting happens in-place, so listdir's return is sorted
        mock_print.assert_any_call("Files in '/fake/dir' (simulated sort by name): ['a.txt', 'b.txt', 'c.doc']")
        mock_isdir.assert_called_once_with("/fake/dir")
        mock_listdir.assert_called_once_with("/fake/dir")

    @patch('os.path.isdir')
    @patch('os.path.abspath')
    def test_execute_sort_files_folder_not_found(self, mock_abspath, mock_isdir):
        mock_abspath.return_value = "/non/existent/dir"
        mock_isdir.return_value = False
        result = self.executor.execute_sort_files("/non/existent/dir")
        self.assertEqual(result, "Error: Folder '/non/existent/dir' not found.")
        mock_isdir.assert_called_once_with("/non/existent/dir")

    @patch('webbrowser.open')
    @patch('builtins.print')
    def test_execute_browse_url(self, mock_print, mock_webbrowser_open):
        url = "https://example.com"
        result = self.executor.execute_browse(url)
        self.assertEqual(result, f"Opened URL: {url}")
        mock_webbrowser_open.assert_called_once_with(url)
        mock_print.assert_any_call(f"Executing browser task: '{url}'")

    @patch('webbrowser.open')
    @patch('builtins.print')
    def test_execute_browse_task(self, mock_print, mock_webbrowser_open):
        task = "search for cats"
        expected_search_url = "https://www.google.com/search?q=search+for+cats"
        result = self.executor.execute_browse(task)
        self.assertEqual(result, f"Opened browser to search for: {task}")
        mock_webbrowser_open.assert_called_once_with(expected_search_url)
        mock_print.assert_any_call(f"Executing browser task: '{task}'")

    @patch('webbrowser.open', side_effect=Exception("Browser not found"))
    @patch('builtins.print')
    def test_execute_browse_no_browser(self, mock_print, mock_webbrowser_open_error):
        task = "some task"
        result = self.executor.execute_browse(task)
        self.assertEqual(result, f"Could not open browser for task '{task}'. This might be due to environment limitations (e.g., no GUI browser available).")
        mock_print.assert_any_call(f"Error opening browser for task '{task}': Browser not found")


    def test_execute_command_search(self):
        with patch.object(self.executor, 'execute_search', return_value="Search done") as mock_search:
            result = self.executor.execute_command("search", "my query")
            self.assertEqual(result, "Search done")
            mock_search.assert_called_once_with("my query")

    def test_execute_command_search_no_arg(self):
        result = self.executor.execute_command("search")
        self.assertEqual(result, "Error: Search query is missing.")

    def test_execute_command_sort_files(self):
        with patch.object(self.executor, 'execute_sort_files', return_value="Sort done") as mock_sort:
            result = self.executor.execute_command("sort_files") # Argument is optional for this one in current design
            self.assertEqual(result, "Sort done")
            mock_sort.assert_called_once_with(".") # Defaulting to current dir

    def test_execute_command_browse(self):
        with patch.object(self.executor, 'execute_browse', return_value="Browse done") as mock_browse:
            result = self.executor.execute_command("browse", "some website")
            self.assertEqual(result, "Browse done")
            mock_browse.assert_called_once_with("some website")

    def test_execute_command_browse_no_arg(self):
        result = self.executor.execute_command("browse")
        self.assertEqual(result, "Error: Browser task or URL is missing.")

    def test_execute_command_unknown(self):
        result = self.executor.execute_command("unknown_cmd", "some arg")
        self.assertEqual(result, "Error: Unknown command 'unknown_cmd'.")

if __name__ == '__main__':
    unittest.main()
