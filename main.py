from NewDes import NewDes
import base58
import os

if __name__ == '__main__':
    my_des = NewDes()
    key = b'random32bytesKey'
    IV = 'Arandom32bytesIVforinitializingg'
    plain_text = input('Insert the plain text: ')
    cipher_text = my_des.encrypt(plain_text.encode(), key, IV.encode())
    again_plain = my_des.decrypt(cipher_text, key).replace(b'\x00', b'')

    print(f'''
        Plain Text : {plain_text}
        Cipher Text : {base58.b58encode(cipher_text)}
        Decrypted Cipher Text : {again_plain.decode()}
''')
