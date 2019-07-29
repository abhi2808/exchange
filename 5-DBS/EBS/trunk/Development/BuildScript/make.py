"""
:: NAME:           make.py
::
:: FUNCTION:       For building the project  
::                    
:: PROJECT:        Daily Build System
::
:: DEVELOPED BY :  Navjot Kaur
:     
"""

import os
import re
import subprocess
import sys
from getopt import getopt, GetoptError


regex_asr_buildpackage = re.compile('.*_ASR(_.*)?')

class Make:
    def __init__(self, project_path, build_package):
        self.__project = project_path
        self.__package = build_package
        self.__launch_path = os.path.join(self.__project, "BuildPackage", self.__package, "util")

    def clean(self):
        cwd = os.getcwd()
        os.chdir(self.__launch_path)

        # To cover EB & Legacy makefile, Make runs asynchronously.
        p = subprocess.Popen("cmd /k @echo off", stdin=subprocess.PIPE, universal_newlines=True)
        p.stdin.write('launch.bat\n')
        p.stdin.flush()
        p.stdin.write('make clean\n')
        p.stdin.flush()
        # make dependency if it is legacy build-package
        if regex_asr_buildpackage.match(self.__package) is None:
            p.stdin.write('make depend\n')
            p.stdin.flush()
        p.communicate('')
        p.wait()

        os.chdir(cwd)

    def build(self, compile_option):
        # list = []
        cwd = os.getcwd()
        os.chdir(self.__launch_path)
        binary_path = os.path.join("..", "output", "bin")

        # Delete binaries
        if os.path.exists(binary_path):
            for file in os.listdir(binary_path):
                os.remove(os.path.join(binary_path, file))

        # To cover EB & Legacy makefile, Make runs asynchronously.
        p = subprocess.Popen("launch.bat", stdin=subprocess.PIPE, universal_newlines=True)
        p.communicate("make %s\n" % compile_option)
        p.wait()

        # Check is binary generated.
        is_success = False

        if os.path.exists(binary_path):
            files = os.listdir(binary_path)
            for file in files:
                if os.path.splitext(file)[1] == ".elf":
                    is_success = True
                    break
        os.chdir(cwd)
        return is_success

        # file = open("make.log", 'r')
        # file_read = file.readlines()
        # file.close()
        # os.chdir(cwd)
        # for line in file_read:
        #     if "[c|l|e]{1,3}tc [E|F]\d{3}" in line or "[a-z]{1,3} [/(/=]\d{1}[\)/]" in line:
        #         list.append(line)
        # if len(list) == 0:
        #     return True
        # else:
        #     return False


# Since here YoungTaek.Son implements #
OPT_HELP = "-h"
OPT_CLEAN = "-c"
OPT_PROJECT_ROOT = "-p"
OPT_COMPILE_OPTION = "-o"


def main() -> bool:
    project_root_path = os.path.dirname(sys.argv[0])

    try:
        opts, args = getopt(sys.argv[1:], "hcp:o:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True
        if len(args) != 1:
            raise GetoptError("Script needs 1 argument : {Build Package}")
    except GetoptError as err:
        print(err)
        show_help()
        return False

    if options.__contains__(OPT_PROJECT_ROOT):
        project_root_path = options[OPT_PROJECT_ROOT]
    if not os.path.exists(project_root_path):
        print("Can not find project root path : %s" % (os.path.join(os.getcwd(), project_root_path)))
        show_help()
        return False

    build_package = args[0]
    maker = Make(project_root_path, build_package)

    if options.__contains__(OPT_CLEAN):
        return maker.clean()
    else:
        if options.__contains__(OPT_COMPILE_OPTION):
            compile_option = options[OPT_COMPILE_OPTION]
        else:
            compile_option = ""

        return maker.build(compile_option)


def show_help():
    text = "\n\n" \
           "Mando make shortcut script\n" \
           "\n" \
           "Usage :\n" \
           "make.py {options} {Build Package}\n" \
           "\n" \
           "make.py provides shortcut of launching Mando make script." \
           "Exit code is 0 if compile is success, otherwise non-zero value.\n" \
           "\n" \
           "Options :\n" \
           "-h          Show help\n" \
           "            Show this help menu.\n" \
           "-c          Clean\n" \
           "            This option equivalents to <make clean> and ignore any other options.\n" \
           "-p          Project root\n" \
           "            Specify root path of project. Default value is current working directory." \
           "-o{text}    Compile options.\n" \
           "            Shortcut script passes this argument to EB tresos make scripts as compile option.\n" \
           "            For example, <python make.py -o""-j32 -s""> equivalents to <make -j32 -s>.\n"
    print(text)


if __name__ == '__main__':
    if main():
        exit(0)
    else:
        exit(1)
