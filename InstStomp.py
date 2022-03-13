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

def do_run(position, user_input, qemu_binary, binary, use_stdin=True, in_asm_mode=True):
    async_group = []
    for x in range(0x21,0x7E):
        x = chr(x)
        input_test = mod_input(user_input, position, x)
        async_group.append(
                run_qemu_command.delay(
                    qemu_binary, input_test,
                    binary, x, use_stdin, in_asm_mode))

    bar = tqdm.tqdm(total=len(async_group), desc="[~] Running on position {}".format(position))
    while not all([x.ready() for x in async_group]):
        done_count = len([x.ready() for x in async_group if x.ready()])
        bar.update(done_count - bar.n)
        time.sleep(1)
    bar.close()

    return [x.get(propagate=False) for x in async_group if not x.failed()]

def solve_ins_count(args):

    # solve_ins_count(args.File, args.inputLength, args.reverse, args.stdin)
    file_name = args.File
    input_length = args.inputLength
    input_rev = args.reverse
    input_stdin = args.stdin

    starting_input = "A"*input_length
    if args.curr:
        starting_input = args.curr
    my_r = range(input_length)
    if input_rev:
         my_r = reversed(my_r)

    if args.curr_iter:
        my_r = my_r[args.curr_iter:]

    arch, is_little_endian= get_file_arch(file_name)
    qemu_binary = get_qemu_binary(arch, is_little_endian)
    file_name = os.path.abspath(file_name)

 
    modified_input = starting_input
    if not args.exec:
        # First try qemu in_asm method
        for val in my_r:

            results = do_run(val, modified_input, qemu_binary, file_name, input_stdin, True)

            if args.verbose:
                for res in results:
                    print("{} : {}".format(res[0],res[1]))
        
            # Are all the lengths the same?
            ins_counts = [x[1] for x in results]
            if ins_counts.count(ins_counts[0]) == len(ins_counts):
                print("All ins counts are equal")
                break

            mod_char = max(results,key=itemgetter(1))[0]
            if args.verbose:
                print("Choosing : {} : {}".format(mod_char, val))
            modified_input = mod_input(modified_input, val,  mod_char)
            print(modified_input)
    
    modified_input = starting_input
    # Then try qemu exec method
    for val in my_r:

        results = do_run(val, modified_input, qemu_binary, file_name, input_stdin, False)
        
        if args.verbose:
            for res in results:
                print("{} : {}".format(res[0],res[1]))

        # Are all the lengths the same?
        ins_counts = [x[1] for x in results]
        if ins_counts.count(ins_counts[0]) == len(ins_counts):
            print("All ins counts are equal")
            break

        mod_char = max(results,key=itemgetter(1))[0]
        if args.verbose:
            print("Choosing : {} : {}".format(mod_char, val))
        modified_input = mod_input(modified_input, val,  mod_char)
        print(modified_input)

def solve_input_len(args):

    file_name = args.File
    input_length = args.inputCheckCount
    input_stdin = args.stdin

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

    parser.add_argument("--exec", help="Use exec qemu mode", default=False, action="store_true")
    parser.add_argument("-v","--verbose",help="enable debug output",default=False, action="store_true")
    parser.add_argument("--curr",help="Current input to start with")
    parser.add_argument("--curr_iter",help="Skip to this value", type=int)

    args = parser.parse_args()

    if not args.getLength:
        solve_ins_count(args)
    else:
        solve_input_len(args)

if __name__ == "__main__":
    main()
