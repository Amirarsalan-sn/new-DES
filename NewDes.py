import bitarray


class NewDes:
    def __init__(self):
        self.substitution_table = [[(0, 1), (4, 2), (1, 3), (3, 3), (2, 1), (5, 1), (3, 3), (7, 6)],
                                   [(2, 0), (0, 1), (0, 7), (2, 6), (5, 0), (3, 1), (2, 0), (1, 4)],
                                   [(2, 4), (2, 3), (2, 7), (3, 7), (1, 4), (2, 7), (6, 7), (7, 6)],
                                   [(5, 6), (4, 5), (3, 4), (3, 7), (2, 3), (3, 1), (7, 3), (3, 6)],
                                   [(6, 5), (5, 7), (7, 6), (7, 4), (3, 2), (2, 5), (6, 4), (6, 0)],
                                   [(1, 0), (2, 0), (3, 4), (5, 0), (0, 0), (2, 5), (4, 0), (2, 2)],
                                   [(3, 3), (4, 6), (3, 2), (1, 2), (4, 6), (7, 4), (2, 7), (5, 5)],
                                   [(1, 1), (1, 7), (3, 5), (4, 3), (6, 5), (1, 6), (6, 7), (7, 7)]]

        self.first_play_fair_key = ['ARSCO',
                                    'MPBDE',
                                    'FGHIK',
                                    'LNQTU',
                                    'VWXYZ']

        self.last_play_fair_key = ['SANCO',
                                   'MPBDE',
                                   'FGHIK',
                                   'LQRTU',
                                   'VWXYZ']

    def encrypt(self, message: bytes, key: bytes, IV: bytes):
        message = message.replace(b' ', b'x')
        message = self.play_fair_encrypt(message, 1)
        message_blocks = [IV]
        for i in range(0, len(message), 32):
            if i + 32 <= len(message):
                message_blocks.append(message[i: i + 32])
            else:
                message_blocks.append(message[i: len(message)])

        message_blocks[-1] = message_blocks[-1] + (32 - len(message_blocks[-1])) * b'\x00'

        round_keys = self.gen_round_key(key)
        cipher_blocks = [self.encrypt_block(IV, round_keys)]
        # CBC mode
        temp = (int.from_bytes(message_blocks[0], 'big') ^ int.from_bytes(message_blocks[1], 'big')).to_bytes(32, 'big',
                                                                                                              signed=False)
        cipher_blocks.append(self.encrypt_block(temp, round_keys))
        i = 1
        for block in message_blocks[2:]:
            temp = (int.from_bytes(cipher_blocks[-1], 'big') ^ int.from_bytes(block, 'big')).to_bytes(32, 'big',
                                                                                                      signed=False)
            cipher_blocks.append(self.encrypt_block(temp, round_keys))
            i += 1

        cipher_text = b''.join(cipher_blocks)
        cipher_text = self.play_fair_encrypt(cipher_text, 2)
        return cipher_text

    def encrypt_block(self, message: bytes, key: list) -> bytes:
        left_block = message[0: 16]
        right_block = message[16: 32]
        for i in range(16):
            temp = right_block
            right_block = (
                    int.from_bytes(self.feistel_function(right_block, key[i]), 'big') ^ int.from_bytes(left_block,
                                                                                                       'big')).to_bytes(
                16, 'big', signed=False)
            left_block = temp

        temp = right_block
        right_block = left_block
        left_block = temp

        return b''.join([left_block, right_block])

    def play_fair_encrypt(self, message: bytes, key_type: int) -> bytes:

        for i in range(0, len(message) - 1, 2):
            if (ord('A') <= message[i] <= ord('Z')) or (ord('a') <= message[i] <= ord('z')):
                if (ord('A') <= message[i + 1] <= ord('Z')) or (ord('a') <= message[i + 1] <= ord('z')):
                    char1, char2 = self.play_fair_replace(chr(message[i]), chr(message[i + 1]), True, key_type)
                    temp = bytearray(message)
                    temp[i] = ord(char1)
                    temp[i + 1] = ord(char2)
                    message = bytes(temp)

        return message

    def play_fair_replace(self, char1, char2, enc_or_dec, key_type) -> (str, str):
        if key_type == 1:
            key = self.first_play_fair_key
        else:
            key = self.last_play_fair_key
        index1 = 0
        index2 = 0
        for i in range(5):
            for j in range(5):
                if (key[i][j] == char1) or (chr(ord(key[i][j]) + 32) == char1):
                    index1 = [i, j]
                if (key[i][j] == char2) or (chr(ord(key[i][j]) + 32) == char2):
                    index2 = [i, j]
                if key[i][j] == 'I':
                    if ('J' == char1) or ('j' == char1):
                        index1 = [i, j]
                    if ('J' == char2) or ('j' == char2):
                        index2 = [i, j]

        if enc_or_dec:
            if index1[0] == index2[0]:
                index1[0] = (index1[0] + 1) % 5
                index2[0] = (index2[0] + 1) % 5
                if ord('A') <= ord(char1) <= ord('Z'):
                    char_r1 = key[index1[0]][index1[1]]
                else:
                    char_r1 = key[index1[0]][index1[1]].lower()
                if ord('A') <= ord(char2) <= ord('Z'):
                    char_r2 = key[index2[0]][index2[1]]
                else:
                    char_r2 = key[index2[0]][index2[1]].lower()
                return char_r1, char_r2
            if index1[1] == index2[1]:
                index1[1] = (index1[1] + 1) % 5
                index2[1] = (index2[1] + 1) % 5
                if ord('A') <= ord(char1) <= ord('Z'):
                    char_r1 = key[index1[0]][index1[1]]
                else:
                    char_r1 = key[index1[0]][index1[1]].lower()
                if ord('A') <= ord(char2) <= ord('Z'):
                    char_r2 = key[index2[0]][index2[1]]
                else:
                    char_r2 = key[index2[0]][index2[1]].lower()
                return char_r1, char_r2
            else:
                if ord('A') <= ord(char1) <= ord('Z'):
                    char_r1 = key[index1[0]][index2[1]]
                else:
                    char_r1 = key[index1[0]][index2[1]].lower()
                if ord('A') <= ord(char2) <= ord('Z'):
                    char_r2 = key[index2[0]][index1[1]]
                else:
                    char_r2 = key[index2[0]][index1[1]].lower()
                return char_r1, char_r2
        else:
            if index1[0] == index2[0]:
                index1[0] = (index1[0] - 1) % 5
                index2[0] = (index2[0] - 1) % 5
                if ord('A') <= ord(char1) <= ord('Z'):
                    char_r1 = key[index1[0]][index1[1]]
                else:
                    char_r1 = key[index1[0]][index1[1]].lower()
                if ord('A') <= ord(char2) <= ord('Z'):
                    char_r2 = key[index2[0]][index2[1]]
                else:
                    char_r2 = key[index2[0]][index2[1]].lower()
                return char_r1, char_r2
            if index1[1] == index2[1]:
                index1[1] = (index1[1] - 1) % 5
                index2[1] = (index2[1] - 1) % 5
                if ord('A') <= ord(char1) <= ord('Z'):
                    char_r1 = key[index1[0]][index1[1]]
                else:
                    char_r1 = key[index1[0]][index1[1]].lower()
                if ord('A') <= ord(char2) <= ord('Z'):
                    char_r2 = key[index2[0]][index2[1]]
                else:
                    char_r2 = key[index2[0]][index2[1]].lower()
                return char_r1, char_r2
            else:
                if ord('A') <= ord(char1) <= ord('Z'):
                    char_r1 = key[index1[0]][index2[1]]
                else:
                    char_r1 = key[index1[0]][index2[1]].lower()
                if ord('A') <= ord(char2) <= ord('Z'):
                    char_r2 = key[index2[0]][index1[1]]
                else:
                    char_r2 = key[index2[0]][index1[1]].lower()
                return char_r1, char_r2

    def gen_round_key(self, key: bytes):
        result = [key]
        for i in range(15):
            bit_arr = bitarray.bitarray()
            bit_arr.frombytes(result[-1])
            result.append(((bit_arr << 8) | (bit_arr >> 120)).tobytes())

        return result

    def feistel_function(self, Ri: bytes, round_key: bytes) -> bytes:
        bit_array = bitarray.bitarray()
        bit_array.frombytes(Ri)
        key_array = bitarray.bitarray()
        key_array.frombytes(round_key)
        for i in range(0, 122):  # live the bits 127 and 128
            index1 = int(bit_array[i: i + 3].to01(), 2)
            index2 = int(bit_array[i + 3: i + 6].to01(), 2)
            replacement_value1, replacement_value2 = self.substitution_table[index1][index2]
            replace1 = bitarray.bitarray(f'{replacement_value1:0{3}b}')  # A 3 bit value is going to be replaced
            replace2 = bitarray.bitarray(f'{replacement_value2:0{3}b}')
            bit_array[i: i + 3] = replace1
            bit_array[i + 3: i + 6] = replace2

        result = bit_array ^ key_array
        return result.tobytes()

    def play_fair_decrypt(self, message: bytes, key_type: int) -> bytes:

        for i in range(0, len(message) - 1, 2):
            if (ord('A') <= message[i] <= ord('Z')) or (ord('a') <= message[i] <= ord('z')):
                if (ord('A') <= message[i + 1] <= ord('Z')) or (ord('a') <= message[i + 1] <= ord('z')):
                    char1, char2 = self.play_fair_replace(chr(message[i]), chr(message[i + 1]), False, key_type)
                    temp = bytearray(message)
                    temp[i] = ord(char1)
                    temp[i + 1] = ord(char2)
                    message = bytes(temp)

        return message

    def decrypt(self, message: bytes, key: bytes):
        message = self.play_fair_decrypt(message, 2)
        cipher_blocks = []
        for i in range(0, len(message), 32):
            if i + 32 <= len(message):
                cipher_blocks.append(message[i: i + 32])

        round_keys = self.gen_round_key(key)

        # CBC mode
        IV = self.decrypt_block(cipher_blocks[0], round_keys)
        message_blocks = [(int.from_bytes(self.decrypt_block(cipher_blocks[1], round_keys), 'big') ^ int.from_bytes(IV,
                                                                                                                    'big')).to_bytes(
            32, 'big', signed=False)]
        temp = cipher_blocks[1]
        i = 1
        for block in cipher_blocks[2:]:
            message_blocks.append((int.from_bytes(self.decrypt_block(block, round_keys),
                                                  'big') ^ int.from_bytes(temp, 'big')).to_bytes(32, 'big',
                                                                                                 signed=False))
            temp = block

        plain_text = b''.join(message_blocks)
        plain_text = self.play_fair_decrypt(plain_text, 1)
        plain_text = plain_text.replace(b'x', b' ')
        return plain_text

    def decrypt_block(self, message: bytes, key) -> bytes:
        left_block = message[0: 16]
        right_block = message[16: 32]
        for i in range(15, -1, -1):
            temp = right_block
            right_block = (
                    int.from_bytes(self.feistel_function(right_block, key[i]), 'big') ^ int.from_bytes(left_block,
                                                                                                       'big')).to_bytes(
                16, 'big', signed=False)
            left_block = temp

        temp = right_block
        right_block = left_block
        left_block = temp

        return b''.join([left_block, right_block])
