import argparse
import os
from src.docker_classes import BuildWithDocker, DockerImages
import src.ssh_utils as ssh

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-proj',
        help='Project directory',
        type=str,
        required=True
    )
    parser.add_argument(
        '-s',
        help='Python script to build',
        type=str,
        required=True
    )
    parser.add_argument(
        '-d',
        help='Dockerfile to use for building',
        type=str,
        required=True
    )
    parser.add_argument(
        '-v',
        help='Extra volumes to mount',
        nargs='*',
        type=str,
    )
    parser.add_argument(
        '-p',
        help='Ports to open, example -p 6006:6006 8080:8081',
        nargs='*',
        type=str,
    )
    parser.add_argument(
        '-gpu',
        help='GPU (or multiple gpus) to run on',
        nargs='*',
        type=int,
    )
    parser.add_argument(
        '-GUI',
        help='Add GUI support to command',
        action='store_true'
    )
    parser.add_argument(
        '-build',
        help='Build the docker image before running',
        action='store_true'
    )
    parser.add_argument(
        '-ssh_ip',
        help='Ip address of the remote-build server',
        default=None,
        type=str
    )
    parser.add_argument(
        '-ssh_user',
        help='The user to login as on the remote-build server',
        default=None,
        type=str
    )
    parser.add_argument(
        '-remote_folder',
        help='The remote folder that stores the remote-builds',
        default=None,
        type=str
    )
    parser.add_argument(
        '-show',
        help='Print the docker command that is run',
        action='store_true'
    )
    args = parser.parse_args()

    # Maybe send the project through a tunnel, then build
    ssh_result = ssh.maybe_send(args)
    bwd = BuildWithDocker(args.proj, ssh_result)
    bwd.add_arguments(args)

    # Rebuild if necessary
    if args.build:
        img = DockerImages(args.proj)
        img.build_one(args.d)

    # Add extras if specified
    command = bwd.get_command()

    if args.show:
        print("Docker command: %s" % command)
        print("Arguments received:")
        for ivar in args.__dict__:
            print("\t{} \t\t:= {}".format(ivar, getattr(args, ivar)))

    os.system(command)
