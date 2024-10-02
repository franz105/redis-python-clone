import sys

def get_port():
    port = 6379
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i+1])
            break
    return port

def get_role():
    """Determines if the server is running as master or slave"""
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--replicaof" and i + 1 < len(sys.argv):
            return 'slave'
    return 'master'

def get_replica_host_port():
    """Get master host and port if running as a replica (slave)"""
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--replicaof" and i + 1 < len(sys.argv):
            host_port = sys.argv[i+1].split()
            return host_port[0], int(host_port[1])
    return None, None