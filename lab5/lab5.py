from Crypto.Hash import SHA256
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS


def generate_keys(username, bytes_num=1024):
    key = DSA.generate(bytes_num)

    with open(username + '_private.pem', 'w') as f:
        f.write(key.export_key().decode('ascii'))

    with open(username + '_public.pem', 'w') as f:
        f.write(key.publickey().export_key().decode('ascii'))


def create_signature(file, username):
    with open(username + '_private.pem', 'r') as f:
        private = DSA.import_key(f.read().encode('ascii'))

    with open(file, 'r') as f:
        message = f.read()

    dss = DSS.new(private, 'fips-186-3')
    signature = dss.sign(SHA256.new(message.encode('utf-8')))

    with open('signed_file.txt', 'wb') as f:
        f.write(message.encode('utf-8') + b'\n' + signature)


def verify_signature(file, username):
    with open(username + '_public.pem', 'r') as f:
        public = DSA.import_key(f.read().encode('ascii'))

    dss = DSS.new(public, 'fips-186-3')

    with open(file, 'rb') as f:
        message = f.read()

    sign = message.rfind(b'\n')

    try:
        dss.verify(SHA256.new(message[:sign]), message[sign + 1:])
        print('verified')
    except ValueError:
        print('corrupted')


if __name__ == '__main__':
    while True:
        print('Choose what to do:\n'
              '1. Generate key\n'
              '2. Sign file\n'
              '3. Verify file')

        c = input()
        if c == '1':
            print('Enter username')
            username = input()
            generate_keys(username)
        elif c == '2':
            print('Enter file')
            file = input()
            print('Enter username')
            username = input()
            create_signature(file, username)
        elif c == '3':
            print('Enter file')
            file = input()
            print('Enter username')
            username = input()
            verify_signature(file, username)
        else:
            break
