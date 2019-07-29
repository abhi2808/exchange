import os
import time
from getopt import getopt, GetoptError

import win32com.client
from win32com.client import *
from win32com.client.connect import *


class CANoe:
    """
    Currently this class doesn't support reuse for multiple test configs.
    Need to be implemented.
    """
    _stop_reason = -2

    class __TestConfigEventHandler:
        def OnStart(self):
            CANoe._stop_reason = -1

        def OnStop(self, reason):
            CANoe._stop_reason = reason

        def OnVerdictChanged(self, verdict):
            pass

        def OnVerdictFail(self):
            pass

    def __init__(self):
        self._application = win32com.client.DispatchEx("CANoe.Application")

    def open(self, config_path):
        self._application.Open(config_path, True, True)

    def start(self):
        self._application.Measurement.Start()
        time.sleep(1)
        for test_config in self._application.Configuration.TestConfigurations:
            test_config_events = win32com.client.DispatchWithEvents(test_config, CANoe.__TestConfigEventHandler)
            time.sleep(1)
            test_config.Start()
            while CANoe._stop_reason < 0:
                pythoncom.PumpWaitingMessages()
                time.sleep(0.01)
            test_config.Stop()

    def close(self):
        if self._application.Measurement.Running:
            self._application.Measurement.Stop()
        self._application.Quit()


OPT_HELP = "-h"

ERROR_WRONG_OPTION = 0x04
ERROR_FILE_NOT_FOUND = 0x08


def main():

    def show_help():
        text =  "\n\n" \
                "Canoe Launcher\n" \
                "\n" \
                "Usage : \n" \
                "canoeTest.py {options} {input_configuration_file_path}\n" \
                "\n" \
                "Exit code is zero if success, otherwise non-zero value is returned.\n" \
                "Default value of configuration file is current working directory. \n " \
                "\n" \
                "Options :\n" \
                "-h         show_help\n" \
                "           show help menu\n" \


        print(text)


    config_file_path     = "Configuration.cfg"


    try:
        opts, args = getopt(sys.argv[1:], ":")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]

        if options.__contains__(OPT_HELP):
            show_help()
            return True

        if len(args) != 0 and len(args) != 1:
            raise GetoptError("Only one argument input configuration file path is available")
        elif len(args) == 1:
            config_file_path = args[0]

    except GetoptError as err:
        print(err)
        show_help()
        return ERROR_WRONG_OPTION

    try:
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(config_file_path)

    except FileNotFoundError as err:
        print("File %s does not exists." % err)
        show_help()
        return ERROR_FILE_NOT_FOUND
    print(config_file_path)
    canoe = CANoe()
    canoe.open(config_file_path)
    canoe.start()
    canoe.close()

    return

if __name__ == '__main__':
    ret = main()
    exit(ret)

