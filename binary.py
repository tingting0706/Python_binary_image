import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import matplotlib

import PIL
from PIL import Image,ImageTk

import cv2
import os
import json
import numpy as np
import math


class BinarySystem(tk.Tk):
     
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self,"show the binary image")
        container = tk.Frame(self)
        container.pack(side="top",fill=None,expand = False)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        
        self.frames = {}
        '''
        for F in (mainPage,showPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky="nsew")
        '''
        frame = mainPage(container,self)
        self.frames[mainPage] = frame
        frame.grid(row=0,column=0,sticky="nsew")
        
        self.show_frame(mainPage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

        
        
class mainPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        tk.Frame(self)
        btn1 = tk.Button(self,text="讀取影像",width=12,height=1, font = ('Microsoft JhengHei',14),background="#ccc",command=lambda: self.openfile())
        btn1.grid(row=0,column=0,sticky="nsew",padx=14,pady=10)
        btn2 = tk.Button(self,text="直方圖均化",width=12,height=1, font = ('Microsoft JhengHei',14),background="#ccc",command=self.show_histogram_equalization)
        btn2.grid(row=1,column=0,sticky="nsew",padx=14,pady=10)
        label = tk.Label(self)
        label.grid(row=0,column=1,sticky="nsew",padx=14,pady=10,columnspan=2)
        
        
        self.filename = ''
        
        self.avg_gray = 0
        self.avg_gray_not_zero = 0
        
    def openfile(self):
        self.filename = fd.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("PNG 檔案","*.png"),("JEPG 檔案","*.jpg"),("all files","*.*")))
        #print(self.filename) #印出選擇的檔案的路徑&名稱
        temp=self.filename.split('/')
        #print(temp[-1])

        label_fname = tk.Label(self,text=temp[-1]) #顯示檔案名稱在介面上
        label_fname.grid(row=0,column=1,sticky="nsew",padx=14,pady=10)
        
        img_org = Image.open(self.filename) #開啟圖片
        #print(img_org.size)
        if img_org.size[0] > img_org.size[1]: #判斷圖片是長型還寬型
            width = 700
        else:
            width = 320
        ratio = float(width)/img_org.size[0]
        height = int(img_org.size[1]*ratio)
        resize_img = img_org.resize((width,height),Image.BILINEAR) #等比縮放
        photo = ImageTk.PhotoImage(resize_img)
        print(resize_img.size)
        
        binary_scale = tk.Scale(self, from_=0, to=255, orient="horizontal",length=100,sliderlength=16,command=self.binary)
        binary_scale.grid(row=3,column=0,sticky="nsew",padx=10,pady=10,columnspan=2)
        
        label_image = tk.Label(self,image = photo)
        label_image.resize_img = photo
        label_image.grid(row=5,column=0,sticky="nsew",padx=14,pady=10,columnspan=2)
        
        self.img = cv2.imread(self.filename,0)
        self.avg_gray_calculate()
        
        label_avg_gray = tk.Label(self,text='平均灰階:'+str(self.avg_gray))
        label_avg_gray.grid(row=2,column=0,sticky="nsew",padx=14,pady=10)
        
        label_avg_gray_not_zero = tk.Label(self,text='平均灰階(扣除黑色):'+str(self.avg_gray_not_zero))
        label_avg_gray_not_zero.grid(row=2,column=1,sticky="nsew",padx=14,pady=10)
        
        #cv2.imshow('org_image', self.img)
        

    
    def show_histogram_equalization(self):
        self.img = cv2.imread(self.filename,0)
        eq = cv2.equalizeHist(self.img)
        #cv2.imshow("Histogram Equalization", np.hstack([self.img, eq]))
        
        
        
        add_img = np.zeros((self.img.shape[0],self.img.shape[1],3),np.uint8)
        imgray = cv2.cvtColor(add_img,cv2.COLOR_BGR2GRAY)

        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                imgray[i][j]=math.ceil((int(self.img[i][j])+int(eq[i][j]))/2)
        
        
        if eq.shape[1] > eq.shape[0]: #判斷圖片是長型還寬型
            width = 700
        else:
            width = 320
        ratio = float(width)/eq.shape[1]
        height = int(eq.shape[0]*ratio)
        
        eq = cv2.resize(eq,(width,height)) #等比縮放
        cv2.imshow("Histogram Equalization", eq)

        imgray = cv2.resize(imgray,(width,height)) #等比縮放
        cv2.imshow("Average image", imgray)
    
    
    def binary(self,value):
        self.img = cv2.imread(self.filename,0)
        bin_value = int(value)
        #print(bin_value)
        ret, self.img = cv2.threshold(self.img, bin_value, 255, cv2.THRESH_BINARY) 
        
        if self.img.shape[1] > self.img.shape[0]: #判斷圖片是長型還寬型
            width = 700
        else:
            width = 320
        ratio = float(width)/self.img.shape[1]
        height = int(self.img.shape[0]*ratio)
        new_selfimg = cv2.resize(self.img,(width,height)) #等比縮放
        
        cv2.imshow('image', new_selfimg)
        cv2.waitKey(1)
        
    def avg_gray_calculate(self):
        h = self.img.shape[0]
        w = self.img.shape[1]
        gray_add = 0
        gray_add_not_zero = 0
        not_zero_count = 0
        for i in range(h):
            for j in range(w):
                gray_add = gray_add+self.img[i][j]
                if self.img[i][j] != 0:
                    gray_add_not_zero = gray_add_not_zero+self.img[i][j]
                    not_zero_count += 1
                
        self.avg_gray = int(gray_add/(h*w))
        self.avg_gray_not_zero = int(gray_add_not_zero/not_zero_count)
        print(self.avg_gray)
        print(not_zero_count)
        print(self.avg_gray_not_zero)
        


app = BinarySystem()
app.mainloop() 