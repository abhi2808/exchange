import csv
import getopt
import os
import re
import sys
from collections import OrderedDict
from datetime import timedelta, datetime
from operator import itemgetter

try:
    from DailyBuildSystem.report import Report, Filter, grouping, subtotal2
except ImportError:
    sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..'))
    from report import Report, Filter, grouping, subtotal2

class WorstHistoryByFile(Report):
    DATE_TOTAL_COVERAGES = 0
    #CATEGORIES = ['Complexity', 'Control Flow', 'Function Coverage', 'Function Calls', 'Statements', 'Branches',
    #              'MC/DC Pairs', 'Expected']
    CATEGORIES = ['Control Flow', 'Function Coverage', 'Function Calls', 'Statements', 'Branches',
                  'MC/DC Pairs', 'Expected']

    def reassign_raw_data(self):
        self._refined = []

        for i in range(0, len(self._raw)):
            cur_row = self._raw[i]
            cur_date = cur_row[self._header.index('date')]
            cur_environment = cur_row[self._header.index('unit')]
            cur_category = cur_row[self._header.index('category')]
            cur_value = cur_row[self._header.index('value')]
            cur_covered = cur_row[self._header.index('covered')]
            cur_cases = cur_row[self._header.index('cases')]

            self._refined.append((cur_date, cur_environment, cur_category, cur_value, cur_covered, cur_cases))

        self._refined_header = ['date', 'unit', 'category', 'value', 'covered', 'cases']

    def analyze(self) -> tuple:
        """
        :param max_file:
        :return:
        (
            category=date, filename, control flow, call, statement, branch, MC/DC, expected
        )
        """
        result = []
        ranked = self._get_worst_rank()
        if len(ranked) > 0:
            result = self._get_statistic(ranked)
        return result

    def _get_worst_rank(self) -> dict:
        """
        :return:
        All dictionaries are ordered.
        {
            date 1 : {
                total rate : {
                            category 1 : rate or count,
                            category 2 : rate or count,
                            ...
                            }
                file 1 : (average rate, {
                            category 1 : rate or count,
                            category 2 : rate or count,
                            ...
                        }
                    ),
                file 2 : (average rate, { ... }),
                file 3 : (average rate, { ... }),
                ...
            },
            date 2 : { ... },
            date 3 : { ... },
            ...
        }
        """
        self.__DATE_AVE_COVERAGES = 'Date Ave Coverages'
        self.__FILE_TOTAL_RATE = 'File Total Rate'
        # Grouping and get sub totals.
        grouped = grouping(self._refined,
                           [self._refined_header.index('date'), self._refined_header.index('unit'),
                            self._refined_header.index('category')])

        dates = list(grouped.keys())
        new_grouped = OrderedDict()
        for date in dates:
            files = OrderedDict()
            for file in grouped[date]:
                if file != '':
                    files[file] = grouped[date][file]
            new_grouped[date] = files

        sub_total = subtotal2(new_grouped, self._refined_header.index('value'),
                              self._refined_header.index('covered'), self._refined_header.index('cases'), None)
        dates = list(sub_total.keys())
        dates.sort(reverse=True)

        for date in dates:
            date_totals = dict()
            for category in self.CATEGORIES:
                date_totals[category] = [0, 0, 0]
            for file in sub_total[date]:
                total_covered = 0
                total_cases = 0

                num_of_files = len(sub_total[date].keys())
                if self.rank == False and self.max_file < num_of_files:
                    self.max_file = num_of_files

                for category in sub_total[date][file]:
                    if category == 'Complexity':
                        sub_total[date][file][category] = int(sub_total[date][file][category][0])
                    else:
                        if category == 'Statements' or category == 'Branches' or category == 'MC/DC Pairs':
                            total_covered += int(sub_total[date][file][category][1])
                            total_cases += int(sub_total[date][file][category][2])
                        date_totals[category][1] += int(sub_total[date][file][category][1])
                        date_totals[category][2] += int(sub_total[date][file][category][2])
                        if int(sub_total[date][file][category][2]) != 0:
                            sub_total[date][file][category] = float(int(sub_total[date][file][category][1]) /
                                                                    int(sub_total[date][file][category][2]))
                if total_cases != 0:
                    sub_total[date][file][self.__FILE_TOTAL_RATE] = float(total_covered / total_cases)
                else:
                    sub_total[date][file][self.__FILE_TOTAL_RATE] = 0

            sub_total[date][self.__DATE_AVE_COVERAGES] = dict()
            for key in date_totals.keys():
                if date_totals[key][2] != 0:
                    sub_total[date][self.__DATE_AVE_COVERAGES][key] = \
                        float(date_totals[key][1] / date_totals[key][2])
                else:
                    sub_total[date][self.__DATE_AVE_COVERAGES][key] = 0

        result = OrderedDict()
        for date in dates:
            violations = sub_total[date]
            rank_by_file = []
            for file in violations:
                if file == self.__DATE_AVE_COVERAGES:
                    continue
                rank_by_file.append((file, violations[file][self.__FILE_TOTAL_RATE], violations[file]))
            rank_by_file.sort(key=itemgetter(1), reverse=False)

            result_file = OrderedDict()
            result_file[self.__DATE_AVE_COVERAGES] = sub_total[date][self.__DATE_AVE_COVERAGES]
            for file in rank_by_file:
                result_file[file[0]] = (file[1], file[2])
            result[date] = result_file

        return result

    def _get_statistic(self, ranked: OrderedDict) -> tuple:
        """
        :param ranked:
        :param max_file:
        :return:
        (
            category=date, filename, control flow, call, statement, branch, MC/DC, expected
        )
        """
        output = []

        target_dates = list(ranked.keys())
        for i in range(len(target_dates), 0, -1):
            date_curr = target_dates[-i]
            files_curr = ranked[date_curr]
            blank_files = self.max_file + 1
            num_of_files = len(ranked[target_dates[len(target_dates)-i]]) + 1
            if self.max_file < num_of_files:
                num_of_files = self.max_file + 1
            target_files = list(ranked[target_dates[len(target_dates)-i]])[:num_of_files]
            for file in target_files[:num_of_files]:
                blank_files -= 1
                if file == self.__DATE_AVE_COVERAGES:
                    target_categories = files_curr[file]
                else:
                    target_categories = files_curr[file][1]

                # Some category may be missing.
                record = []
                record.append(date_curr)
                if file == self.__DATE_AVE_COVERAGES:
                    record.append('<<overall>>')
                else:
                    record.append(file)
                for category in WorstHistoryByFile.CATEGORIES:
                    value = 0
                    if category in target_categories:
                        value = target_categories[category]
                    record.append(value)
                output.append(tuple(record))

            for i in range(blank_files):
                output.append((date_curr, ''))

        return tuple(output)

