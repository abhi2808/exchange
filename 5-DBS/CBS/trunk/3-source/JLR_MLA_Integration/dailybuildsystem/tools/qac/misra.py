"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""

import csv
import getopt
import os
import re
import sys
from collections import OrderedDict
from datetime import timedelta, datetime
from operator import itemgetter

try:
    from DailyBuildSystem.report import Report, Filter, grouping, subtotal
except ImportError:
    sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..'))
    from report import Report, Filter, grouping, subtotal

try:
    from DailyBuildSystem.dbs import IgnoreList
except ImportError:
    sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..'))
    from dbs import IgnoreList


class WorstHistoryByRule(Report):
    def filter_ignore_list(self, ignore_list: IgnoreList):
        """
        :param ignore_list: the list of files needed to ignore for processing worst rank
        """
        filtered_raw = []

        for idx in range(0, len(self._raw)):
            cur_row = self._raw[idx]
            cur_file = cur_row[self._idx_filename]
            # if IgnoreList.is_skipped_file(ignore_list, cur_file) == False:
            if not ignore_list.is_skipped_file(cur_file):
                filtered_raw.append(cur_row)
        self._raw = tuple(filtered_raw)


    def analyze(self, max_rule: int=5, max_file: int=5) -> tuple:
        """

        :param max_rule:
        :param max_file:
        :return:
        (
            category=RULE|FILE, date, rule major, rule minor, rule name, filename, file short name, count, comparing
        )
        """
        result = []
        ranked = self._get_worst_rank()
        if len(ranked) > 0:
            result = self._get_statistic(ranked, max_rule, max_file)
        return result

    def _get_worst_rank(self) -> dict:
        """
        :return:
        All dictionaries are ordered.
        {
            date 1 : {
                rule 1 : (major, minor, count, {
                            filename 1 : count,
                            filename 2 : count,
                            ...
                        }
                    ),
                rule 2 : (major, minor, count, { ... }),
                rule 3 : (major, minor, count, { ... }),
                ...
            },
            date 2 : { ... },
            date 3 : { ... },
            ...
        }
        """
        # Grouping and get sub totals.
        grouped = grouping(self._raw, [self._idx_date, self._idx_major, self._idx_minor, self._idx_filename])
        sub_total = subtotal(grouped, self._idx_count, None)
        dates = list(sub_total[1].keys())
        dates.sort(reverse=True)

        result = OrderedDict()
        for date in dates:
            violations = sub_total[1][date][1]

            # Ranking of violated rules
            rank_by_rule = []
            for major in violations:
                for minor in violations[major][1]:
                    rank_by_rule.append((violations[major][1][minor][0], major, minor))
            rank_by_rule.sort(key=itemgetter(0), reverse=True)

            result_date = OrderedDict()
            for rule in rank_by_rule:
                count = rule[0]
                major = rule[1]
                minor = rule[2]
                key = '%d.%d' % (int(major), int(minor))
                files = sub_total[1][date][1][major][1][minor][1]

                # Ranking violated files of a rule set.
                rank_by_file = []
                for file in files:
                    rank_by_file.append((file, files[file][0]))
                rank_by_file.sort(key=itemgetter(1), reverse=True)

                result_file = OrderedDict()
                for file in rank_by_file:
                    result_file[file[0]] = file[1]

                # Ordering violation rule set and
                result_date[key] = (major, minor, count, result_file)

            result[date] = result_date
        return result

    def _get_statistic(self, ranked: OrderedDict, max_rule: int, max_file: int) -> tuple:
        """
        :param ranked:
        :param max_rule:
        :param max_file:
        :return:
        (
            category=RULE|FILE, date, rule major, rule minor, rule name, filename, file short name, count, comparing
        )
        """
        output = []

        target_dates = list(ranked.keys())
        target_rules = list(ranked[target_dates[0]].keys())[:max_rule]
        for i in range(len(target_dates), 0, -1):
            date_curr = target_dates[-i]
            if i > 1:
                date_prev = target_dates[-i+1]
            else :
                date_prev = date_curr

            rules_curr = ranked[date_curr]
            rules_prev = ranked[date_prev]
            blank_rules = max_rule
            for rule in target_rules[:max_rule]:
                blank_rules -= 1
                files_curr = rules_curr[rule][3]
                files_prev = rules_prev[rule][3]
                major = rules_curr[rule][0]
                minor = rules_curr[rule][1]

                # Get statistic of rule level
                count_by_rule_curr = rules_curr[rule][2]
                count_by_rule_prev = 0
                if rule in rules_prev:
                    count_by_rule_prev = rules_prev[rule][2]
                output.append(('RULE', date_curr, major, minor, rule, '', '', count_by_rule_curr, count_by_rule_curr - count_by_rule_prev))

                # Get statistic of file level
                blank_files = max_file
                for file in list(files_curr.keys())[:max_file]:
                    blank_files -= 1
                    count_by_file_curr = files_curr[file]
                    count_by_file_prev = 0
                    if file in files_prev:
                        count_by_file_prev = files_prev[file]
                    output.append(('FILE', date_curr, major, minor, rule, file, os.path.split(file)[1], count_by_file_curr, count_by_file_curr - count_by_file_prev))
                for i in range(blank_files):
                    output.append(('FILE', date_curr, major, minor, rule))
            for i in range(blank_rules):
                output.append(('RULE', date_curr))
                for i in range(max_file):
                    output.append(('FILE', date_curr))

        return tuple(output)

