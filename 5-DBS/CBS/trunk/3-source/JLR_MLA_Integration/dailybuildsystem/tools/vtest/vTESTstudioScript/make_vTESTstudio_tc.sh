#!/bin/sh
CASE_FILE="ea_testcase.as"

DATE=$(date '+%H:%M:%S');
echo ${DATE}


i=0
while read LINE; do
	IFS=',' read -a ARRY <<< "${LINE}"

	if [[ ( ${ARRY[0]} == *"F"* )  || ( ${ARRY[0]} == *"U"* )  || ( ${ARRY[0]} == *"W"* ) ]]; then
		FILE_NAME=${ARRY[0]}
		echo ${FILE_NAME}
		cat /dev/null > ${FILE_NAME}.vtt
		i=0
	else

		if [[ ${ARRY[4]} == *"INT16"* ]]; then
			MIN="0"
			MAX="5000"
		elif [[ ${ARRY[4]} == *"INT32"* ]]; then
			MIN="0"
			MAX="5000"
		elif [[ ${ARRY[4]} == *"SINT16"* ]]; then
			MIN="0"
			MAX="5000"
		elif [[ ${ARRY[4]} == *"UINT8"* ]]; then
			MIN="0"
			MAX="255"
		elif [[ ${ARRY[4]} == *"UINT16"* ]]; then
			MIN="0"
			MAX="5000"
		elif [[ ${ARRY[4]} == *"UINT32"* ]]; then
			MIN="0"
			MAX="5000"
		fi

		if [[ ${ARRY[4]} == *"INT"* ]]; then
			echo "      <awaitvaluematch>">> ${FILE_NAME}.vtt
			echo "        <title> "${ARRY[1]}"_within ["${MIN}".."${MAX}"] (1."${i}")</title>">> ${FILE_NAME}.vtt
			echo "        <timeout>">> ${FILE_NAME}.vtt
			echo "          <value>">> ${FILE_NAME}.vtt
			echo "            <const>30</const>">> ${FILE_NAME}.vtt
			echo "          </value>">> ${FILE_NAME}.vtt
			echo "          <unit>ms</unit>">> ${FILE_NAME}.vtt
			echo "        </timeout>">> ${FILE_NAME}.vtt
			echo "        <compare>">> ${FILE_NAME}.vtt
			echo "          <dbobject>SysVar_BEGIN_OF_OBJECT|1|"${ARRY[1]}"|XCP::XCP_Configuration|-1|0|END_OF_OBJECT_SysVar|</dbobject>">> ${FILE_NAME}.vtt
			echo "          <range>">> ${FILE_NAME}.vtt
			echo "            <fromto>">> ${FILE_NAME}.vtt
			echo "              <from>">> ${FILE_NAME}.vtt
			echo "                <const>"${MIN}"</const>">> ${FILE_NAME}.vtt
			echo "              </from>">> ${FILE_NAME}.vtt
			echo "              <to>">> ${FILE_NAME}.vtt
			echo "                <const>"${MAX}"</const>">> ${FILE_NAME}.vtt
			echo "              </to>">> ${FILE_NAME}.vtt
			echo "            </fromto>">> ${FILE_NAME}.vtt
			echo "          </range>">> ${FILE_NAME}.vtt
			echo "        </compare>">> ${FILE_NAME}.vtt
			echo "      </awaitvaluematch>">> ${FILE_NAME}.vtt
		else
			echo "      <awaitvaluematch>">> ${FILE_NAME}.vtt
			echo "        <title> "${ARRY[1]}"=="${ARRY[3]}" (1."${i}")</title>">> ${FILE_NAME}.vtt
			echo "        <timeout>">> ${FILE_NAME}.vtt
			echo "          <value>">> ${FILE_NAME}.vtt
			echo "            <const>30</const>">> ${FILE_NAME}.vtt
			echo "          </value>">> ${FILE_NAME}.vtt
			echo "          <unit>ms</unit>">> ${FILE_NAME}.vtt
			echo "        </timeout>">> ${FILE_NAME}.vtt
			echo "        <compare>">> ${FILE_NAME}.vtt
			echo "          <dbobject>SysVar_BEGIN_OF_OBJECT|1|"${ARRY[1]}"|XCP::XCP_Configuration|-1|0|END_OF_OBJECT_SysVar|</dbobject>">> ${FILE_NAME}.vtt
			echo "          <eq>">> ${FILE_NAME}.vtt
			echo "            <const>"${ARRY[3]}"</const>">> ${FILE_NAME}.vtt
			echo "          </eq>">> ${FILE_NAME}.vtt
			echo "        </compare>">> ${FILE_NAME}.vtt
			echo "      </awaitvaluematch>">> ${FILE_NAME}.vtt
		fi
		i=$((i+1))
	fi
done < ${CASE_FILE}

DATE=$(date '+%H:%M:%S');
echo ${DATE}
echo "End"



