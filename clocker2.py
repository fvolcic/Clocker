

# Step 1: Create the data structure that allows for easy access
#         to the clocker interface.

# design:
#           clocker will support multiple users
#           clocker will support multiple projects
#
#           clocker changer-user franklin
#               create new user named franklin?
#
#           clocker change-project <project-name>
#
#           clocker in --note "clock note"
#           clocker out --note "clock note"

from datetime import datetime
import json
from typing import Dict, List
import sys
import argparse


def get_current_timestamp():
    return str(datetime.now())

def get_datetime_from_string(dt_string):
    return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")

def get_clocker_file_location():
    return "clocker_file.json"

class CLI_engine:

    def __init__(self):

        available_commands = {"in",
                              "out",
                              "new-user",
                              "change-user",
                              "new-project",
                              "change-project",
                              "time-view"
                              }

        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            'command',
            help="The clocker command which you would like to execute.")
        arg_parser.add_argument(
            '--override',
            action='store_true',
            help="Override safety checks for certain commands."
        )
        arg_parser.add_argument(
            '-n', 
            '--name',
            help='The name which you would like to use for the command'
        )
        arg_parser.add_argument(
            '-u',
            '--user',
            help="The user to use for the specified command"
        )
        arg_parser.add_argument(
            '--note',
            default="",
            help="A note to attach to an operation."
        )
        arg_parser.add_argument(
            '--clocker-file-location',
            help="Use a custom clocker file location."
        )
        self.args = vars(arg_parser.parse_args(sys.argv[1:]))
        print(self.args) 
    def get_args(self):
        return vars(self.args)

    def run(self):
        
        clocker_filepath = get_clocker_file_location()
        if self.args["clocker_file_location"] is not None:
            clocker_filepath = self.args["clocker_file_location"]
        c_engine = ClockerEngine(clocker_filepath) 

        if self.args["command"] == "in":
            c_engine.clock_in(**self.args) 
        elif self.args["command"] == "out":
            c_engine.clock_out(**self.args)
        elif self.args["command"] == "change-user":
            c_engine.change_user(**self.args) 
        elif self.args["command"] == "change-project":
            c_engine.change_project(**self.args)
        elif self.args["command"] == "add-project":
            c_engine.add_project(**self.args) 

        print(c_engine.clocker.emit())

        c_engine.save(clocker_filepath) 
    
class ClockerEngine:

    def __init__(self, clocker_file):
        self.clocker: Clocker = Clocker(clocker_file)

    def save(self, file: str):
        with open(file, 'w') as f:
            json.dump(self.clocker.emit(), f)

    def clock_in(self, *args, **kwargs):

        time = get_current_timestamp()
        cur_user = self.clocker.state.get_current_user()
        cur_project = self.clocker.state.get_current_project()

        # Step 1: Generate the punch object.
        punch = ClockerPunch()
        punch.set_clock_direction("in")
        punch.set_note(kwargs.get("note", ""))
        punch.set_punch_time(time)

        self.clocker.data.get_user(cur_user).get_project(
            cur_project).get_punch_data().add_punch(punch)

    def clock_out(self, *args, **kwargs):

        time = get_current_timestamp()
        cur_user = self.clocker.state.get_current_user()
        cur_project = self.clocker.state.get_current_project()

        punch = ClockerPunch()
        punch.set_clock_direction("out")
        punch.set_note(kwargs("note", ""))
        punch.set_punch_time(time)

        self.clocker.data.get_user(cur_user).get_project(
            cur_project).get_punch_data().add_punch(punch)

    def change_user(self, *args, user, **kwargs):
        if user is None:
            raise Exception("Please specify a user.")
        self.clocker.state.set_current_user(user)

    def change_project(self, *args, name, **kwargs):
        if name is None:
            raise Exception("Please specify a project.")
        self.clocker.state.set_current_project(name)

    def add_project(self, *args, name, override, **kwargs):
        if name is None or len(name) == 0:
            raise Exception("Please specify a project.")
        self.clocker.data.get_user(self.clocker.state.get_current_user()).add_project(ClockerProject(), name, override)

class ClockerPunch:

    def __init__(self, punch_data: Dict = None):
        if punch_data is None:
            self.clock_direction = None
            self.punch_time = None
            self.note = None
        else:
            self.clock_direction = punch_data["direction"]
            self.punch_time = punch_data["punch_time"]
            self.note = punch_data.get("note", "")

    def get_clock_direction(self, direction: str) -> str:
        return self.clock_direction

    def set_clock_direction(self, direction: str):
        if direction not in {"in", "out"}:
            raise Exception(f"Invalid clock direction: {direction}")
        self.clock_direction = direction

    def get_punch_time(self) -> str:
        return self.punch_time

    def set_punch_time(self, punch_time: str):
        self.punch_time = punch_time

    def get_note(self) -> str:
        return self.note

    def set_note(self, note: str):
        self.note = note

    def emit(self):
        return {
            "direction": self.clock_direction,
            "punch_time": self.punch_time,
            "note": self.note
        }


