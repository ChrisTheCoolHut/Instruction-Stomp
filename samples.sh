#!/bin/bash

#Get user input length
./InstStomp.py -g -c 30 --stdin challenges/wyvern_c85f1be480808a9da350faaa6104a19b
./InstStomp.py -i 29  --stdin challenges/wyvern_c85f1be480808a9da350faaa6104a19b

#Run in reverse
./InstStomp.py --stdin -i 25 -r challenges/ELF-NoSoftwareBreakpoints

#Run on binary with command line argument
./InstStomp.py challenges/crypt4 -i 26 --arg --exec
