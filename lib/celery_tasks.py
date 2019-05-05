from celery import Celery

app = Celery('CeleryTask')
app.config_from_object('celeryconfig')
qemu_command = "{} -d exec,nochain {} {} 2>&1 | wc -l"
import subprocess
import shlex

@app.task
def run_qemu_command(qemu_binary, content, binary, character, stdin_input=True):
    ins_count = -1
    if stdin_input:

        content = str.encode(content)
        proc_command = qemu_command.format(
                qemu_binary, binary, "")

        qemu_proc = subprocess.Popen(proc_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True)

        ins_count = qemu_proc.communicate(content)[0]
        
    else:
        proc_command = qemu_command.format(
                qemu_binary, binary, content)

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

