#!/usr/bin/env python
#coding:utf-8
import sys, os, subprocess, re, time, json
import requests
import commands

#subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
#a= subprocess.call(cmd,shell=True)
#output =os.system(cmd)
#(status, output) = commands.getstatusoutput(cmd)
# |findstr duration"
#a=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
#print (a)

def get_duration():
  cmd="ffprobe -show_entries format=duration " + sys.argv[1]
  output = os.popen(cmd)
  line = output.readline()
  while line:
    if line.find("duration")>=0:
       list = line.split('=')
       return list[1]
    line = output.readline()   
    
def get_sliceDuration():
  return float(duration)/sliceSum

def get_fFStart():
  cmd="ffprobe -show_entries format=start_time " + sys.argv[1]
  output = os.popen(cmd)
  line = output.readline()
  while line:
    if line.find("start_time")>=0:
       list = line.split('=')
    line = output.readline()
  return list[1]  
    
def get_sliceStartTime(sliceStartTime):
  for i in range(1,sliceSum):
     cmd="ffprobe -show_frames -select_streams v:0 -read_intervals "
     cmd+= str(float(fFStart)+sliceDuration*i) + "%+" + str(sliceDuration)
     cmd+=" -i " + sys.argv[1] + " -print_format csv"
     print (cmd)
     output = os.popen(cmd)
     line = output.readline()
     while line:
        list = line.split(',')
        if(list[3] == '1'):
              sliceStartTime.append(list[7] if list[5] =="N/A" else list[5])
              break;        
        line = output.readline()

def get_stArray(stArray):
  stArray.insert(0, 0)
  for i in range(1,sliceSum):
      stArray.insert(i,float(sliceStartTime[i-1])-float(fFStart))
  
def get_intervalArray(intervalArray):     
    for i in range(0,len(stArray)-1):
       intervalArray.append(stArray[i+1]-stArray[i])
    intervalArray.append(-1)   
   
def sliceTranscoding():
  i=0
  while i<sliceSum:
      if i == 0:
          cmd = "ffmpeg -t " + str(intervalArray[i])
          cmd+= " -i " + sys.argv[1] + " -y " + sys.argv[1] +"_test"+str(i)+".mp4" 
      elif i == sliceSum-1:
          cmd = "ffmpeg -ss " + str(stArray[sliceSum-1])
          cmd+= " -i " + sys.argv[1] + " -y " + sys.argv[1] +"_test"+str(i)+".mp4" 
      else:
          cmd = "ffmpeg -ss " + str(stArray[i])
          cmd += " -t " + str(intervalArray[i])
          cmd += " -i " + sys.argv[1] + " -y " + sys.argv[1] +"_test"+str(i)+".mp4"
      print("sliceTranscoding:%s" % cmd)    
      os.popen(cmd)   
      i+=1
          
def concatSlices():
   i=0
   f = open('file.txt', 'w')
   while i < sliceSum:
       f.write("file \'" + sys.argv[1] + "_test" + str(i) + ".mp4\'\n")
       i+=1
   f.close( )
   
   cmd="ffmpeg -f concat -i file.txt -c copy " + sys.argv[1] +"_concat.mp4"
   print("concatSlices:%s" % cmd)
   os.popen(cmd)
   

if __name__ == "__main__":
   sliceSum=int(sys.argv[2])
   duration=get_duration()
   sliceDuration=get_sliceDuration()
   fFStart=get_fFStart()
   print("sliceSum=%s" % sliceSum)
   print("duration=%s" % duration)
   print ("sliceDuration=%s" % sliceDuration)
   print ("fFStart=%s" % fFStart)
   
   sliceStartTime=[]
   stArray=[]
   intervalArray=[]
   get_sliceStartTime(sliceStartTime)  
   get_stArray(stArray)
   get_intervalArray(intervalArray)
   print("sliceStartTime=%s" % sliceStartTime) 
   print("stArray=%s" % stArray) 
   print("intervalArray=%s" % intervalArray)   

   sliceTranscoding()
   concatSlices()
    
   

  


