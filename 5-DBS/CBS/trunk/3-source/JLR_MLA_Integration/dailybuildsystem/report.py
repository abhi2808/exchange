"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""


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
#from xlsxwriter import *

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from dbs import DBS
except ImportError:
    from DailyBuildSystem.dbs import DBS

class BuildParser:
    BUILD_STATUS = "dbs_build_status"

    def __init__(self, log_file_path, reportee_file_path=None):
        self.log_file = log_file_path
        self.reportee_file = reportee_file_path

        self.log_file_name = None

        self.__reportee_list = {}
        self.__record = []

        self.__Flag_Licence_error = False
        self.__Flag_reportee_file_var_exist = False
        self.__Flag_reportee_file_path_exist = False
        self.__timestamp_date = time.strftime("%Y-%m-%d")
        self.__timestamp_time = time.strftime("%H:%M:%S")
        self.__forced_status = None
        self.__fatal_error  = False

        if os.path.exists(self.log_file):
            self.log_file_name = os.path.basename(self.log_file)
            if self.reportee_file is not None:
                self.__Flag_reportee_file_var_exist = True
                self.recipient_file = os.path.basename(self.reportee_file)
                if os.path.exists(self.reportee_file):
                    self.__Flag_reportee_file_path_exist = True
                    xlwb = xlrd.open_workbook(self.reportee_file)
                    input_worksheet = xlwb.sheet_by_index(0)

                    for row_id in range(1, input_worksheet.nrows):
                        row = input_worksheet.row(row_id)
                        filename = str(row[0].value).strip()
                        devname = str(row[1].value).strip()
                        email = str(row[2].value).strip()

                        if filename not in self.__reportee_list:
                            self.__reportee_list[filename] = []
                        self.__reportee_list[filename].append((devname, email))

                else:
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.recipient_file)
            read_log = open(self.log_file, 'r').readlines()

            for num, line in enumerate(read_log, 0):

                error = "((.*?).c)(\((\d+)\)):\serror\s([A-Z]\d+):\s\'.*\'\s:\s(.*)"

                m = re.match(error, line)

                if m is not None:

                    error_code = m.group(5)
                    message    = m.group(6).split(".")[0]
                    error_line = m.group(4)
                    filename   = m.group(1)

                    error_record = [filename, None, None, error_code, error_line, message]

                    if self.__Flag_reportee_file_var_exist and self.__Flag_reportee_file_path_exist:
                        names = []
                        if filename in self.__reportee_list:
                            for reportee in self.__reportee_list[filename]:
                                names.append(reportee)
                        else:
                            names.append(('<unknown>', None))

                        for name in names:
                            temp = list(error_record)
                            temp[1:3] = name
                            self.__record.append(temp)
                    else:
                        self.__record.append(error_record)
            self.__record.sort()

        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.log_file_name)

    def save_to_archive(self, output_file, type_value):
        is_new_file = False
        if not os.path.exists(output_file):
            is_new_file = True

        archive_file = open(output_file, 'a+', newline='', encoding='utf-8')
        writer = csv.writer(archive_file)

        if is_new_file:
            writer.writerow(['Date', 'Time', 'Build Type', 'File Name', 'Engineer Name', 'Error Code',
                             'Error Line', 'Message'])

        for file in range(len(self.__record)):

            row = [self.__timestamp_date, self.__timestamp_time, type_value, self.__record[file][0],
                        self.__record[file][1], self.__record[file][3], self.__record[file][4], self.__record[file][5]]
            writer.writerow(row)
        archive_file.close()
        return True

    def save_to_excel(self, destination_path):
        excel_workbook = Workbook(destination_path)
        excel_sheet = excel_workbook.add_worksheet()
        excel_format = excel_workbook.add_format({'bold': True, 'bg_color': 'yellow', 'border': 1})
        list_of_fields1 = ['File Name', 'Engineer Name', 'Error Code', 'Error Line', 'Error Message']
        list_of_fields2 = ['File Name', 'Error Command', 'Error code', 'Error Line', 'Error Message' ]

        if self.__Flag_reportee_file_var_exist:
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
            if self.__Flag_reportee_file_var_exist and self.__Flag_reportee_file_path_exist:
                item.append(record[1])
            item += record[3:]
            for col, value in enumerate(item):
                excel_sheet.write(row+1, col, value)
        return True

    def save_mailing_list(self, output_file, truncate=False) -> bool:

        emails = []

        #for record in self.__record:
         #  if record[1] is not None:
          #      emails.append(record[1])
        if '*' in self.__reportee_list:
            for reportee in self.__reportee_list['*']:
                emails.append(reportee[1])

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
            #return not self.__Flag_Licence_error and len(self.__record) == 0
            return True

    def set_forced_status(self, is_success: bool):
        self.__forced_status = is_success


