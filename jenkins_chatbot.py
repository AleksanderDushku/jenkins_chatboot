import openai
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import time

import threading

# Set up initial encryption key
encryption_key = get_random_bytes(32)
key_rotation_interval = 2  # Key rotation interval in seconds

# Lock for key rotation
key_rotation_lock = threading.Lock()

def generate_new_key():
    global encryption_key
    encryption_key = get_random_bytes(32)

def encrypt_data(data):
    cipher = AES.new(encryption_key, AES.MODE_CBC)
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_data(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    cipher = AES.new(encryption_key, AES.MODE_CBC)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode('utf-8')

def handle_user_query(query):
    if query == 'build':
        return encrypt_data('Build triggered successfully.')
    elif query == 'status':
        return encrypt_data('The latest build is successful.')
    elif query == 'notify':
        return encrypt_data('You will now receive Jenkins build notifications.')
    else:
        return encrypt_data('Sorry, I couldn\'t understand your query.')

def generate_chat_response(query):
    try:
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=query,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except openai.error.APIError as e:
        raise RuntimeError(f'Failed to generate chat response: {e}')

def validate_api_key():
    try:
        openai.Completion.create(
            engine='text-davinci-003',
            prompt='Hello'
        )
    except openai.error.AuthenticationError:
        return False
    return True

def key_rotation_thread_func():
    while True:
        time.sleep(key_rotation_interval)
        with key_rotation_lock:
            generate_new_key()

def main():
    if not validate_api_key():
        print('Invalid OpenAI API key. Please check your API key and try again.')
        return

    # Start the key rotation thread
    key_rotation_thread = threading.Thread(target=key_rotation_thread_func)
    key_rotation_thread.daemon = True
    key_rotation_thread.start()

    try:
        while True:
            user_query = input('Enter your query: ')
            if user_query.lower() == 'exit':
                break

            if not user_query:
                print('Please enter a query.')
                continue

            encrypted_user_query = encrypt_data(user_query)

            try:
                encrypted_chat_response = generate_chat_response(encrypted_user_query)
                decrypted_chat_response = decrypt_data(encrypted_chat_response)

                decrypted_jenkins_response = None
                with key_rotation_lock:
                    encrypted_jenkins_response = handle_user_query(decrypted_chat_response)
                    decrypted_jenkins_response = decrypt_data(encrypted_jenkins_response)

                print(decrypted_jenkins_response)

            except Exception as e:
                print(f'An error occurred while processing the query: {str(e)}')

    except KeyboardInterrupt:
        print('\nChatbot session terminated.')

if __name__ == '__main__':
    main()
