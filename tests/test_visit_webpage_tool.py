import sys
import types
import unittest
from unittest.mock import Mock, patch

import requests

from tools.visit_webpage import VisitWebpageTool


class TestVisitWebpageTool(unittest.TestCase):
    def setUp(self):
        self.tool = VisitWebpageTool()

    def _markdownify_module(self):
        module = types.ModuleType("markdownify")
        module.markdownify = lambda html: html.replace("<h1>", "").replace("</h1>", "").replace("<p>", "").replace("</p>", "")
        return module

    def test_returns_markdown_from_html(self):
        mock_response = Mock()
        mock_response.text = "<h1>Hello</h1><p>World</p>\n\n\n<p>Again</p>"
        mock_response.raise_for_status.return_value = None

        with patch.dict(sys.modules, {"markdownify": self._markdownify_module()}):
            with patch("requests.get", return_value=mock_response):
                result = self.tool.forward("https://example.com")

        self.assertIn("Hello", result)
        self.assertIn("World", result)
        self.assertNotIn("\n\n\n", result)

    def test_returns_timeout_message(self):
        with patch.dict(sys.modules, {"markdownify": self._markdownify_module()}):
            with patch("requests.get", side_effect=requests.exceptions.Timeout):
                result = self.tool.forward("https://slow.example.com")
        self.assertIn("timed out", result)

    def test_returns_request_error_message(self):
        with patch.dict(sys.modules, {"markdownify": self._markdownify_module()}):
            with patch("requests.get", side_effect=requests.exceptions.RequestException("boom")):
                result = self.tool.forward("https://bad.example.com")
        self.assertIn("Error fetching the webpage", result)
        self.assertIn("boom", result)


if __name__ == "__main__":
    unittest.main()
