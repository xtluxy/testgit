#!/bin/bash

fragNum=3
duration=$(ffprobe -show_entries format=duration $1 |grep duration |awk -F = '{print $2}')
echo "duration is:" $duration
seginteger=$(($(echo ${duration%.*})/$fragNum))
echo "seginteger is:" $seginteger
fFStart=$(ffprobe -show_entries format=start_time $1 |grep start_time |awk -F = '{print $2}')
echo "fFStart is:" $fFStart

rm -f file4.bin
for (( i=1; i<=$fragNum; i++ )) 
do  
ffprobe -show_frames -select_streams v:0 -read_intervals $(awk 'BEGIN{print "'$i'"*"'$seginteger'";}')%+$seginteger -i $1 -print_format csv |
awk 'BEGIN{ FS="," }{if($4 == 1){print $0;exit 1;}}'|
awk 'BEGIN { FS="," } { if($6 =="N/A") print $8 ; else print $6}' >>file4.bin
done

startTime=$(awk '{st=st" "$1}END{print st}' file4.bin) 
echo $startTime
stArray[0]=0
echo ${stArray[0]}
i=1
for elemenet in $startTime  
do  
    stArray[$i]=$(awk 'BEGIN{print "'$elemenet'"-"'$fFStart'"}')
    echo ${stArray[$i]}  
    let i++
done 

for (( i=0; i<${#stArray[*]}; i++ )) 
do  
    if [ $i -eq $((${#stArray[*]}-1)) ] 
    then
        intervalArray[$i]=-1
    else  
      intervalArray[$i]=$(awk 'BEGIN{print "'${stArray[($i+1)]}'"-"'${stArray[$i]}'"}')
    fi    
    echo ${intervalArray[$i]}  
done 

rm -f file.txt
for (( i=0; i<${#stArray[*]}; i++ ))
do
    echo "stArray is:" ${stArray[$i]}
    echo "intervalArray is:" ${intervalArray[$i]}
    if [ $i == 0 ]
    then 
        ffmpeg -t ${intervalArray[$i]} -i $1 -y $1_test$i.mp4 
    elif [ ${intervalArray[$i]} != -1 ]
    then
        ffmpeg -ss ${stArray[$i]} -t ${intervalArray[$i]} -i $1 -y $1_test$i.mp4 
    else
        ffmpeg -ss ${stArray[$i]} -i $1 -y $1_test$i.mp4
    fi
    awk 'BEGIN{print "file '\''"  "'$1'" "_test" "'$i'" ".mp4'\''" }' >>file.txt
done

ffmpeg -f concat -i file.txt -c copy $1_concat.mp4
