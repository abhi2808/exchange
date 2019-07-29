"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""


import sys
import os
import csv
import matlab.engine
import io
import re
import configparser
import errno
import time
import xlrd
from xlsxwriter import *
from mako.template import Template
from getopt import getopt, GetoptError


sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..\..'))
try:
    from dbs import DBS
except ImportError:
    from dailybuildsystem.dbs import DBS


class Matlab:

    MATLAB_STATUS = "dbs_matlab_status"

    def __init__(self):

        self.__log = None
        self.__model_path = None
        self.__eng = None
        self.__model = ""
        self.__subsystem = ""
        self.__timestamp_date = time.strftime("%Y-%m-%d")
        self.__timestamp_time = time.strftime("%H:%M:%S")
        self.__Flag_reportee_file_var_exist = False
        self.__Flag_reportee_file_path_exist = False
        self.__record = []
        self.__reportee_list = {}


    def start(self, model_path):

        self.__model_path = model_path
        self.__eng = matlab.engine.start_matlab('-nodesktop')
        self.__eng.addpath('{}'.format(self.__model_path), nargout=0)

    def buildmodel(self, model,  subsystem, logfile_path):

        self.__model = model
        self.__log = logfile_path
        log = io.StringIO()
        self.__eng.open('{}'.format(self.__model))
        self.__model = self.__model.split('.')[0]
        self.__subsystem = str(self.__model + "/" + subsystem)
        self.__eng.Simulink.fileGenControl('set', 'CacheFolder', '{}'.format(self.__model_path), 'CodeGenFolder', '{}'.format(self.__model_path), nargout=0)
        self.__eng.rtwbuild('{}'.format(self.__subsystem), stdout=log, nargout=0)
        with open('{}'.format(self.__log), 'w') as f:
            f.write(log.getvalue())

    def stop(self):
        self.__eng.quit()


    def parse_log(self, reportee_file, logfile_path):


        self.__log = logfile_path

        if os.path.exists(self.__log):

            if reportee_file is not None:
                self.__Flag_reportee_file_var_exist = True
                recipient_file = os.path.basename(reportee_file)
                if os.path.exists(reportee_file):
                    self.__Flag_reportee_file_path_exist = True
                    xlwb = xlrd.open_workbook(reportee_file)
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
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), recipient_file)
            read_log = open(self.__log, 'r').readlines()

            for num, line in enumerate(read_log, 0):

                error = "### (Successful completion of code generation for model):\s(.*)"

                m = re.match(error, line)

                if m is not None:

                    message = m.group(1)
                    modelname = m.group(2)

                    error_record = [modelname, None, None, message]

                    if self.__Flag_reportee_file_var_exist and self.__Flag_reportee_file_path_exist:
                        names = []
                        if modelname in self.__reportee_list:
                            for reportee in self.__reportee_list[modelname]:
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
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.__log)

    def save_to_archive(self, output_file, type_value):
        is_new_file = False
        if not os.path.exists(output_file):
            is_new_file = True

        archive_file = open(output_file, 'a+', newline='', encoding='utf-8')
        writer = csv.writer(archive_file)

        if is_new_file:
            writer.writerow(['Date', 'Time', 'Build Type', 'File Name', 'Engineer Name', 'Message'])

        for file in range(len(self.__record)):

            row = [self.__timestamp_date, self.__timestamp_time, type_value, self.__record[file][0],
                        self.__record[file][1], self.__record[file][3]]
            writer.writerow(row)
        archive_file.close()
        return True

    def save_to_excel(self, destination_path):
        excel_workbook = Workbook(destination_path)
        excel_sheet = excel_workbook.add_worksheet()
        excel_format = excel_workbook.add_format({'bold': True, 'bg_color': 'yellow', 'border': 1})
        list_of_fields1 = ['Model Name', 'Engineer Name', 'Message']
        list_of_fields2 = ['Model Name', 'Engineer Name', 'Message']

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
            item += record[1:]
            for col, value in enumerate(item):
                excel_sheet.write(row+1, col, value)
        return True

    def save_mailing_list(self, output_file, truncate=False) -> bool:

        emails = []

        for record in self.__record:
           if record[1] is not None:
                emails.append(record[1])
        if '*' in self.__reportee_list:
            for reportee in self.__reportee_list['*']:
                emails.append(reportee[1])

        return DBS.set_mail_recipients(output_file, sorted(set(emails)), truncate)

    def save_mail_body(self, output_file, mako_template, truncate=False, jenkins=None):
        mako_template = os.path.abspath(mako_template)

        if os.path.exists(mako_template):
            build_args = {
                "date": self.__timestamp_date,
                "time": self.__timestamp_time,
                "jenkins": jenkins,
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
            current_body = template.render_unicode(is_success=True, args=build_args)
            return DBS.set_mail_body(output_file, current_body, truncate)
        else:
            return False

    def save_build_status(self, output_file_path: str) -> bool:

        build_status = "SUCCESS"

        parser = configparser.RawConfigParser()
        parser.read(output_file_path, encoding='utf-8')
        if not parser.has_section(DBS.Section.BUILD):
            parser.add_section(DBS.Section.BUILD)
        parser.set(DBS.Section.BUILD, Matlab.MATLAB_STATUS, build_status)
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                parser.write(f)
            return True

        except:
            return False


OPT_HELP = "-h"
OPT_MODEL = "-m"
OPT_MODEL_PATH = "-p"
OPT_LOG_FILE = "-l"
OPT_SUBSYSTEM = "-s"
OPT_REPORTEE_FILE = "-f"
OPT_MATLAB_REPORT = "-r"
OPT_MATLAB_SUMMARY = "-x"
OPT_OUTPUT= "-o"
OPT_MAIL_BODY= "-b"

def main() -> int:

    subsystem = None
    model = None
    logfile_path = None
    model_path = None
    reportee_file = None
    matlab_report_file = None
    matlab_summary = None
    output_file = None
    mail_template = None


    try:
        opts, args = getopt(sys.argv[1:], "h:m:p:l:s:f:r:x:o:b:")
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True

        if  options.__contains__(OPT_MODEL):
            model = options[OPT_MODEL]

        if not options.__contains__(OPT_LOG_FILE):
            raise GetoptError("No logfile path found.")
        else:
            logfile_path = options[OPT_LOG_FILE]

        if not options.__contains__(OPT_MODEL_PATH):
            raise GetoptError("No models to generate code found")
        else:
            model_path = options[OPT_MODEL_PATH]

        if options.__contains__(OPT_SUBSYSTEM):
            subsystem = options[OPT_SUBSYSTEM]

        if options.__contains__(OPT_REPORTEE_FILE):
            reportee_file = options[OPT_REPORTEE_FILE]

        if options.__contains__(OPT_MATLAB_REPORT):
            matlab_report_file = options[OPT_MATLAB_REPORT]

        if options.__contains__(OPT_MATLAB_SUMMARY):
            matlab_summary = options[OPT_MATLAB_SUMMARY]

        if options.__contains__(OPT_OUTPUT):
            output_file = options[OPT_OUTPUT]

        if options.__contains__(OPT_MAIL_BODY):
            mail_template = options[OPT_MAIL_BODY]

    except GetoptError as err:
        print(err)

    mat = Matlab()
    mat.start(model_path)
    mat.buildmodel(model, subsystem, logfile_path)
    mat.stop()
    mat.parse_log(reportee_file, logfile_path)
    mat.save_build_status(output_file)
    mat.save_to_archive(matlab_report_file, "U")
    mat.save_to_excel(matlab_summary)
    mat.save_mailing_list(output_file)

    jenkins = {}
    jenkins_params = [
        "BUILD_URL",
        "GIT_BRANCH",
        "GIT_URL",
        "BUILD_CAUSE",
        "BUILD_NUMBER", 'COMPUTERNAME', 'JOB_BASE_NAME', 'NODE_NAME', 'USERNAME']
    for param in jenkins_params:
        if os.environ.__contains__(param):
            value = os.environ[param]
        else:
            value = "not available"
        jenkins[param] = value

    mat.save_mail_body(output_file, mail_template, False, jenkins)

    return 0


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







