import csv
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from enum import IntEnum, auto, Enum
from getopt import getopt
from operator import itemgetter

import xlsxwriter
from mako.template import Template

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from dbs import DBS, traverse_list
except ImportError:
    from DailyBuildSystem.dbs import DBS, traverse_list

MACRO_CM_FUNC = '''
STAKI = auto()
STAV1 = auto()
STAV2 = auto()
STAV3 = auto()
STBAK = auto()
STCAL = auto()
STCYC = auto()
STELF = auto()
STFN1 = auto()
STFN2 = auto()
STGTO = auto()
STKDN = auto()
STKNT = auto()
STLCT = auto()
STLIN = auto()
STLOP = auto()
STM07 = auto()
STM19 = auto()
STM29 = auto()
STMCC = auto()
STMIF = auto()
STPAR = auto()
STPBG = auto()
STPDN = auto()
STPTH = auto()
STRET = auto()
STST1 = auto()
STST2 = auto()
STST3 = auto()
STSUB = auto()
STUNR = auto()
STUNV = auto()
STXLN = auto()
STFDN = auto()
STFDT = auto()
'''

MACRO_CM_FILE = '''
STBME = auto()
STBMO = auto()
STBMS = auto()
STBUG = auto()
STCDN = auto()
STDEV = auto()
STDIF = auto()
STECT = auto()
STEFF = auto()
STFCO = auto()
STFNC = auto()
STHAL = auto()
STM20 = auto()
STM21 = auto()
STM22 = auto()
STM28 = auto()
STM33 = auto()
STOPN = auto()
STOPT = auto()
STSCT = auto()
STSHN = auto()
STTDE = auto()
STTDO = auto()
STTDS = auto()
STTLN = auto()
STTOT = auto()
STTPP = auto()
STVAR = auto()
STVOL = auto()
STZIP = auto()
'''

MACRO_ARCHIVE_COMMON = '''
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
rule = auto()
filename = auto()
'''


class CmCriteria(Enum):
    REQUIRED = auto()
    ADVISORY = auto()


CM_CRITERIA_FUNC_MANDO = {
    "STCYC": [CmCriteria.REQUIRED, 0, 10],
    "STGTO": [CmCriteria.REQUIRED, 0, 0],
    "STMIF": [CmCriteria.REQUIRED, 0, 4],
    "STPTH": [CmCriteria.REQUIRED, 1, 80],
    "STRET": [CmCriteria.REQUIRED, 0, 5],
    "STST3": [CmCriteria.REQUIRED, 0, 50],
}


CM_METRIC_SKIP = [
    # Project metrics
    'STNRA',
    'STNEA',
    'STNFA',
    'STCYA',
    'STNGV',

    # QA-C 9 Extended metrics(?)
    'STCBO',
    'STWMC',
    'STNOC',
    'STRFC',
    'STLCM',
]

class CmFunc(IntEnum):
    # Function-based
    DUMMY = 0
    exec(MACRO_CM_FUNC)


class CmFile(IntEnum):
    # File-based
    DUMMY = 0
    exec(MACRO_CM_FILE)


class ArchHeaderFile(IntEnum):
    exec(MACRO_ARCHIVE_COMMON)
    exec(MACRO_CM_FILE)


class ArchHeaderFunc(IntEnum):
    exec(MACRO_ARCHIVE_COMMON)
    function = auto()
    exec(MACRO_CM_FUNC)


class ArchHeaderMisra(IntEnum):
    exec(MACRO_ARCHIVE_COMMON)
    major = auto()
    minor = auto()
    count = auto()
    message = auto()


