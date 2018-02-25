import os
import getpass
import src.custom_exceptions as ce
import src.utils as utils
GPU = ['A', 'B', 'C', 'D', 'E', 'F', 'G']


class BuildWithDocker():
    """Class use to generate a docker run command."""
    def __init__(self, project_dir):
        """Initialize class

        Parameters
        ----------
        project_dir : str
            Full path to the project directory

        """
        self._cmd = "docker run -it --rm -w %s" % project_dir
        self._has_gpu = None
        self._project_dir = project_dir

        self._volumes = None
        self._ports = None
        self._gpus = None
        self._gui = False
        self._exec = None
        self._docker_image = None

        # Add project as volume
        self.add_volume(project_dir)

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

    def add_gui(self):
        """Adds GUI support."""
        self._gui = "-e DISPLAY=$DISPLAY"
        self._gui = "%s -v %s" % (self._gui, "/tmp/.X11-unix:/tmp/.X11-unix")
        self._gui = "%s %s" % (self._gui, "--env=\"QT_X11_NO_MITSHM=1\"")

    def add_gpu(self, gpu_nr):
        """Exposes GPUs to the container."""
        if gpu_nr is None:
            return
        self._has_gpu = gpu_nr
        self._gpus = "NV=%s nvidia-" % ','.join(["%d" % g for g in gpu_nr])

    def add_exec_script(self, script_path, shell="python"):
        """Adds the execution script."""
        module = utils.get_module_path(self._project_dir, script_path)
        self._exec = "%s -m %s" % (shell, module)

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
    def __init__(self, project_dir):
        self._project_dir = project_dir
        self._docker_build = utils.get_docker_build_commands(project_dir)

    def build_all(self):
        for i_cmd in self._docker_build:
            os.system(self._docker_build[i_cmd])

    def build_one(self, docker_name):
        if docker_name in self._docker_build:
            os.system(self._docker_build[docker_name])