OPT_HELP = "-h"
OPT_OUTPUT = "-o"
OPT_ARCHIVE = "-a"
OPT_EXCEL = "-s"
OPT_MAILING = "-r"
OPT_MAIL_BODY = "-m"
OPT_REPORTEE = "-e"
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
    reportee_file_path = None
    build_type = "U"

    try:
        opts, args = getopt(sys.argv[1:], "o:a:s:rm:e:t:f:")
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
            if not options.__contains__(OPT_REPORTEE):
                raise GetoptError("Generating mailing list needs engineer list")
            else:
                is_create_mailing_list = True

        # Save mail body
        if options.__contains__(OPT_MAIL_BODY):
            mail_template_file_path = options[OPT_MAIL_BODY]

        # Engineer list
        if options.__contains__(OPT_REPORTEE):
            reportee_file_path = options[OPT_REPORTEE]

        # Extra information
        if options.__contains__(OPT_BUILD_TYPE):
            build_type = options[OPT_BUILD_TYPE]

    except GetoptError as err:
        print(err)
        show_help()
        return ERROR_WRONG_OPTION

    try:
        if not os.path.exists(log_file_path):
            raise FileNotFoundError(log_file_path)

        if mail_template_file_path is not None and not os.path.exists(mail_template_file_path):
            raise FileNotFoundError(mail_template_file_path)

        if reportee_file_path is not None and not os.path.exists(reportee_file_path):
            raise FileNotFoundError(reportee_file_path)

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

    parser = BuildParser(log_file_path, reportee_file_path)
    if is_forced_fail:
        # Currently BuildParser can not get any cases of build error.
        # So make.py will pass "-f" option if it can't find output binaries.
        parser.set_forced_status(False)
    if output_file_path is not None:
        is_ok = is_ok & parser.save_build_status(output_file_path)
    if archiving_file_path is not None:
        is_ok = is_ok & parser.save_to_archive(archiving_file_path, build_type)
    if summary_file_path is not None:
        is_ok = is_ok & parser.save_to_excel(summary_file_path)
    if is_create_mailing_list:
        is_ok = is_ok & parser.save_mailing_list(output_file_path, is_truncate)
    if mail_template_file_path:
        jenkins = {}
        jenkins_params = [
            "SVN_URL",
            "BUILD_URL",
            "WORKSPACE",
            "JOB_URL", 'CLIENTNAME', 'BUILD_CAUSE', 'OS', 'PROCESSOR_ARCHITECTURE', 'COMPUTERNAME']
        for param in jenkins_params:
            if os.environ.__contains__(param):
                value = os.environ[param]
            else:
                value = "not available"
            jenkins[param] = value

        is_ok = is_ok & parser.save_mail_body(output_file_path,
                                              mail_template_file_path,
                                              is_truncate,
                                              jenkins)

    result = 0
    #if not parser.is_success():
     #   result = result | ERROR_COMPILE_FAIL
    #if not is_ok:
     #   result = result | ERROR_PROCESS_FAIL

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
           "            Set build result fail even there isn't any error.\n" \
           "-l          Option for link_template_error_list.\n" \
           "            Used as a reference for all the link errors.\n"
    print(text)


if __name__ == '__main__':
    ret_val = main()
    exit(ret_val)

