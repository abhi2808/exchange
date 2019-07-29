import os
import sys
from enum import Enum
from getopt import getopt, GetoptError


class Tool(Enum):
    QAC = "QAC"
    CodeSonar = "CodeSonar"


class Target(Enum):
    IGNORE = r"1.[Tresos-Tasking] Ignore.makefile"
    QUICK = r"2.[Tresos-Tasking] Quick.makefile"


class STManager:
    def __init__(self, path: str):
        if type(self) == STManager:
            raise NotImplementedError("Class STManager can not be initiated directly.")
        self._path:str = path
        self._tool: Tool = None
        self._project_name: str = None
        self._source_path: str = None
        self._source_project: str = None
        self._source_target: Target = None
        self._is_wait_until_finish: bool = False
        self._COMPILER_PATH: str = r"C:\Compiler\TASKING\TriCore_v5.0r2\ctc\bin\ctc.exe"

    @staticmethod
    def builder(tool: Tool, path: str = None) -> 'STManager':
        if path is None:
            path = r"C:\STManager"
        o: STManager = eval(tool.value)(path)
        o._tool = tool.value
        return o

    def set_compiler_path(self, path: str) -> 'STManager':
        self._COMPILER_PATH = path
        return self

    def set_project_name(self, project_name: str) -> 'STManager':
        self._project_name = project_name
        return self

    def set_source_path(self, source_path: str) -> 'STManager':
        self._source_path = source_path
        return self

    def set_source_project(self, source_project: str) -> 'STManager':
        self._source_project = source_project
        return self

    def _generate_command(self) -> str:
        return r'STManager.exe -result -t "%s" -pn "%s" -sp "%s" -sn "%s" -st "%s" -cf "%s"' % (self._tool, self._project_name, self._source_path, self._source_project, self._source_target.value, self._COMPILER_PATH)

    def launch(self) -> int:
        batch = self._generate_command()
        print(batch)

        current_path: str = os.getcwd()
        execute_abs_path: str = os.path.abspath(self._path)
        os.chdir(execute_abs_path)
        exit_code = os.system(batch)
        os.chdir(current_path)

        return exit_code


class QAC(STManager):
    def __init__(self, path: str):
        STManager.__init__(self, path)
        self._misra_rule = 10
        self._source_target = Target.IGNORE

    def set_misra_rule(self, rule: int) -> STManager:
        self._misra_rule = rule
        return self

    def _generate_command(self):
        batch = STManager._generate_command(self)
        if self._misra_rule is not None:
            batch += r" -qacrule %d" % self._misra_rule
        return batch


class CodeSonar(STManager):
    def __init__(self, path: str):
        STManager.__init__(self, path)
        self._source_target = Target.QUICK

OPT_HELP = "-h"
OPT_QAC = "-q"
OPT_CODESONAR= "-c"

OPT_UNBLOCK = "-u"
OPT_PATH = "-s"
OPT_TASKING = "-t"
OPT_MISRA_RULE = "-m"

TOOLS = {
    OPT_QAC: Tool.QAC,
    OPT_CODESONAR: Tool.CodeSonar,
}

def main() -> bool:
    tools = []
    path = None
    misra_rule = None
    compiler_path = None
    is_blocking_mode = True

    try:
        options = {}
        opts, args = getopt(sys.argv[1:], "qchus:t:m:")
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        if len(args) != 3:
            raise GetoptError("Number of input arguments shall be three.")

        if not options.__contains__(OPT_QAC) and not options.__contains__(OPT_CODESONAR):
            raise GetoptError("At least one of tool should be chosen.")

        for too_opt in TOOLS:
            if options.__contains__(too_opt):
                tools.append(TOOLS[too_opt])

        if options.__contains__(OPT_PATH):
            path = options[OPT_PATH]

        if options.__contains__(OPT_MISRA_RULE):
            misra_rule = int(options[OPT_MISRA_RULE])

        if options.__contains__(OPT_TASKING):
            compiler_path = options[OPT_TASKING]

        if options.__contains__(OPT_UNBLOCK):
            is_blocking_mode = False

    except GetoptError as err:
        print(err)
        show_help()
        return False
    except ValueError as err:
        print(err)
        show_help()
        return False

    for tool in tools:
        manager = STManager.builder(tool, path)\
            .set_project_name(args[0])\
            .set_source_path(args[1])\
            .set_source_project(args[2])

        if compiler_path is not None:
            manager.set_compiler_path(compiler_path)

        if tool == Tool.QAC and misra_rule is not None:
            manager.set_misra_rule(misra_rule)

        # Unblock 모드 구현 필요.
        manager.launch()
    return True


def show_help():
    text = "\n\n" \
           "STManager launcher\n" \
           "\n" \
           "Usage :\n" \
           "STManager.py -{q|c} {options} {name} {project root} {project file path}\n" \
           "\n" \
           "-q          Launch QAC.\n" \
           "-c          Launch CodeSonar.\n" \
           "\n" \
           "Note :      -q and -c options can be used simultaneously.\n" \
           "            Also, at least one of them shuld be choosen.\n" \
           "\n" \
           "Options :\n" \
           "-h          Show help\n" \
           "            Show this help menu.\n" \
           "-u          Launch STManager in unblocked mode.\n" \
           "            Script won't be suspended and will be finished regardless of running status of STManager.\n" \
           "-s{path}    Specifiy path of STManager.\n" \
           "            Default path of STManager is \"c:\STManager\".\n" \
           "-t{path}    Speicify path of Tasking Compiler.\n" \
           "            Default path of Tasking Compiler is \"C:\\Compiler\\TASKING\\TriCore_v5.0r2\\ctc\\bin\\ctc.exe\".\n" \
           "-m{n}       Misra rule.\n" \
           "            1  : Mando required rules Misra-C 2004\n" \
           "            10 : Mando Standard rules Misra-C 2012 (Default)\n" \
           "            2 : ...\n" \
           "            3 : ...\n" \
           "            This option only valid for QAC mode. Otherwise will be ignored.\n"
    print(text)


if __name__ == '__main__':
    main()
    exit(0)
