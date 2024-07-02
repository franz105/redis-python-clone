import sys

def get_port():
    port = 6379
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i+1])
            break
    return port
