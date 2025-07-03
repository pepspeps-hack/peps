# tests/test_voice_parser.py

import unittest
from utils.voice_parser import VoiceParser

class TestVoiceParser(unittest.TestCase):
    def setUp(self):
        self.parser = VoiceParser()

    def test_parse_search_command(self):
        command, arg = self.parser.parse_command("Search for AI advancements")
        self.assertEqual(command, "search")
        self.assertEqual(arg, "AI advancements")

        command, arg = self.parser.parse_command("search for recipes for pasta")
        self.assertEqual(command, "search")
        self.assertEqual(arg, "recipes for pasta")

    def test_parse_sort_files_command(self):
        command, arg = self.parser.parse_command("Sort files in this folder")
        self.assertEqual(command, "sort_files")
        self.assertIsNone(arg) # No argument expected for this version

        command, arg = self.parser.parse_command("sort files")
        self.assertEqual(command, "sort_files")
        self.assertIsNone(arg)

    def test_parse_browse_command(self):
        command, arg = self.parser.parse_command("Use my browser to check news")
        self.assertEqual(command, "browse")
        self.assertEqual(arg, "check news")

        command, arg = self.parser.parse_command("use my browser to visit https://example.com")
        self.assertEqual(command, "browse")
        self.assertEqual(arg, "visit https://example.com")

    def test_parse_unknown_command(self):
        command, arg = self.parser.parse_command("Play some music")
        self.assertIsNone(command)
        self.assertIsNone(arg)

    def test_parse_empty_input(self):
        command, arg = self.parser.parse_command("")
        self.assertIsNone(command)
        self.assertIsNone(arg)

    def test_case_insensitivity(self):
        command, arg = self.parser.parse_command("SEARCH FOR case test")
        self.assertEqual(command, "search")
        self.assertEqual(arg, "case test")

        command, arg = self.parser.parse_command("SoRt FiLeS")
        self.assertEqual(command, "sort_files")
        self.assertIsNone(arg)

if __name__ == '__main__':
    unittest.main()
