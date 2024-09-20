import unittest
import os
from dotenv import load_dotenv
from openai_utils import test_openai_api

class TestOpenAIUtils(unittest.TestCase):

    def test_test_openai_api(self):
        # Load the .env file
        load_dotenv()

        # Test when API key is not set
        original_api_key = os.getenv('OPENAI_API_KEY')
        os.environ['OPENAI_API_KEY'] = ''
        self.assertIsNone(test_openai_api())
        os.environ['OPENAI_API_KEY'] = original_api_key

        # Test when API key is set and API call is successful
        os.environ['OPENAI_API_KEY'] = original_api_key
        result = test_openai_api()
        print(f"Test response: {result}")
        self.assertIsNotNone(result)
        self.assertIn('OpenAI', result)

if __name__ == '__main__':
    unittest.main()