class QAC:
    CmSource = "STFIL"
    CmName = "STNAM"
    CmEtc = [
        "STNTB",
        "STTKB",
        "STBCS",
        "STCOM",
    ]
    regex_int = re.compile('^\d+$')
    regex_float = re.compile('^\d+\.\d+$')

    def __init__(self, path: str):
        self._template_path = os.path.abspath(os.path.join(os.path.split(os.sys.argv[0])[0], 'resources', 'mail.QAC.html'))
        self._project_root = path
        self._timestamp_date = time.strftime("%Y-%m-%d")
        self._timestamp_time = time.strftime("%H:%M:%S")
        self._misra_rule = None
        self._misra_violations = None
        self._code_metrics = None

    def __make_common(self, args: list) -> list:
        common = [""] * 11
        common[0] = self._timestamp_date
        common[1] = self._timestamp_time
        if args is not None:
            for i in range(len(args)):
                common[i + 2] = args[i]

        common[2 + len(args)] = self._misra_rule
        return common

    def archive_file_based(self, path: str, args: list = None) -> bool:
        if self._code_metrics is None:
            return False

        common = self.__make_common(args)
        try:
            f = open(path, 'a+', newline='')
        except OSError as err:
            print(err)
            return False
        else:
            with f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    # if it is a new file
                    header = []
                    for h in ArchHeaderFile:
                        header.append(h.name)
                    writer.writerow(header)

                for filename in self._code_metrics:
                    writer.writerow(common + [filename] + self._code_metrics[filename][0][1:])

            return True

    def archive_func_based(self, path: str, args: list = None) -> bool:
        if self._code_metrics is None:
            return False

        common = self.__make_common(args)
        try:
            f = open(path, 'a+', newline='')
        except OSError as err:
            print(err)
            return False
        else:
            with f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    # if it is a new file
                    header = []
                    for h in ArchHeaderFunc:
                        header.append(h.name)
                    writer.writerow(header)

                for filename in self._code_metrics:
                    for function in self._code_metrics[filename][1]:
                        writer.writerow(common + [filename, function] + self._code_metrics[filename][1][function][1:])

            return True

    def archive_misra(self, path: str, args: list = None) -> bool:
        if self._misra_violations is None:
            return False

        common = self.__make_common(args)
        try:
            f = open(path, 'a+', newline='')
        except OSError as err:
            print(err)
            return False
        else:
            with f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    # if it is a new file
                    header = []
                    for h in ArchHeaderMisra:
                        header.append(h.name)
                    writer.writerow(header)

                for filename in self._misra_violations:
                    majors = list(self._misra_violations[filename].keys())
                    majors.sort()
                    for major in majors:
                        minors = list(self._misra_violations[filename][major])
                        minors.sort()
                        for minor in minors:
                            for violation in self._misra_violations[filename][major][minor]:
                                writer.writerow(common + [filename, major, minor] + violation)

            return True

    def generate_report(self, filepath: str, args: list = None) -> bool:
        if os.path.exists(filepath):
            os.remove(filepath)
        wb = xlsxwriter.Workbook(filepath)
        format_header = wb.add_format({'border': 1, 'bg_color': 'yellow'})
        format_cell = wb.add_format({'border': 1})

        if self._misra_violations is not None:
            ws_header = ['Full path', 'File name', 'Rule', 'Count', 'Message']
            ws_content = []

            ws = wb.add_worksheet('MISRA-C %s' % self._misra_rule)
            ws.write_row('A1', ws_header, format_header)

            for fullpath in self._misra_violations:
                filename = os.path.split(fullpath)[1]
                row_common = [fullpath, filename]
                for major in self._misra_violations[fullpath]:
                    for minor in self._misra_violations[fullpath][major]:
                        rule_name = '%d.%d' % (major, minor)
                        for violation in self._misra_violations[fullpath][major][minor]:
                            row = [] + row_common + [rule_name] + violation
                            ws_content.append(row)

            for i in range(len(ws_content)):
                ws.write_row('A%d' % (i + 2), ws_content[i], format_cell)

        if self._code_metrics is not None:
            # Distinguish required and advisory metric for Mando rule
            class FuncMetric(IntEnum):
                exec(MACRO_CM_FUNC)

            metric_required = {}
            metric_advisory = {}
            for metric in FuncMetric:
                metric_advisory[metric.name] = metric.value
            for metric in CM_CRITERIA_FUNC_MANDO:
                metric_required[metric] = metric_advisory[metric]
                metric_advisory.pop(metric)

            ws_header = ['Full path', 'File name', 'Function']
            for metric in metric_required:
                ws_header.append(metric)
            for metric in metric_advisory:
                ws_header.append(metric)
            ws_content = []

            ws = wb.add_worksheet('Code metric')
            ws.write_row('A1', ws_header, format_header)

            for fullpath in self._code_metrics:
                if len(self._code_metrics[fullpath][1]) == 0:
                    continue

                filename = os.path.split(fullpath)[1]
                row_common = [fullpath, filename]
                for function in self._code_metrics[fullpath][1]:
                    row = [] + row_common
                    metrics = self._code_metrics[fullpath][1][function]

                    row.append(function)
                    for metric in metric_required:
                        row.append(metrics[metric_required[metric]])
                    for metric in metric_advisory:
                        row.append(metrics[metric_advisory[metric]])
                    ws_content.append(row)

            for i in range(len(ws_content)):
                ws.write_row('A%d' % (i + 2), ws_content[i], format_cell)

        wb.close()

        return True

    def generate_summary(self, output_path: str, extras: list = None, rank: int = 10) -> bool:
        if self._misra_violations is None and self._code_metrics is None:
            return False

        args = {
            'date': self._timestamp_date,
            'time': self._timestamp_time,
        }

        # 메일링 로직 수정 필요
        if os.environ.__contains__('SERVICE_ID') and os.environ.get('SERVICE_ID') == 'Jenkins':
            args['jenkins'] = {}
            if os.environ.__contains__('SVN_REVISION'):
                args['jenkins']['SVN_REVISION'] = os.environ.get('SVN_REVISION')
            if os.environ.__contains__('SVN_URL'):
                args['jenkins']['SVN_URL'] = os.environ.get('SVN_URL')
        if extras is not None:
            args['extras'] = extras

        if self._misra_violations is not None:
            args['misra'] = {}
            args['misra']['rule'] = self._misra_rule
            args['misra']['violations'] = []

            totals = []
            for filename in self._misra_violations:
                total = 0
                rules = {}
                for major in self._misra_violations[filename]:
                    for minor in self._misra_violations[filename][major]:
                        for violation in self._misra_violations[filename][major][minor]:
                            rule = '%d.%d' % (major, minor)
                            if not rules.__contains__(rule):
                                rules[rule] = 0
                            rules[rule] += violation[0]
                            total += violation[0]

                if total > 0:
                    rules = sorted(rules.items(), key=itemgetter(1), reverse=True)
                    totals.append((total, os.path.split(filename)[1], rules))

            totals.sort(reverse=True)
            totals = totals[:rank]
            for total in totals:
                sum = {}
                sum['filename'] = total[1]
                sum['count'] = total[0]
                sum['rules'] = []

                for rule in total[2][:5]:
                    sum['rules'].append('%s(%d)' % (rule[0], rule[1]))
                if len(total[2]) > 5:
                    sum['rules'].append('...')

                args['misra']['violations'].append(sum)

        if self._code_metrics is not None:
            args['codemetric'] = {}
            args['codemetric']['rules'] = CM_CRITERIA_FUNC_MANDO.keys()
            args['codemetric']['violations'] = []

            totals = []
            for filename in self._code_metrics:
                for function in self._code_metrics[filename][1]:
                    total = 0
                    values = []
                    metrics = self._code_metrics[filename][1][function]
                    for name in CM_CRITERIA_FUNC_MANDO:
                        criteria = CM_CRITERIA_FUNC_MANDO[name]
                        value = metrics[CmFunc[name]]
                        values.append(value)
                        if value > criteria[2]:
                            total += value

                    if total > 0:
                        totals.append((total, os.path.split(filename)[1], function, values))

            totals.sort(reverse=True)
            totals = totals[:rank]
            for total in totals:
                args['codemetric']['violations'].append({
                    'filename': total[1],
                    'function': total[2],
                    'values': total[3]
                })

        tmpl = Template(filename=self._template_path, input_encoding='utf-8')
        DBS.set_mail_body(output_path, tmpl.render(args=args))

        return True

    def qualify_codemetric_mando(self) -> bool:
        is_qualified = True

        for filename in self._code_metrics:
            cm_file = self._code_metrics[filename]
            for function in self._code_metrics[filename][1]:
                cm_func = cm_file[1][function]
                for category in CM_CRITERIA_FUNC_MANDO:
                    criteria = CM_CRITERIA_FUNC_MANDO[category]
                    value_str = cm_func[CmFunc[category].value]
                    value = float(value_str)
                    if value < criteria[1] or value > criteria[2]:
                        print("[ERROR] %s %s %s=%s" % (os.path.split(filename)[-1], function, category, value_str))
                        is_qualified = False

        return is_qualified

    def analyze_codemetric(self) -> bool:
        raise NotImplementedError
        """
        self._code_metric = 
        {
            filename 1 : [
                    [File-based code metrics, ...],
                    {
                        Function 1 : [Function-based code metrics, ...],
                        Function 2 : [Function-based code metrics, ...],
                        ...
                    }
            filename 2 : {
                ...
                },
            ...
        }
        """

    def analyze_misra(self) -> bool:
        raise NotImplementedError
        """
        self._misra_violations = 
        {
            filename 1 : {
                major 1 : {
                    minor 0 : [[occurrences, message 1], [occurrences, message 2], ...],
                    minor 1 : [[occurrences, message], ...],
                    ...
                    },
                major 2 : {
                    minor 21 : [[occurrences, message], ...],
                    minor 22 : [[occurrences, message], ...],
                    ...
                    },
                ...
                },
            filename 2 : {
                ...
                },
            ...
        }
        """


