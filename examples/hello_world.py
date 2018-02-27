import getpass

print("I am printing from within a docker container")
print("The current user is %s" % getpass.getuser())