class ClockerPunchData:

    def __init__(self, punch_data: List = None):
        if punch_data is None:
            self.punches = []

        self.punches = [ClockerPunch(punch) for punch in punch_data]

    def add_punch(self, punch: ClockerPunch):

        if len(self.punches) and punch.get_punch_time() < self.punches[-1].get_punch_time():
            raise Exception(
                "Invalid punch time. Cannot punch before previous punch.")

        self.punches.append(punch)

    def get_punch_data(self) -> List[ClockerPunch]:
        return self.punches

    def get_most_recent_punch(self) -> ClockerPunch:
        return self.punches[-1]

    def get_last_n_punches(self, n: int) -> List[ClockerPunch]:
        if len(self.punches) < n:
            n = len(self.punches)
        return self.punches[len(self.punches)-n:]

    def emit(self):
        return [punch.emit() for punch in self.punches]


class ClockerProject:

    def __init__(self, project_data=None):
        if project_data is None:
            self.punch_data = ClockerPunchData([])
        else:
            self.punch_data = ClockerPunchData(project_data["punch_data"])

    def get_punch_data(self) -> ClockerPunchData:
        return self.punch_data

    def emit(self):
        return {
            "punch_data": self.punch_data.emit()
        }


class ClockerUser:

    def __init__(self, user_data={}):
        self.projects = {}
        for project in user_data["projects"]:
            self.projects[project] = ClockerProject(
                user_data["projects"][project])

    def get_project(self, project_name: str) -> ClockerProject:
        if project_name not in self.projects:
            raise Exception(
                f"Error: project {project_name} not found... Are you logged in with the correct user?")
        return self.projects[project_name]

    def add_project(self, project, project_name: str, override: bool = False):
        if project_name in self.projects and not override:
            raise Exception(
                f"Error: Project {project_name} already exists.. To overwrite, rerun command with '--override' flag")
        self.projects[project_name] = project

    def get_projects(self) -> List[ClockerProject]:
        return self.projects

    def emit(self):
        return {
            "projects": {
                p[0]: p[1].emit()
                for p in self.projects.items()
            }
        }


class ClockerData:

    def __init__(self, data={}):

        self.users = {}
        for user in data:
            self.users[user] = ClockerUser(data[user])

    def emit(self):
        return {f"{user}": self.users[user].emit() for user in self.users}

    def get_user(self, user_name: str) -> ClockerUser:
        if user_name not in self.users:
            raise Exception("Error: user not found.")
        return self.users[user_name]

    def add_user(self, user, user_name: str, override=False):
        if user_name in self.users and not override:
            raise Exception(
                "Error: cannot add user. User already exists. To override user, add the '--override' flag")
        self.users[user_name] = user

    def get_users(self) -> Dict[str, ClockerUser]:
        return self.users


class Clocker:

    def __init__(self, clocker_file):

        with open(clocker_file, 'r') as f:
            self.clocker_json_raw = json.load(f)

        self.data = ClockerData(self.clocker_json_raw['clocker-data'])
        self.settings = ClockerSettings(
            self.clocker_json_raw['clocker-settings'])
        self.state = ClockerState(self.clocker_json_raw['clocker-state'])

    def emit(self):
        return {
            "clocker-data": self.data.emit(),
            "clocker-settings": self.settings.emit(),
            "clocker-state": self.state.emit()
        }


class ClockerSettings:

    def __init__(self, settings):
        self.settings_data = settings

    def emit(self):
        return {}

class ClockerUserState:

    def __init__(self, user_state):
        self.current_project = user_state["project"]

    def get_current_project(self) -> str:
        return self.current_project
    
    def set_current_project(self, project_name: str):
        self.current_project = project_name

    def emit(self):
        return {
            "project":self.current_project
        }

class ClockerState:

    def __init__(self, state):
        
        self.current_user = state['user']

        self.user_state: Dict[str, ClockerUserState] = {} 
        for user in state['user-state']:
            self.user_state[user] = ClockerUserState(state['user-state'][user])

    def get_current_project(self) -> str:
        return self.user_state[self.current_user()].get_current_project() 

    def get_current_user(self) -> str:
        return self.current_user

    def set_current_project(self, project_name: str):
        self.user_state[self.current_user()].set_current_project(project_name)

    def set_current_user(self, user_name: str):
        self.current_user = user_name

    def emit(self):
        return self.state_data

class ArgParse:

    def __init__(self, args: List[str]):
        self.args = args


def main():
    cli_engine = CLI_engine()
    cli_engine.run() 

if __name__ == "__main__":
    main()
