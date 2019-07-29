"""
:: NAME:           dbs.py
::
:: FUNCTION:       To generate temporary dbs output folder
::
:: PROJECT:        Daily Build System
::
:: DEVELOPED BY :  Abhishek Srivastava
::
"""


import csv
import os
import re
import sys
import time
from getopt import getopt, GetoptError


sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from buildparser import BuildParser
except ImportError:
    from DailyBuildSystem.buildparser import BuildParser


class Logger:

    def __init__(self):
        self.__timestamp_date = time.strftime("%Y-%m-%d")
        self.__timestamp_time = time.strftime("%H:%M:%S")

    def log_build_status(self, dbs_log_file, type_value, val_of_args = None, build_status=None):
        is_new_file = False

        if not os.path.exists(dbs_log_file):
            is_new_file = True

        list_of_args = [""] * 8
        for argument in range(len(val_of_args)):
            val = val_of_args[argument]
            list_of_args[argument] = val

        output_file = open(dbs_log_file, 'a+', newline='')
        writer = csv.writer(output_file)

        if is_new_file:
            writer.writerow(['Date', 'Time', 'Built_Type', 'Result'])

        row = [self.__timestamp_date, self.__timestamp_time, type_value, build_status]
        writer.writerow(row)

        output_file.close()
        return True


OPT_HELP = "-h"
OPT_OUTPUT = "-o"
OPT_BUILD_TYPE = "-t"
OPT_BUILD_RESULT = "-r"

BUILD_TYPE_PERIODIC = "P"
BUILD_TYPE_USER = "U"
BUILD_TYPES = [BUILD_TYPE_PERIODIC, BUILD_TYPE_USER]

ERROR_WRONG_OPTION = 0x04


def main() -> int:

    dbs_log_file_path = None
    build_type = "U"
    extra_args = [""] * 8
    build_status = None

    try:
        opts, args = getopt(sys.argv[1:], "0:1:2:3:4:5:6:7:t:r:o:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        # Output file path
        if options.__contains__(OPT_OUTPUT):
            dbs_log_file_path = options[OPT_OUTPUT]

        if options.__contains__(OPT_BUILD_RESULT):
            build_status = options[OPT_BUILD_RESULT]

        # Extra information
        if options.__contains__(OPT_BUILD_TYPE):
            build_type = options[OPT_BUILD_TYPE]
        pattern = re.compile("-(\d)")
        for option in options:
            m = pattern.match(option)
            if m:
                extra_args[int(m.group(1))] = options[option]
    except GetoptError as err:
        print(err)
        show_help()
        return ERROR_WRONG_OPTION

    try:
        if build_type not in BUILD_TYPES:
            raise ValueError(build_type)

        if build_status is None:
            raise ValueError(build_status)

    except ValueError as err:
        print("Argument value %s is not correct." % err)
        show_help()
        return ERROR_WRONG_OPTION

    result = 0
    log = Logger()

    if dbs_log_file_path is not None:
        result = result | log.log_build_status(dbs_log_file_path, build_type, extra_args, build_status)

    return result


def show_help():
    text = "\n\n" \
           "dbs build status logger\n" \
           "\n" \
           "Usage :\n" \
           "log.py {options} {dbs log file path}\n" \
           "\n" \
           "Default value of {dbs log file path} is \"DBS_log.csv\".\n" \
           "\n" \
           "Options :\n" \
           "-h          Show help\n" \
           "            Show this help menu.\n" \
           "-t{c}       Build type\n" \
           "            Build type provides information who triggers this compile.\n" \
           "            Currently only P(eriodic) and U(ser) is available.\n" \
           "            Default : U\n" \
           "-r{BUILD_RESULT} Build status of DBS transaction.Values are PASS=0, UNSTABLE=1, FAIL =2.\n" \
           "-o{path}    Target output build_status log file.\n" \
           "            Default : DBS_log.csv\n"

    print(text)


if __name__ == '__main__':
    ret_val = main()
    exit(ret_val)