class QAC_8(QAC):
    def __init__(self, path:str):
        QAC.__init__(self, path)
        self._qac_path = r'C:\PRQA\QAC-8.1.2-R'
        self._qaw_path = os.path.join(os.path.split(os.sys.argv[0])[0], 'resources', 'QAW-2.3.2-Win')
        self._misra_rule = 2004

    def analyze_codemetric(self) -> bool:
        # Get CodeMetric files

        file_list = []
        for file in traverse_list(self._project_root):
            if os.path.splitext(file)[1] == ".met":
                file_list.append(file)

        self._code_metrics = {}
        for file in file_list:
            metric = self.__parse_codemetric(file)
            if metric is not None:
                self._code_metrics.update(metric)

        return True

    def analyze_misra(self) -> bool:
        project_file = None
        for file in os.listdir(self._project_root):
            if os.path.splitext(file)[1] == '.prj':
                project_file = os.path.join(self._project_root, file)
                break
        if project_file is None:
            return False

        # M2CM rules 확인
        misra_rule_map = {}
        try:
            regex_map_file = re.compile('M2CM.+Message_Map.csv')
            path_m2cm_doc = os.path.join(self._qac_path, 'm2cm', 'doc')
            f = None
            for file in os.listdir(path_m2cm_doc):
                if regex_map_file.match(file):
                    f = open(os.path.join(path_m2cm_doc, file))
                    break

            if f is None:
                raise FileNotFoundError

            with f:
                for row in csv.reader(f):
                    # Get only MISRA-C violations
                    if row[2] != '4':
                        continue

                    number = int(row[0])
                    rule = row[3]
                    if rule == '':
                        continue
                    major, minor = rule.split('.')
                    major = int(major)
                    minor = int(minor)

                    misra_rule_map[number] = (rule, major, minor)
        except OSError as e:
            print(e)
            return False

        # QAW 으로 QA-C 실행
        # M2CM 으로 분석
        current_path = os.getcwd()
        os.chdir(self._project_root)
        p = subprocess.Popen('cmd', stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, shell=False)
        cmd = '"%s"' % os.path.join(self._qac_path, 'bin', 'QACCONF.BAT')
        p.stdin.write(cmd + '\n')

        # cmd = '"%s" qac "%s" -mode none -plog -disp > "%s"' % (os.path.join(self._PATH_QAW, 'bin', 'qaw.exe'), project_file, tempfile)
        cmd = '"%s" qac "%s" -mode none -plog -disp' % (os.path.join(self._qaw_path, 'bin', 'qaw.exe'), project_file)
        p.stdin.write(cmd + '\n')

        cmd = 'exit'
        p.stdin.write(cmd + '\n')

        self._misra_violations = {}
        output_buffer = ''

        p.stdin.flush()

        # State-Machine variables for output parser
        regex_output = [
            # 0. New target
            re.compile(r'<S>STFIL\s+Name of File \s+(.+)'),

            # 1. M2CM message
            re.compile(r'<S>COUNT\s+(\d+)\s+(\d+)\s+(\d+)'),

            # 2. Detail message
            re.compile(r'\s+(.+)')

        ]
        current_target = None
        current_rule = None

        while p.poll() is None:
            ch = p.stdout.readline(1)
            if ch == '':
                break
            print(ch, end='')
            sys.stdout.flush()

            if ch == '\n':
                for i in range(len(regex_output)):
                    m = regex_output[i].match(output_buffer)
                    if m is None:
                        continue

                    if i == 0:
                        target_name = m.group(1)
                        self._misra_violations[target_name] = {}
                        current_target = self._misra_violations[target_name]
                        break
                    elif i == 1:
                        level = int(m.group(1))
                        if level != 4:
                            continue

                        number = int(m.group(2))
                        occurrence = int(m.group(3))
                        m2cm = misra_rule_map[number]  # (rule, major, minor)
                        rule = m2cm[0]
                        major = m2cm[1]
                        minor = m2cm[2]
                        if not current_target.__contains__(major):
                            current_target[major] = {}
                        if not current_target[major].__contains__(minor):
                            current_target[major][minor] = []
                        current_rule = [occurrence, '']
                        current_target[major][minor].append(current_rule)
                        break
                    elif i == 2:
                        if current_rule is not None:
                            current_rule[1] = m.group(1)
                            # print('Gotcha!')
                            # sys.stdout.flush()
                        current_rule = None
                        break
                else:
                    # MISSING!
                    current_rule = None

                output_buffer = ''
            else:
                output_buffer += ch

        os.chdir(current_path)
        return True

    def __parse_codemetric(self, file: str) -> []:
        # print(file)
        result = [[], {}]

        with open(file, "r") as f:
            # Regular expression to pick CodeMetric related string.
            regex_metric = re.compile("<S>([A-Z0-9]{5})\s+(\S*\s\S+\)|\S*)")

            # Define state-machine variables
            last_position = -1
            current_file = None
            current_target = None
            current_category = None

            while True:
                line = f.readline()
                if last_position == f.tell():
                    break
                last_position = f.tell()
                m = regex_metric.match(line)
                if m is None:
                    continue

                category = m.group(1)
                value = m.group(2)
                if self.CmEtc.__contains__(category):
                    # Skip. Currently uncovered category.
                    # print("\t[%s] %s is not covered" % (current_file, category))
                    pass

                elif category == QAC.CmSource:
                    current_file = value
                    # Filename may skipped.
                    # if current_file is None:
                    #     current_file = value
                    # Debugging code.
                    # assert (current_file == value)
                    # A code metric file may contain multiple files but merged into a file in QA-C Viewer.

                elif category == QAC.CmName:
                    # Initializing a new CodeMetric table.
                    if value == current_file:  # When parsing file
                        current_target = result[0]
                        current_category = CmFile
                    else:  # When parsing function
                        result[1][value] = []
                        current_target = result[1][value]
                        current_category = CmFunc

                    for i in range(len(current_category)):
                        current_target.append(0)
                elif category in CM_METRIC_SKIP:
                    # Skip Project-Wide Metrics file
                    return None
                else:
                    # Put CodeMetric value into target field
                    if QAC.regex_int.match(value) is not None:
                        value = int(value)
                    elif QAC.regex_float.match(value) is not None:
                        value = float(value)
                    current_target[current_category[category].value] = value
        return {current_file: result}


