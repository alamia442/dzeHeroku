import subprocess, os
print("import docker")
print("Starting Docker Services.......")
print("Starting Docker Services.......")


class Config(object):
    # your repo name
    RP_NAME = os.environ.get("RP_NAME", "")
    # YOUR github username
    UNAME = os.environ.get("UNAME", "")
    # git hub access token
    GTOKEN = os.environ.get("GTOKEN", None)

#Don't touch this
RP_NAME = Config.RP_NAME
UNAME = Config.UNAME
GTOKEN = Config.GTOKEN


print("Please wait until docker build completes......")


if GTOKEN is None:
    print("Please wait building docker....")
    print("GitHub token not provided,provide github token if your repo is private")
    os.system('cd /app && rm -rf * && git clone https://github.com/$UNAME/$RP_NAME .')
else:
    print("Please wait building docker....")
    os.system('cd /app && rm -rf * && git clone https://$GTOKEN@github.com/$UNAME/$RP_NAME .')
print("Please wait building docker done....")
print("Please wait building docker done....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
print("Please wait starting docker images....")
#os.system("cd /app && chmod +x *.sh && bash aria2.sh && bash start.sh")
#os.system("cd /app\nchmod +x *.sh\nbash start.sh")

subprocess.run(['cd /app && chmod +x *.sh && bash start.sh'], shell=True)
