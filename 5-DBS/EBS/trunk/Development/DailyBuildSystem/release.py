import os
import re
import shutil
import subprocess
import sys
from getopt import getopt, GetoptError

sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from dbs import DBS
except ImportError:
    from DailyBuildSystem.dbs import DBS


class ReleaseCenterException(Exception):
    pass


class ReleaseCenter:
    SVN_MAX_DEPTH = 4

    def __init__(self, binary_path: str, app_path: str, app_file: str, dbs_conf: str = None):
        self._binary_path = binary_path
        self._app_path = app_path
        self._app_file = app_file
        self._dbs_conf = dbs_conf
        self._outputs = None

        if not self._is_binary_exists():
            raise ReleaseCenterException('Can not find Tasking output binary.')

        if not self._generate_app():
            raise ReleaseCenterException('Fail to generate binaries. Please check build package.')

    def _is_binary_exists(self) -> bool:
        if not os.path.exists(self._binary_path):
            return False

        is_exist = False
        for file in os.listdir(self._binary_path):
            if os.path.splitext(file)[1] == '.elf':
                is_exist = True
                break

        return is_exist

    def _generate_app(self) -> bool:
        cwd = os.getcwd()
        os.chdir(self._app_path)
        p = subprocess.Popen(self._app_file, stdin=subprocess.PIPE, universal_newlines=True)
        p.communicate('\n')
        p.wait()
        exit_code = p.returncode
        os.chdir(cwd)
        if exit_code != 0:
            return False

        self._outputs = []
        for file in os.listdir(self._app_path):
            if os.path.splitext(file)[1] == '.bat' or os.path.isdir(os.path.join(self._app_path, file)):
                continue
            self._outputs.append(file)
        return True

    def archive(self, path: str) -> bool:
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            for file in self._outputs:
                shutil.copy2(os.path.join(self._app_path, file), os.path.join(path, file))

            if self._dbs_conf is not None:
                link_path = os.path.abspath(os.path.join(os.getcwd(), path))
                DBS.set_release_jenkins(self._dbs_conf, link_path + '/*zip*/archive.zip')
            return True
        except Exception as err:
            print(err)
            return False

    def svn_commit(self, path: str) -> bool:
        cwd = os.getcwd()

        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            for file in self._outputs:
                shutil.copy2(os.path.join(self._app_path, file), os.path.join(path, file))

            # Traverse to find valid svn root until reach max depth.
            os.chdir(os.path.join(cwd, path))
            path_svn_cwd = None
            path_prev = '.'
            for i in range(ReleaseCenter.SVN_MAX_DEPTH):
                current_dir = os.getcwd()
                if current_dir == path_prev:
                    break
                elif os.path.exists('.svn'):
                    path_svn_cwd = current_dir
                    break

                path_prev = os.getcwd()
                os.chdir('..')
            if path_svn_cwd is None:
                return False

            if os.system('svn add %s --force' % path_prev) != 0:
                return False

            os.chdir(os.path.join(cwd, path))
            svn_url = subprocess.check_output('svn info --show-item url').decode().replace('\r\n', '')
            os.chdir(path_svn_cwd)
            message = 'Released by DailyBuildSystem\r\n%s' % svn_url
            if os.system('svn commit -m"%s"' % message) != 0:
                return False

            if self._dbs_conf is not None:
                os.chdir(cwd)
                DBS.set_release_svn(self._dbs_conf, svn_url)
            return True
        except Exception as err:
            print(err)
            return False
        finally:
            os.chdir(cwd)


class ReleaseMGH100(ReleaseCenter):
    def __init__(self, project_path: str, build_package: str, oem: str, dbs_conf: str = None):
        build_package_path = os.path.join(project_path, 'BuildPackage', build_package)
        binary_path = os.path.join(build_package_path, 'output', 'bin')
        app_path = os.path.join(build_package_path, 'binary', oem)

        re_ASR = re.compile(r'_ASR(_.*)?')
        name_parts = re_ASR.sub('', build_package).split('_')
        if len(name_parts) < 2:
            raise ReleaseCenterException(build_package_path + ' is not a proper build-package name')
        name_parts.insert(1, oem)
        app_file = '_'.join(name_parts) + '.bat'

        ReleaseCenter.__init__(self, binary_path, app_path, app_file, dbs_conf)


