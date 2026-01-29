from collections import deque


class CommandQueue:
    def __init__(self):
        self.queue = deque()

    def add_command(self, command):
        self.queue.append(command)

    def get_next_command(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def is_empty(self):
        return len(self.queue) == 0
    
    def delete_command(self, command_id):
        self.queue.remove(command_id)
    
    def get_all_commands(self):
        return list(self.queue)


command_queue = CommandQueue()