class PRQA_Framework(QAC):
    def __init__(self, path:str):
        QAC.__init__(self, path)
        self._qacli_path = r'C:\PRQA\PRQA-Framework-2.2.0\common\bin\qacli.exe'
        self._misra_rule = 2012
        self._output_path = os.path.join(self._project_root, 'prqa', 'configs', 'Initial_Config', 'reports')

    def analyze_codemetric(self):
        exit_code = 0
        current_path = os.getcwd()
        os.chdir(self._project_root)
        cmd = self._qacli_path + r' report -t MDR'
        exit_code = os.system(cmd)
        os.chdir(current_path)

        if exit_code != 0:
            return False

        mdr_files = []
        regex_mdr = re.compile(os.path.split(self._project_root)[1] + '_MDR_.+')
        for function_name in os.listdir(self._output_path):
            if regex_mdr.match(function_name):
                mdr_files.append(function_name)
        if len(mdr_files) == 0:
            return False

        self._code_metrics = {}

        mdr_files.sort(reverse=True)
        mdr_file = os.path.join(self._output_path, mdr_files[0])
        metrics = ET.parse(mdr_file).getroot()
        for file in metrics:
            filename = file.attrib['name']
            result = [[], {}]

            for entity in file:
                entity_type = entity.attrib['type']
                if entity_type == 'file':
                    current_target = result[0]
                    current_category = CmFile
                elif entity.attrib['type'] == 'function':
                    function_name = entity.attrib['name']
                    result[1][function_name] = []
                    current_target = result[1][function_name]
                    current_category = CmFunc
                else:
                    assert('Entity type ' + entity_type + ' is not defined')

                for i in range(len(current_category)):
                    current_target.append(0)

                for metric in entity:
                    metric_name = metric.attrib['name']
                    value = metric.attrib['value']
                    if QAC.regex_int.match(value) is not None:
                        value = int(value)
                    elif QAC.regex_float.match(value) is not None:
                        value = float(value)

                    if metric_name in CM_METRIC_SKIP:
                        current_target.clear()
                    else:
                        current_target[current_category[metric_name].value] = value

            if len(result[0]) > 0:
                for function_name in list(result[1].keys()):
                    if len(result[1][function_name]) == 0:
                        result[1].pop(function_name)
                self._code_metrics[filename] = result

        os.chdir(current_path)
        return True

    def analyze_misra(self):
        exit_code = 0
        current_path = os.getcwd()
        os.chdir(self._project_root)
        cmd = self._qacli_path + r' report -t RCR'
        exit_code = os.system(cmd)
        os.chdir(current_path)

        if exit_code != 0:
            return False

        rcr_file = os.path.join(self._output_path, 'results_data.xml')
        if not os.path.exists(rcr_file):
            return False

        self._misra_violations = {}
        dataroot = ET.parse(rcr_file).getroot().find('dataroot[@type="per-file"]')

        regex_rule = re.compile('Rule-(\d+).(\d+)')
        regex_message = re.compile('\d+.\s+(.+)')
        for file in dataroot:
            self._misra_violations[file.attrib['path']] = {}
            target = self._misra_violations[file.attrib['path']]

            violations = file.findall('./tree[@type="rules"]/RuleGroup[@name="M3CM"]/Rule/Rule/Rule')
            for violation in violations:
                rule = violation.attrib['id']
                m = regex_rule.match(rule)
                if m is None:
                    # print('check rule ' + rule)
                    continue
                major = int(m.group(1))
                minor = int(m.group(2))

                for message in violation.findall('Message'):
                    message_raw = message.attrib['text']
                    m = regex_message.match(message_raw)
                    if m is None:
                        # print('check message ' + message_raw)
                        continue
                    text = m.group(1)
                    total = int(message.attrib['total'])
                    active = int(message.attrib['active'])

                    if not target.__contains__(major):
                        target[major] = {}
                    if not target[major].__contains__(minor):
                        target[major][minor] = []
                    target[major][minor].append([total,  text])

        return True


