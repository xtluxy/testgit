#!/usr/bin/env python
#coding:utf-8
import sys, os,time,subprocess,time,re,logging

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
     logging.info("get_sliceStartTime(): %s", cmd)
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
      process=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
      output =process.communicate()[1]
      logging.info("sliceTranscoding(): %s", cmd) 
      logging.info("%s", output.decode()) 
          
 def concatSlices(self):
   f = open('file.txt', 'w')
   for i in range(0,self.__sliceSum):
       f.write("file \'" + self.__filepath + "_test" + str(i) + ".mp4\'\n")
   f.close( )
   cmd="ffmpeg -f concat -i file.txt -c copy -y " + self.__filepath +"_concat.mp4"
   process=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)    
   output =process.communicate()[1]
   logging.info("concatSlices(): %s", cmd) 
   logging.info("%s", output.decode()) 
   
   
 def __init__(self,filepath,sliceSum):
     self.__logger = logging.getLogger()
     self.__logger.setLevel(logging.DEBUG)
     handler = logging.FileHandler('test.log')
     handler.setLevel(logging.DEBUG)
     formatter = logging.Formatter('[%(levelname)s]  %(asctime)s  %(name)s  %(message)s')
     handler.setFormatter(formatter)
     self.__logger.addHandler(handler)
        
     self.__filepath=filepath
     self.__sliceSum=int(sliceSum)
     self.__duration=float(self.get_duration())
     self.__sliceDuration=self.get_sliceDuration()
     self.__fFStart=float(self.get_fFStart())   
     logging.info("self.__filepath: %s, self.__sliceSum: %d", self.__filepath, self.__sliceSum)
     logging.info("self.__duration: %f, self.__sliceDuration: %f, self.__fFStart: %f", self.__duration, self.__sliceDuration,self.__fFStart)

     self.__sliceStartTime=[] 
     self.__stArray=[]
     self.__intervalArray=[]
     self.get_sliceStartTime() 
     self.get_stArray()
     self.get_intervalArray()     
     self.__averageBitrate=self.get_averageBitrate()
     
     logging.info("self.__sliceStartTime: %s", self.__sliceStartTime)
     logging.info("self.__stArray: %s", self.__stArray)
     logging.info("self.__intervalArray: %s", self.__intervalArray)
     logging.info("self.__averageBitrate: %s", self.__averageBitrate)
     
 def __del__(self):
    pass
 
 def get_averageBitrate(self):
    bitrate=[]
    count=0
    for i in range(0,self.__sliceSum-1):
        cmd="ffmpeg -ss " + self.__sliceStartTime[i] + " -t 30 -i " + self.__filepath + " -c:v libx264 -crf 32 -an -f mp4 -y null"
    #   cmd="ffmpeg -ss " + self.__sliceStartTime[i] + " -t 30 -i " + self.__filepath
    #   cmd+=" -c:v libx264 -crf 32 -an -f mp4 -y null 2>&1 |grep kb/s: |awk -F : '{print $2}'"   
        process=subprocess.Popen(cmd,stderr=subprocess.PIPE, shell=True)
        output =process.communicate()[1]
        logging.info("get_averageBitrate(): %s", cmd) 
        logging.info("%s", output.decode()) 
        m=re.search('kb/s:[\d|.]+',output.decode())
        if m:
            list=re.split(':',m.group())
            bitrate.append(list[1])                                     
    logging.info("bitrate=%s", bitrate) 
    for i in range(0,len(bitrate)):
       count+=float(bitrate[i])
    count/=len(bitrate)
    return count
   
          
if __name__ == "__main__":
   tsbegin = int(time.time())
  
   logging.info("sys.argv[1]=%s,sys.argv[2]=%s", sys.argv[1],sys.argv[2])
   t=SliceTransClass(sys.argv[1],sys.argv[2])
   t.sliceTranscoding()
   t.concatSlices()
 
   tsend = int(time.time())
   logging.info("tsbegin=%s,tsend=%s,used=%f", tsbegin,tsend,(float(tsend)-float(tsbegin)))


  

    
   

  