if __name__ == '__main__':
    def help():
        print('* Usage :\n'
              'python vectorcast_rank.py --src={src} --dst={dst} --argN={value} {yyyy-mm-dd} ...\n'
              '\n'
              '--src                    File path of Codemetric rule violation archive\n'
              '--dst                    File path of worst ranking result\n'
              '--rank                   Number of files to present in worst rank file'
              '--argN (optional)        Customize arguments : arg0 ~ arg7\n'
              '\n'
              '{yyyy-mm-dd} (optional)  Target extraction dates. Without any value, Today and additional\n'
              '                         previous four days of same weekday would be automatically choosen.\n'
              '\n'
              '* example :\n'
              'python vectorcast_rank.py --src=VectorCAST.csv --dst=VectorCAST_ranking.csv 2018-06-05 2018-06-01 2018-05-23\n')


    OUTPUT_HEADER = ['date', 'filename', 'control flow', 'function', 'call', 'statement', 'branch', 'MC/DC', 'expected']

    OPTION_SRC = '--src'
    OPTION_DST = '--dst'
    OPTION_RANK = '--rank'
    OPTION_ARG0 = '--arg0'
    OPTION_ARG1 = '--arg1'
    OPTION_ARG2 = '--arg2'
    OPTION_ARG3 = '--arg3'
    OPTION_ARG4 = '--arg4'
    OPTION_ARG5 = '--arg5'
    OPTION_ARG6 = '--arg6'
    OPTION_ARG7 = '--arg7'

    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['src=', 'dst=', 'rank=', 'arg0=', 'arg1=', 'arg2=', 'arg3=', 'arg4=', 'arg5=', 'arg6=', 'arg7='])
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

    worst_history = WorstHistoryByFile(src, builder.build())

    #if options[OPTION_RANK] != None:
    if OPTION_RANK in options:
        worst_history.rank = True
        worst_history.max_file = int(options[OPTION_RANK])
    else:
        worst_history.rank = False
        worst_history.max_file = 0


    worst_history.reassign_raw_data()
    statistics = worst_history.analyze()

    with open(dst, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADER)
        for line in statistics:
            writer.writerow(line)