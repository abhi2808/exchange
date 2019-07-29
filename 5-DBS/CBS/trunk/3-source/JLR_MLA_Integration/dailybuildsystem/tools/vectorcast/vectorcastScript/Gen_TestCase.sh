#!/bin/sh
TESTSCRIPT_DIR="C:\VCAST\Environments\TEST"

FILE_NAME=$1
COMPONENT=$2
CASE_FILE=$3

DATE=$(date '+%H:%M:%S');
echo ${DATE}

cat /dev/null > ${FILE_NAME}.tst

echo "-- VectorCAST 6.4.6 (10/17/18)">> ${FILE_NAME}.tst
echo "-- Test Case Script">> ${FILE_NAME}.tst
echo "-- ">> ${FILE_NAME}.tst
echo "-- Environment    : "${FILE_NAME}>> ${FILE_NAME}.tst
echo "-- Unit(s) Under Test: "${COMPONENT}" PBC">> ${FILE_NAME}.tst
echo "-- ">> ${FILE_NAME}.tst
echo "-- Script Features">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:C_DIRECT_ARRAY_INDEXING">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:CPP_CLASS_OBJECT_REVISION">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:MULTIPLE_UUT_SUPPORT">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:MIXED_CASE_NAMES">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:STATIC_HEADER_FUNCS_IN_UUTS">> ${FILE_NAME}.tst
echo "--">> ${FILE_NAME}.tst
echo "">> ${FILE_NAME}.tst


while read LINE; do
	IFS=',' read -a ARRY <<< "${LINE}"
	NUMBER=`echo ${ARRY[0]} | awk '{printf ("%04i", $1)}'`

	if [[ ${ARRY[4]} == *"ENUM"* ]]; then
		VALUE=${ARRY[6]}
	elif [[ ( ${ARRY[4]} == *"SINT16"* ) || ( ${ARRY[4]} == *"SINT32"* ) ]]; then
		if [[ ${ARRY[6]} == "-"* ]]; then
			VALUE="MIN"
		elif [[ ${ARRY[6]} == *"0"* ]]; then
			VALUE="MID"
		else
			VALUE="MAX"
		fi
	elif [[ ( ${ARRY[4]} == *"UINT16"* ) || ( ${ARRY[4]} == *"UINT32"* ) ]]; then
		if [[ ( ${ARRY[6]} == *"65535"* ) || ( ${ARRY[6]} == *"4294967295"* ) ]]; then
			VALUE="MAX"
		elif [[ ( ${ARRY[6]} == *"32768"* ) || ( ${ARRY[6]} == *"2147483648"* ) ]]; then
			VALUE="MID"
		else
			VALUE="MIN"
		fi
	fi


	if [[ ${ARRY[3]} == *"IN"* ]]; then
		echo "-- Test Case: "${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
		echo "TEST.UNIT:PBC">> ${FILE_NAME}.tst
		echo "TEST.SUBPROGRAM:PBC_output">> ${FILE_NAME}.tst
		echo "TEST.NEW">> ${FILE_NAME}.tst
		echo "TEST.NAME:"${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
		echo "TEST.NOTES:">> ${FILE_NAME}.tst
		echo "Interface Test between "${ARRY[1]}" and "${ARRY[2]}". Expected Value of "${ARRY[1]}" is "${VALUE}>> ${FILE_NAME}.tst
		echo "TEST.END_NOTES:">> ${FILE_NAME}.tst
		echo "TEST.STUB:"${ARRY[1]}"."${ARRY[1]}>> ${FILE_NAME}.tst
		echo "TEST.VALUE:PBC.<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
		echo "TEST.EXPECTED:"${ARRY[1]}"."${ARRY[1]}".rtu_"${ARRY[5]}"[0]:"${ARRY[6]}>> ${FILE_NAME}.tst
		echo "TEST.END">> ${FILE_NAME}.tst
		echo "">> ${FILE_NAME}.tst
	elif [[ ${ARRY[3]} == *"OUT"* ]]; then
		echo "-- Test Case: "${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
		echo "TEST.UNIT:PBC">> ${FILE_NAME}.tst
		echo "TEST.SUBPROGRAM:PBC_output">> ${FILE_NAME}.tst
		echo "TEST.NEW">> ${FILE_NAME}.tst
		echo "TEST.NAME:"${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
		echo "TEST.NOTES:">> ${FILE_NAME}.tst
		echo "Interface Test between "${ARRY[1]}" and "${ARRY[2]}". Expected Value of Global is "${VALUE}>> ${FILE_NAME}.tst
		echo "TEST.END_NOTES:">> ${FILE_NAME}.tst
		echo "TEST.STUB:"${ARRY[1]}"."${ARRY[1]}>> ${FILE_NAME}.tst
		echo "TEST.VALUE:"${ARRY[1]}"."${ARRY[1]}".rty_"${ARRY[5]}"[0]:"${ARRY[6]}>> ${FILE_NAME}.tst
		echo "TEST.EXPECTED:PBC.<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
		echo "TEST.END">> ${FILE_NAME}.tst
		echo "">> ${FILE_NAME}.tst
	fi

done < ${CASE_FILE}

DATE=$(date '+%H:%M:%S');
echo ${DATE}
echo "End"



