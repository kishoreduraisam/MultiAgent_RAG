import unittest

from tools.superhero_party_theme_generator import SuperheroPartyThemeTool


class TestSuperheroPartyThemeTool(unittest.TestCase):
    def setUp(self):
        self.tool = SuperheroPartyThemeTool()

    def test_returns_known_theme_case_insensitive(self):
        result = self.tool.forward("ClAsSiC HeRoEs")
        self.assertIn("Justice League Gala", result)

    def test_returns_fallback_for_unknown_category(self):
        result = self.tool.forward("space pirates")
        self.assertIn("Themed party idea not found", result)


if __name__ == "__main__":
    unittest.main()
