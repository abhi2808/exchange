import os
import sys
import ctypes # module for C data types
import subprocess
import time
import shutil
from getopt import getopt, GetoptError

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))


class Trace32Flash:

    def __init__(self, t32_cmm_file):

        self.__t32practice_script = t32_cmm_file

        t32_exe = 'C:\\T32_ForAurix\\bin\\windows64\\t32mtc.exe'

        config_file = 'C:\T32_ForAurix\config.t32'

        start_up = self.__t32practice_script

        command = [t32_exe, '-c', config_file]

        process = subprocess.Popen(command)

        time.sleep(5)

    def flash(self):

        # Load TRACE32 Remote API DLL
        t32api = ctypes.cdll.LoadLibrary('C:\\T32_ForAurix\\demo\\api\\python\\t32api64.dll')

        # Establish communication channel
        t32api.T32_Config(b"NODE=", b"localhost")
        t32api.T32_Config(b"PORT=", b"20000")
        t32api.T32_Config(b"PACKLEN=", b"1024")
        rc = t32api.T32_Init()

        # TRACE32 control commands

        path = self.__t32practice_script
        flash_cmd = "CD.DO {}".format(path)
        flash_cmd = flash_cmd.encode()

        rc = t32api.T32_Cmd(b"B::RESet")
        rc = t32api.T32_Cmd(flash_cmd)

        # Release communication channel
        rc = t32api.T32_Exit()


OPT_HELP = "-h"
OPT_BIN_SRC = "-s"
OPT_BIN_DST = "-d"

ERROR_WRONG_OPTION = 0x04
ERROR_FILE_NOT_FOUND = 0x08


def main():

    def show_help():
        text = "\n\n" \
               "Trace32 launcher and flash downloader\n" \
               "\n" \
               "Usage :\n" \
               "t32.py {options} {Practice cmm file}\n" \
               "\n" \
               "Exit code is 0 if trace32 runs successfully, otherwise non-zero value.\n" \
               "\n" \
               "Options :\n" \
               "-h          Show help\n" \
               "            Show this help menu.\n" \
               " -s          option for source binary flash file\n" \
               "\n" \
               " -d            option fro binary file to copy\n"

        print(text)

    t32_cmm_file = None
    bin_src_path = None
    bin_dst_path = None

    try:
        opts, args = getopt(sys.argv[1:], "s:d:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        # Argument for source path to copy sb1 file

        if options.__contains__(OPT_BIN_SRC):
            bin_src_path = options[OPT_BIN_SRC]

        # Argument for destination path to copy sb1 file
        if options.__contains__(OPT_BIN_DST):
            bin_dst_path = options[OPT_BIN_DST]

        # Argument for cmm file path.

        if len(args) != 0 and len(args) == 1:
            t32_cmm_file = args[0]
        else:
            raise GetoptError("No argument for cmm file path is available")

    except GetoptError as err:
        print(err)
        show_help()
        return ERROR_WRONG_OPTION

    try:
        if not os.path.exists(t32_cmm_file):
            raise FileNotFoundError(t32_cmm_file)

    except FileNotFoundError as err:
        print("File %s does not exists." % err)
        show_help()
        return ERROR_FILE_NOT_FOUND

    for fname in os.listdir(bin_src_path):
        if fname.endswith('.sb1'):
            src_file = os.path.join(bin_src_path, fname)
            shutil.copy2(src_file, bin_dst_path)
            file1 = os.path.join(bin_dst_path, fname)
            file2 = os.path.join(bin_dst_path, "dbs_flash.sb1")
            shutil.move(file1, file2)

    t32 = Trace32Flash(t32_cmm_file)
    time.sleep(5)
    t32.flash()
    time.sleep(5)

    return


if __name__ == '__main__':
    ret = main()
    exit(ret)