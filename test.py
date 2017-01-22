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
     logging.info("get_sliceStartTime func:%s", cmd)
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
     self.sliceTranscodingPass1()
     self.sliceTranscodingPass2() 
      
 def sliceTranscodingPass1(self):
  processes=[]
  for i in range(0,self.__sliceSum):
      if i == 0:
          cmd = "ffmpeg -t " + str(self.__intervalArray[i])+ " -i " + self.__filepath + " -c:v libx264 -pass 1 -passlogfile " + self.__filepath +str(i) 
          cmd+= " -vb " +str(self. __averageBitrate)
          cmd+=  "k -c:a aac -ac 2 -f mpegts -y null &" 
      elif i == self.__sliceSum-1:
          cmd = "ffmpeg -ss " + str(self.__stArray[self.__sliceSum-1])+ " -i " + self.__filepath + " -c:v libx264 -pass 1 -passlogfile " + self.__filepath +str(i) 
          cmd+= " -vb " +str(self. __averageBitrate)
          cmd+= "k -c:a aac -ac 2 -f mpegts -y null &" 
      else:
          cmd = "ffmpeg -ss " + str(self.__stArray[i])+ " -t " + str(self.__intervalArray[i])+ " -i " + self.__filepath + " -c:v libx264 -pass 1 -passlogfile " + self.__filepath +str(i)
          cmd += " -vb " +str(self. __averageBitrate)
          cmd += "k -c:a aac -ac 2 -f mpegts -y null &"  
      logging.info("sliceTranscodingPass1 func: %s", cmd)     
      p=subprocess.Popen(cmd, stderr=subprocess.PIPE,shell=True)
      processes.append(p)
              
  logging.info("pass1 processes list: %s", processes)  
  for p in processes:
    output =p.communicate()[1]
    logging.info("%s", output.decode('utf-8', 'replace'))   
  logging.info("pass1 processes finished")
  
 def sliceTranscodingPass2(self):
  processes=[]
  for i in range(0,self.__sliceSum):
      if i == 0:
          cmd = "ffmpeg -t " + str(self.__intervalArray[i])+ " -i " + self.__filepath + " -c:v libx264 -pass 2 -passlogfile " + self.__filepath +str(i) 
          cmd+= " -vb " +str(self. __averageBitrate)
          cmd+= "k -c:a aac -ac 2 -ab 32k -f mpegts -y " + self.__filepath +"_test"+str(i)+".ts &" 
      elif i == self.__sliceSum-1:
          cmd = "ffmpeg -ss " + str(self.__stArray[self.__sliceSum-1])+ " -i " + self.__filepath + " -c:v libx264 -pass 2 -passlogfile " + self.__filepath +str(i) 
          cmd+= " -vb " +str(self. __averageBitrate)
          cmd+= "k -c:a aac -ac 2 -ab 32k -f mpegts -y " + self.__filepath +"_test"+str(i)+".ts &" 
      else:
          cmd = "ffmpeg -ss " + str(self.__stArray[i])+ " -t " + str(self.__intervalArray[i])+ " -i " + self.__filepath + " -c:v libx264 -pass 2 -passlogfile " + self.__filepath +str(i)
          cmd += " -vb " +str(self. __averageBitrate)
          cmd += "k -c:a aac -ac 2 -ab 32k -f mpegts -y " + self.__filepath +"_test"+str(i)+".ts &"
      logging.info("sliceTranscodingPass2 func: %s", cmd)     
      p=subprocess.Popen(cmd, stderr=subprocess.PIPE,shell=True)
      processes.append(p)
          
  logging.info("pass2 processes list: %s", processes)  
  for p in processes:
    output =p.communicate()[1]
    logging.info("%s", output.decode('utf-8', 'replace'))   
  logging.info("pass2 processes finished")
          
 def concatSlices(self):
   f = open('file.txt', 'w')
   for i in range(0,self.__sliceSum):
       f.write("file \'" + self.__filepath + "_test" + str(i) + ".ts\'\n")
   f.close( )
   cmd="ffmpeg -f concat -safe 0 -i file.txt -c copy -y " + self.__filepath +"_concat.ts"
   process=subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)    
   output =process.communicate()[1]
   logging.info("concatSlices func:%s", cmd) 
   logging.info("%s", output.decode('utf-8', 'replace')) 
   
   
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
     logging.info("filepath: %s, sliceSum: %d", filepath, self.__sliceSum)
     logging.info("duration: %f, sliceDuration: %f, fFStart: %f", self.__duration, self.__sliceDuration,self.__fFStart)

     self.__sliceStartTime=[] 
     self.__stArray=[]
     self.__intervalArray=[]
     self.get_sliceStartTime() 
     self.get_stArray()
     self.get_intervalArray()     
     self.__averageBitrate=self.get_averageBitrate()
     
     logging.info("sliceStartTime: %s", self.__sliceStartTime)
     logging.info("stArray: %s", self.__stArray)
     logging.info("intervalArray: %s", self.__intervalArray)
     logging.info("averageBitrate: %s", self.__averageBitrate)
     
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
        logging.info("get_averageBitrate func:%s", cmd) 
        logging.info("%s", output.decode('utf-8', 'replace')) 
        m=re.search('kb/s:[\d|.]+',output.decode('utf-8', 'replace' ))
        if m:
            list=re.split(':',m.group())
            bitrate.append(list[1])                                     
    logging.info("get_averageBitrate func:bitrate=%s", bitrate) 
    bitrate.sort()
    bitrate=bitrate[1:]
    logging.info("get_averageBitrate func:after del minValue,bitrate=%s", bitrate)
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


  

    
   

  


