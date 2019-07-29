"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""

import csv
import html
import os
import re
import subprocess
import sys
import time
from enum import IntEnum, auto, Enum
from getopt import getopt
from typing import Optional

from mako.template import Template
from pyquery import PyQuery as pq

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from dbs import merge_dict, DBS
except ImportError:
    from DailyBuildSystem.dbs import merge_dict, DBS


class MetricCategory(Enum):
    # Metrics
    COMPLEXITY = 'Complexity'  # integer value
    FUNCTION_COVERAGE = 'Function Coverage'  # percentage
    FUNCTION_CALLS = 'Function Calls'  # covered / cases (rate%)
    STATEMENTS = 'Statements'  # covered / cases (rate%)
    BRANCHES = 'Branches'  # covered / cases (rate%)
    PAIRS = 'MC/DC Pairs'  # covered / cases (rate%)


class ArchivingHeader(IntEnum):
    date = 0
    time = auto()
    arg0 = auto()
    arg1 = auto()
    arg2 = auto()
    arg3 = auto()
    arg4 = auto()
    arg5 = auto()
    arg6 = auto()
    arg7 = auto()
    environment = auto()
    unit = auto()
    subprogram = auto()
    category = auto()
    value = auto()
    covered = auto()
    cases = auto()


RESULT_CAT_EXPECTED = 'Expected'
RESULT_CAT_CONTROL = 'Control Flow'
RESULT_CAT_METRICS = 'Metrics'

RESULT_UNIT = re.compile('Unit.*')
RESULT_SUBPROGRAM = re.compile('Subprogram.*')
RESULT_TC_NAME = re.compile('Test Case Name.*')

RESULT_TCS_HEADER = re.compile('Test Case Section : (.*)')
RESULT_TCS_RESULT = re.compile('(\(\s(\d+)\s/\s(\d+)\s\))?\s?(PASS|FAIL)')
RESULT_TCS_EXPECTED = re.compile('Expected Results matched.*')
RESULT_TCS_CONTROL = re.compile('Control Flow.*')
RESULT_TCS_STATUS = re.compile('Test Status.*')
RESULT_TCS_PASS = 'PASS'
RESULT_TCS_FAIL = 'FAIL'

RESULT_MET_HEADER = re.compile('Metrics')


