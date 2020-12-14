import unittest
import sort_keys


class TestSortKeyMethods(unittest.TestCase):

	def test_key_next(self):
		result = sort_keys.key_next("A")
		self.assertEqual(result, "B")

	def test_key_between_basic(self):
		result = sort_keys.key_between("A", "C")
		self.assertEqual(result, "B", result)

	def test_key_between_advanced(self):
		result = sort_keys.key_between("A", "B")
		self.assertEqual(result, "AN", result)


if __name__ == "__main__":
	unittest.main()