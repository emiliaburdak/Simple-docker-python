import subprocess
import sys
import tempfile
import os
import shutil
import ctypes
import json
import tarfile
import urllib.request
import io

BASE_REGISTRY_URL = "https://registry.hub.docker.com"
AUTH_URL = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull"
AUTH_TOKEN = None

# A bit value representing a flag used in the system call for unshare in Linux.
CLONE_NEWPID = 0x20000000

# image layer and image manifest --need--> request --need--> header --need--> token authentication
# token authentication step also needs request but without headers


def request(url, headers=None, type="json"):
    if headers is None:
        headers = {}

    # request is an object used to represent a specific request operation, containing information such as the URL...
    # available arguments : (url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None)
    req = urllib.request.Request(url, None, headers)

    # make connection to url using request object and return response
    with urllib.request.urlopen(req) as response:
        if type == "json":
            return json.loads(response.read().decode("urf-8"))
        return response.read()


def get_token():

    global AUTH_TOKEN
    if AUTH_TOKEN is not None:
        return AUTH_TOKEN
    auth_response = request(AUTH_URL)
    AUTH_TOKEN = auth_response["access_token"]
    return AUTH_TOKEN


def get_headers():

    global AUTH_TOKEN
    if AUTH_TOKEN is None:
        AUTH_TOKEN = get_token()
    return {"Authorization": f"Bearer {AUTH_TOKEN}"}


def pull_image_layer(name, layer):

    # Pull a specific layer of an image (changes) from the Docker registry.
    url = f"{BASE_REGISTRY_URL}/v2/library/{name}/blobs/{layer}"
    headers = get_headers()
    return request(url, headers, "blob")


def fetch_image_manifest(name, reference):

    # fetch metadata about image (manifest) from Docker Registery
    url = f"{BASE_REGISTRY_URL}/v2/library/{name}/manifests/{reference}"
    headers = get_headers()
    return request(url, headers)


def main():

    image_name = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]

    # temporary directory
    temp_dir = tempfile.TemporaryDirectory()

    # fetch manifest
    manifest = fetch_image_manifest(image_name, "latest")

    # get each image layer in manifest and extract to directory
    for layer in manifest["fsLayers"]:
        image_layer_blob = pull_image_layer(image_name, layer["blobSum"])
        # is used to create a byte stream with the layer content, and tarfile.open opens this byte stream as a tar file.
        with tarfile.open(fileobj=io.BytesIO(image_layer_blob)) as tar:
            # All files and directories contained in the tar file are extracted to temporary directory.
            tar.extractall(temp_dir.name)

    # loads the C standard library (libc) into the current Python process
    libc = ctypes.cdll.LoadLibrary(None)

    # creation of a new PID namespace for the process and its descendants
    libc.unshare(CLONE_NEWPID)

    # Execute, change root to extracted image file system
    completed_process = subprocess.run(["chroot", temp_dir.name, command, *args], capture_output=True)

    # it works like print
    sys.stdout.write(completed_process.stdout.decode("utf-8"))
    sys.stderr.write(completed_process.stderr.decode("utf-8"))

    # process that has been executed by .run or .popen has attribute .returncode that is the number
    # witch indicates success of the process, sys.exit ends the process and pass the result to the initial environment
    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
