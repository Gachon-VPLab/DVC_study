import re
import numpy
import os
import torch

print(list(range(torch.cuda.device_count())))

# size_line = []
# pattern = r'size= '

#with open('ffreport.log') as f:
#    a = f.readlines()
    
#for line in a:
#    print(re.search(pattern, line))


# with open('C:/Users/VPLab/Documents/Video processing lab/AI Based Video Coding/PyTorchVideoCompression-master/DVC/data/UVG/CreateI/ffreport.log') as f:
#         lines = f.readlines()

# size_line = []

# for l in lines:
#     if "size= " in l:
#          size = l.split('=')[4]
#          print(size)
#          break
#          size_line.append(int(size.strip(" ").strip("kB time")))

#print(size_line)

#size_line = numpy.array(size_line)*8.0/(1920*1024)

#print(size_line)
#print(len(size_line))

# root = '/home/tannidas/Codes/AI_Based_Video_Coding/DVC/PyTorchVideoCompression-master/DVC/data/UVG/images/'
# filelist="/home/tannidas/Codes/AI_Based_Video_Coding/DVC/PyTorchVideoCompression-master/DVC/data/UVG/images/Beauty/"#"/home/tannidas/Codes/AI_Based_Video_Coding/DVC/PyTorchVideoCompression-master/DVC/data/UVG/originalv.txt"

#with open(filelist) as f:
#     folders = f.readlines()

#for folder in folders:
#    #print(folder.rstrip)
#    seq = folder.rstrip()
#    imlist = os.listdir(os.path.join(root, seq))
#    print(len(folders)
#    break

#imlist = os.listdir(filelist)
#print(len(imlist))