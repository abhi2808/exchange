"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""

:: DBS Integrated builder for JLA_MLR
@echo off
setlocal EnableDelayedExpansion

:: Default Parameters
if not defined MODEL_TEST_SVN set MODEL_TEST_SVN=%SVN_REVISION_1%_%SVN_URL_1%
if not defined MODEL_TEST_GIT set MODEL_TEST_GIT=
if not defined MODEL_SVN  set MODEL_SVN=%SVN_REVISION_2%_%SVN_URL_2%
if not defined MODEL_GIT set MODEL_GIT=
if not defined MODEL_SOURCE set MODEL_SOURCE=%SVN_REVISION_3%_%SVN_URL_3%
if not defined MODEL_HOST set MODEL_HOST=%SVN_REVISION_4%_%SVN_URL_4%

:: Required parameters for JLA_MLR
if not defined PROJECT          set PROJECT=JLA_MLR
if not defined DEBUG_MODE       set DEBUG_MODE=ON
if not defined PATH_PROJECT     set PATH_PROJECT=%WORKSPACE%
if not defined PATH_DBS         set PATH_DBS=%WORKSPACE%\dailybuildsystem
if not defined PATH_BUILD       set PATH_BUILD=%WORKSPACE%\dailybuildsystem\build
if not defined PATH_ARCH		set PATH_ARCH=%WORKSPACE%\archive
if not defined PATH_TEMP        set PATH_TEMP=%WORKSPACE%\dailybuildsystem\report\.dbs
if not defined DBS_OUTPUT       set DBS_OUTPUT=%WORKSPACE%\dailybuildsystem\report\.dbs\dbs.conf
if not defined DBS_LOG          set DBS_LOG=%WORKSPACE%\dailybuildsystem\log\dbs.log 
if not defined DBS_TOOL			set DBS_TOOL=%WORKSPACE%\dailybuildsystem\tools

:: Release information
if not defined RELEASE_DIR  	set RELEASE_DIR=%WORKSPACE%\dailybuildsystem\release
del %DBS_LOG%

if %ROOT_BUILD_CAUSE%==TIMERTRIGGER (
	set BUILD_TYPE=P
) else (
	set BUILD_TYPE=U
)


@echo %DEBUG_MODE%

:: Initialize DBS 

cd %WORKSPACE%
python %PATH_DBS%\dbs.py init %PATH_TEMP%

rmdir /s /q %PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model\Integration_ert_rtw 
rmdir /s /q %PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model\slprj 


::Build matlab model 
python %PATH_BUILD%\matlabgen.py -p"PbcGen3_Parameter" -m"Integration" -l"%PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model\matlab.log" -x"%PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model"
if %ERRORLEVEL%==0 (
    set MODEL_GENERATION=SUCCESS
) else (
   set MODEL_GENERATION=FAIL
)
python %PATH_PROJECT%\dailybuildsystem\report\report.py -m "matlab" -a"%PATH_ARCH%\matlab.csv" "%PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model\matlab.log"

if %MODEL_GENERATION%==SUCCESS (
	
::copying and merging files
	for /R %PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model %%f in (*.h) do copy "%%f" %PATH_PROJECT%\dailybuildsystem\build 
	for /R %PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\model %%f in (*.c) do copy "%%f" %PATH_PROJECT%\dailybuildsystem\build
	copy %PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\source\* %PATH_PROJECT%\dailybuildsystem\build
	copy %PATH_PROJECT%\dailybuildsystem\repository\svn\JLR_MLA\host\*	 %PATH_PROJECT%\dailybuildsystem\build
) else (
	set BUILD_RESULT=FAIL
)
:: Build
::SKIP_CLEAN

python %PATH_BUILD%\make.py -p %PATH_BUILD%\jlr_mla.vcxproj -l %PATH_PROJECT%\dailybuildsystem\log\build.log 
copy %PATH_PROJECT%\dailybuildsystem\log\build.log %PATH_ARCH%\ /y
@echo %DEBUG_MODE%
if %ERRORLEVEL%==0 (
    set BUILD_RESULT=SUCCESS
	@echo SUCCESS
) else (
   set BUILD_RESULT=FAIL
)

cd %WORKSPACE%

:: Prepare post-build

set PARSER_ARGS=
set RELEASE_ARGS=
set LOG_PARSER_ARGS=
if %BUILD_RESULT%==SUCCESS (
    set RELEASE_ARGS=-a%RELEASE_DIR%\%SVN_REVISION%
    if exist %RELEASE_SVN%(
        set RELEASE_ARGS=-s%RELEASE_SVN%\%SVN_REVISION%
    )
)   else (
        set PARSER_ARGS=-f !PARSER_ARGS!
)


::Release
if %BUILD_RESULT%==SUCCESS (
    python %PATH_DBS%\release.py %RELEASE_ARGS% -0%DBS_OUTPUT% -p%PATH_PROJECT% -tJLA_MLR $PATH_PROJECT%\build_output
)

::Reporting
:SKIP_RELEASE
 
python %PATH_DBS%\buildparser.py %PARSER_ARGS% -tU -r -o"%DBS_OUTPUT%" -e"%PATH_DBS%\resources\mail.recipients.xlsx" -a"%PATH_ARCH%\BuildError.csv" -m"%PATH_DBS%\resources\mail.build.template.html" "%PATH_PROJECT%\build\build.log"

::DBS transaction logging
::DBS_LOGGING
 
python %PATH_DBS%\log.py %LOG_PARSER% -t%BUILD_TYPE% -r%BUILD_RESULT% -o"%PATH_ARCH%\DBS_Log.csv"
 
:: Prevent incremental build
if %BUILD_RESULT% NEQ SUCCESS (
    del %PATH_PROJECT%\dailybuildsystem\log\build.log
 )
::SKIP_FULL_BUILD

:: override exit code
exit 0


:HELP
@echo off
echo DBS integrated builder for CBS Daily Build System
echo Optional :
echo   PATH_PROJECT  	(Default : %WORKSPACE%)
echo   PATH_DBS         (Default : %WORKSPACE%\DailyBuildSystem)
echo   PATH_BUILD       (Default : %WORKSPACE%\BuildScript)
echo   PATH_ARCH        (Default : %WORKSPACE%\archive)
echo   PATH_TEMP        (Default : %WORKSPACE%\.dbs)
echo   DBS_OUTPUT       (Default : %WORKSPACE%\.dbs\dbs.conf)
echo   DEBUG_MODE       (Default : OFF)
echo   RELEASE_DIR      (Default : %WORKSPACE%\release)
echo   RELEASE_SVN      (Default : %WORKSPACE%\dist)
echo %SVN_REVISION%

exit 1

