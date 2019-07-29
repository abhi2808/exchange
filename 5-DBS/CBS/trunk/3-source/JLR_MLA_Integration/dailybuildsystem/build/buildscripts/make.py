"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""

import os
import sys
import subprocess
import errno
from getopt import getopt, GetoptError

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))


class Make:

    def __init__(self, project_root_path, compiler_path, build_log_path):

        self.__project = project_root_path
        self.__compiler = compiler_path
        self.__log_file = build_log_path
        #self.__build_output = build_output_path

    def clean(self):
        clean = "/t:Clean"
        cmd = [self.__compiler, self.__project, clean]
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def build(self) -> int:

        log = "-flp:logfile=" + self.__log_file
        #output = "/p:OutputPath=" + self.__build_output
        cmd = [self.__compiler, self.__project, log]
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return 0


OPT_HELP = "-h"
OPT_PROJECT_ROOT = "-p"
OPT_COMPILER_PATH = "-m"
OPT_COMPILE_OPTION = "-o"
OPT_BUILD_LOG = "-l"
OPT_BUILD_OUT = "-b"

def main() -> int:

    project_root_path = None
    compiler_path     = "C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319\\MSBuild.exe"
    build_log_path = None
    build_output_path = None

    try:
        opts, args = getopt(sys.argv[1:], "h:p:o:m:l:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        if not options.__contains__(OPT_PROJECT_ROOT):
            raise GetoptError("No project found to build.")
        else:
            project_root_path = options[OPT_PROJECT_ROOT]

        if options.__contains__(OPT_COMPILER_PATH):
            compiler_path = options[OPT_COMPILER_PATH]

        if options.__contains__(OPT_BUILD_LOG):
            build_log_path = options[OPT_BUILD_LOG]

        #if options.__contains__(OPT_BUILD_OUT):
         #   build_output_path = options[OPT_BUILD_OUT]


    except GetoptError as err:
        print(err)
        show_help()
        return False

    if not os.path.exists(project_root_path):
        print("Can not find project file : %s" , project_root_path)
        show_help()
        return False

    maker = Make(project_root_path, compiler_path, build_log_path)

    maker.clean()

    return maker.build()


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
    ret = main()
    exit(ret)