class VectorCAST:
    def __init__(self, environment_path: str, environment_name: str):
        self._template_path = os.path.abspath(os.path.join(os.path.split(os.sys.argv[0])[0], 'resources', 'mail.VectorCAST.html'))
        self._environment_path = environment_path
        self._environment_name = environment_name
        self._timestamp_date = time.strftime('%Y-%m-%d')
        self._timestamp_time = time.strftime('%H:%M:%S')
        self._compiler_path = r'C:\Compiler\TASKING\TriCore_v5.0r2'
        self._t32sim_path = r'C:\T32sim'
        self._mail_template = os.path.join(os.path.split(sys.argv[0])[0], 'resources', 'mail.VectorCAST.html')
        self._CMD_PREFIX = '%VECTORCAST_DIR%\clicast -e ' + self._environment_name + ' '
        self._result = None

    def __error_check(self, output: str) -> int:
        """
        Parse output and get error if exists.\n
        :param output: Output stream text.
        :return: 0 if no error exists, otherwise non-zero value.\n
        \t1 = Can not get license.\n
        \t2 = Can not access to license server.\n
        """
        errors = {
            # Limit of license.
            1: [
                'FLEXlm Error: Licensed number of users already reached.',
            ],
            # License server down or connection error.
            2: [
                'FLEXlm Error: Cannot connect to license server system.',
            ],
        }

        for code in errors:
            for error in errors[code]:
                if output.find(error) >= 0:
                    return code

        return 0

    def set_compiler_path(self, path: str) -> 'VectorCAST':
        self._compiler_path = path
        return self

    def set_t32sim_path(self, path: str) -> 'VectorCAST':
        self._t32sim_path = path
        return self

    def launch(self) -> int:
        """
        :return:\n\n
        000. Success\n
        101. Can not update Test-Environment
        201. Can not execute test
        """
        # 0. initialize environment
        current_path = os.getcwd()
        os.chdir(self._environment_path)

        os.putenv('VCAST_T32_INSTALL_BASE', self._t32sim_path)
        os.putenv('VCAST_TASKING_TRICORE_INSTALL_BASE', self._compiler_path)
        os.putenv('PATH',
                  os.environ['PATH'] + r';%s\bin\windows64;%s\ctc\bin' % (self._t32sim_path, self._compiler_path))

        try:
            # # 1. Release lock if exists.
            # output_buffer = ''
            #
            # print("*** Check project lock ***")
            # print(os.getcwd() + '>' + self._CMD_PREFIX + '--release-locks')
            # p = subprocess.Popen(self._CMD_PREFIX + '--release-locks',
            #                      stdout=subprocess.PIPE,
            #                      stdin=subprocess.PIPE,
            #                      universal_newlines=True,
            #                      shell=True)
            # is_released = False
            # while p.poll() is None:
            #     ch = p.stdout.readline(1)
            #     if ch == '':
            #         continue
            #     elif ch != '\n':
            #         output_buffer += ch
            #     print(ch, end='')
            #     sys.stdout.flush()
            #
            #     # To prevent unlimited waiting for user-input,
            #     # Check output_buffer immediately after reading pipe.
            #     if error_code == 0:
            #         error_code = self.__error_check(output_buffer)
            #
            #     if output_buffer.find('Do you wish to continue? ( yes or no )') >= 0:
            #         print(' yes')
            #         sys.stdout.flush()
            #
            #         p.stdin.write('yes\n')
            #         p.stdin.flush()
            #
            #         output_buffer = ''
            #         is_released = True
            #
            #     if ch == '\n':
            #         output_buffer = ''
            #
            # if error_code == 0:
            #     if is_released:
            #         print('Lock released.')
            #     else:
            #         print('done.')
            # else:
            #     print('')
            #     return error_code
            # print('')

            err_a = -1
            err_b = -1
            err_c = -1
            # 2. Recompile
            err_a = os.system(self._CMD_PREFIX + 'EN Incremental Rebuild')
            if err_a > 0:
                # 2.1. Build environment
                err_b = os.system(self._CMD_PREFIX + 'EN RE_build')

                # Fail to update Test-Environment
                if err_b > 0:
                    return 100 + err_b

            # 3. Execute test
            err_c = os.system(self._CMD_PREFIX + 'execute batch')
            if err_c > 0:
                return 200 + err_c
            else:
                return 0
        finally:
            # Always recover previous status.
            if err_c != 0:
                final_result = 'FAIL'
            else:
                final_result = ' OK '
            print('[%s] CLI Code: %d / %d / %d' % (final_result, err_a, err_b, err_c))

            os.chdir(current_path)

    def generate_full_report(self, full_report: str) -> int:
        dst = os.path.abspath(full_report)

        current_path = os.getcwd()
        os.chdir(self._environment_path)
        cmd_generate_report = self._CMD_PREFIX + 'reports custom full ' + dst
        exit_code = os.system(cmd_generate_report)
        os.chdir(current_path)

        return exit_code

    def analyze_full_report(self, full_report: str) -> Optional[dict]:
        """
        Structure of result :
        {
            'Unit 1' : {
                'Subprogram 1' : {
                    'Expected' : {
                        TC 1 : (matched, cases, PASS|FAIL),
                        TC 2 : (matched, cases, PASS|FAIL),
                        ...
                    },
                    'Control Flow' : {
                        TC 1 : ( Covered, Cases ),
                        ...
                    },
                    'Metrics' : {
                        MetricCategory 1 : ( Covered, Cases ),
                        MetricCategory 2 : ( Covered, Cases ),
                        ...
                    }
                },
                'Subprogram 2' : {
                    ...
                },
                ...
            },
            'Unit 2' : {
                ...
            },
            '' : {
                '<<COMPOUND>>' : {
                    'Expected' : {
                        '<<COMPOUND>>.001' : (100, 100, PASS),
                        '<<COMPOUND>>.002' : (0, 0, PASS),
                        '<<COMPOUND>>.003' : (24, 25, FAIL),
                        ...
                    }
                }
            }
        }
        """

        def get_tc_status(table_tcs) -> dict:
            unit = ''
            subprogram = ''
            tcs_name = ''

            # Get TC configuration
            config_rows = table_tcs('table > tr:last table:eq(1) > tr:last table > tr')
            for i in range(len(config_rows)):
                row = config_rows.eq(i)
                category = row('td:eq(0)').text()
                value = row('td:eq(1)').text()

                if RESULT_UNIT.match(category):
                    unit = value
                elif RESULT_SUBPROGRAM.match(category):
                    subprogram = value
                elif RESULT_TC_NAME.match(category):
                    tcs_name = value

            tcs_result = {unit: {subprogram: {}}}
            # result = {unit: { subprogram: {RESULT_CAT_EXPECTED: {}}}}
            # expected = result[unit][subprogram][RESULT_CAT_EXPECTED]

            # Get TCS result
            result_rows = table_tcs('table > tr:last table:last > tr:last table table:last > tr')
            for i in range(1, len(result_rows)):
                row = result_rows.eq(i)
                category_text = row('td:eq(0)').text()
                result_text = row('td:eq(1)').text()

                if RESULT_TCS_EXPECTED.match(category_text):
                    tcs_result[unit][subprogram][RESULT_CAT_EXPECTED] = {}
                    dst = tcs_result[unit][subprogram][RESULT_CAT_EXPECTED]
                elif RESULT_TCS_CONTROL.match(category_text):
                    tcs_result[unit][subprogram][RESULT_CAT_CONTROL] = {}
                    dst = tcs_result[unit][subprogram][RESULT_CAT_CONTROL]
                elif RESULT_TCS_STATUS.match(category_text):
                    continue
                else:
                    raise NotImplementedError(category_text)

                m = re.match(RESULT_TCS_RESULT, result_text)
                if m is not None:
                    conclusion = m.group(4) == RESULT_TCS_PASS
                    passed = 0
                    if m.group(2) is not None:
                        passed = int(m.group(2))
                    cases = 0
                    if m.group(3) is not None:
                        cases = int(m.group(3))
                    dst[tcs_name] = (passed, cases, conclusion)

            return tcs_result

        def get_metrics(table_metrics) -> dict:
            rows = table_metrics('table > tr:last table > tr')
            current_unit = None

            # Read first row to get columns
            categories = []
            headers = rows.eq(0)('td')

            # Return nothing without any metric information
            if RESULT_UNIT.match(headers.eq(0).text()) is None or RESULT_SUBPROGRAM.match(headers.eq(1).text()) is None:
                return {}

            for i in range(2, len(headers)):
                header = headers.eq(i).text().upper().replace(' ', '_')
                assert MetricCategory.__members__.keys().__contains__(header)
                categories.append(MetricCategory[header])

            metrics = {}
            for i in range(1, len(rows)):
                row = rows.eq(i)
                cols = row.children('td')

                unit = cols.eq(0).text()
                subprogram = cols.eq(1).text()

                if unit == 'TOTALS':
                    pass  # print(unit)
                elif unit == 'GRAND TOTALS':
                    pass  # print(unit)
                elif unit == '' and subprogram == '':
                    pass  # print("blank line")
                else:
                    if unit != '':
                        metrics[unit] = {}
                        current_unit = metrics[unit]
                    metric = {}
                    for i in range(0, len(categories)):
                        cat = categories[i]
                        value = cols.eq(i + 2).text()
                        if cat == MetricCategory.COMPLEXITY:
                            metric[cat] = int(value)
                        elif cat == MetricCategory.FUNCTION_COVERAGE:
                            metric[cat] = [int(int(value.replace('%', '')) / 100), 1]
                        else:
                            value_set = parse_result_value(value, is_nullable=True)
                            if value_set is None:
                                continue
                            else:
                                metric[categories[i]] = value_set

                    current_unit[subprogram] = {}
                    current_unit[subprogram][RESULT_CAT_METRICS] = metric
            return metrics

        def parse_result_value(text: str, is_nullable: bool = False) -> Optional[tuple]:
            r = re.compile('(\d+)\s+/\s+(\d+)')
            m = r.match(text)
            if m is not None:
                return int(m.group(1)), int(m.group(2))
            elif is_nullable:
                return None
            else:
                return 0, 0

        content = ''
        try:
            with open(full_report) as f:
                while True:
                    lines = f.readline(1024 * 1024)
                    if lines == '':
                        break
                    else:
                        content += lines
        except OSError as err:
            print(err)
            return None
        html = pq(content.replace('&nbsp;', ' '))

        # Group 별로 iteration 해보자
        result = dict()
        tables = html('body > table')
        for i in range(len(tables)):
            table = tables.eq(i)
            table_header = table.children('tr').eq(0).text()

            if RESULT_TCS_HEADER.match(table_header):
                result = merge_dict(result, get_tc_status(table))
            elif RESULT_MET_HEADER.match(table_header):
                result = merge_dict(result, get_metrics(table))

        self._result = result

    def generate_summary(self, output_path: str, status: DBS.Section, extras: list = None, rank: int = 10) -> bool:
        args = {
            'date': self._timestamp_date,
            'time': self._timestamp_time,
            'status': status,
        }

        # 메일링 로직 수정 필요
        if 'SERVICE_ID' in os.environ and os.environ['SERVICE_ID'] == 'Jenkins':
            jenkins = {}
            jenkins_params = [
                "SVN_URL",
                "SVN_REVISION",
                "BUILD_URL",
                "WORKSPACE",
                "JOB_URL"]
            for param in jenkins_params:
                if param in os.environ:
                    value = os.environ[param]
                else:
                    value = "not available"
                jenkins[param] = value
            args['jenkins'] = jenkins

        if extras is not None:
            args['extras'] = extras

        if status == DBS.Status.SUCCESS:
            # Check available data
            itr_target = {}
            itr_available = {
                RESULT_CAT_EXPECTED: False,
                RESULT_CAT_CONTROL: False
            }

            metric_target = {}
            metric_available = {}
            for metric in MetricCategory:
                metric_available[metric.value] = False

            summary = {}
            # Summarize by unit
            for unit in self._result:
                unit_name = unit
                for subprogram in self._result[unit]:
                    if unit_name == '':
                        unit_name = subprogram
                    if not summary.__contains__(unit_name):
                        summary[unit_name] = {}

                    for category in self._result[unit][subprogram]:
                        if category != RESULT_CAT_METRICS:
                            summary_category = category
                            itr_available[summary_category] = True
                            itr_target[unit_name] = None

                        for key in self._result[unit][subprogram][category]:
                            if category == RESULT_CAT_METRICS:
                                summary_category = key.value
                                metric_available[summary_category] = True
                                metric_target[unit_name] = None

                            if not summary[unit_name].__contains__(summary_category):
                                summary[unit_name][summary_category] = [0, 0]

                            source = self._result[unit][subprogram][category][key]

                            if summary_category == MetricCategory.COMPLEXITY.value:
                                summary[unit_name][summary_category][0] += source
                            else:
                                summary[unit_name][summary_category][0] += source[0]
                                summary[unit_name][summary_category][1] += source[1]

            # Prepare data for summary report.
            overall = {}
            itr_index = {}
            for itr in itr_available:
                if itr_available[itr]:
                    index = len(itr_index)
                    itr_index[itr] = index
                    overall[itr] = [0, 0]
            for unit in itr_target:
                itr_target[unit] = [[0, 0] for i in range(len(itr_index))]

            metric_index = {}
            for metric in metric_available:
                if metric_available[metric]:
                    index = len(metric_index)
                    metric_index[metric] = index
                    overall[metric] = [0, 0]
            for unit in metric_target:
                metric_target[unit] = [[0,0] for i in range(len(metric_index))]

            for unit in summary:
                for category in summary[unit]:
                    value = summary[unit][category]

                    overall[category][0] += value[0]
                    overall[category][1] += value[1]

                    if category in itr_index.keys():
                        dst = itr_target
                        index = itr_index
                    else:
                        dst = metric_target
                        index = metric_index
                    dst[unit][index[category]][0] += value[0]
                    dst[unit][index[category]][1] += value[1]

             # Fill mako arguments
            args['overall'] = {}
            for category in overall:
                if category == MetricCategory.COMPLEXITY.value:
                    continue
                cover = overall[category][0]
                case = overall[category][1]
                coverage = int(cover / case * 100)
                args['overall'][category] = {
                        'value': '%3d%% (%d / %d)' % (coverage, cover, case),
                        'pass': cover == case
                    }

            result_set = [
                ('itr', itr_index, itr_target),
                ('metrics', metric_index, metric_target),
            ]

            for result in result_set:
                type = result[0]
                index = result[1]
                target = result[2]

                if len(target) > 0:
                    args[type] = {'header': [], 'values': {}}
                    for key in index:
                        args[type]['header'].append(key)

                    # Preparing for testing multiple environments
                    args[type]['values'][self._environment_name] = {}
                    for unit in target:
                        unit_name = html.escape(unit)

                        args[type]['values'][self._environment_name][unit_name] = []
                        src = target[unit]
                        dst = args[type]['values'][self._environment_name][unit_name]
                        for i in range(len(index)):
                            if src[i][0] == 0 and src[i][1] == 0:
                                value = None
                            elif src[i][1] == 0:
                                value = {
                                    'value': '%s' % src[i][0],
                                    'pass': None
                                }
                            else:
                                cover = src[i][0]
                                case = src[i][1]
                                coverage = int(cover / case * 100)
                                value = {
                                    'value': '%3d%% (%s / %s)' % (coverage, cover, case),
                                    'pass': src[i][0] == src[i][1]
                                }
                            dst.append(value)
        # Render!
        tmpl = Template(filename=self._template_path, input_encoding='utf-8')
        DBS.set_mail_body(output_path, tmpl.render(args=args))

        return True

    def archive(self, dst: str, args: list = None) -> bool:
        if self._result is None:
            return False

        common = [''] * 11
        common[0] = self._timestamp_date
        common[1] = self._timestamp_time
        if args is not None:
            for i in range(len(args)):
                common[i + 2] = args[i]
        common[10] = self._environment_name
        try:
            f = open(dst, 'a+', newline='')
        except OSError as err:
            print(err)
            return False
        else:
            with f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    # if it is a new file
                    header = []
                    for h in ArchivingHeader:
                        header.append(h.name)
                    writer.writerow(header)

                for unit in self._result:
                    for subprogram in self._result[unit]:
                        target = self._result[unit][subprogram]

                        for category in target:
                            if category == RESULT_CAT_EXPECTED or category == RESULT_CAT_CONTROL:
                                # 1. Get summary of TCS if exists and write
                                tcs_result = target[category]

                                covered = 0
                                cases = 0
                                for tc in tcs_result:
                                    covered += tcs_result[tc][0]
                                    cases += tcs_result[tc][1]
                                row = list(common)
                                row.append(unit)
                                row.append(subprogram)
                                row.append(category)
                                row.append('')
                                row.append(covered)
                                row.append(cases)
                                writer.writerow(row)
                            elif category == RESULT_CAT_METRICS:
                                # 2. Write metric if exists
                                metric = target[RESULT_CAT_METRICS]

                                for category in metric:
                                    row = list(common)
                                    row.append(unit)
                                    row.append(subprogram)
                                    row.append(category.value)

                                    if category == MetricCategory.COMPLEXITY:
                                        row.append(metric[category])
                                        row.append('')
                                        row.append('')
                                    else:
                                        row.append('')
                                        row.append(metric[category][0])
                                        row.append(metric[category][1])
                                    writer.writerow(row)
        return True


