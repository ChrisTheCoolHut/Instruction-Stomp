#!/usr/bin/env python
from elftools.elf.elffile import ELFFile
import tqdm
from lib.celery_tasks import *
import argparse
import subprocess
import string
import time
import os
from operator import itemgetter 



qemu_match = {
        'arm' : 'qemu-arm',
        'armeb' : 'qemu-armeb',
        'mips' :  'qemu-mips',
        'mipsel' : 'qemu-mipsel',
        'i386' : 'qemu-i386',
        'x64' : 'qemu-x86_64'
        }

# <qemu-usermode> -d in_asm,nochain <Binary> <Bianry Args>
qemu_command = "{} -d in_asm,nochain {} {}"

def get_file_arch(file_name):
    with open(file_name, 'rb') as f:
        elf = ELFFile(f)
        arch = elf.get_machine_arch()
        is_little_endian = elf.little_endian
        return arch, is_little_endian

def get_qemu_binary(arch, is_little):

    if arch == "ARM":
        if is_little:
            return qemu_match['arm']
        return qemu_match['armeb']
    if arch == "MIPS":
        if is_little:
            return qemu_match['mipsel']
        return qemu_match['mips']
    if arch == "x86":
        return  qemu_match['i386']
    if arch == "x64":
        return qemu_match['x64']
    return None
    

def make_input_file(file_name, contents):
    with open(file_name, 'w') as f:
        f.write(contents)

def do_run(position, user_input, qemu_binary, binary, use_stdin=True):
    async_group = []
    for x in string.printable:
        input_test = mod_input(user_input, position, x)
        async_group.append(
                run_qemu_command.delay(
                    qemu_binary, input_test,
                    binary, x, use_stdin))

    bar = tqdm.tqdm(total=len(async_group), desc="[~] Running on position {}".format(position))
    while not all([x.ready() for x in async_group]):
        done_count = len([x.ready() for x in async_group if x.ready()])
        bar.update(done_count - bar.n)
        time.sleep(1)
    bar.close()

    return [x.get(propagate=False) for x in async_group if not x.failed()]

def solve_ins_count(file_name, input_length, input_rev, input_stdin):

    starting_input = "A"*input_length
    run_dict = {}
    my_r = range(input_length)
    if input_rev:
         my_r = reversed(my_r)

    arch, is_little_endian= get_file_arch(file_name)
    qemu_binary = get_qemu_binary(arch, is_little_endian)
    file_name = os.path.abspath(file_name)


    modified_input = starting_input
    for val in my_r:

        results = do_run(val, modified_input, qemu_binary, file_name, input_stdin)
        mod_char = max(results,key=itemgetter(1))[0]
        modified_input = mod_input(modified_input, val,  mod_char)
        print(modified_input)

def solve_input_len(file_name, input_length, input_stdin):

    arch, is_little_endian= get_file_arch(file_name)
    qemu_binary = get_qemu_binary(arch, is_little_endian)
    file_name = os.path.abspath(file_name)

    async_group = []
    for x in range(input_length):
        input_test = "A" * x
        async_group.append(
                run_qemu_command.delay(
                    qemu_binary, input_test,
                    file_name, x, input_stdin))

    bar = tqdm.tqdm(total=len(async_group), desc="[~] Running input length check")
    while not all([x.ready() for x in async_group]):
        done_count = len([x.ready() for x in async_group if x.ready()])
        bar.update(done_count - bar.n)
        time.sleep(1)
    bar.close()

    results = [x.get(propagate=False) for x in async_group if not x.failed()]
    print(results)

    input_len = max(results,key=itemgetter(1))[0]

    print ("Input Length: {}".format(input_len))

def mod_input(user_input, position, character):
        user_input = list(user_input)
        user_input[position] = character
        return ''.join(user_input)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("File", help="File to analyze")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stdin", action="store_true", default=False, help="Send inputs through STDIN")
    group.add_argument("--arg", action="store_false", help="Send inputs through argv[2]")

    parser.add_argument("-i", "--inputLength", help="Length of input", type=int)
    parser.add_argument("-r", "--reverse", help="Reverse input checking", default=False, action='store_true')
    parser.add_argument("-g", "--getLength", help="Get input length", default=False, action='store_true')
    parser.add_argument("-c", "--inputCheckCount", help="How much length to check", default=30, type=int)

    args = parser.parse_args()

    if not args.getLength:
        solve_ins_count(args.File, args.inputLength, args.reverse, args.stdin)
    else:
        solve_input_len(args.File, args.inputCheckCount, args.stdin)

if __name__ == "__main__":
    main()
