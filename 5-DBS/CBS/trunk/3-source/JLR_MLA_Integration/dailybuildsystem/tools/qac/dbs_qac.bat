"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""

:: DBS Integrated builder for MGH-100
@echo off
setlocal EnableDelayedExpansion

:: Optional parameters for MGH-100
if not defined MISRA_TYPE		set MISRA_TYPE=2012
if not defined QAC_PROJECT_NAME set QAC_PROJECT_NAME=DBS_JLA_MLR
if not defined QAC_CM_FILE 		set QAC_CM_FILE=CodeMetric_file.csv
if not defined QAC_CM_FUNC 		set QAC_CM_FUNC=CodeMetric_func.csv
if not defined QAC_MISRA 		set QAC_MISRA=misra.csv
if not defined PATH_ST_MANAGER  set PATH_ST_MANAGER=D:\workspace-Jenkins\STManager_%MISRA_TYPE%
if not defined DEBUG_MODE       set DEBUG_MODE=OFF
if not defined PATH_PROJECT     set PATH_PROJECT=%WORKSPACE%
if not defined PATH_DBS         set PATH_DBS=%WORKSPACE%\..\..\DailyBuildSystem
if not defined PATH_BUILD       set PATH_BUILD=%WORKSPACE%\..\..\BuildScript_MGH-100
if not defined PATH_ARCH		set PATH_ARCH=%WORKSPACE%\..\..\archive
if not defined PATH_TEMP        set PATH_TEMP=%WORKSPACE%\.dbs
if not defined DBS_OUTPUT       set DBS_OUTPUT=%PATH_TEMP%\dbs.conf

:: Additional report path
if not defined PATH_REPORT		set PATH_REPORT=%PATH_ARCH%\report\%VARIANT_CODE%

if %ROOT_BUILD_CAUSE%==TIMERTRIGGER (
	set BUILD_TYPE=P
) else (
	set BUILD_TYPE=U
)

@echo %DEBUG_MODE%

:: Initialize DBS
set PREFIX_ATTACH=%VARIANT_CODE%_%SVN_REVISION%
cd %WORKSPACE%
python %PATH_DBS%\dbs.py init %PATH_TEMP%

:: Clean
goto SKIP_CLEAN
if not exist %PATH_PROJECT%\BuildPackage\%BUILD_PACKAGE%\util\make.log (
	echo Cleaning previous build...
	python %PATH_BUILD%\make.py -c -p%PATH_PROJECT% %BUILD_PACKAGE%
	echo DONE
)

:: Build
: SKIP_CLEAN
python %PATH_BUILD%\make.py -p%PATH_PROJECT% -o"-j8 -s" %BUILD_PACKAGE%
@echo %DEBUG_MODE%
if %ERRORLEVEL%==0 (
    set BUILD_RESULT=SUCCESS
) else (
    set BUILD_RESULT=FAIL
)
cd %WORKSPACE%

:: Preparing post-build
: SKIP_BUILD
set args=-0"%CAR_MAKER%" -1"%CAR_NAME%" -2"%VARIANT_CODE%" -3"%BUILD_PACKAGE%"
if %MISRA_TYPE%==2004 (
    set args=%args% -q
)

set EXTRA_ARGS=--arg0="%CAR_MAKER%" --arg1="%CAR_NAME%" --arg2="%VARIANT_CODE%" --arg3="%BUILD_PACKAGE%"
if defined SVN_REVISION (
	set args=%args% -4%SVN_REVISION%
	set EXTRA_ARGS=%EXTRA_ARGS% --arg4=%SVN_REVISION%
)


:: Run QAC & reporting
python %PATH_DBS%\STManager.py -s%PATH_ST_MANAGER% -q -m%MISRA_RULE% %QAC_PROJECT_NAME% %PATH_PROJECT% BuildPackage\%BUILD_PACKAGE%\util\Makefile.mak
python %PATH_DBS%\qac.py -o"%DBS_OUTPUT%" -r"%PATH_TEMP%\%VARIANT_CODE%_%SVN_REVISION%.xlsx" -a"%PATH_ARCH%\%QAC_CM_FILE%" -b"%PATH_ARCH%\%QAC_CM_FUNC%" -c"%PATH_ARCH%\%QAC_MISRA%" %args% "%PATH_ST_MANAGER%\Projects\qac_%QAC_PROJECT_NAME%"
if exist %PATH_REPORT% (
python %PATH_DBS%\report\misra.py --src="%PATH_ARCH%\%QAC_MISRA%" --dst="%PATH_REPORT%\MISRA-C_WorstRanking.csv" --ign="%PATH_DBS%\resources\ignore.qac.xlsx" %EXTRA_ARGS%
python %PATH_DBS%\report\codemetric.py --src="%PATH_ARCH%\%QAC_CM_FUNC%" --dst="%PATH_REPORT%\CodeMetric_WorstRanking.csv" --ign="%PATH_DBS%\resources\ignore.qac.xlsx" %EXTRA_ARGS%

copy %PATH_REPORT%\%VARIANT_CODE%-CodeMetric_WorstRankByRule.xlsx %PATH_TEMP%
copy %PATH_REPORT%\%VARIANT_CODE%-MISRA-C_WorstRankByRule.xlsx %PATH_TEMP%
)
:: Override exit code
exit 0

:HELP
@echo off
echo DBS integrated builder for MGH-100
echo.
echo This script needs build-environment variables provided by DailyBuildSystem.
echo Please check and inject these environment variables.
echo.
echo Required :
echo   BUILD_PACKAGE
echo   VARIANT_CODE
echo   CAR_MAKER
echo   CAR_NAME
echo   MISRA_RULE
echo.
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
exit 1



