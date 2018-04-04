# build-with-docker
This repo allows the user to build their Python project from within a Docker container, without having to copy said project into the container. It will simply mount the project into the container and run it from there.

It will also support specifying an SSH endpoint to which to run the project from, which will take care of zipping, sending, extracting and running, from the same command.

## Prerequisites

 * Only tested on Ubuntu 14.04 and 16.04
 * Docker https://docs.docker.com/install/
 * Nvidia-Docker [Optional] https://github.com/NVIDIA/nvidia-docker

## Installing

You can install this directly with pip by running
``` bash
sudo pip install git+https://github.com/Dammi87/build-with-docker
```

## How to use
To use this, the project __must__ have a _Dockerfiles_ folder in the root of the project. Within that folder, put in your Dockerfiles. The layout should be the following:

``` txt
+-- Project_root
|   +-- Dockerfiles
|	+--+-- some_name.Dockerfile
|   +-- bwd.json
|   +-- ...
|   +-- .
```

You can initialize the project via a command rather than doing this manually.

### Initializing a project
If you have installed this repo already, you can run this command
``` bash
bwd -proj <your_project_folder> -init
```

or if you rather run from the repository directly instead of installing it
``` bash
python3 -u bwd/bwd.py -proj <your_project_folder> -init
```

this will create a default Dockerfiles folder and build settings file for you at the ```<your_project_folder>``` folder location.

# Enable building on a remote server

First you must install the SSH client
``` bash
sudo apt-get update
sudo apt-get install openssh-server
```

Next we create an ssh directory to store the generated ssh keys
``` bash
mkdir ~/.ssh
chmod 700 ~/.ssh
cd ~/.ssh
```

Now, it's time to generate an SSH key (Set whatever filename and password you like)
``` bash
ssh-keygen -t rsa -b 4096
```

And copy the ID over to the remote server
```
ssh-copy-id remote_user@remote_ip
```

Now you should be able to use the remote_user / remote_ip settings in the build config and run your builds on a remote server!
## Authors

* **Adam Fjeldsted** - *Initial work* - [Dammi87](https://github.com/Dammi87)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
