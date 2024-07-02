import sys

def get_port():
    port = 6379
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i+1])
            break
    return port

def get_replication():
    result = "" # "master" if empty
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--replicaof" and i + 1 < len(sys.argv):
            result = sys.argv[i+1]
            break
    return result
