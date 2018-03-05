import os
import sys


from . import custom_exceptions as ce
from .ssh_utils import append_ssh


def run_command(cmd, debug=False):
    """Run a shell command and return output
    
    Parameters
    ----------
    cmd : str
        Shell command to run
    debug : bool, optional
        Print command and response
    
    Returns
    -------
    str
        Raw response from terminal
    """
    response = os.popen(cmd).read()
    if debug:
        print("Running: %s" % cmd)
        print("Response: \n\n%s" % response)

    return response


def listdir(directory, ssh_user=None, ssh_ip=None):
    """Lists files/folders in a directory, both locally and remote"""
    if ssh_ip is None:
        return os.listdir(directory)
    else:
        return run_command("ssh %s@%s ls %s" % (ssh_user, ssh_ip, directory)).split('\n')


def get_as_list(parameter):
    """Make sure 'parameter' is a list."""
    if not isinstance(parameter, list):
        return [parameter]
    return parameter


def has_dockerfiles_folder(project_dir, ssh_user=None, ssh_ip=None):
    """Check if project has 'Dockerfiles' folder, return location if found.
    
    Parameters
    ----------
    project_dir : str
        Full path to the project directory
    ssh_user : None, optional
        User name of the remote-host machine
    ssh_ip : None, optional
        IP address of the remote-host machine
    
    Returns
    -------
    str
        Location of Dockerfiles folder
    
    Raises
    ------
    ce.DockerFolderMissing
        Description
    """
    all_folders = listdir(project_dir, ssh_user, ssh_ip)
    docker_folder = os.path.join(project_dir, 'Dockerfiles')
    if 'Dockerfiles' not in all_folders:
        raise ce.DockerFolderMissing()
    return docker_folder



def get_docker_build_commands(project_dir, ssh_user=None, ssh_ip=None):
    """Generate docker build commands for the project.
    
    Parameters
    ----------
    project_dir : str
        Full path to the project directory
    ssh_user : None, optional
        User name of the remote-host machine
    ssh_ip : None, optional
        IP address of the remote-host machine
    
    Returns
    -------
    dict
        Dictionary where the key is the name of the docker-file
        and the value is the corresponding build command
    
    Raises
    ------
    ce.DockerFilesMissing
        Description
    
    """


    # Make sure the path exsits
    docker_folder = has_dockerfiles_folder(project_dir, ssh_user, ssh_ip)

    # Get all docker files here
    all_files = listdir(docker_folder, ssh_user, ssh_ip)

    if len(all_files) == 0:
        raise ce.DockerFilesMissing()

    # Create the command
    project_name = os.path.basename(project_dir)
    all_cmd = []
    all_images = []
    for i_file in all_files:
        docker_tag = i_file.replace('.Dockerfile', '')
        full_path = os.path.join(docker_folder, i_file)
        cmd = "docker build -t %s:%s -f %s %s" \
            % (project_name, docker_tag, full_path, docker_folder)

        if ssh_user is not None:
            cmd = append_ssh(ssh_user, ssh_ip, cmd)
        all_cmd.append(cmd)
        all_images.append(docker_tag)

    return dict(zip(all_images, all_cmd))


def get_module_path(project_dir, script_path):
    """Extracts the module path from the two paths.
    
    Parameters
    ----------
    project_dir : str
        Project root path
    script_path : str
        Script to run
    
    Returns
    -------
    str
        The module relative path to the script
    
    """
    left_over = os.path.abspath(script_path).replace(project_dir, '')
    if left_over[-1] == '/':
        left_over.pop(-1)
    left_over = left_over.replace('.py', '')
    module = left_over.replace('/', '.')

    # If top module, remove first dot
    if '.' == module[0]:
        module = module[1:]

    return module


def is_file_in_project(project, dockerfile, ssh_user=None, ssh_ip=None):
    """Check if specified docker file is in project.
    
    Parameters
    ----------
    project_dir : str
        Full path to the project directory
    dockerfile: str
        The name of the dockerfile we are looking for
    ssh_user : None, optional
        User name of the remote-host machine
    ssh_ip : None, optional
        IP address of the remote-host machine
    
    Returns
    -------
    boolean
        True if dockerfile exists
    """
    docker_folder = has_dockerfiles_folder(project, ssh_user, ssh_ip)

    all_files = os.listdir(docker_folder)
    all_files = [file.split('.')[0] for file in all_files]
    dockerfile = dockerfile.replace('.Dockerfile', '')

    return dockerfile in all_files


all_colors = {
    'RED' : "\033[1;31m" ,
    'BLUE' : "\033[1;34m",
    'CYAN' : "\033[1;36m",
    'GREEN' : "\033[0;32m",
    'WHITE' : "\033[0;37m",
    'RESET' : "\033[0;0m",
    'BOLD' : "\033[;1m",
    'REVERSE' : "\033[;7m"
}


def set_color(color):
    sys.stdout.write(all_colors[color])
    sys.stdout.flush()