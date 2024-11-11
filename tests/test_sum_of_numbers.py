import unittest
from src.sum_of_numbers import sum_of_numbers
import time

# sample unittests for updated function
class TestSumOfNumbers(unittest.TestCase):
    
    def test_sum_of_numbers(self):
        # Test with various positive integers
        test_cases = [
            (5, 15),     # 1 + 2 + 3 + 4 + 5 = 15
            (10, 55),    # 1 + 2 + ... + 10 = 55
            (1, 1),      # Sum of first 1 number should be 1
            (100, 5050)  # Sum of first 100 numbers should be 5050
        ]
        
        for n, expected in test_cases:
            with self.subTest(n=n):
                self.assertEqual(sum_of_numbers(n), expected)

    def test_sum_of_numbers_zero(self):
        self.assertEqual(sum_of_numbers(0), 0)  # Sum of first 0 numbers should be 0

    def test_performance(self):
        # Performance test with a very large number
        start_time = time.time()
        result = sum_of_numbers(10**7)  # 10 million
        end_time = time.time()
        expected_sum = 10**7 * (10**7 + 1) // 2
        self.assertEqual(result, expected_sum)
        
        # Check performance time (e.g., should not exceed 2 seconds)
        self.assertLess(end_time - start_time, 2.0, "Performance test took too long")

if __name__ == '__main__':
    unittest.main()
