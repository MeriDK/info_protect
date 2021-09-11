from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from time import time
from lab3.code import RC5

path = 'lab4//'


# create keys
def create_keys():
    print('Create keys')
    private_key = RSA.generate(4096)
    public_key = private_key.publickey()
    print('Your pair of keys:')
    print(private_key.exportKey(format='PEM'))
    print(public_key.exportKey(format='PEM'))
    return private_key, public_key


# save keys
def save_keys(private_key, public_key, username):
    with open(path + username + '_private' + '.pem', 'wb') as f:
        f.write(private_key.exportKey('PEM'))
    with open(path + username + '_public' + '.pem', 'wb') as f:
        f.write(public_key.exportKey('PEM'))
    print(f'Keys for {username} are saved!\n')


# encrypt message
def encrypt_message(message, receiver, file_name):
    with open(path + receiver + '_public.pem', 'rb') as key_file:
        key = RSA.importKey(key_file.read())

    with open(path + file_name + '_' + receiver + '.txt', 'wb') as message_file:
        cipher = PKCS1_OAEP.new(key)
        encrypted_message = cipher.encrypt(bytes(message, encoding='utf-8'))
        message_file.write(encrypted_message)

    print('Message is encrypted!')


# decrypt message
def decrypt_message(file_name, username):
    with open(path + file_name + '.txt', 'rb') as f:
        data = f.read()

    with open(path + username + '_private.pem', 'rb') as f:
        key = RSA.importKey(f.read())

    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(data)

    print('Message is decrypted!')
    return message.decode()


# create and save keys for users: user1 and user2
private_key, public_key = create_keys()
save_keys(private_key, public_key, 'user1')
private_key, public_key = create_keys()
save_keys(private_key, public_key, 'user2')

# send message from user1 to user2
encrypt_message('This is first message from user1 to user2', 'user2', 'msg1')
encrypt_message('This is second message from user1 to user2', 'user2', 'msg2')

# send message from user2 to user1
encrypt_message('This is first message from user2 to user1', 'user1', 'msg1')

# read messages
print(decrypt_message('msg1_user2', 'user2'))
print(decrypt_message('msg2_user2', 'user2'))
print(decrypt_message('msg1_user1', 'user1'))

# try ro read with wrong user key
try:
    print(decrypt_message('msg1_user2', 'user1'))
except ValueError:
    print('Incorrect decryption.')

# compare time
with open(path + 'test.txt', 'r') as f:
    message = f.read()
    start = time()
    encrypt_message(message, 'user1', 'msg2')
    rsa_enc_time = time() - start
    print('Rsa encryption time:', rsa_enc_time)

key = 'qwerty12'
start = time()
cipher = RC5(16, 16, key.encode())
cipher.encrypt_file(path + 'test.txt', path + 'res.txt')
rc5_enc_time = time() - start
print('Rc5 encryption time:', rc5_enc_time)
