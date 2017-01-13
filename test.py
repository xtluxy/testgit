#!/usr/bin/env python
#coding:utf-8
import sys, os,time,subprocess

class SliceTransClass:
 def get_duration(self):
  cmd="ffprobe -show_entries format=duration " + self.__filepath
  output = os.popen(cmd)
  lines = output.readlines()
  for line in lines:
    if line.find("duration")>=0:
       list = line.split('=')
       return list[1]   
    
 def get_sliceDuration(self):
  return self.__duration/self.__sliceSum

 def get_fFStart(self):
  cmd="ffprobe -show_entries format=start_time " + self.__filepath
  output = os.popen(cmd)
  lines = output.readlines()
  for line in lines:
    if line.find("start_time")>=0:
       list = line.split('=')
       return list[1]  
    
 def get_sliceStartTime(self):
  for i in range(1,self.__sliceSum):
     cmd="ffprobe -show_frames -select_streams v:0 -read_intervals "
     cmd+= str(self.__fFStart+self.__sliceDuration*i) + "%+" + str(self.__sliceDuration)
     cmd+=" -i " + self.__filepath + " -print_format csv"
     print ("get_sliceStartTime:%s" % cmd)
     output = os.popen(cmd)
     lines = output.readlines()
     for line in lines:
        list = line.split(',')
        if(list[3] == '1'):
              self.__sliceStartTime.append(list[7] if list[5] =="N/A" else list[5])
              break;        

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
          cmd+= " -vb " +str(self. __averageBitrate)
          cmd+= " -i " + self.__filepath + " -y " + self.__filepath +"_test"+str(i)+".mp4" 
      elif i == self.__sliceSum-1:
          cmd = "ffmpeg -ss " + str(self.__stArray[self.__sliceSum-1])
          cmd+= " -vb " +str(self. __averageBitrate) 
          cmd+= " -i " + self.__filepath + " -y " + self.__filepath +"_test"+str(i)+".mp4" 
      else:
          cmd = "ffmpeg -ss " + str(self.__stArray[i])+ " -t " + str(self.__intervalArray[i])
          cmd += " -vb " +str(self. __averageBitrate)
          cmd += " -i " + self.__filepath + " -y " + self.__filepath +"_test"+str(i)+".mp4"
      print("transcoding:%s" % cmd)    
   #   os.popen(cmd)   
      process=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
      while process.poll() is None:
          process.stderr.read(1024)
          #.decode("utf-16")
          
 def concatSlices(self):
   f = open('file.txt', 'w')
   for i in range(0,self.__sliceSum):
       f.write("file \'" + self.__filepath + "_test" + str(i) + ".mp4\'\n")
   f.close( )
   cmd="ffmpeg -f concat -i file.txt -c copy " + self.__filepath +"_concat.mp4"
   print("concatSlices:%s" % cmd)
 #  os.popen(cmd)
   process=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
   while process.poll() is None:
       process.stderr.read(1024).decode("utf-8")
   
   
 def __init__(self,filepath,sliceSum):
     self.__filepath=filepath
     self.__sliceSum=int(sliceSum)
     self.__duration=float(self.get_duration())
     self.__sliceDuration=self.get_sliceDuration()
     self.__fFStart=float(self.get_fFStart())   
     print("filepath=%s" % self.__filepath)
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
     self.__averageBitrate=self.get_averageBitrate()
     print("sliceStartTime=%s" % self.__sliceStartTime) 
     print("stArray=%s" % self.__stArray) 
     print("intervalArray=%s" % self.__intervalArray) 
     print("averageBitrate=%s" % self.__averageBitrate)   
     
 def __del__(self):
    pass
 
 def get_averageBitrate(self):
    bitrate=[]
    count=0
    for i in range(0,self.__sliceSum-1):
        filename="output"+str(i)+".bin"
        cmd="ffmpeg -ss " + self.__sliceStartTime[i] + " -t 30 -i " + self.__filepath + " -c:v libx264 -crf 32 -an -f mp4 -y null >"
        cmd+=filename+ " 2>&1"
    #     cmd="ffmpeg -ss " + self.__sliceStartTime[i] + " -t 30 -i " + self.__filepath
   #     cmd+=" -c:v libx264 -crf 32 -an -f mp4 -y null 2>&1 |grep kb/s: |awk -F : '{print $2}'"
        print("get_averageBitrate:%s" % cmd)
    #    os.popen(cmd) 
        process=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
        while process.poll() is None:
            process.stderr.read(1024).decode("utf-8")
          
        f = open(filename,'r')
        for line in f.readlines():  
           if line.find("kb/s:")>=0:
               list = line.split(':')
               bitrate.append(list[1])   
        f.close()  
        
              
    print("bitrate=%s" % bitrate)
    for i in range(0,len(bitrate)):
       count+=float(bitrate[i])
    count/=len(bitrate)
    return count
   
          
if __name__ == "__main__":
   print(sys.argv[1])
   print(sys.argv[2])
   t=SliceTransClass(sys.argv[1],sys.argv[2])
   t.sliceTranscoding()
   t.concatSlices()


  

    
   

  


