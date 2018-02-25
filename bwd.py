import argparse
import os

from src.docker_classes import BuildWithDocker, DockerImages


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
        type=bool,
    )

    args = parser.parse_args()
    print(args)
    cmd = BuildWithDocker(args.proj)
    img = DockerImages(args.proj)

    img.build_all()

    # Add extras if specified
    cmd.add_volume(args.v)
    cmd.add_port(args.p)
    cmd.add_docker_image(args.d)
    cmd.add_gpu(args.gpu)
    if args.GUI:
        cmd.add_gui()
    cmd.add_exec_script(args.s)

    os.system(cmd.get_command())
