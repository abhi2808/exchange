#!/bin/sh
FILE_NAME=$1
RESULT_FILE="expect_result.as"


DATE=$(date '+%H:%M:%S');
echo ${DATE}
echo "start"

cat /dev/null > ${RESULT_FILE}

FLAG=0
while read LINE; do

	if [[ ( ${FLAG} == 1 ) && ( ${LINE} != *"INPUT"* ) && ( ${LINE} != *"CHECK"* ) ]]; then
		echo ${LINE}>> ${RESULT_FILE}
	fi
	
	if [[ ${LINE} == *"CHECK"* ]]; then
		FLAG=1

	elif [[ ${LINE} == *"INPUT"* ]]; then
		FLAG=0
		if [[ ${LINE} == *"\""* ]]; then
			echo "\"">> ${RESULT_FILE}
		fi
	fi

done < ${FILE_NAME}

echo "\"">> ${RESULT_FILE}
sed -i -e '/^"$/N;s/\n//' ${RESULT_FILE}

DATE=$(date '+%H:%M:%S');
echo ${DATE}
echo "End"
