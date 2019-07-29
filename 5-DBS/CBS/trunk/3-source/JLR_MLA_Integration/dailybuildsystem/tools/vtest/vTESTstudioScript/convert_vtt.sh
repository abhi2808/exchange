#!/bin/sh
FILE_NAME="vtt_testcase.as"

VTT_LIST="vtt_list.as"
#ls *.vtt > ${VTT_LIST}
find . -maxdepth 10 -name "*.vtt" -type f > ${VTT_LIST}

cat /dev/null > ${FILE_NAME}

while read FILE_LINE; do
	VTT_FILE=${FILE_LINE}
	SUBJECT=`echo ${VTT_FILE} | sed -r -n 's/^.*\/(.*)\..*/\1/gp'`

	DATE=$(date '+%H:%M:%S');
	echo ${DATE}" : "${VTT_FILE}

	echo -e  ${SUBJECT}"\t\"">> ${FILE_NAME}

	while read LINE; do

		if [[ ( ${LINE} == *"<title>"* ) && ( ${LINE} == *"</title>"* ) && ( ${LINE} != *"<tc>"* )  && ( ${PREVIOUS_LINE} != *"<tc>"* ) && ( ${LINE} != *"<comment>"* ) && ( ${PREVIOUS_LINE} != *"<comment>"* ) ]]; then
			echo ${PREVIOUS_LINE}>> ${FILE_NAME}
			echo -e "    "${LINE}>> ${FILE_NAME}
			i=$((i+1))
		fi
		PREVIOUS_LINE=${LINE}
	done < ${VTT_FILE}
	echo -e "\"\t\"">> ${FILE_NAME}

	while read LINE; do
		if [[ ( ${LINE} == *"<title>"* ) && ( ${LINE} == *"</title>"* ) && ( ${LINE} != *"<tc>"* )  && ( ${PREVIOUS_LINE} != *"<tc>"* ) && ( ${LINE} != *"<comment>"* ) && ( ${PREVIOUS_LINE} != *"<comment>"* ) ]]; then
			echo ${LINE}>> ${FILE_NAME}
		fi
		PREVIOUS_LINE=${LINE}
	done < ${VTT_FILE}
	echo "\"">> ${FILE_NAME}

done < ${VTT_LIST}

sed -r -i 's/<title>//g' ${FILE_NAME}
sed -r -i 's/<\/title>//g' ${FILE_NAME}
sed -r -i 's/,/\n   /g' ${FILE_NAME}
sed -r -i 's/<//g' ${FILE_NAME}
sed -r -i 's/>//g' ${FILE_NAME}
sed -i -e '/\t"$/N;s/\n//' ${FILE_NAME}

rm -rf ./vtt_list.as

DATE=$(date '+%H:%M:%S');
echo ${DATE}
echo "End"
