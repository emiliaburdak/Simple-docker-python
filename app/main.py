import subprocess
import sys


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage

    command = sys.argv[3]
    args = sys.argv[4:]

    # completed_process = subprocess.run([command, *args], capture_output=True)
    # print(completed_process.stdout.decode("utf-8"))

    # Execute with command, args but capture out and err
    # communicate() reads all the processes inputs and outputs and stores it in the variables
    completed_process = subprocess.Popen([command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = completed_process.communicate()

    # it works like print
    sys.stdout.write(stdout.decode("utf-8"))
    sys.stderr.write(stderr.decode("utf-8"))

    # process that has been executed by .run or .popen has attribute .returncode that is the number
    # witch indicates success of the process, sys.exit ends the process and pass the result to the initial environment
    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
