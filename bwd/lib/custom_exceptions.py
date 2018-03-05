class DockerFolderMissing(Exception):
    def __init__(self, message=None):
        if message is None:
            msg = "Make sure you have a folder called Dockerfiles in the root of the project"
            Exception.__init__(msg)


class DockerFilesMissing(Exception):
    def __init__(self, message=None):
        if message is None:
            msg = "Could not find a .Dockerfile in the specified folder"
            Exception.__init__(msg)


class FileMissing(Exception):
    def __init__(self, message=None):
        if message is None:
            msg = "Missing file"
            Exception.__init__(msg)


class ExecutionScriptMissing(Exception):
    def __init__(self, message=None):
        if message is None:
            msg = "You need to specify what script to execute"
            Exception.__init__(msg)


class NoDockerfileSpecified(Exception):
    def __init__(self, message=None):
        if message is None:
            msg = "You need to specify which Dockerfile to use as image"
            Exception.__init__(msg)
