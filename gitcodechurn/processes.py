import subprocess
from copy import copy


class Process:

    @classmethod
    def get_proc_out(cls, command, project_dir):
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_dir,
            shell=True
        )
        resp = process.communicate()
        value = copy(resp[0])
        try:
            return value.decode('utf-8')
        except Exception as e:
            return value.decode("latin-1")