class ReleaseMRE(ReleaseCenter):
    def __init__(self, project_path: str, mcu: str, target: str, dbs_conf: str = None):
        project_root = os.path.join(project_path, mcu, 'ws', 'Brake')
        binary_path = os.path.join(project_root, 'output', 'bin')
        app_path = os.path.join(project_root, 'util', 'binary')
        app_file = target + '_PostBuild.bat'

        ReleaseCenter.__init__(self, binary_path, app_path, app_file, dbs_conf)


# Since here YoungTaek.Son implements #
OPT_HELP = '-h'
OPT_PROJECT_ROOT = '-p'
OPT_PROJECT_TYPE = '-t'
OPT_ARCHIVE = '-a'
OPT_SVN = '-s'
OPT_OUTPUT = '-o'

PROJECT_TYPE_MGH_100 = 'MGH-100'
PROJECT_TYPE_MRE = 'MRE'

PROJECT_TYPE_INFO = {
    # [MIN, MAX, ReleaseCenter class]
    PROJECT_TYPE_MGH_100: [2, 2, ReleaseMGH100],
    PROJECT_TYPE_MRE: [2, 2, ReleaseMRE]
}


def main() -> bool:
    def show_help():
        text = '\n\n' \
               'MGH-100 release center\n' \
               '\n' \
               'Usage :\n' \
               'release.py {option} {arguments}\n' \
               '\n' \
               'Release center triggers post-build script to generate APP and CAL file\n' \
               'and archives those output to specific path.\n' \
               '{arguments} are different depend on project-type.' \
               '\n' \
               '{arguments} :\n' \
               '    MGH-100     {build-package} {oem}\n' \
               '    MRE         {MCU} {target car}\n' \
               '\n' \
               'Options :\n' \
               '-h          Show help\n' \
               '            Show this help menu.\n' \
               '-p{path}    Project root\n' \
               '            Specify root path of project. Default value is current working directory.\n' \
               '-t{name}    Project type\n' \
               '            - MGH-100 (Default option)\n' \
               '            - MRE\n' \
               '-a{path}    Archive outputs.\n' \
               '            Archives output binary and others into destination.\n' \
               '-s{path}    Commit to svn.\n' \
               '            Copy outputs to svn-dist directory and commit.\n' \
               '-o{path}    Target output configuration file.\n' \
               '            Save release information if provided.\n'
        print(text)

    project_path = os.path.dirname(sys.argv[0])
    project_type = PROJECT_TYPE_MGH_100
    archive_path = None
    svn_path = None
    dbs_conf = None

    try:
        opts, args = getopt(sys.argv[1:], 'hp:t:a:s:o:')
        options = {}
        for opt in opts:
            options[opt[0]] = opt[1]
        if options.__contains__(OPT_HELP):
            show_help()
            return True
    except GetoptError as err:
        print(err)
        show_help()
        return False

    release_center = None
    try:
        if options.__contains__(OPT_PROJECT_ROOT):
            project_path = options[OPT_PROJECT_ROOT]
        if not os.path.exists(project_path):
            raise ReleaseCenterException(
                'Can not find project root path : %s' % (os.path.join(os.getcwd(), project_path)))

        if options.__contains__(OPT_PROJECT_TYPE):
            project_type = options[OPT_PROJECT_TYPE]
        if project_type not in PROJECT_TYPE_INFO.keys():
            raise ReleaseCenterException('Project type %s is not defined' % project_type)
        if len(args) < PROJECT_TYPE_INFO[project_type][0] or len(args) > PROJECT_TYPE_INFO[project_type][1]:
            raise ReleaseCenterException('Project type %s needs %d ~ %d arguments' % (
            project_type, PROJECT_TYPE_INFO[project_type][0], PROJECT_TYPE_INFO[project_type][1]))
        release_center = PROJECT_TYPE_INFO[project_type][2]

        if options.__contains__(OPT_OUTPUT):
            dbs_conf = options[OPT_OUTPUT]
            if not os.path.exists(dbs_conf):
                raise ReleaseCenterException('Can not find output configuration file.')

        if options.__contains__(OPT_ARCHIVE):
            archive_path = options[OPT_ARCHIVE]

        if options.__contains__(OPT_SVN):
            svn_path = options[OPT_SVN]

    except ReleaseCenterException as e:
        print(e)
        show_help()
        return False

    try:
        release = release_center(project_path, *args, dbs_conf=dbs_conf)
        if archive_path is not None:
            result = release.archive(archive_path)
            if not result:
                return False

        if svn_path is not None:
            result = release.svn_commit(svn_path)
            if not result:
                return False
    except ReleaseCenterException as err:
        print(err)
        return False

    return True


if __name__ == '__main__':
    if main():
        exit(0)
    else:
        exit(1)
