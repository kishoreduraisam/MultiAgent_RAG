import sys
import types
import unittest
from unittest.mock import patch

from tools.web_search import DuckDuckGoSearchTool


class _FakeDDGSSuccess:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def text(self, query, max_results=10):
        return [
            {
                "title": "Port Report",
                "href": "https://example.com/ports",
                "body": f"Results for {query}",
            }
        ]


class _FakeDDGSNoResults:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def text(self, query, max_results=10):
        return []


class TestDuckDuckGoSearchTool(unittest.TestCase):
    def _module_with_ddgs(self, ddgs_class):
        module = types.ModuleType("duckduckgo_search")
        module.DDGS = ddgs_class
        return module

    def test_formats_search_results(self):
        fake_module = self._module_with_ddgs(_FakeDDGSSuccess)
        with patch.dict(sys.modules, {"duckduckgo_search": fake_module}):
            tool = DuckDuckGoSearchTool(max_results=1)
            result = tool.forward("busiest ports")
            self.assertIn("## Search Results", result)
            self.assertIn("[Port Report](https://example.com/ports)", result)
            self.assertIn("Results for busiest ports", result)

    def test_raises_when_no_results(self):
        fake_module = self._module_with_ddgs(_FakeDDGSNoResults)
        with patch.dict(sys.modules, {"duckduckgo_search": fake_module}):
            tool = DuckDuckGoSearchTool(max_results=1)
            with self.assertRaises(Exception) as context:
                tool.forward("query with no results")
            self.assertIn("No results found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
