#!/bin/sh
TESTSCRIPT_DIR="C:\VCAST\Environments\TEST"

FILE_NAME="PBC_INTERFACE"
CASE_FILE="PBC_INTERFACE.as"

DATE=$(date '+%H:%M:%S');
echo ${DATE}

cat /dev/null > ${FILE_NAME}.tst

echo "-- VectorCAST 6.4l (10/03/16)">> ${FILE_NAME}.tst
echo "-- Test Case Script">> ${FILE_NAME}.tst
echo "-- ">> ${FILE_NAME}.tst
echo "-- Environment    : "${FILE_NAME}>> ${FILE_NAME}.tst
echo "-- Unit(s) Under Test: DynCtrlr EpbSnsr ErrHndlr ExtDrvr MdPbcWrapper ModMgr MotDrvr PBC Pbc_Main RawSnsr StatCtrlr StorgHndlr div_s32_sat div_su32 mul_s32_sat mul_ssu32_sat mul_u32_sat mul_usu32_sat mul_wide_s32 mul_wide_su32 mul_wide_u32">> ${FILE_NAME}.tst
echo "-- ">> ${FILE_NAME}.tst
echo "-- Script Features">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:C_DIRECT_ARRAY_INDEXING">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:CPP_CLASS_OBJECT_REVISION">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:MULTIPLE_UUT_SUPPORT">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:MIXED_CASE_NAMES">> ${FILE_NAME}.tst
echo "TEST.SCRIPT_FEATURE:STATIC_HEADER_FUNCS_IN_UUTS">> ${FILE_NAME}.tst
echo "--">> ${FILE_NAME}.tst
echo "">> ${FILE_NAME}.tst
echo "-- Subprogram: Pbc_Cyclic">> ${FILE_NAME}.tst
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

	if [[ ${ARRY[1]} == *"MdPbcWrapper"* ]]; then
		if [[ ${ARRY[3]} == *"IN"* ]]; then
			echo "-- Test Case: "${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.UNIT:Pbc_Main">> ${FILE_NAME}.tst
			echo "TEST.SUBPROGRAM:Pbc_Cyclic">> ${FILE_NAME}.tst
			echo "TEST.NEW">> ${FILE_NAME}.tst
			echo "TEST.NAME:"${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.NOTES:">> ${FILE_NAME}.tst
			echo "Interface Test between "${ARRY[1]}" and "${ARRY[2]}". Expected Value of "${ARRY[1]}" is "${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.END_NOTES:">> ${FILE_NAME}.tst
			echo "TEST.STUB:"${ARRY[2]}"."${ARRY[2]}>> ${FILE_NAME}.tst
			echo "TEST.VALUE:PBC.<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
			echo "TEST.EXPECTED:"${ARRY[1]}".<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
			echo "TEST.END">> ${FILE_NAME}.tst
			echo "">> ${FILE_NAME}.tst
		elif [[ ${ARRY[3]} == *"OUT"* ]]; then
			echo "-- Test Case: "${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.UNIT:Pbc_Main">> ${FILE_NAME}.tst
			echo "TEST.SUBPROGRAM:Pbc_Cyclic">> ${FILE_NAME}.tst
			echo "TEST.NEW">> ${FILE_NAME}.tst
			echo "TEST.NAME:"${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.NOTES:">> ${FILE_NAME}.tst
			echo "Interface Test between "${ARRY[1]}" and "${ARRY[2]}". Expected Value of Global is "${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.END_NOTES:">> ${FILE_NAME}.tst
			echo "TEST.VALUE:"${ARRY[1]}".<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
			echo "TEST.EXPECTED:PBC.<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
			echo "TEST.END">> ${FILE_NAME}.tst
			echo "">> ${FILE_NAME}.tst
		fi
	else
		if [[ ${ARRY[3]} == *"IN"* ]]; then
			echo "-- Test Case: "${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.UNIT:Pbc_Main">> ${FILE_NAME}.tst
			echo "TEST.SUBPROGRAM:Pbc_Cyclic">> ${FILE_NAME}.tst
			echo "TEST.NEW">> ${FILE_NAME}.tst
			echo "TEST.NAME:"${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.NOTES:">> ${FILE_NAME}.tst
			echo "Interface Test between "${ARRY[1]}" and "${ARRY[2]}". Expected Value of "${ARRY[1]}" is "${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.END_NOTES:">> ${FILE_NAME}.tst
			echo "TEST.STUB:"${ARRY[1]}"."${ARRY[1]}>> ${FILE_NAME}.tst
			if [[ ${ARRY[2]} == *"MdPbcWrapper"* ]]; then
				echo "TEST.STUB:"${ARRY[2]}".PBC_vSetPBCINData">> ${FILE_NAME}.tst
				echo "TEST.STUB:"${ARRY[2]}".PBC_vSetPBCOUTData">> ${FILE_NAME}.tst
			else
				echo "TEST.STUB:"${ARRY[2]}"."${ARRY[2]}>> ${FILE_NAME}.tst
			fi
			echo "TEST.VALUE:PBC.<<GLOBAL>>."${ARRY[5]}":"${ARRY[6]}>> ${FILE_NAME}.tst
			echo "TEST.EXPECTED:"${ARRY[1]}"."${ARRY[1]}".rtu_"${ARRY[5]}"[0]:"${ARRY[6]}>> ${FILE_NAME}.tst
			echo "TEST.END">> ${FILE_NAME}.tst
			echo "">> ${FILE_NAME}.tst
		elif [[ ${ARRY[3]} == *"OUT"* ]]; then
			echo "-- Test Case: "${NUMBER}"_"${ARRY[1]}"_"${ARRY[3]}"_"${ARRY[5]}"_"${VALUE}>> ${FILE_NAME}.tst
			echo "TEST.UNIT:Pbc_Main">> ${FILE_NAME}.tst
			echo "TEST.SUBPROGRAM:Pbc_Cyclic">> ${FILE_NAME}.tst
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
	fi

done < ${CASE_FILE}

DATE=$(date '+%H:%M:%S');
echo ${DATE}
echo "End"



