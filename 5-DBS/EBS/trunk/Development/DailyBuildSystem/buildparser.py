import configparser
import csv
import errno
import os
import re
import sys
import time
from getopt import getopt, GetoptError

import xlrd
from mako.template import Template
from xlsxwriter import *

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from dbs import DBS
except ImportError:
    from DailyBuildSystem.dbs import DBS


class BuildParser:
    BUILD_STATUS = "dbs_build_status"
    # archive_list = []
    # default_list = []

    def __init__(self, log_file_path, engineer_file_path=None):
        self.log_file = log_file_path
        self.engineer_file = engineer_file_path
        # self.error_list = []  # <- Local variable in instance scope raises some bug. Bad code.
        # self.file = None      # <- Local variable in instance scope raises some bug. Bad code.
        self.log_file_name = None
        # self.__excel_data = None
        self.__engineer_list = {}
        self.__record = []
        # self.__recipient_list = []    # <- Local variable in instance scope raises some bug. Bad code.
        self.__Flag_Licence_error = False
        self.__Flag_engineer_file_var_exist = False
        self.__Flag_engineer_file_path_exist = False
        self.__timestamp_date = time.strftime("%Y-%m-%d")
        self.__timestamp_time = time.strftime("%H:%M:%S")
        self.__forced_status = None

        if os.path.exists(self.log_file):
            self.log_file_name = os.path.basename(self.log_file)
            if self.engineer_file is not None:
                self.__Flag_engineer_file_var_exist = True
                self.recipient_file = os.path.basename(self.engineer_file)
                if os.path.exists(self.engineer_file):
                    self.__Flag_engineer_file_path_exist = True
                    xlwb = xlrd.open_workbook(self.engineer_file)
                    input_worksheet = xlwb.sheet_by_index(0)

                    for row_id in range(1, input_worksheet.nrows):
                        row = input_worksheet.row(row_id)
                        filename = str(row[0].value).strip()
                        devname = str(row[1].value).strip()
                        email = str(row[2].value).strip()

                        if filename not in self.__engineer_list:
                            self.__engineer_list[filename] = []
                        self.__engineer_list[filename].append((devname, email))

                    # data_input_worksheet = [[] for i in range(input_worksheet.ncols)]
                    # for i in range(input_worksheet.nrows):
                    #     for j in range(len(data_input_worksheet)):
                    #         data_input_worksheet[j].append((str(input_worksheet.cell_value(i, j))).strip())
                    # self.__excel_data = data_input_worksheet
                else:
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.recipient_file)
            read_log = open(self.log_file, 'r').readlines()

            developer_list = []
            for num, line in enumerate(read_log, 0):
                regex = "[c|e]{1,3}tc [E]\d{3}"
                if re.search(regex, line):
                    temp = line.split(":")[0]
                    command = temp.split()[0]
                    m = re.match('.*?([0-9]+)$', temp)
                    if m is None or m.group(1) is None:
                        continue
                    code = m.group(1)
                    message1 = line.split("[")[-1]
                    message1 = message1.split("]")[0]
                    message2 = line.split("] ")[-1]
                    message2 = message2.strip("\n")
                    error_type = re.search(r'([F|E])', line).group(0)
                    line1 = line.split("[\"")[-1]
                    line2 = line1.split("\"")[0]
                    line3 = line2.split("\\")[-1]
                    # self.file = line3.split("/")[-1]
                    # if self.__Flag_engineer_file_var_exist == self.__Flag_engineer_file_path_exist == True:
                    #     if not self.file.endswith(".c") or self.file.endswith(".h"):
                    #         new_name = self.file.split(".")[0]
                    #         self.file = new_name + ".c"
                    #     if self.file in (self.__excel_data[0]):
                    #         for x in range(len(self.__excel_data[0])):
                    #             if self.file == self.__excel_data[0][x]:
                    #                 dev_name = self.__excel_data[1][x]
                    #                 email_id = self.__excel_data[2][x]
                    #                 self.__recipient_list.append(email_id)
                    #                 developer_list.append(dev_name)
                    #         for i in range(len(developer_list)):
                    #             self.error_list = [self.file, developer_list[i], command, error_type, code,
                    #                                message1, message2]
                    #             if self.error_list not in self.__record:
                    #                 self.__record.append(self.error_list)
                    #     else:
                    #         self.error_list = [self.file, "<unknown>", command, error_type, code, message1, message2]
                    #         if self.error_list not in self.__record:
                    #             self.__record.append(self.error_list)
                    # else:
                    #     self.error_list = [self.file, command, error_type, code, message1, message2]
                    #     if self.error_list not in self.__record:
                    #         self.__record.append(self.error_list)

                    filename = line3.split("/")[-1]
                    error_record = [filename, None, None, command, error_type, code, message1, message2]
                    if self.__Flag_engineer_file_var_exist and self.__Flag_engineer_file_path_exist:
                        names = []
                        if filename in self.__engineer_list:
                            for engineer in self.__engineer_list[filename]:
                                names.append(engineer)
                        else:
                            names.append(('<unknown>',None))

                        for name in names:
                            temp = list(error_record)
                            temp[1:3] = name
                            self.__record.append(temp)
                    else:
                        self.__record.append(error_record)

                if re.search("[a-z]{1,4} [(][a-z][=]\d[)]", line) or re.search("[c|e]{1,3}tc [F]\d{3}", line):
                    self.__Flag_Licence_error = True
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.log_file_name)

    def save_to_archive(self, output_file, type_value, val_of_args=None):
        is_new_file = False
        if not os.path.exists(output_file):
            is_new_file = True

        list_of_args = [""] * 8
        for argument in range(len(val_of_args)):
            val = val_of_args[argument]
            list_of_args[argument] = val

        archive_file = open(output_file, 'a+', newline='')
        writer = csv.writer(archive_file)

        if is_new_file:
            writer.writerow(['Date', 'Time', 'Build Type', 'arg[0]', 'arg[1]', 'arg[2]', 'arg[3]', 'arg[4]',
                             'arg[5]', 'arg[6]', 'arg[7]', 'File Name', 'Engineer Name', 'Error Command',
                             'Error Type', 'Error Code', 'Error Message-1', 'Error Message-2'])

        for file in range(len(self.__record)):
            # if len(self.__record[0]) == 7:
            #     row = [self.__timestamp_date, self.__timestamp_time, type_value, list_of_args[0],
            #                                 list_of_args[1], list_of_args[2], list_of_args[3], list_of_args[4],
            #                                 list_of_args[5], list_of_args[6], list_of_args[7], self.__record[file][0],
            #                                 self.__record[file][1], self.__record[file][2], self.__record[file][3],
            #                                 self.__record[file][4], self.__record[file][5], self.__record[file][6]]
            # else:
            #     row = [self.__timestamp_date, self.__timestamp_time, type_value, list_of_args[0],
            #                                 list_of_args[1], list_of_args[2], list_of_args[3], list_of_args[4],
            #                                 list_of_args[5], list_of_args[6], list_of_args[7], self.__record[file][0],
            #                                 "", self.__record[file][1], self.__record[file][2], self.__record[file][3],
            #                                 self.__record[file][4], self.__record[file][5]]
            row = [self.__timestamp_date, self.__timestamp_time, type_value, list_of_args[0],
                        list_of_args[1], list_of_args[2], list_of_args[3], list_of_args[4],
                        list_of_args[5], list_of_args[6], list_of_args[7], self.__record[file][0],
                        self.__record[file][1], self.__record[file][3], self.__record[file][4],
                        self.__record[file][5], self.__record[file][6], self.__record[file][7]]
            writer.writerow(row)
        archive_file.close()
        return True

    def save_to_excel(self, destination_path):
        excel_workbook = Workbook(destination_path)
        excel_sheet = excel_workbook.add_worksheet()
        excel_format = excel_workbook.add_format({'bold': True, 'bg_color': 'yellow', 'border': 1})
        list_of_fields1 = ['File Name', 'Engineer Name', 'Error Command', 'Error Type', 'Error Code', 'Error Message-1', 'Error Message-2']
        list_of_fields2 = ['File Name', 'Error Command', 'Error Type', 'Error Code', 'Error Message-1', 'Error Message-2']

        if self.__Flag_engineer_file_var_exist:
            header = list_of_fields1
        else:
            header = list_of_fields2

        for column in range(len(header)):
            excel_sheet.write(0, column, header[column], excel_format)
            excel_sheet.set_column(column, column, 20)

        for row, record in enumerate(self.__record):
            # for col, value in enumerate(record):
            #     excel_sheet.write((row + 1), col, value)
            item = []
            item.append(record[0])
            if self.__Flag_engineer_file_var_exist and self.__Flag_engineer_file_path_exist:
                item.append(record[1])
            item += record[3:]
            for col, value in enumerate(item):
                excel_sheet.write(row+1, col, value)
        return True

    def save_mailing_list(self, output_file, truncate=False) -> bool:
        # for engineer in range(len(self.__excel_data[0])):
        #     if self.__excel_data[0][engineer] == "*":
        #         BuildParser.default_list.append(self.__excel_data[2][engineer])
        # self.__recipient_list.extend(BuildParser.default_list)
        #
        # return DBS.set_mail_recipients(output_file, self.__recipient_list, truncate)

        emails = []
        for record in self.__record:
            if record[2] is not None:
                emails.append(record[2])
        if '*' in self.__engineer_list:
            for engineer in self.__engineer_list['*']:
                emails.append(engineer[1])

        return DBS.set_mail_recipients(output_file, sorted(set(emails)), truncate)

    def save_mail_body(self, output_file, mako_template, truncate=False, jenkins=None, extra=None):
        mako_template = os.path.abspath(mako_template)

        if os.path.exists(mako_template):
            build_args = {
                "date": self.__timestamp_date,
                "time": self.__timestamp_time,
                "jenkins": jenkins,
                "extras": extra
            }

            release = DBS.get_config(output_file, DBS.Section.RELEASE)
            if release is not None:
                build_args[DBS.Section.RELEASE] = release
                if release.__contains__(DBS.RELEASE_JENKINS) and jenkins is not None:
                    path = "ws/" + release[DBS.RELEASE_JENKINS].replace(jenkins["WORKSPACE"], "")
                    path = path.replace("\\", "/")
                    release[DBS.RELEASE_JENKINS] = jenkins["JOB_URL"] + path

            template = Template(filename=(mako_template), input_encoding='utf-8', output_encoding="utf-8")
            # current_body = template.render_unicode(is_success=self.__build_result, args=build_args)
            current_body = template.render_unicode(is_success=self.is_success(), args=build_args)
            return DBS.set_mail_body(output_file, current_body, truncate)
        else:
            return False

    def save_build_status(self, output_file_path: str) -> bool:
        if self.is_success():
            build_status = "SUCCESS"
        else:
            build_status = "FAIL"

        parser = configparser.RawConfigParser()
        parser.read(output_file_path, encoding='utf-8')
        if not parser.has_section(DBS.Section.BUILD):
            parser.add_section(DBS.Section.BUILD)
        parser.set(DBS.Section.BUILD, BuildParser.BUILD_STATUS, build_status)
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                parser.write(f)
            return True
        except:
            return False

    def is_success(self) -> bool:
        if self.__forced_status is not None:
            return self.__forced_status
        else:
            return not self.__Flag_Licence_error and len(self.__record) == 0

    def set_forced_status(self, is_success: bool):
        self.__forced_status = is_success


