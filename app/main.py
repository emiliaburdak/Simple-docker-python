import subprocess
import sys
import tempfile
import os
import shutil


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage

    command = sys.argv[3]
    args = sys.argv[4:]

    # temporary directory
    temp_dir_path = tempfile.mkdtemp()

    # copy directory
    shutil.copy2(command, temp_dir_path)

    # change path from root to temp_dir_path
    os.chroot(temp_dir_path)

    # make new path
    # This is useful because you only need the file name to refer to it in the new chroot environment
    new_command = "/" + os.path.basename(command)

    # create new PID namespace
    new_command_unshare = ["unshare", "--fork", "--pid", "--mount-proc", new_command]

    # Execute with command, args but capture out and err
    # communicate() reads all the processes inputs and outputs and stores it in the variables
    completed_process = subprocess.Popen(new_command_unshare + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = completed_process.communicate()

    # it works like print
    sys.stdout.write(stdout.decode("utf-8"))
    sys.stderr.write(stderr.decode("utf-8"))

    # process that has been executed by .run or .popen has attribute .returncode that is the number
    # witch indicates success of the process, sys.exit ends the process and pass the result to the initial environment
    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
