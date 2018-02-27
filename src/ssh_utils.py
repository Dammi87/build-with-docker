import zipfile
import subprocess
import time
import os
import getpass


def zipdir(path, zip_path, ignore_paths=None):
    """Creates a zip file of the folder at zip_path.

    Parameters
    ----------
    path : str
        Folder that should get zipped
    zip_path : str
        Destination of this zip file
    ignore_paths : None, optional
        List of folders to ignore
    """
    # Create ziph
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        zip_this = True
        for file in files:
            if ignore_paths:
                for ign_path in ignore_paths:
                    if ign_path in root:
                        zip_this = False
                        break
            if zip_this:
                file_path = os.path.join(root, file)
                if file_path != zip_path:
                    zipf.write(file_path, os.path.relpath(file_path, path))
            else:
                break

    # Close zip
    zipf.close()


def zip_send_and_unzip(ssh_user, ssh_ip, proj_root, remote_folder, ignore_paths=None):
    """Zip the project, send it and unzip at remote location.

    Parameters
    ----------
    ssh_user : str
        The user to ssh to
    ssh_ip : str
        Ip of the workstation
    proj_root : str
        The root of the project that is running
    remote_folder : str
        Folder path to create (On remote location)
    ignore_paths : None, optional
        Paths to ignore in project root
    """
    # Zip the file
    tmp_build = time.strftime("%Y_%m_%d_%H%M%S")
    zip_path = os.path.join(proj_root, "%s.zip" % tmp_build)
    zipdir(proj_root, zip_path, ignore_paths=ignore_paths)

    # Create the zip folder on receiving end
    remote_zip_folder = os.path.join(remote_folder, 'zip_files')
    command = "ssh %s@%s mkdir -p %s" % (ssh_user, ssh_ip, remote_zip_folder)
    run_system_command(command)

    # Send the zip file
    command = "scp %s %s@%s:%s" % (zip_path, ssh_user, ssh_ip, remote_zip_folder)
    run_system_command(command)

    # Delete the local zipfile
    command = "rm %s" % zip_path
    run_system_command(command)

    # Unzip the file at remote location
    tmp_build = time.strftime("%Y_%m_%d_%H%M%S")
    tmp_path = os.path.join(remote_folder, tmp_build)
    remote_zip = os.path.join(remote_zip_folder, "%s.zip" % tmp_build)
    create_cmd = "ssh %s@%s mkdir -p %s" % (ssh_user, ssh_ip, tmp_path)
    unzip_cmd = "ssh %s@%s unzip %s -d %s" % (ssh_user, ssh_ip, remote_zip, tmp_path)
    run_system_command(create_cmd)
    run_system_command(unzip_cmd)

    return tmp_path


def create_remote_dir(ssh_user, ssh_ip, proj_root, remote_folder):
    """Create a folder on the remote host.

    Parameters
    ----------
    ssh_user : str
        The user to ssh to
    ssh_ip : str
        Ip of the workstation
    proj_root : str
        Path of the project
    remote_folder : str
        Folder path to create (On remote location)

    Returns
    -------
    TYPE
        Description
    """
    # Append the user to the remote dir
    remote_folder = os.path.join(
        remote_folder,
        getpass.getuser(),
        os.path.basename(proj_root)
    )
    cmd = "ssh %s@%s mkdir -p %s" % (ssh_user, ssh_ip, remote_folder)
    run_system_command(cmd)

    return remote_folder


def run_system_command(command):
    """Run command in a shell process."""
    result = subprocess.check_output(command, shell=True)
    return result


def maybe_send(args):
    """Check the values of args and send the project if desired.

    Parameters
    ----------
    args : argparse
        Parsed argparse dict from bwd.py

    """
    check_list = [
        'ssh_ip',
        'ssh_user',
        'remote_folder'
    ]

    for item in check_list:
        if getattr(args, item) is None:
            print(item, getattr(args, item))
            raise
            return None

    # Begin by creating the end remote folder
    remote_folder = create_remote_dir(
        args.ssh_user,
        args.ssh_ip,
        args.proj,
        args.remote_folder)

    # Send it over
    zip_send_and_unzip(
        args.ssh_user,
        args.ssh_ip,
        args.proj,
        remote_folder,
        ignore_paths=None)

    return remote_folder
