#!/usr/bin/python3

from datetime import datetime, timedelta
import json
import os
import sys
import shutil

def main(option): 
    if option == "help":
        clock_help()
        exit(0)
    if option != 'init':
        check_initialization()
    if option == "in":
        clock_in()
    elif option == "out":
        clock_out()
    elif option == "init":
        clock_init()
    elif option == "timesheet":
        clock_timesheet()
    elif option == "reinit":
        clock_reinit()
    elif option == "uninit":
        clock_uninit()
def clock_in():
    clock_file = ClockFile()
    clock_file.punch_in() 
    clock_file.save()

def clock_out():
    clock_file = ClockFile()
    clock_file.punch_out() 
    clock_file.save()

def clock_uninit():
    shutil.rmtree(os.path.expanduser("~/.clocker"))

def clock_help():
    print("Welcome to clocker!")
    print("Clocker is currently under development, so its use is limited.")
    print("\nClocker is a command line clock utility allowing easy clocking in and out for a user.")
    print("Functions: ")
    print("clocker init - initialize clocker")
    print("clocker in - clock in")
    print("clocker out - clocker out")
    print("clocker reinit - reinit the clocker file.")

def clock_init():
    """Initialize clocker for the given user."""
    if os.path.exists(os.path.expanduser("~/.clocker/clocker_file.json")):
        print("Clocker has already been initialized. Run 'clocker reset -hard' to reinitialize clocker.")
    else:
        os.makedirs(os.path.expanduser("~/.clocker"), exist_ok=True)
        with open(os.path.expanduser("~/.clocker/clocker_file.json"), 'w') as f:
            f.write(json.dumps({
                "clocked_hours":[]
            }))

def clock_timesheet():
    pass

def clock_reinit():
    shutil.rmtree(os.path.expanduser("~/.clocker"))
    clock_init() 

def check_initialization():
    if not os.path.exists(os.path.expanduser("~/.clocker/clocker_file.json")):
        print("Clocker has not been initialized. Run 'clocker init' before using clocker.")
        exit(1) 

def get_dt(dt_string):
    return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")

class ClockFile:

    def __init__(self):
        with open(os.path.expanduser("~/.clocker/clocker_file.json"), 'r') as f:
            self.clocker_json = json.load(f) 

    def _gen_punch_stamp(self, time, in_out):
        return {"direction":in_out, "time":str(time)}

    def _generate_punch(self, in_out):
        if in_out == "in": 
            if not len(self.clocker_json["clocked_hours"]):
                self.clocker_json["clocked_hours"].append(self._gen_punch_stamp(str(datetime.now()), "in"))
            elif self.clocker_json["clocked_hours"][-1]["direction"] == "in":
                return -1, "Error: already punched in."
            else:
                self.clocker_json["clocked_hours"].append(self._gen_punch_stamp(str(datetime.now()), "in"))
                print("Punched in at: " + self.clocker_json["clocked_hours"][-1]["time"])
        if in_out == "out":
            if not (len(self.clocker_json["clocked_hours"])):
                return -1, "Error: not currently punched in."
            elif self.clocker_json["clocked_hours"][-1]["direction"] == "out":
                return -1, "Error: not currently punched in."
            else:
                self.clocker_json["clocked_hours"].append(self._gen_punch_stamp(str(datetime.now()), "out"))
                time_in = get_dt(self.clocker_json["clocked_hours"][-2]["time"])
                time_out = get_dt(self.clocker_json["clocked_hours"][-1]["time"])
                shift_duration = time_out - time_in
                print(f"Clocked out. Shift duration: {shift_duration}")
                


    def punch_in(self):
        result = self._generate_punch("in")
        if result:
            print(result[1])
            return -1

    def punch_out(self):
        result = self._generate_punch("out")
        if result:
            print(result[1])
            return -1

    def timesheet(self, start_time, end_time):
        pass

    def compute_time(self, start_time, end_time):
        pass

    def last_shift(self):
        pass

    def last_N_shifts(self, N):
        pass

    def save(self):
        with open(os.path.expanduser("~/.clocker/clocker_file.json"), 'w') as f:
            f.write(json.dumps(self.clocker_json))

if __name__ == "__main__":
    valid_args = {"in", "out", "init", "reinit", "help"}
    if len(sys.argv) < 2:
        print("Error: please specify an action.")
        exit(1)
    if not sys.argv[1] in valid_args:
        exit(1) 
    main(sys.argv[1])