#!/bin/bash
mamama
create new branch is quick



seginteger=$(ffprobe -show_entries format=duration $1 |grep duration |awk -F = '{print $2}')
seginteger=$(($(echo ${seginteger%.*})/3))
echo "seginteger is:" $seginteger

ffprobe -show_frames -select_streams v:0 -print_format csv $1 |awk '{if($0!="") print $0}'  >file1.bin
stream_index=$(awk 'BEGIN{ FS="," } NR==1 {print $3}' file1.bin)
echo "stream_index is:" $stream_index

pkt_pts_time=$(awk 'BEGIN{ FS="," } NR==1 {print $6}' file1.bin)
echo "pkt_pts_time is:" $pkt_pts_time

grep -n frame,video,$stream_index,1 file1.bin|
awk 'BEGIN { FS="," } { if("'$pkt_pts_time'" =="N/A") print $1 " " $8 ; else print $1 " " $6}'|
sed 's/:frame//g' > file2.bin
fFStart=$(awk 'BEGIN{ FS=" " } NR==1 {print $2}' file2.bin)
echo "fFStart is:" $fFStart

rm -f file3.bin
awk 'BEGIN {splitStart="'$fFStart'" }   
     {  split($2,time,"."); current=time[1]; 
        if (current-splitStart >= "'$seginteger'"+0)
         { print $0;splitStart=current; }
      }' file2.bin >> file3.bin

startTime=$(awk '{st=st" "$2}END{print st}' file3.bin) 
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

for (( i=0; i<${#stArray[*]}; i++ ))
do
    echo "stArray is:" ${stArray[$i]}
    echo "intervalArray is:" ${intervalArray[$i]}
    if [ ${intervalArray[$i]} != -1 ]
    then
        ffmpeg -ss ${stArray[$i]} -t ${intervalArray[$i]} -i $1 -y $1_test$i.mp4 
    else
        ffmpeg -ss ${stArray[$i]} -i $1 -y $1_test$i.mp4
    fi
done
