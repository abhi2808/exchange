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
    def merge_rows_with_same_file(self):
        self._refined = []

        rules = self._header[13:]
        self._refined_header = ['date', 'filename']
        for rule in rules:
            self._refined_header.append(rule)

        prev_file = None
        cur_dst = []
        for idx in range(0, len(self._raw)):
            cur_row = self._raw[idx]
            cur_file = cur_row[self._idx_filename]
            if prev_file != cur_file:
                cur_date = cur_row[self._idx_date]
                cur_dst = [cur_date, cur_file]
                for i in range(0, len(rules)):
                    cur_dst.append(0)
                self._refined.append(cur_dst)
                prev_file = cur_file

            for rule in rules:
                cur_val = cur_row[self._header.index(rule)]
                if rule == 'STMCC':
                    cur_val = int(re.findall('\d+', cur_val)[0])
                elif rule == 'STKDN' or rule == 'STPDN':
                    cur_val = float(cur_val)
                else:
                    cur_val = int(cur_val)
                cur_dst[self._refined_header.index(rule)] += cur_val

    def reorder_of_raw_data(self, ignore_list: IgnoreList):
        new_refined = []
        rules = self._refined_header[2:]

        for i in range(0, len(self._refined)):
            # Remove the rows including to the file or path in ignore list from _refined[]
            cur_row = self._refined[i]
            cur_date = cur_row[self._refined_header.index('date')]
            cur_file = cur_row[self._refined_header.index('filename')]

            # if IgnoreList.is_skipped_file(ignore_list, cur_file) == True:
            if ignore_list is not None and ignore_list.is_skipped_file(cur_file) == True:
                continue

            for rule in rules:
                cur_count = cur_row[self._refined_header.index(rule)]
                new_refined.append((cur_date, rule, cur_file, cur_count))

        self._refined = new_refined
        self._refined_header = ['date', 'rule', 'filename', 'count']

    def analyze(self, max_rule: int = 5, max_file: int = 5) -> tuple:
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
                rule 1 : (rule, count, {
                            filename 1 : count,
                            filename 2 : count,
                            ...
                        }
                    ),
                rule 2 : (rule, count, { ... }),
                rule 3 : (rule, count, { ... }),
                ...
            },
            date 2 : { ... },
            date 3 : { ... },
            ...
        }
        """
        # Grouping and get sub totals.
        grouped = grouping(self._refined,
                           [self._refined_header.index('date'), self._refined_header.index('rule'),
                            self._refined_header.index('filename')])
        sub_total = subtotal(grouped, self._refined_header.index('count'), None)
        dates = list(sub_total[1].keys())
        dates.sort(reverse=True)

        result = OrderedDict()
        for date in dates:
            violations = sub_total[1][date][1]

            rank_by_rule = []
            for rule in violations:
                rank_by_rule.append((violations[rule][0], rule))
            rank_by_rule.sort(key=itemgetter(0), reverse=True)

            result_date = OrderedDict()
            for rule in rank_by_rule:
                count = rule[0]
                key = rule[1]
                files = sub_total[1][date][1][key][1]

                rank_by_file = []
                for file in files:
                    rank_by_file.append((file, files[file][0]))
                rank_by_file.sort(key=itemgetter(1), reverse=True)

                result_file = OrderedDict()
                for file in rank_by_file:
                    result_file[file[0]] = file[1]

                result_date[key] = (rule, count, result_file)

            result[date] = result_date
        return result

    def _get_statistic(self, ranked: OrderedDict, max_rule: int, max_file: int) -> tuple:
        """
        :param ranked:
        :param max_rule:
        :param max_file:
        :return:
        (
            category=RULE|FILE, date, rule name, filename, file short name, count, comparing
        )
        """
        output = []

        target_dates = list(ranked.keys())
        target_rules = list(ranked[target_dates[0]].keys())[:max_rule]
        for i in range(len(target_dates), 0, -1):
            date_curr = target_dates[-i]
            if i > 1:
                date_prev = target_dates[-i + 1]
            else:
                date_prev = date_curr

            rules_curr = ranked[date_curr]
            rules_prev = ranked[date_prev]
            blank_rules = max_rule
            for rule in target_rules[:max_rule]:
                blank_rules -= 1
                files_curr = rules_curr[rule][2]
                files_prev = rules_prev[rule][2]

                # Get statistic of rule level
                count_by_rule_curr = rules_curr[rule][1]
                count_by_rule_prev = 0
                if rule in rules_prev:
                    count_by_rule_prev = rules_prev[rule][1]
                output.append(('RULE', date_curr, rule, '', '', count_by_rule_curr,
                               count_by_rule_curr - count_by_rule_prev))

                # Get statistic of file level
                blank_files = max_file
                for file in list(files_curr.keys())[:max_file]:
                    blank_files -= 1
                    count_by_file_curr = files_curr[file]
                    count_by_file_prev = 0
                    if file in files_prev:
                        count_by_file_prev = files_prev[file]
                    output.append(('FILE', date_curr, rule, file, os.path.split(file)[1],
                                   count_by_file_curr, count_by_file_curr - count_by_file_prev))
                for i in range(blank_files):
                    output.append(('FILE', date_curr, rule))
            for i in range(blank_rules):
                output.append(('RULE', date_curr))
                for i in range(max_file):
                    output.append(('FILE', date_curr))

        return tuple(output)

if __name__ == '__main__':
    def help():
        print('* Usage :\n'
              'python codemetric.py --src={src} --dst={dst} --argN={value} {yyyy-mm-dd} ...\n'
              '\n'
              '--src                    File path of Codemetric rule violation archive\n'
              '--dst                    File path of worst ranking result\n'
              '--ign                    File path of ignore list excel file\n'
              '--argN (optional)        Customize arguments : arg0 ~ arg7\n'
              '\n'
              '{yyyy-mm-dd} (optional)  Target extraction dates. Without any value, Today and additional\n'
              '                         previous four days of same weekday would be automatically choosen.\n'
              '\n'
              '* example :\n'
              'python codemetric.py --src=CodeMtric_func.csv --dst=codemetric_ranking.csv --ign=ignore_list.xlsx 2018-04-06 2018-04-13 2018-04-16 2018-04-27 2018-05-04 2018-05-08 2018-05-09 2018-05-10 2018-06-05\n')


    OUTPUT_HEADER = ['category', 'date', 'rule name', 'path', 'filename', 'count', 'comparing']

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
    if OPTION_IGN in options:
        ignore_list = IgnoreList(options[OPTION_IGN])
    else:
        ignore_list = None

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

    '''
        _header = [date, time, arg0, ..., arg7, filename, function, <Code Metric Rule#1>, ..., <Code Metric Rule#n >]
            -> _refined_header = [date, filename, <Code Metric Rule#1>, ..., <Code Metric Rule#n>]
    '''
    worst_history.merge_rows_with_same_file()

    '''
        _refined_header = [date, filename, <Code Metric Rule#1>, ..., <Code Metric Rule#n>]
            -> _refined_header = [date, rule, filename, count]
    '''
    worst_history.reorder_of_raw_data(ignore_list)

    statistics = worst_history.analyze()

    with open(dst, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADER)
        for line in statistics:
            writer.writerow(line)