import os
import getpass
from . import custom_exceptions as ce
from . import utils as utils
GPU = ['A', 'B', 'C', 'D', 'E', 'F', 'G']


class BuildWithDocker():
    """Class use to generate a docker run command."""
    def __init__(self, project_dir, remote_folder=None):
        """Initialize class

        Parameters
        ----------
        project_dir : str
            Full path to the project directory
        remote_folder : str, optional
            States the the folder this project was copied to
            on the remote location.

        """
        self._cmd = "docker run -t --rm -w %s" % project_dir
        self._has_gpu = None
        self._project_dir = project_dir

        self._volumes = None
        self._ports = None
        self._gpus = None
        self._gui = False
        self._exec = None
        self._docker_image = None
        self._custom_cmd = None

        # Add project as volume. If this is a ssh build, then we
        # want to mount the remote folder into the docker container
        # instead, all other mount points should still be the same.
        if remote_folder is None:
            self.add_volume(project_dir)
        else:
            self.add_custom_command("-v %s:%s" % (remote_folder, project_dir))

    def add_custom_command(self, cmd):
        if cmd is None:
            return
        if self._custom_cmd is None:
            self._custom_cmd = ""
        for i_cmd in utils.get_as_list(cmd):
            self._custom_cmd = "%s %s" % \
                (self._custom_cmd, i_cmd)

    def add_volume(self, volume):
        if volume is None:
            return
        if self._volumes is None:
            self._volumes = ""
        for vol in utils.get_as_list(volume):
            self._volumes = "%s -v %s:%s" % \
                (self._volumes, vol, vol)

    def add_port(self, port):
        if port is None:
            return
        if self._ports is None:
            self._ports = ""
        for p in utils.get_as_list(port):
            self._ports = "%s -p %s" % \
                (self._ports, p)

    def add_gui(self, gui_on):
        """Adds GUI support."""
        if gui_on is None or not gui_on:
            return
        self._gui = "-e DISPLAY=$DISPLAY"
        self._gui = "%s -v %s" % (self._gui, "/tmp/.X11-unix:/tmp/.X11-unix")
        self._gui = "%s %s" % (self._gui, "--env=\"QT_X11_NO_MITSHM=1\"")

    def add_gpu(self, gpu_nr):
        """Exposes GPUs to the container."""
        if gpu_nr is None:
            return
        self._has_gpu = gpu_nr
        self._gpus = "NV=%s nvidia-" % ','.join(["%d" % g for g in gpu_nr])

    def add_exec_script(self, script_path, run_as_module=False, shell="python -m"):
        """Adds the execution script."""
        if run_as_module:
            suffix = utils.get_module_path(self._project_dir, script_path)
        else:
            suffix = os.path.relpath(script_path, self._project_dir)
        self._exec = "%s %s" % (shell, suffix)

    def add_docker_image(self, docker_file):
        """Adds the desired docker image to run from."""
        if not utils.is_file_in_project(self._project_dir, docker_file):
            raise ce.FileMissing("Specified dockerfile not found.")

        proj_name = os.path.basename(self._project_dir).lower()
        tag_name = os.path.basename(docker_file).replace('.Dockerfile', '').lower()
        ctr_name = '%s_%s' % (getpass.getuser(), proj_name)
        if self._has_gpu:
            ctr_name = "GPU_%s_%s" (GPU[self._has_gpu], ctr_name)
        self._docker_image = "--name %s %s:%s" % (ctr_name, proj_name, tag_name)

    def add_arguments(self, args):
        self.add_volume(args.v)
        self.add_port(args.p)
        self.add_docker_image(args.d)
        self.add_gpu(args.gpu)
        self.add_gui(args.GUI)
        self.add_custom_command(args.custom_cmd)
        self.add_exec_script(args.s, args.run_as_module, shell=args.build_cmd)

    def get_command(self):
        """Returns the complete docker command."""
        if self._exec is None:
            raise ce.ExecutionScriptMissing()

        if self._docker_image is None:
            raise ce.NoDockerfileSpecified()

        add_order = [
            self._volumes,
            self._ports,
            self._gui,
            self._custom_cmd,
            self._docker_image,
            self._exec
        ]

        for add in add_order:
            self.append_command(add)

        # Special case for gpu
        if self._gpus:
            self._cmd = "%s%s" % (self._gpus, self._cmd)

        return self._cmd

    def append_command(self, cmd):
        if cmd is None:
            return
        if cmd is "":
            return
        if not cmd:
            return

        self._cmd = "%s %s" % (self._cmd, cmd)


class DockerImages():
    def __init__(self, project_dir, ssh_user=None, ssh_ip=None):
        self._project_dir = project_dir
        self._docker_build = utils.get_docker_build_commands(project_dir, ssh_user, ssh_ip)

    def build_all(self):
        for ibuild in self._docker_build:
            utils.run_command(ibuild)

    def build_one(self, docker_name):
        utils.run_command(self._docker_build[docker_name])