if __name__ == '__main__':
    def help():
        print('* Usage :\n'
              'python misra.py --src={src} --dst={dst} --argN={value} {yyyy-mm-dd} ...\n'
              '\n'
              '--src                    File path of Misra-C rule violation archive\n'
              '--dst                    File path of worst ranking result\n'
              '--ign                    File path of ignore list excel file\n'
              '--argN (optional)        Customize arguments : arg0 ~ arg7\n'
              '\n'
              '{yyyy-mm-dd} (optional)  Target extraction dates. Without any value, Today and additional\n'
              '                         previous four days of same weekday would be automatically choosen.\n'
              '\n'
              '* example :\n'
              'python misra.py --src=misra.csv --dst=ranking.csv --ign=ignore_list.xlsx --arg2=MGH100_ESCBASE_ASR --arg4=KMC_RJ_VAR_01 2018-04-05 2018-03-29\n')


    OUTPUT_HEADER = ['category', 'date', 'major', 'minor', 'rule_name', 'filename', 'short name', 'count', 'comparing']

    OPTION_SRC = '--src'
    OPTION_DST = '--dst'
    OPTION_IGN = '--ign'
    OPTION_ARG0 = '--arg0'
    OPTION_ARG1 = '--arg1'
    OPTION_ARG2 = '--arg2'
    OPTION_ARG3 = '--arg3'
    OPTION_ARG4 = '--arg4'
    OPTION_ARG5 = '--arg5'
    OPTION_ARG6 = '--arg6'
    OPTION_ARG7 = '--arg7'

    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['src=', 'dst=', 'ign=', 'arg0=', 'arg1=', 'arg2=', 'arg3=', 'arg4=', 'arg5=', 'arg6=', 'arg7='])
    options = {}
    for opt in opts:
        options[opt[0]] = opt[1]

    if OPTION_DST not in options and OPTION_SRC not in options:
        help()
        exit(1)

    if len(args) == 0:
        today = datetime.today()
        dates = []
        for i in range(5):
            delta = timedelta(weeks=i)
            dates.append((today - delta).date().isoformat())
    else:
        dates = args

    src = options[OPTION_SRC]
    dst = options[OPTION_DST]

    builder = Filter.builder()
    for date in dates:
        builder.put('date', date)

    regex_argN = re.compile('--(arg\d)')
    for option in options:
        m = regex_argN.match(option)
        if m is None:
            continue
        builder.put(m.group(1), options[option])

    worst_history = WorstHistoryByRule(src, builder.build())
    if OPTION_IGN in options:
        # Get ignore list from excel file
        worst_history.filter_ignore_list(IgnoreList(options[OPTION_IGN]))
    statistic = worst_history.analyze()

    with open(dst, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADER)
        for line in statistic:
            writer.writerow(line)
