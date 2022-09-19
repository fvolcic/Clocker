

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

from abc import ABC
from calendar import c
import json
from msilib.schema import Error
from typing import Dict, List


class Clocker:

    def Clocker(self, clocker_file):

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


class ClockerData:

    def ClockerData(self, data={}):

        self.users = {}
        for user in data:
            self.users[user] = ClockerUser[self.users[user]]

    def emit(self):
        return {f"{user}": self.users[user].emit() for user in self.users}


class ClockerUser:

    def ClockerUser(self, user_data={}):
        self.projects = {}
        for project in user_data["projects"]:
            self.projects[project] = ClockerProject(
                user_data["projects"][project])


class ClockerProject:

    def ClockerProject(self, project_data=None):
        if project_data is None:
            self.punch_data = ClockerPunchData(project_data["punch_data"])
        self.punch_data = ClockerPunchData(project_data["punch_data"])

    def emit(self):
        return {
            "punch_data": self.punch_data.emit()
        }


class ClockerPunchData:

    def ClockerPunchData(self, punch_data: List = None):
        if punch_data is None:
            self.punches = []

        self.punches = [ClockerPunch(punch) for punch in punch_data]

    def add_punch(self, punch_direction: str, time, note):
        new_punch = ClockerPunch()

        new_punch.set_clock_direction(punch_direction)
        new_punch.set_punch_time(time)
        new_punch.set_note(note)

        if len(self.punches) and new_punch.get_punch_time() < self.punches[-1].get_punch_time():
            raise Exception(
                "Invalid punch time. Cannot punch before previous punch.")

        self.punches.append(new_punch)

    def emit(self):
        return [punch.emit() for punch in self.punches]


class ClockerPunch:

    def ClockerPunch(self, punch_data: Dict = None):
        if punch_data is None:
            self.clock_direction = None
            self.punch_time = None
            self.note = None
        self.clock_direction = punch_data["direction"]
        self.punch_time = punch_data["punch_time"]
        self.note = punch_data.get("note", "")

    def get_clock_direction(self, direction: str):
        return self.clock_direction

    def set_clock_direction(self, direction: str):
        if direction not in {"in", "out"}:
            raise Exception(f"Invalid clock direction: {direction}")
        self.clock_direction = direction

    def get_punch_time(self):
        return self.punch_time

    def set_punch_time(self, punch_time):
        self.punch_time = punch_time

    def get_note(self):
        return self.note

    def set_note(self, note: str):
        self.note = note

    def emit(self):
        return {
            "direction": self.clock_direction,
            "punch_time": self.punch_time,
            "note": self.note
        }


class ClockerSettings:

    def ClockerSettings(self, settings):
        self.settings_data = settings

    def emit(self):
        return {}


class ClockerState:

    def ClockerState(self, state):
        self.state_data = state

    def get_current_project(self) -> str:
        return self.state_data["user-state"][self.get_current_user()]["project"]

    def get_current_user(self) -> str:
        return self.state_data["data"]

    def set_current_project(self, project_name: str):
        self.state_data["user-state"][self.get_current_user()
                                      ]["project"] = project_name

    def set_current_user(self, user_name: str):
        self.state_data["user"] = user_name

    def emit(self):
        return self.state_data
