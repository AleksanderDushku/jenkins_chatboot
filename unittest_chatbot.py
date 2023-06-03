import unittest
from unittest.mock import patch, MagicMock
from jenkins_chatbot import generate_chat_response, handle_user_query, decrypt_data, encrypt_data, main

class ChatbotTestCase(unittest.TestCase):

    def setUp(self):
        self.openai_completion_create_patcher = patch('openai.Completion.create')
        self.openai_completion_create = self.openai_completion_create_patcher.start()

    def tearDown(self):
        self.openai_completion_create_patcher.stop()

    def test_generate_chat_response(self):
        response = MagicMock()
        response.choices[0].text.strip.return_value = 'Test response'
        self.openai_completion_create.return_value = response

        response = generate_chat_response('Test query')
        self.assertEqual(response, 'Test response')

    def test_handle_user_query(self):
        response = handle_user_query('build')
        self.assertIn('Build triggered successfully.', response)

    def test_encrypt_data(self):
        encrypted_data = encrypt_data('Test data')
        self.assertIsInstance(encrypted_data, str)

    def test_decrypt_data(self):
        encrypted_data = encrypt_data('Test data')
        decrypted_data = decrypt_data(encrypted_data)
        self.assertEqual(decrypted_data, 'Test data')

    @patch('builtins.input', side_effect=['test', 'exit'])
    def test_main(self, mock_input):
        with patch('builtins.print') as mock_print:
            main()

        mock_print.assert_called_with('Please enter a query.')

if __name__ == '__main__':
    unittest.main()
