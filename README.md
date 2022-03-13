# Instruction Stomp

Another instruction counting tool. This one uses QEMU and celery to count instructions and run in parallel. It works cross architecture, so  ARM/MIPS/PPC binaries should all be  supported.

![Instruction Stomp](https://media.giphy.com/media/THUxzpKmIrZvtAlMZQ/giphy.gif)

## Install

This project uses python3

```
sudo apt install qemu-user rabbitmq-server
pip3 install tqdm celery numpy pyelftools
```
## Usage
Setup celery worker in Instruction Stomp Directory:

```bash
# python3 -m celery -A lib.celery_tasks worker --loglevel=info
celery -A lib.celery_tasks worker --loglevel=info
```

``` bash
$ python3 InstStomp.py -h
usage: InstStomp.py [-h] (--stdin | --arg) [-i INPUTLENGTH] [-r] [-g] [-c INPUTCHECKCOUNT]
                    [--exec] [-v] [--curr CURR] [--curr_iter CURR_ITER]
                    File

positional arguments:
  File                  File to analyze

optional arguments:
  -h, --help            show this help message and exit
  --stdin               Send inputs through STDIN
  --arg                 Send inputs through argv[2]
  -i INPUTLENGTH, --inputLength INPUTLENGTH
                        Length of input
  -r, --reverse         Reverse input checking
  -g, --getLength       Get input length
  -c INPUTCHECKCOUNT, --inputCheckCount INPUTCHECKCOUNT
                        How much length to check
  --exec                Use exec qemu mode
  -v, --verbose         enable debug output
  --curr CURR           Current input to start with
  --curr_iter CURR_ITER
                        Skip to this value
```

## Examples
Get user input length:
```bash
$ python3 InstStomp.py -g -c 30  --stdin challenges/wyvern_c85f1be480808a9da350faaa6104a19b 
[~] Running input length check:  67%|██████████████████████████████████████                   | 20/30 [00:03<00:01,  6.31it/s]
[[0, 337770], [1, 337562], [2, 337823], [3, 337823], [4, 337821], [5, 337821], [6, 337821], [7, 337821], [8, 337820], [9, 337820], [10, 337820], [11, 337820], [12, 337820], [13, 337820], [14, 337820], [15, 337820], [16, 337822], [17, 337826], [18, 337826], [19, 337826], [20, 337826], [21, 337826], [22, 337826], [23, 337826], [24, 337826], [25, 337826], [26, 337826], [27, 337826], [28, 337826], [29, 339147]]
Input Length: 29

```

Solve for binary stdin:
```bash
$ ./InstStomp.py --stdin -i 25 -r challenges/ELF-NoSoftwareBreakpoints 
[~] Running on position 24:   0%|                                                                     | 0/100 [00:00<?, ?it/s]
AAAAAAAAAAAAAAAAAAAAAAAAS
[~] Running on position 23:   0%|                                                                     | 0/100 [00:00<?, ?it/s]
AAAAAAAAAAAAAAAAAAAAAAAkS
[~] Running on position 22:   0%|                                                                     | 0/100 [00:00<?, ?it/s]
AAAAAAAAAAAAAAAAAAAAAAckS
... SNIP ...
[~] Running on position 2:   0%|                                                                      | 0/100 [00:00<?, ?it/s]
AArdW@re_Br3akPoiNT_r0ckS
[~] Running on position 1:   0%|                                                                      | 0/100 [00:00<?, ?it/s]
AardW@re_Br3akPoiNT_r0ckS
[~] Running on position 0:   0%|                                                                      | 0/100 [00:00<?, ?it/s]
HardW@re_Br3akPoiNT_r0ckS

```
