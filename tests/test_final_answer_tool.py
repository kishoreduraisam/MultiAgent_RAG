import unittest

from tools.final_answer import FinalAnswerTool


class TestFinalAnswerTool(unittest.TestCase):
    def test_returns_primitive_answer(self):
        tool = FinalAnswerTool()
        self.assertEqual(tool.forward("done"), "done")

    def test_returns_same_object_reference(self):
        tool = FinalAnswerTool()
        payload = {"ports": ["Shanghai", "Singapore"]}
        returned = tool.forward(payload)
        self.assertIs(returned, payload)


if __name__ == "__main__":
    unittest.main()
