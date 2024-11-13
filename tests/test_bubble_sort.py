import unittest
from src.bubble_sort import bubble_sort

class TestBubbleSort(unittest.TestCase):

    def test_bubble_sort(self):
        # Test cases with different types of lists
        test_cases = [
            ([5, 3, 8, 6, 2], [2, 3, 5, 6, 8]),     # Unsorted list
            ([], []),                               # Empty list
            ([1], [1]),                             # Single element
            ([3, 3, 3], [3, 3, 3]),                 
            ([9, 1, 4, 6, 7, 2], [1, 2, 4, 6, 7, 9])  # Random order
        ]

        for arr, expected in test_cases:
            with self.subTest(arr=arr):
                self.assertEqual(bubble_sort(arr), expected)

    def test_already_sorted(self):
        # Test with an already sorted list
        arr = [1, 2, 3, 4, 5]
        self.assertEqual(bubble_sort(arr), [1, 2, 3, 4, 5])

    def test_reverse_sorted(self):
        # Test with a list sorted in reverse order
        arr = [5, 4, 3, 2, 1]
        self.assertEqual(bubble_sort(arr), [1, 2, 3, 4, 5])

if __name__ == '__main__':
    unittest.main()
