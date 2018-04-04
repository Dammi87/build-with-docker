import argparse
from argparse import Namespace
import os
import json
import getpass
import sys

from lib.docker_classes import BuildWithDocker, DockerImages
from lib import ssh_utils as ssh
from lib import utils

# Make all print statements RED until we run the actual build command
utils.set_color('RED')

def check_for_cfg(project_dir):
    return os.path.exists(os.path.join(project_dir, "bwd.json"))


def parse_cfg_file(project_dir):
    file = os.path.join(project_dir, "bwd.json")
    with open(file, 'r') as f:
        cfg = json.load(f)

    # Add user
    for user in cfg:
        for build in cfg[user]:
            build["user"] = user

    # Fetch the current user
    current_user = getpass.getuser()

    # Check for these fields
    check_these = [current_user, "common"]

    # Fetch the configs
    build_settings = []
    for iCheck in check_these:
        if iCheck in cfg:
            build_settings += cfg[iCheck]

    # Make sure it has build_cmd specified, if not
    # issue a warning.
    for i, i_setting in enumerate(build_settings):
        if "build_cmd" not in i_setting:
            print("Warning, build_cmd for %s / common not found" % current_user)
        if "build_name" not in i_setting:
            set_name = "%s_%d" % (i_setting["user"], i)
            print("Warning, build_name for %s / common not found" % current_user)
            print("Generated build name is %s" % set_name)
            i_setting["build_name"] = set_name


    build_names = [i_setting['build_name'] for i_setting in build_settings]
    return build_settings, build_names


def get_build_setting(args):
    # Make sure that we are using absolute paths
    args.proj = os.path.abspath(args.proj)
    args.s = os.path.abspath(args.s)

    build_settings, build_names = parse_cfg_file(args.proj)

    # Check build
    nr = 0
    if args.build_name is not None:
        if args.build_name in build_names:
            nr = build_names.index(args.build_name)
        else:
            print("Could not find %s in build config." % args.build_name)
            print("Using the first build settings as default.")
    else:
        print("No build name specified, using %s as default" % build_settings[nr]['build_name'])


    def get_namespace(**kwargs):
        param = {
            'proj': args.proj,
            's': args.s,
            'd': kwargs.get('docker_file', None),
            'v': kwargs.get('volumes', None),
            'p': kwargs.get('ports', None),
            'gpu': kwargs.get('gpu', None),
            'GUI': kwargs.get('GUI', None),
            'ssh_ip': kwargs.get('ssh_ip', None),
            'ssh_user': kwargs.get('ssh_user', None),
            'remote_folder': kwargs.get('remote_folder', None),
            'run_as_module': kwargs.get('run_as_module', False),
            'build_cmd': kwargs.get('build_cmd', None),
            'custom_cmd': kwargs.get('custom_cmd', None)
        }

        return Namespace(**param)

    return get_namespace(**build_settings[nr])


def init_project(project_dir):
    docker_folder = os.path.join(project_dir, 'Dockerfiles')

    if check_for_cfg(project_dir) or os.path.exists(docker_folder):
        print("\tbwd.json and/or Dockerfiles folder already present in the project! Delete the bwd.json and the Dockefiles folder")
        exit()

    # Create the dir
    os.makedirs(docker_folder)

    # Create a dockerfile
    with open(os.path.join(docker_folder, 'python3.Dockerfile'), 'w') as f:
        f.write("FROM python:3.4-slim")

    # Create a json config file
    user = getpass.getuser()
    base_cfg = {
            user: [
                {
                    "build_name": "build_with_docker",
                    "docker_file" : "python3",
                    "build_cmd": "python3",
                    "run_as_module": False
                },
                {
                    "docker_file" : "python3",
                    "volumes": ["/home/%s" % user],
                    "ports": ["8000:8000"],
                    "build_cmd": "python3 -m",
                    "run_as_module": True
                }
            ],
            "common": [
                {
                    "build_name": "build_on_remote",
                    "docker_file" : "python3",
                    "volumes": ["/data"],
                    "ports": ["8000:8000"],
                    "gpu": [0, 1],
                    "GUI": False,
                    "ssh_ip": "10.0.1.173",
                    "ssh_user": "protolab", 
                    "remote_folder": "/hdd/users/",
                    "build_cmd": "python3 -u",
                    "run_as_module": False
                }
            ]
        }

    print("\tDone!")

    # And write to file
    with open(os.path.join(project_dir, 'bwd.json'), 'w') as f:
        json.dump(base_cfg, f)



parser = argparse.ArgumentParser()
parser.add_argument(
    '-s',
    help='Python script to build',
    type=str
)
parser.add_argument(
    '-proj',
    help='Project directory',
    type=str
)
parser.add_argument(
    '-build_name',
    help='Which build setting from "common" or "$USER" to build with. Default is first one from user.',
    type=str,
    default=''
)
parser.add_argument(
    '-build_image',
    help='Build the projects docker images, supply "all" as parameter to build all images',
    type=str,
    const='all',
    default=None,
    action='store',
    nargs='?',
)
parser.add_argument(
    '-init',
    help='Initialize the project by creating a build config file and a Dockerfile.',
    type=str,
    const='',
    default=None,
    action='store',
    nargs='?',
)
args = parser.parse_args()


# Make sure that either -s or -build_images is provided
if args.s is None and args.build_image is None and args.init is None:
    parser.error("Could not determine what to do. Make sure that you either provide this with -s or -build_image")

# If project dir is not specified, assume its the cwd<
if args.proj is None:
    args.proj = os.getcwd()
    print("No project specified, assuming %s is project root" % args.proj)


if args.init is not None:
    # User wants to initialize the project
    print("Initializing project..")
    init_project(args.proj)
    exit()

# Check for a config file
if not check_for_cfg(args.proj):
    parser.error("Could not find a config file in root directory!")

# Build
if args.build_image is not None:
    docker_images = DockerImages(args.proj)
    utils.set_color('RESET')
    if args.build_image == 'all':
        print("No specific Dockerfile mentioned, building all files..")
        docker_images.build_all()
        print("Finished building all docker images")
    else:
        print("Building %s.." % args.build_image)
        docker_images.build_one(args.build_image)
        print("Finished building %s docker image" % args.build_image)


# If no s argument is specified and we reach this spot, exit
if args.s is None:
    exit()

# Otherwise, we load in the config file
args = get_build_setting(args)

# Maybe send the project through a tunnel, then build
ssh_result = ssh.maybe_send(args)

# Get the docker builder class
bwd = BuildWithDocker(args.proj, ssh_result)
# Pass it our arguments
bwd.add_arguments(args)

# Get the command
command = bwd.get_command()

# Append ssh command if needed
if ssh_result is not None:
    command = ssh.append_ssh(args.ssh_user, args.ssh_ip, command)

# Run
utils.set_color('GREEN')
print("Docker command:\n\t--> %s" % command)
utils.set_color('RESET')
os.system(command)
