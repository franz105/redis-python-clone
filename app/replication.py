import hashlib
import time

class Replication:
    def __init__(self, role='master'):
        self.role = role
        self.replication_id = self.generate_replication_id()
        self.replication_offset = 0

    def generate_replication_id(self):
        """Generates a pseudo-random replication ID"""
        return hashlib.sha1(str(time.time()).encode()).hexdigest()

    def get_role(self):
        return self.role

    def get_replication_id(self):
        return self.replication_id

    def get_replication_offset(self):
        return self.replication_offset