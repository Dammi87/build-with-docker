import os
import custom_exceptions as ce


def get_as_list(parameter):
    if not isinstance(parameter, list):
        return [parameter]
    return parameter


def get_docker_build_commands(project_dir):
    """Generate docker build commands for the project.

    Parameters
    ----------
    project_dir : str
        Full path to the project directory

    """
    # Make sure the path exsits
    docker_folder = os.path.join(project_dir, 'Dockerfiles')
    if not os.path.exists(docker_folder):
        raise ce.DockerFolderMissing()

    # Get all docker files here
    all_files = os.listdir(docker_folder)

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
        all_cmd.append(cmd)
        all_images.append(docker_tag)

    return dict(zip(all_images, all_cmd))


def get_module_path(project_dir, script_path):
    """Extracts the module path from the two paths.

    Parameters
    ----------
    project_dir : str
    script_path : str

    """
    left_over = script_path.replace(project_dir, '')
    if left_over[-1] == '/':
        left_over.pop(-1)
    left_over = left_over.replace('.py', '')
    module = left_over.replace('/', '.')

    # If top module, remove first dot
    if '.' == module[0]:
        module = module[1:]

    return module


def is_file_in_project(project, dockerfile):
    """Check if specified docker file is in project."""
    docker_folder = os.path.join(project, 'Dockerfiles')
    if not os.path.exists(docker_folder):
        raise ce.DockerFolderMissing()

    all_files = os.listdir(docker_folder)
    all_files = [file.split('.')[0] for file in all_files]
    dockerfile = dockerfile.replace('.Dockerfile', '')

    return dockerfile in all_files
