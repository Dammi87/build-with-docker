# build-with-docker
This repo allows the user to build their Python project from within a Docker container, without having to copy said project into the container. It will simply mount the project into the container and run it from there.

It will also support specifying an SSH endpoint to which to run the project from, which will take care of zipping, sending, extracting and running, from the same command.

### Prerequisites

 * Docker https://docs.docker.com/install/
 * Nvidia-Docker [Optional] https://github.com/NVIDIA/nvidia-docker

To use this for a python project, the project __must__ have a _Dockerfiles_ folder in the root of the project. Within that folder, put in your Dockerfiles. If you are interested in using a GPU as well, 

### Installing

The project is currently not pip-installable. But if you are interested in trying this out in alpha-mode perform the following steps

  1. git clone https://github.com/Dammi87/build-with-docker
  2. cd build-with-docker
  3. python -m test.hello-world

## Authors

* **Adam Fjeldsted** - *Initial work* - [Dammi87](https://github.com/Dammi87)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
