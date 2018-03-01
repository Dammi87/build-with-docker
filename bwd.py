import argparse
from argparse import Namespace
import os
import json
from src.docker_classes import BuildWithDocker
import src.ssh_utils as ssh
import getpass


def check_for_cfg(project_dir):
    return os.path.exists(os.path.join(project_dir, "bwd.json"))


def parse_cfg_file(project_dir):
    file = os.path.join(project_dir, "bwd.json")
    with open(file, 'r') as f:
        cfg = json.load(f)

    # Fetch the current user
    current_user = getpass.getuser()

    # Check for these fields
    check_these = [current_user, "common"]

    # Fetch the configs
    build_settings = []
    for iCheck in check_these:
        if iCheck in cfg:
            build_settings += cfg[iCheck]

    return build_settings


def get_build_setting(args, nr=2):
    build_settings = parse_cfg_file(args.proj)[nr]

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
            'remote_folder': kwargs.get('remote_folder', None)
        }

        return Namespace(**param)

    return get_namespace(**build_settings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        help='Python script to build',
        type=str,
        required=True,
    )
    parser.add_argument(
        '-proj',
        help='Project directory',
        type=str,
        required=True
    )
    args = parser.parse_args()

    # Check for a config file
    if not check_for_cfg(args.proj):
        parser.error("Could not find a config file in root directory!")

    # Otherwise, we load in the config file
    args = get_build_setting(args)

    # Maybe send the project through a tunnel, then build
    ssh_result = ssh.maybe_send(args)
    bwd = BuildWithDocker(args.proj, ssh_result)
    bwd.add_arguments(args)

    # Add extras if specified
    command = bwd.get_command()

    # Append ssh command if needed
    if ssh_result is not None:
        command = ssh.append_ssh(args.ssh_user, args.ssh_ip, command)

    # Run
    os.system(command)
