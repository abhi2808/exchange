"""
:: NAME:           carpargenerator.py
::
:: FUNCTION:       For generating Header files and creating header files in VIL folder for particular scenario
::                    
:: PROJECT:        Daily Build System
::
:: DEVELOPED BY :  Navjot Kaur
:     
"""

import errno
import os
import shutil
import sys
import re
from getopt import getopt, GetoptError

import xlrd
from mako.template import Template


class CarParGenerator:
    def __init__(self, template_path: str, mako_path: str):
        self.template = template_path
        self.mako = mako_path
        self.__folder_name = []
        self.__unique_names = []
        self.__excel_data = None
        self.__mytemplate1 = []
        self.__scenario_list = {}
        self.__folder_list = []
        temp_name = os.path.basename(self.template)
        if os.path.exists(self.template):
            xlwb = xlrd.open_workbook(self.template)
            input_worksheet = xlwb.sheet_by_index(0)
            data_input_worksheet = [[] for i in range(input_worksheet.ncols)]
            for i in range(input_worksheet.nrows):
                for j in range(len(data_input_worksheet)):
                    data_input_worksheet[j].append((str(input_worksheet.cell_value(i, j))).strip())
                    if (j == 0) and (i >= 2):
                        if str(input_worksheet.cell_value(i, 0)) not in self.__unique_names:
                            self.__unique_names.append(str(input_worksheet.cell_value(i, 0)))
            self.__excel_data = data_input_worksheet
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), temp_name)
        self.generate_header_files()

    def generate_header_files(self):
        package = []
        genDump1 = []
        for n in range((len(self.__excel_data)) - 2):
            self.__folder_name.append(self.__excel_data[n + 2][0] + '_' + self.__excel_data[n + 2][1])
            package.append(self.__excel_data[n + 2][0])
        for m in range(len(self.__folder_name)):
            for header_file in range(len(self.__unique_names)):
                mako_file = self.__unique_names[header_file] + ".mako"
                mako_file_path = self.mako + "\\" + mako_file
                if os.path.exists(mako_file_path):
                    mytemplate = Template(filename=mako_file_path)
                    for n in range((len(self.__excel_data[1]))):
                        if n >= 2:
                            row_no = n
                            for f in range((len(self.__excel_data)) - 2):
                                if self.__folder_name[f] == (
                                        (self.__excel_data[f + 2][0]) + '_' + (self.__excel_data[f + 2][1])):
                                    col_no = f + 2
                                    if (self.__folder_name[f]) in self.__scenario_list:
                                        self.__scenario_list[self.__folder_name[f]][(self.__excel_data[1][n])] = \
                                            self.check_and_process_dynamic_value(self.__excel_data[col_no][row_no])
                                    else:
                                        if (self.__excel_data[col_no][row_no]).isnumeric():
                                            self.__scenario_list[self.__folder_name[f]] = {
                                                ((self.__excel_data[1][n]).split('.')[0]): (
                                                self.check_and_process_dynamic_value(self.__excel_data[col_no][row_no]))}
                                        else:
                                            self.__scenario_list[self.__folder_name[f]] = {
                                                (self.__excel_data[1][n]):
                                                    (self.check_and_process_dynamic_value(self.__excel_data[col_no][row_no]))}
                    genDump1.append(mytemplate.render(Car_Par=self.__scenario_list, Car_Test_Par=self.__scenario_list,
                                                      folder=self.__folder_name, count=m).replace('\r\n', '\n'))
                    self.__mytemplate1.append(mako_file)
                else:
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), mako_file)

    '''
        Description: check_and_process_dynamic_value() checks whether there is a "dynamic value" in the macro value included to
        the excel or not, process the "dynamic value", and return the processed value if there is.
        
        Returns: "processed value" is returned if there is a "dynamic value" and there is a "readable environment variable"
        in the "dynamic value", otherwise, the "original macro value in the excel" 
    '''
    def check_and_process_dynamic_value(self, origin_data) -> str:
        ret_str = []
        result = re.match(r'(.*)(\{(-)?(\d+)?\|?(\w+)\})(.*)', origin_data)
        if result != None:                      # when there is a "dynamic value"
            groups = result.groups()
            env = os.getenv(groups[4])
            if env != None:                     # when there is "a environment variable" named macro value in the excel
                ret_str = groups[0]

                env_align = ''
                env_length = ''
                if result.regs[3][0] != -1:     # when there is "-" in the dynamic value, do assign at the left
                    env_align = groups[2]
                if groups[3] != None:           # when there is no "-" in the dynamic value, do assign at the right
                    env_length = groups[3]
                env_str = '%' + env_align + env_length + 's'

                ret_str = ret_str + env_str % env
                if groups[5] != None:           # when there is a string "behind" the dynamic value, add it
                    ret_str = ret_str + groups[5]
            else:                               # when there is "no environment variable" named macro value in the excel
                ret_str = ""
        else:                                   # when there is "no dynamic value", return the original macro value
            ret_str = (origin_data).split('.')[0]
        return ret_str

    def set_tresos(self, project_path: str, scenario) -> bool:
        VIL_path = (project_path + "\\" + "SourceCode" + "\\" + "VIL")
        if scenario in self.__folder_name:
            if os.path.exists(VIL_path):
                self.generate_VIL_file(project_path, scenario)
                return True
            else:
                print("VIL folder does not exist")
                return False
        else:
            print("Scenario does not exist")
            return False

    def generate_VIL_file(self, project, scenario):
        for m in range(len(self.__folder_name)):
            if self.__folder_name[m] == scenario:
                for header_file in range(len(self.__unique_names)):
                    for n in range(len(self.__mytemplate1)):
                        if self.__unique_names[header_file] == self.__mytemplate1[n].strip('.mako'):
                            mytemplate = Template(filename=(self.mako + "\\" + self.__mytemplate1[n]))
                            genfile1 = mytemplate.render(Car_Par=self.__scenario_list,
                                                         Car_Test_Par=self.__scenario_list, folder=self.__folder_name,
                                                         count=m).replace('\r\n', '\n')
                            filepath = os.path.join(project, "SourceCode", "VIL", (self.__unique_names[header_file]))
                            read_file = open(filepath, 'r')
                            list = read_file.readlines()
                            genfile_list = genfile1.splitlines()
                            for line1, line2 in zip(list, genfile_list):
                                line1 = line1.rstrip('\n')
                                if not line1 == line2:
                                    f1 = open(filepath, 'w')
                                    f1.write(genfile1)
                                    f1.close()

    def save(self, output_path: str) -> bool:
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        self.generate_output(output_path)

        # Implement return True if only being success.
        return True

    def generate_output(self, output):
        for the_file in os.listdir(output):
            shutil.rmtree(output + "\\" + the_file)
        for m in range(len(self.__folder_name)):
            for n in range((len(self.__excel_data)) - 2):
                if (self.__folder_name[m]) == (self.__excel_data[n + 2][0] + '_' + self.__excel_data[n + 2][1]):
                    packagepath = (output + "/" + self.__excel_data[n + 2][0])
                    if not os.path.exists(packagepath):
                        os.mkdir(packagepath)
                        os.mkdir(packagepath + "/" + self.__folder_name[m])
                    else:
                        os.mkdir(packagepath + "/" + self.__folder_name[m])
                    for header_file in range(len(self.__unique_names)):
                        for n in range(len(self.__mytemplate1)):
                            if self.__unique_names[header_file] == self.__mytemplate1[n].strip('.mako'):
                                mytemplate = Template(filename=(self.mako + "\\" + self.__mytemplate1[n]))
                                genfile1 = mytemplate.render(Car_Par=self.__scenario_list,
                                                             Car_Test_Par=self.__scenario_list,
                                                             #version_par=self.__scenario_list,
                                                             folder=self.__folder_name, count=m).replace('\r\n', '\n')
                                f1 = open(os.path.join(packagepath, self.__folder_name[m],
                                                       (self.__unique_names[header_file])), 'w')
                                f1.write(genfile1)
                                f1.close()


