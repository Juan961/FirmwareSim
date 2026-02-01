import json
from collections import deque


class CommandQueue:
    def __init__(self):
        self.commands = self.__read_local_commands()
        self.commands_id = deque()

    def is_empty(self):
        return len(self.commands) == 0

    def get_all_commands(self):
        return list(self.commands)

    def __read_local_commands(self):
        try:
            with open("./remote/local_commands.json", "r") as f:
                data = json.load(f)
                return data.get("commands", [])

        except FileNotFoundError:
            pass

        except Exception as e:
            print(f"Error reading local commands: {e}")

    def __update_local_commands(self):
        try:
            with open("./remote/local_commands.json", "w") as f:
                data = {"commands": self.commands}
                json.dump(data, f)

        except FileNotFoundError:
            pass

        except Exception as e:
            print(f"Error reading local commands: {e}")

    def add_command(self, command):
        self.commands.append(command)
        self.__update_local_commands()

    def get_next_command(self):
        if self.commands:
            item = self.commands.pop(0)

            self.__update_local_commands()

            self.__update_current_command(item)

            return item 

        return None

    def priorized_command_available(self, current_command):
        return False # TODO: Implement prioritization logic

        if not self.commands:
            return False

        next_command = self.commands[0]
        if next_command != current_command:
            return True

        return False

    def __update_current_command(self, command):
        try:
            with open("./remote/command_status.json", "w") as f:
                json.dump(command, f)

        except FileNotFoundError:
            pass

        except Exception as e:
            print(f"Error reading local commands: {e}")
    
    def __get_current_command(self):
        try:
            with open("./remote/command_status.json", "r") as f:
                data = json.load(f)
                return data

        except FileNotFoundError:
            pass

        except Exception as e:
            print(f"Error reading local commands: {e}")

    def mark_command_completed(self, command_id):
        data = self.__get_current_command()
        if data["message_id"] != command_id:
            print("Command ID mismatch on complete")
            return
        data["status"] = "COMPLETED"
        self.__update_current_command(data)

    def mark_command_failed(self, command_id):
        data = self.__get_current_command()
        if data["message_id"] != command_id:
            print("Command ID mismatch on fail")
            return
        data["status"] = "FAILED"
        self.__update_current_command(data)

    def mark_command_in_progress(self, command_id):
        data = self.__get_current_command()
        if data["message_id"] != command_id:
            print("Command ID mismatch on in-progress")
            return
        data["status"] = "IN_PROGRESS"
        self.__update_current_command(data)

commands_queue = CommandQueue()
