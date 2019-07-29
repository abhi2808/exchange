"""
:: NAME:           dbs.py
::
:: FUNCTION:       To generate temporary folder with cleaning up
::                    
:: PROJECT:        Daily Build System
::
:: DEVELOPED BY :  Navjot Kaur
::
"""
import configparser
import os
import sys
import openpyxl
from itertools import groupby
from operator import itemgetter, eq

import re


class IgnoreList:
    def __init__(self, excel_path):
        self._ignore_files = []
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active
        #ws = wb.get_active_sheet()
        for row in ws.rows:
            for cell in row:
                value = re.match('((.+\/)?(.+))', cell.value)
                value = value.groups()
                value = list(value)
                file = value[len(value)-1]
                replaced_file = file.replace('*', '\\w+')
                replaced_file = replaced_file.replace(".", "[.]")
                value[len(value)-1] = replaced_file
                self._ignore_files.append((value))


    def is_skipped_file(self, file) -> bool:
        ret = False
        temp = re.match('((.+\/)?(.+))', file)
        temp = temp.groups()
        cur_path = temp[len(temp)-2]
        cur_file = temp[len(temp)-1]

        for idx in range(0, len(self._ignore_files)):
            filter_path = self._ignore_files[idx][len(self._ignore_files[idx]) - 2]
            filter_file = self._ignore_files[idx][len(self._ignore_files[idx]) - 1]
            if filter_path != None:
                if filter_path in cur_path:
                    if re.match(filter_file, cur_file) != None:
                        ret = True
            else:
                if re.match(filter_file, cur_file) != None:
                    ret = True

        return ret


# Configuration should be changed into singleton pattern in the future.
class DBS:
    def __init__(self):
        pass

    class Section:
        MAIL = "dbs_mail"
        BUILD = "dbs_build"
        RELEASE = "dbs_release"

    @classmethod
    def initialize(cls, temp_path:str, config_file=None):
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        for item in (os.listdir(temp_path)):
            file = os.path.join(temp_path, item)
            os.remove(file)
        if config_file is not None:
            with open(os.path.join(temp_path, config_file), "w") as f:
                f.write("")

        return True

    @classmethod
    def __init_config(cls, output_file_path:str, section:Section) -> configparser.RawConfigParser:
        config = configparser.RawConfigParser()
        config.read(output_file_path)
        if not config.has_section(section):
            config.add_section(section)
        return config

    @classmethod
    def __save_config(cls, output_file_path:str, config:configparser.RawConfigParser) -> bool:
        try:
            with open(output_file_path, "w") as f:
                config.write(f)
            return True
        except Exception as err:
            print(err)
            return False

    @classmethod
    def get_config(cls, output_file_path:str, section:Section) -> []:
        config = configparser.RawConfigParser()
        config.read(output_file_path)
        if config.has_section(section):
            return config[section]
        else:
            None

    # [dbs_release]
    RELEASE_JENKINS = "dbs_release_jenkins"
    RELEASE_SVN = "dbs_release_svn"
    @classmethod
    def set_release_jenkins(cls, output_file_path:str, url:str) -> bool:
        config = cls.__init_config(output_file_path, cls.Section.RELEASE)
        config[cls.Section.RELEASE][cls.RELEASE_JENKINS] = url

        return cls.__save_config(output_file_path, config)

    @classmethod
    def set_release_svn(cls, output_file_path:str, url:str) -> bool:
        config = cls.__init_config(output_file_path, cls.Section.RELEASE)
        config[cls.Section.RELEASE][cls.RELEASE_SVN] = url

        return cls.__save_config(output_file_path, config)

    # [dbs_mail]
    MAIL_RECIPIENTS = "dbs_mail_recipients"
    MAIL_BODY = "dbs_mail_body"

    @classmethod
    def set_mail_recipients(cls, output_file_path: str, recipients: tuple, truncate: bool=False) -> bool:
        config = cls.__init_config(output_file_path, cls.Section.MAIL)
        if not truncate and config[cls.Section.MAIL].__contains__(cls.MAIL_RECIPIENTS):
            recipients = recipients + config[cls.Section.MAIL][cls.MAIL_RECIPIENTS].split(",")
        config[cls.Section.MAIL][cls.MAIL_RECIPIENTS] = ",".join(list(map(itemgetter(0), groupby(sorted(recipients)))))

        return cls.__save_config(output_file_path, config)

    @classmethod
    def set_mail_body(cls, output_file_path: str, content: str, truncate: bool=False) -> bool:
        content = re.sub("\s*\r\n\s*", "", content)
        config = cls.__init_config(output_file_path, cls.Section.MAIL)
        prev_content = ""
        if not truncate and config[cls.Section.MAIL].__contains__(cls.MAIL_BODY):
            prev_content = config[cls.Section.MAIL][cls.MAIL_BODY]
        config[cls.Section.MAIL][cls.MAIL_BODY] = prev_content + content
        return cls.__save_config(output_file_path, config)


def traverse(path: str) -> dict:
    if not os.path.isdir(path) or not os.path.exists(path):
        raise OSError("%s doesn't exist or is not a directory." % path)

    children = [{},[]]
    for child in os.listdir(path):
        if os.path.isdir(os.path.join(path, child)):
            children[0][child] = (traverse(os.path.join(path, child)))
        else :
            children[1].append(child)

    return children


def traverse_list(path: str) -> list:
    root = traverse(path)
    output = __traverse_list(path, root)

    return output


def __traverse_list(current_path: str, children: dict) -> list:
    # 1. Append files
    output = []
    for file in children[1]:
        output.append(os.path.join(current_path, file))

    # 2. Traverse to children
    for child in children[0]:
        output = output + __traverse_list(os.path.join(current_path, child), children[0][child])

    # 3. Return result.
    return output


def main() -> bool:
    CMD_INIT = "init"

    def show_help():
        text = "\n\n" \
               "DailyBuildSystem common script\n" \
               "\n" \
               "Usage :\n" \
               "dbs.py {cmd} {argument(s)}\n" \
               "\n" \
               "cmd :\n" \
               "init | init {path} | init {path} {filename}\n" \
               "        Create and clean DBS temporal workspace.\n" \
               "        Default path is .dbs\n" \
               "        Defailt filename is dbs.conf\n"
        print(text)

    try:
        cmd = sys.argv[1]
        args = sys.argv[2:]
        if cmd == CMD_INIT:
            path = ".dbs"
            filename = "dbs.conf"

            if len(args) > 0:
                path = args[0]
            if len(args) > 1:
                filename = args[1]
            if len(args) > 2:
                raise ValueError
            input_path = DBS()
            input_path.initialize(path, filename)
        else:
            show_help()
            return False
    except IndexError or ValueError:
        show_help()
        return False
    except IOError as err:
        print(err)
        return False

    return True


def merge_dict(dst:dict, src:dict) -> dict:
    r = dst.copy()
    for key in src:
        value = src[key]
        if not r.__contains__(key):
            r[key] = value
        elif isinstance(value, list):
            r[key] += value
        elif isinstance(value, dict):
            r[key] = merge_dict(dst[key], src[key])
        else:
            r[key] = value
    return r


if __name__ == '__main__':
    if main():
        exit(0)
    else:
        exit(1)