# Since here YoungTaek.Son implements #
OPT_HELP = "-h"
OPT_TRESOS = "-t"
OPT_SAVE = "-s"
OPT_PROJECT = "-p"
OPT_EXCEL = "-e"
OPT_MAKO = "-m"


def main() -> bool:
    # carpargenerator.py functinos.
    #
    # 1. Set CarPar of tresos project
    #    python carpargenerator.py -t buildpackage variant
    #
    # 2. Save all CarPars
    #    python carpargenerator.py -s output_path

    script_path = os.path.dirname(sys.argv[0])
    project_root_path = os.path.abspath(os.getcwd())
    excel_file_path = os.path.abspath(os.path.join(script_path, r".\resources\CarPar.xlsx"))
    mako_path = os.path.abspath(os.path.join(script_path, r".\resources"))
    running_mode = ""

    try:
        opts, args = getopt(sys.argv[1:], "hstp:e:m:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        if options.__contains__(OPT_TRESOS) and options.__contains__(OPT_SAVE):
            raise GetoptError("option " + OPT_TRESOS + "and " + OPT_SAVE + " can not be used at same time.")
        elif not options.__contains__(OPT_TRESOS) and not options.__contains__(OPT_SAVE):
            raise GetoptError(OPT_TRESOS + " or " + OPT_SAVE + " is required.")
        elif options.__contains__(OPT_SAVE):
            running_mode = OPT_SAVE
            if len(args) != 1:
                raise GetoptError(OPT_SAVE + " requires 1 argument.")
        elif options.__contains__(OPT_TRESOS):
            running_mode = OPT_TRESOS
            if len(args) != 2:
                raise GetoptError(OPT_TRESOS + " requires 2 arguments.")
        else:
            raise GetoptError("Undefined error")

        if options.__contains__(OPT_PROJECT):
            project_root_path = os.path.abspath(options[OPT_PROJECT])

        if options.__contains__(OPT_EXCEL):
            excel_file_path = os.path.abspath(options[OPT_EXCEL])

        if options.__contains__(OPT_MAKO):
            mako_path = os.path.abspath(options[OPT_MAKO])

    except GetoptError as err:
        print(err)
        show_help()
        return False

    try:
        generator = CarParGenerator(excel_file_path, mako_path)
    except FileNotFoundError as err:
        print(err)
        return False

    if running_mode == OPT_SAVE:
        return generator.save(args[0])
    elif running_mode == OPT_TRESOS:
        # This should be changed set_tresos(project_root_path, args[0], args[1])
        return generator.set_tresos(project_root_path, args[0] + "_" + args[1])
    else:
        return False


def show_help():
    text = "\n\n" \
           "CarPar files generator\n" \
           "\n" \
           "Usage :\n" \
           "carpargenerator.py {options} -s {path}\n" \
           "carpargenerator.py {options} -t {build package} {variant code}\n" \
           "\n" \
           "Required arguments :\n" \
           "-s          Save all CarPar files to {path}\n" \
           "-t          Set variant option of Tresos project. Script will replace CarPar files in VIL folder\n" \
           "            with newly generated one if not identical.\n" \
           "\n" \
           "Options :\n" \
           "-h          Show help\n" \
           "            Show this help menu.\n" \
           "-p{path}    Specify root path of Tresos project.\n" \
           "            Default : Current directory.\n" \
           "-e{path}    Specify file path of CarPar Excel sheet.\n" \
           "            Default : {script path}\\resources\\CarPar.xlsx\n" \
           "-m{path}    Specify path of CarPar template files.\n" \
           "            Default : {script path}\\resources\n"

    print(text)


if __name__ == '__main__':
    if main():
        exit(0)
    else:
        exit(1)