# Since here YoungTaek.Son implements #
OPT_HELP = "-h"
OPT_OUTPUT = "-o"
OPT_ARCHIVE = "-a"
OPT_EXCEL = "-s"
OPT_MAILING = "-r"
OPT_MAIL_BODY = "-m"
OPT_ENGINEER = "-e"
OPT_BUILD_TYPE = "-t"
OPT_FORCED_FAIL = "-f"

BUILD_TYPE_PERIODIC = "P"
BUILD_TYPE_USER = "U"
BUILD_TYPES = [BUILD_TYPE_PERIODIC, BUILD_TYPE_USER]

ERROR_COMPILE_FAIL = 0x01
ERROR_PROCESS_FAIL = 0x02
ERROR_WRONG_OPTION = 0x04
ERROR_FILE_NOT_FOUND = 0x08


def main() -> int:
    # buildparser.py functions.
    #
    # Default. Parse compile log and return success or fail
    #    Result of compiling set in 0 bit. 0 is success, otherwise 1.
    #
    # 1. Archiving
    #    Archive compile fail log into target file. Build type and arguments can be set.
    #
    # 2. Save to excel
    #    Create summary excel which contains list of error files.Save mailing list
    #
    # 3.
    #    Extract e-mail recipients and store into target output configuration file.
    #
    # 4. Save mail body
    #    Create result summary e-mail and store into target output configuration file.

    is_truncate = True
    is_forced_fail = False
    log_file_path = "make.log"
    output_file_path = "dbs.conf"
    archiving_file_path = None
    summary_file_path = None
    is_create_mailing_list = False
    mail_template_file_path = None
    engineer_file_path = None
    build_type = "U"
    extra_args = [""] * 8

    try:
        opts, args = getopt(sys.argv[1:], "o:a:s:rm:e:t:f0:1:2:3:4:5:6:7:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        # Argument for log file path.
        if len(args) != 0 and len(args) != 1:
            raise GetoptError("Only one argument (log file path) is available")
        elif len(args) == 1:
            log_file_path = args[0]

        # Output file path
        if options.__contains__(OPT_OUTPUT):
            output_file_path = options[OPT_OUTPUT]

        if options.__contains__(OPT_FORCED_FAIL):
            is_forced_fail = True

        # Archiving
        if options.__contains__(OPT_ARCHIVE):
            archiving_file_path = options[OPT_ARCHIVE]

        # Save to excel
        if options.__contains__(OPT_EXCEL):
            summary_file_path = options[OPT_EXCEL]

        # Save to mailing list
        if options.__contains__(OPT_MAILING):
            if not options.__contains__(OPT_ENGINEER):
                raise GetoptError("Generating mailing list needs engineer list")
            else:
                is_create_mailing_list = True

        # Save mail body
        if options.__contains__(OPT_MAIL_BODY):
            mail_template_file_path = options[OPT_MAIL_BODY]

        # Engineer list
        if options.__contains__(OPT_ENGINEER):
            engineer_file_path = options[OPT_ENGINEER]

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
        if not os.path.exists(log_file_path):
            raise FileNotFoundError(log_file_path)

        if mail_template_file_path is not None and not os.path.exists(mail_template_file_path):
            raise FileNotFoundError(mail_template_file_path)

        if engineer_file_path is not None and not os.path.exists(engineer_file_path):
            raise FileNotFoundError(engineer_file_path)

        if build_type not in BUILD_TYPES:
            raise ValueError(build_type)

    except FileNotFoundError as err:
        print("File %s is not exists." % err)
        show_help()
        return ERROR_FILE_NOT_FOUND

    except ValueError as err:
        print("Argument value %s is not suitable." % err)
        show_help()
        return ERROR_WRONG_OPTION

    is_ok = True

    parser = BuildParser(log_file_path, engineer_file_path)
    if is_forced_fail:
        # Currently BuildParser can not get any cases of build error.
        # So make.py will pass "-f" option if it can't find output binaries.
        parser.set_forced_status(False)
    if output_file_path is not None:
        is_ok = is_ok & parser.save_build_status(output_file_path)
    if archiving_file_path is not None:
        is_ok = is_ok & parser.save_to_archive(archiving_file_path, build_type, extra_args)
    if summary_file_path is not None:
        is_ok = is_ok & parser.save_to_excel(summary_file_path)
    if is_create_mailing_list:
        is_ok = is_ok & parser.save_mailing_list(output_file_path, is_truncate)
    if mail_template_file_path:
        jenkins = {}
        jenkins_params = [
            "SVN_URL",
            "SVN_REVISION",
            "BUILD_URL",
            "WORKSPACE",
            "JOB_URL"]
        for param in jenkins_params:
            if os.environ.__contains__(param):
                value = os.environ[param]
            else:
                value = "not available"
            jenkins[param] = value

        is_ok = is_ok & parser.save_mail_body(output_file_path,
                                              mail_template_file_path,
                                              is_truncate,
                                              jenkins,
                                              extra_args)

    result = 0
    if not parser.is_success():
        result = result | ERROR_COMPILE_FAIL
    if not is_ok:
        result = result | ERROR_PROCESS_FAIL

    return result


def show_help():
    text = "\n\n" \
           "Compile log parser\n" \
           "\n" \
           "Usage :\n" \
           "buildparser.py {options} {log file path}\n" \
           "\n" \
           "Exit code is 0 if compile is success, otherwise non-zero value.\n" \
           "Default value of {log file path} is \"make.log\".\n" \
           "\n" \
           "Options :\n" \
           "-h          Show help\n" \
           "            Show this help menu.\n" \
           "-o{path}    Target output configuration file.\n" \
           "            Recipients of mailing list and E-Mail content will be stored in this file.\n" \
           "            Default : dbs.conf\n" \
           "-a{path}    Path of archiving file.\n" \
           "            This options archives compile error log.\n" \
           "-s{path}    Path of summary excel file.\n" \
           "            This option generates compile error summary excel file.\n" \
           "-r          To generate mail recipients.\n" \
           "            With this option, script will determine proper e-mail recipients and\n" \
           "            generate mailing list. Data will be stored in output configuration file.\n" \
           "            This option shall need -e(engineer list) option.\n" \
           "-m{path}    To generate e-mail content of compile report.\n" \
           "            This option will generate e-mail content of compile summary using provided\n" \
           "            provided template file. Data will be stored in output configuration file.\n" \
           "-e{path}    Path of engineer list.\n" \
           "            -a and -e are effected by this option. With this option, output data will contains\n" \
           "            responsible engineer names of each compile error. Also engineer list shall need\n" \
           "            while making mailing list.\n" \
           "-t{c}       Build type\n" \
           "            Build type provides information who triggers this compile.\n" \
           "            Currently only P(eriodic) and U(ser) is available.\n" \
           "            Default : U\n" \
           "-[n]{text}  Extra arguments for archiving\n" \
           "            Archiving file may contains up to 8 arguments to specify build environment.\n" \
           "            User can put those values through 0 ~ 7.\n" \
           "-f          Force build result fail.\n" \
           "            Set build result fail even there isn't any error.\n"
    print(text)


if __name__ == '__main__':
    ret_val = main()
    exit(ret_val)
