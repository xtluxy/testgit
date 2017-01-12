#!/usr/bin/env python
#coding:utf-8
import sys, os

class SliceTransClass:
 def get_duration(self):
  cmd="ffprobe -show_entries format=duration " + self.filepath
  output = os.popen(cmd)
  line = output.readline()
  while line:
    if line.find("duration")>=0:
       list = line.split('=')
       return list[1]
    line = output.readline()   
    
 def get_sliceDuration(self):
  return self.__duration/self.__sliceSum

 def get_fFStart(self):
  cmd="ffprobe -show_entries format=start_time " + self.filepath
  output = os.popen(cmd)
  line = output.readline()
  while line:
    if line.find("start_time")>=0:
       list = line.split('=')
    line = output.readline()
  return list[1]  
    
 def get_sliceStartTime(self):
  for i in range(1,self.__sliceSum):
     cmd="ffprobe -show_frames -select_streams v:0 -read_intervals "
     cmd+= str(self.__fFStart+self.__sliceDuration*i) + "%+" + str(self.__sliceDuration)
     cmd+=" -i " + self.filepath + " -print_format csv"
     print ("get_sliceStartTime:%s" % cmd)
     output = os.popen(cmd)
     line = output.readline()
     while line:
        list = line.split(',')
        if(list[3] == '1'):
              self.__sliceStartTime.append(list[7] if list[5] =="N/A" else list[5])
              break;        
        line = output.readline()

 def get_stArray(self):
  self.__stArray.insert(0, 0)
  for i in range(1,self.__sliceSum):
      self.__stArray.insert(i,float(self.__sliceStartTime[i-1])-self.__fFStart)
  
 def get_intervalArray(self):     
    for i in range(0,len(self.__stArray)-1):
       self.__intervalArray.append(self.__stArray[i+1]-self.__stArray[i])
    self.__intervalArray.append(0)   
   
 def sliceTranscoding(self):
  for i in range(0,self.__sliceSum):
      if i == 0:
          cmd = "ffmpeg -t " + str(self.__intervalArray[i])
          cmd+= " -i " + self.filepath + " -y " + self.filepath +"_test"+str(i)+".mp4" 
      elif i == self.__sliceSum-1:
          cmd = "ffmpeg -ss " + str(self.__stArray[self.__sliceSum-1])
          cmd+= " -i " + self.filepath + " -y " + self.filepath +"_test"+str(i)+".mp4" 
      else:
          cmd = "ffmpeg -ss " + str(self.__stArray[i])
          cmd += " -t " + str(self.__intervalArray[i])
          cmd += " -i " + self.filepath + " -y " + self.filepath +"_test"+str(i)+".mp4"
      print("transcoding:%s" % cmd)    
      os.popen(cmd)   
          
 def concatSlices(self):
   f = open('file.txt', 'w')
   for i in range(0,self.__sliceSum):
       f.write("file \'" + self.filepath + "_test" + str(i) + ".mp4\'\n")
   f.close( )
   
   cmd="ffmpeg -f concat -i file.txt -c copy " + self.filepath +"_concat.mp4"
   print("concatSlices:%s" % cmd)
   os.popen(cmd)
   
 def __init__(self,filepath,sliceSum):
     self.filepath=filepath
     self.__sliceSum=int(sliceSum)
     self.__duration=float(self.get_duration())
     self.__sliceDuration=self.get_sliceDuration()
     self.__fFStart=float(self.get_fFStart())   
     print("filepath=%s" % self.filepath)
     print("sliceSum=%d" % self.__sliceSum)
     print("duration=%f" % self.__duration)
     print("sliceDuration=%f" % self.__sliceDuration)
     print("fFStart=%f" % self.__fFStart)
     
     self.__sliceStartTime=[] 
     self.__stArray=[]
     self.__intervalArray=[]
     self.get_sliceStartTime() 
     self.get_stArray()
     self.get_intervalArray()     
     print("sliceStartTime=%s" % self.__sliceStartTime) 
     print("stArray=%s" % self.__stArray) 
     print("intervalArray=%s" % self.__intervalArray)   
     
 def __del__(self):
     pass
  
if __name__ == "__main__":
   print(sys.argv[1])
   print(sys.argv[2])
   t=SliceTransClass(sys.argv[1],sys.argv[2])
   t.sliceTranscoding()
   t.concatSlices()


  

    
   

  