RETRY_MAX = 2
RETRY_DELAY = 3

OPT_HELP = "-h"
OPT_ARCHIVE = "-a"
OPT_COMPILER = "-t"
OPT_REPORT = "-r"
OPT_OUTPUT = "-o"
OPT_ARG0 = "-0"
OPT_ARG1 = "-1"
OPT_ARG2 = "-2"
OPT_ARG3 = "-3"
OPT_ARG4 = "-4"
OPT_ARG5 = "-5"
OPT_ARG6 = "-6"
OPT_ARG7 = "-7"


def main():
    def show_help():
        text = "\n\n" \
               "VectorCAST launcher\n" \
               "\n" \
               "Usage :\n" \
               "vectorcast.py {options} {Project environment file}\n" \
               "\n" \
               "Exit code is 0 if VectorCAST runs successfully, otherwise non-zero value.\n" \
               "\n" \
               "Options :\n" \
               "-h          Show help\n" \
               "            Show this help menu.\n" \
               "-t{path}    Specify path of Tasking Compiler.\n" \
               "            Default path of Tasking Compiler is \"C:\\Compiler\\TASKING\\TriCore_v5.0r2\\ctc\\bin\\ctc.exe\".\n" \
               "-a{path}    Path of archiving file.\n" \
               "            This option archives VectorCAST result log.\n" \
               "-r{path}    Path of report file.\n" \
               "            This option specify the name of outout report file.\n" \
               "            Default : <Current Working Dir>\\<EnvName>_full_report.html\n" \
               "-[n]{text}  Extra arguments for archiving\n" \
               "            Archiving file may contains up to 8 arguments to specify build environment.\n" \
               "            User can put those values through 0 ~ 7.\n"
        print(text)

    options = {}
    try:
        opts, args = getopt(sys.argv[1:], "ha:r:o:t:0:1:2:3:4:5:6:7:")
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP) or len(options) == 0 and len(args) == 0:
            show_help()
            return True

        if len(args) != 1:
            show_help()
            return False
        else:
            arguments = args
    except IndexError or ValueError:
        show_help()
        return False
    except OSError as err:
        print(err)
        return False

    if not os.path.isfile(arguments[0]):
        return False

    environment_path = os.path.split(arguments[0])[0]
    environment_name = os.path.splitext(os.path.split(arguments[0])[1])[0]
    compiler_path = None
    archive_path = None
    report_path = os.path.join(os.getcwd(), environment_name + "_full_report.html")
    output_path = None

    if options.__contains__(OPT_COMPILER):
        compiler_path = options[OPT_COMPILER]

    if options.__contains__(OPT_ARCHIVE):
        archive_path = options[OPT_ARCHIVE]

    if options.__contains__(OPT_REPORT):
        report_path = options[OPT_REPORT]

    if options.__contains__(OPT_OUTPUT):
        output_path = options[OPT_OUTPUT]

    extras = [''] * 8
    pattern_args = re.compile("-(\d)")
    for option in options:
        m = pattern_args.match(option)
        if m:
            extras[int(m.group(1))] = options[option]

    v = VectorCAST(environment_path, environment_name)
    if compiler_path is not None:
        v.set_compiler_path(compiler_path)

    is_analyzed = False
    error_code = 0
    for i in range(RETRY_MAX + 1):
        error_code = v.launch()
        is_analyzed = error_code == 0

        # License error --> continue
        # elif error_code == 1:
        #     if i < RETRY_MAX:
        #         print('Retry(%d/%d) in %d seconds.' % (i + 1, RETRY_MAX, RETRY_DELAY))
        #         time.sleep(RETRY_DELAY)
        #         print('')
        #     else:
        #         print('Fail to get license.')
        #     continue
        # else:
        #     print("License server error. Job terminated.")
        #     break

        break

    if is_analyzed:
        # Generate full-report
        v.generate_full_report(report_path)

        # Analyze full-report
        v.analyze_full_report(report_path)

        # Archive result
        if archive_path is not None:
            v.archive(archive_path, extras)
    if error_code == 0:
        status = DBS.Status.SUCCESS
    else:
        status = DBS.Status.FAIL
    # UNSTABLE shall be defined in the future.

    # if error_code == 0:
    #     status = DBS.Status.SUCCESS
    # elif error_code < 199:
    #     status = DBS.Status.FAIL
    # else:
    #     status = DBS.Status.UNSTABLE

    # Save result
    if output_path is not None:
        DBS.set_vectorcast_status(output_path, status)

    # Generate summary
    if output_path is not None:
        v.generate_summary(output_path, status)

    return error_code


if __name__ == '__main__':
    ret_val = main()
    exit(ret_val)
