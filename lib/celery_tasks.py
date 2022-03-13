from celery import Celery

app = Celery('CeleryTask')
app.config_from_object('celeryconfig')
#qemu_command = "{} -E LD_PRELOAD=/home/chris/projects/Instruction-Stomp/preload_libs/slow_memcmp.so_64 -d {} {} {} 2>&1 | wc -l"
qemu_command = "{} -d {} {} {} 2>&1 | wc -l"

in_asm_mode = "in_asm,nochain"
exec_mode = "exec,nochain"
import subprocess
import shlex

@app.task
def run_qemu_command(qemu_binary, content, binary, character, stdin_input=True, asm_mode=True):
    ins_count = -1

    if asm_mode:
        mode = in_asm_mode
    else:
        mode = exec_mode

    if stdin_input:

        content = str.encode(content)
        proc_command = qemu_command.format(
                qemu_binary, mode, binary, "")
        print(proc_command)

        qemu_proc = subprocess.Popen(proc_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True)

        ins_count = qemu_proc.communicate(content)[0]
        
    else:
        proc_command = qemu_command.format(
                qemu_binary, mode, binary, content)

        qemu_proc = subprocess.Popen(proc_command, shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)

        ins_count = qemu_proc.communicate()[0]

    try:
        ins_count = int(ins_count.decode('utf-8', 'ignore'))
    except AttributeError as e:
        print("Couldn't process None type")
        return (character, -1)
    print(content)
    print(ins_count)
    return (character, ins_count)

