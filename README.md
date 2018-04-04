# build-with-docker
This repo allows the user to build their Python project from within a Docker container, without having to copy said project into the container. It will simply mount the project into the container and run it from there.

It will also support specifying an SSH endpoint to which to run the project from, which will take care of zipping, sending, extracting and running, from the same command.

## Prerequisites

 * Docker https://docs.docker.com/install/
 * Nvidia-Docker [Optional] https://github.com/NVIDIA/nvidia-docker

To use this for a python project, the project __must__ have a _Dockerfiles_ folder in the root of the project. Within that folder, put in your Dockerfiles. The layout should be the following:

``` txt
+-- Project_root
|   +-- Dockerfiles
|	+--+-- some_name.Dockerfile
|   +-- bwd.json
|   +-- ...
|   +-- .
```
## Installing

You can install this directly with pip by running
``` bash
sudo pip install git+https://github.com/Dammi87/build-with-docker
```

## How to use
Similar to the structure of this repo, you need to have a basic structure in your project root to be able to use this. ..



## Authors

* **Adam Fjeldsted** - *Initial work* - [Dammi87](https://github.com/Dammi87)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
