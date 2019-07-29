#!/bin/sh

FILE_NAME="01_MPW_CHK"
COMPONENT="MdPbcWrapper"
CASE_FILE="01_MdPbcWrapper_case.as"


sh Gen_TestCase_main.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="02_SH_CHK"
COMPONENT="StorgHndlr"
CASE_FILE="02_StorgHndlr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="03_RS_CHK"
COMPONENT="RawSnsr"
CASE_FILE="03_RawSnsr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="04_ES_CHK"
COMPONENT="EpbSnsr"
CASE_FILE="04_EpbSnsr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="05_EH_CHK"
COMPONENT="ErrHndlr"
CASE_FILE="05_ErrHndlr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="06_MM_CHK"
COMPONENT="ModMgr"
CASE_FILE="06_ModMgr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="07_SC_CHK"
COMPONENT="StatCtrlr"
CASE_FILE="07_StatCtrlr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="08_DC_CHK"
COMPONENT="DynCtrlr"
CASE_FILE="08_DynCtrlr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="09_MD_CHK"
COMPONENT="MotDrvr"
CASE_FILE="09_MotDrvr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}

FILE_NAME="10_ED_CHK"
COMPONENT="ExtDrvr"
CASE_FILE="10_ExtDrvr_case.as"

sh Gen_TestCase.sh ${FILE_NAME} ${COMPONENT} ${CASE_FILE}
