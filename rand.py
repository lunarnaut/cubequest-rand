#!/usr/bin/env python3

import argparse
import datetime
import random
import string

a = 1664525
b = 1013904223
M = 2**32

MASK32 = 2**32 - 1

def lcg(x):
    """Linear congruent generator"""
    return (a * x + b) % M

def generate_block(x):
    words = []

    # Each block is 1024-bit
    for _ in range(1024//32):
        x = lcg(x)
        words.append(x)

    return words, x

def random_key():
    key = ''

    for _ in range(256):
        key += random.choice(string.ascii_letters + string.digits)

    return key

def generate_seed(key, timestamp):
    """
    XOR each 32-bit component together.
    key is 256-bit ascii, timestamp 128-bit ascii

    NOTE: I am not certain that the CommsProc intends the key to be
    ASCII.  I am also unsure of the byte order I should convert the
    ASCII with.
    """
    ret = 0

    key = key.encode('ascii')
    key = int.from_bytes(key, byteorder='big')

    ret ^= key & MASK32
    ret ^= (key >> 32) & MASK32
    ret ^= (key >> 64) & MASK32
    ret ^= (key >> 96) & MASK32
    ret ^= (key >> 128) & MASK32
    ret ^= (key >> 160) & MASK32
    ret ^= (key >> 224) & MASK32

    timestamp = timestamp.encode('ascii')
    timestamp = int.from_bytes(timestamp, byteorder='big')

    ret ^= timestamp & MASK32
    ret ^= (timestamp >> 32) & MASK32
    ret ^= (timestamp >> 64) & MASK32
    ret ^= (timestamp >> 96) & MASK32

    return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate CubeQuest random data')
    parser.add_argument('--team-key', type=str, help='Team key',
                        default=random_key())
    parser.add_argument('--timestamp', type=str, default=None,
                        help='''Timestamp to use instead of current time.
                                Must be in YYYYMMDDHHMMSS.S format''')
    parser.add_argument('-i', '--iterations', type=int, default=3,
                        help='Number of blocks to output')
    args = parser.parse_args()

    print('Team key: %s' % args.team_key)

    if args.timestamp:
        timestamp = args.timestamp
    else:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        timestamp = timestamp.strftime('%Y%m%d%H%M%S.%f')

        # Silly hack to reduce precision to 1/10 sec
        timestamp = timestamp[:-5]

    print('Timestamp: %s' % timestamp)

    seed = generate_seed(args.team_key, timestamp)

    print('Seed: %d' % seed)

    x = seed

    print('Blocks:')
    for i in range(args.iterations):
        block, x = generate_block(x)
        print('%d: %s' % (i, block))
