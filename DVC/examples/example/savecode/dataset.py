import os
import torch
import logging
import cv2
from PIL import Image
import imageio
import numpy as np
import torch.utils.data as data
from os.path import join, exists
import math
import random
import sys
import json
import random
import os # modified
from subnet.basics import *
from subnet.ms_ssim_torch import ms_ssim
from augmentation import random_flip, random_crop_and_pad_image_and_labels

#filelist="./data/UVG/originalv.txt" #original
filePath = "/home/tannidas/Codes/AI_Based_Video_Coding/DVC/PyTorchVideoCompression-master/DVC/data/UVG/originalv.txt"
#root = "./data/UVG/images/"
root = "/home/tannidas/Codes/AI_Based_Video_Coding/DVC/PyTorchVideoCompression-master/DVC/data/UVG/images/"


class UVGDataSet(data.Dataset):
    def __init__(self, root=root, filelist=filePath, refdir='L12000', testfull=False):
        with open(filelist) as f:
            folders = f.readlines()
        self.ref = []
        self.refbpp = []
        self.input = []
        self.hevcclass = []
        AllIbpp = self.getbpp(refdir)
        ii = 0
        for folder in folders:
            seq = folder.rstrip()
            seqIbpp = AllIbpp[ii]
            imlist = os.listdir(os.path.join(root, seq))
            cnt = 0
            for im in imlist:
                if im[-4:] == '.png':
                    cnt += 1
            if testfull:
                framerange = cnt // 12
            else:
                framerange = 1
            for i in range(framerange):
                refpath = os.path.join(root, seq, refdir, 'im'+str(i * 12 + 1).zfill(4)+'.png')  ### original 4  ### original im
                #print(len(imlist))
                inputpath = []
                #print(refpath)
                for j in range(12):
                    inputpath.append(os.path.join(root, seq, 'im' + str(i * 12 + j + 1).zfill(3)+'.png'))
                #print(inputpath)
                self.ref.append(refpath)
                self.refbpp.append(seqIbpp)
                self.input.append(inputpath)
            ii += 1


    def getbpp(self, ref_i_folder):
        Ibpp = None
        if ref_i_folder == 'H265L20':
            print('use H265L20')
            Ibpp = [1.220703125e-05, 1.220703125e-05, 1.220703125e-05, 1.220703125e-05, 1.220703125e-05, 1.220703125e-05, 1.220703125e-05]# you need to fill bpps after generating crf=20
        elif ref_i_folder == 'H265L23':
            print('use H265L23')
            Ibpp = [1.220703125e-05, 1.220703125e-05, 0.0011637369791666667, 0.0012858072916666667, 1.220703125e-05, 1.220703125e-05, 1.220703125e-05]# you need to fill bpps after generating crf=23
        elif ref_i_folder == 'H265L26':
            print('use H265L26')
            Ibpp = [1.220703125e-05, 1.220703125e-05, 0.00062255859375, 0.0007405598958333333, 0.0011962890625, 1.220703125e-05, 1.220703125e-05]# you need to fill bpps after generating crf=26
        elif ref_i_folder == 'H265L29':
            print('use H265L29')
            Ibpp = [0.00072021484375, 0.0006022135416666667, 0.0003987630208333333, 0.00047607421875, 0.0008382161458333333, 1.220703125e-05, 1.220703125e-05]# you need to fill bpps after generating crf=29
        else:
            print('cannot find ref : ', ref_i_folder)
            exit()
        if len(Ibpp) == 0:
            print('You need to generate I frames and fill the bpps above!')
            exit()
        return Ibpp

    
    def __len__(self):
        return len(self.ref)

    def __getitem__(self, index):
        ref_image = imageio.imread(self.ref[index]).transpose(2, 0, 1).astype(np.float32) / 255.0
        #print('reference image: ',self.ref[index])
        h = (ref_image.shape[1] // 64) * 64
        w = (ref_image.shape[2] // 64) * 64
        ref_image = np.array(ref_image[:, :h, :w])
        input_images = []
        refpsnr = None
        refmsssim = None
        for filename in self.input[index]:
            input_image = (imageio.imread(filename).transpose(2, 0, 1)[:, :h, :w]).astype(np.float32) / 255.0
            #print('input image: ',filename)
            if refpsnr is None:
                refpsnr = CalcuPSNR(input_image, ref_image)
                refmsssim = ms_ssim(torch.from_numpy(input_image[np.newaxis, :]), torch.from_numpy(ref_image[np.newaxis, :]), data_range=1.0).numpy()
            else:
                input_images.append(input_image[:, :h, :w])

        input_images = np.array(input_images)
        return input_images, ref_image, self.refbpp[index], refpsnr, refmsssim

filePath = "../../data/vimeo_septuplet/vimeo_90k/vimeo_septuplet/test.txt"
rootPath = "../../data/vimeo_septuplet/vimeo_90k/vimeo_septuplet/sequences/"
#data/vimeo_septuplet/test.txt


class DataSet(data.Dataset):
    def __init__(self, path=filePath, im_height=256, im_width=256):
        # with open(filePath) as f:
        #     data = f.readlines()
        # sys.exit(data)
        self.image_input_list, self.image_ref_list = self.get_vimeo()
        self.im_height = im_height
        self.im_width = im_width
        
        self.featurenoise = torch.zeros([out_channel_M, self.im_height // 16, self.im_width // 16])
        self.znoise = torch.zeros([out_channel_N, self.im_height // 64, self.im_width // 64])
        self.mvnois = torch.zeros([out_channel_mv, self.im_height // 16, self.im_width // 16])
        print("dataset find image: ", len(self.image_input_list))

    def get_vimeo(self, rootdir=rootPath):
        with open(filePath) as f:
            data = f.readlines()


        ### for training on 5000 data
        newData = []
        dataChoice = np.random.randint(low=0, high=len(data), size=5000)
        for i in range (len(dataChoice)):
            newData.append(data[dataChoice[i]])
        data = newData
        #########
        
        fns_train_input = []
        fns_train_ref = []

        for n, line in enumerate(data, 1):
            y = os.path.join(rootdir, line.rstrip())
            fns_train_input += [y]
            refnumber = int(y[-5:-4]) - 2
            refname = y[0:-5] + str(refnumber) + '.png'
            fns_train_ref += [refname]

        return fns_train_input, fns_train_ref

    def __len__(self):
        return len(self.image_input_list)

    def __getitem__(self, index):
        # sys.exit(os.getcwd())
        #sys.exit(imageio.imread(rootPath + "00019/0830/im5.png"))
        input_image = imageio.imread(self.image_input_list[index])
        ref_image = imageio.imread(self.image_ref_list[index])

        input_image = input_image.astype(np.float32) / 255.0
        ref_image = ref_image.astype(np.float32) / 255.0

        input_image = input_image.transpose(2, 0, 1)
        ref_image = ref_image.transpose(2, 0, 1)
        
        input_image = torch.from_numpy(input_image).float()
        ref_image = torch.from_numpy(ref_image).float()

        input_image, ref_image = random_crop_and_pad_image_and_labels(input_image, ref_image, [self.im_height, self.im_width])
        input_image, ref_image = random_flip(input_image, ref_image)

        quant_noise_feature, quant_noise_z, quant_noise_mv = torch.nn.init.uniform_(torch.zeros_like(self.featurenoise), -0.5, 0.5), torch.nn.init.uniform_(torch.zeros_like(self.znoise), -0.5, 0.5), torch.nn.init.uniform_(torch.zeros_like(self.mvnois), -0.5, 0.5)
        return input_image, ref_image, quant_noise_feature, quant_noise_z, quant_noise_mv
        