OPT_HELP = "-h"
OPT_FILE = "-a"
OPT_FUNC = "-b"
OPT_MISRA = "-c"
OPT_REPORT = "-r"
OPT_OUTPUT = "-o"
OPT_QAC8 = "-q"
OPT_ARG0 = "-0"
OPT_ARG1 = "-1"
OPT_ARG2 = "-2"
OPT_ARG3 = "-3"
OPT_ARG4 = "-4"
OPT_ARG5 = "-5"
OPT_ARG6 = "-6"
OPT_ARG7 = "-7"


def main() -> bool:
    def show_help():
        text = "\n\n" \
               "QA-C report generator\n" \
               "\n" \
               "Usage :\n" \
               "qac.py {options} {QA-C project path}\n" \
               "\n" \
               "Exit code is 0 if compile is success, otherwise non-zero value.\n" \
               "Default value of {QA-C project path} is current working directory.\n" \
               "\n" \
               "Options :\n" \
               "-h          Show help\n" \
               "            Show this help menu.\n" \
               "-q          Uses QA-C 8.xx with MISRA-C 2004 rule\n" \
               "            Default tool for static analysis is QA-Framework with MISRA-C 2012.\n" \
               "            But with this option, script regards the QA-C project built by QA-C 8.xx with MISRA-C 2004.\n" \
               "-a{path}    Archive file-based code metric\n" \
               "            Save file-based code metric result to file in CSV format.\n" \
               "-b{path}    Archive function-based code metric\n" \
               "            Save function-based code metric result to a file in CSV format.\n" \
               "-c{path}    Archive MISRA-C rule viloation result\n" \
               "            Save MISRA-C rule violation results in CSV format.\n" \
               "-r{path}    Path of report file.\n" \
               "            This option specify the name of outout report file.\n" \
               "            Default : <Current Working Dir>\\<Project Name>_report.xlsx\n" \
               "-o{path}    Target output configuration file.\n" \
               "            Recipients of mailing list and E-Mail content will be stored in this file.\n" \
               "-[n]{text}  Extra arguments for archiving\n" \
               "            Archiving file may contains up to 8 arguments to specify build environment.\n" \
               "            User can put those values through 0 ~ 7.\n" \
               ""

        print(text)

    options = {}
    qac_root_path = None
    try:
        opts, args = getopt(sys.argv[1:], "ha:b:c:r:o:q0:1:2:3:4:5:6:7:")
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP) or len(options) == 0 and len(args) == 0:
            show_help()
            return True

        if len(args) == 0:
            qac_root_path = "."
        elif len(args) == 1:
            qac_root_path = args[0]
        else:
            show_help()
            return False
    except IndexError or ValueError:
        show_help()
        return False
    except OSError as err:
        print(err)
        return False

    file_based_path = None
    func_based_path = None
    misra_path = None
    report_path = None
    output_path = None

    if options.__contains__(OPT_FILE):
        file_based_path = options[OPT_FILE]

    if options.__contains__(OPT_FUNC):
        func_based_path = options[OPT_FUNC]

    if options.__contains__(OPT_MISRA):
        misra_path = options[OPT_MISRA]

    if options.__contains__(OPT_REPORT):
        report_path = options[OPT_REPORT]

    if options.__contains__(OPT_OUTPUT):
        output_path = options[OPT_OUTPUT]

    qac_target = None
    if options.__contains__(OPT_QAC8):
        qac_target = QAC_8
    else:
        qac_target = PRQA_Framework

    extras = [''] * 8
    pattern_args = re.compile("-(\d)")
    for option in options:
        m = pattern_args.match(option)
        if m:
            extras[int(m.group(1))] = options[option]

    qac = qac_target(qac_root_path)
    qac.analyze_misra()
    qac.analyze_codemetric()

    if file_based_path is not None:
        qac.archive_file_based(file_based_path, extras)

    if func_based_path is not None:
        qac.archive_func_based(func_based_path, extras)

    if misra_path is not None:
        qac.archive_misra(misra_path, extras)

    # Generate report excel file
    if report_path is not None:
        qac.generate_report(report_path, extras)

    # Generate summary
    if output_path is not None:
        qac.generate_summary(output_path, extras, rank=5)

if __name__ == "__main__":
    main()
