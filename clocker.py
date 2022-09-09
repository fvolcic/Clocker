#!/usr/bin/python3

import json
import click
import os

@click.command()
@click.argument('option')
def main(option): 
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

def clock_in():
    pass

def clock_out():
    pass

def clock_init():
    if os.path.exists("/var/lib/clocker/clocker_file.json"):
        print("Clocker has already been initialized. Please run clocker re-init to reinitialize clocker.")
    else:
        os.makedirs("/var/lib/clocker")
        with open("/var/lib/clocker/clocker_file.json") as f:
            f.write(json.dumps({}))

def clock_timesheet():
    pass

def clock_reinit():
    pass

class ClockFile:

    def __init__(self):
        self.clocker_json = {} 

    def punch_in(self):
        pass

    def punch_out(self):
        pass

    def timesheet(self, start_time, end_time):
        pass

    def compute_time(self, start_time, end_time):
        pass

    def last_shift(self):
        pass

    def last_N_shifts(self, N):
        pass

    def save(self):
        pass

if __name__ == "__main__":
    main()