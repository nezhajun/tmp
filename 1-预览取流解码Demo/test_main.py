# coding=utf-8

import os
import platform
import tkinter
from tkinter import *
from HCNetSDK import *
from PlayCtrl import *
from time import sleep
from queue import Queue
import threading
import cv2
import numpy as np


# yv12_frame_data = np.frombuffer(item, dtype=np.uint8).reshape((height + height // 2, width))

# # 使用OpenCV将YV12转换为BGR格式
# bgr_frame = cv2.cvtColor(yv12_frame_data, cv2.COLOR_YUV2BGR_YV12)


queue_YV12_data = Queue(maxsize=100)
exit_event = threading.Event()

# 定义消费者
def consumer_get_queue_data():
    while not exit_event.is_set():
        q_size=queue_YV12_data.qsize()
        if q_size>10:
            print("queue_YV12_data = ",queue_YV12_data.qsize() )
        item = queue_YV12_data.get()
        sleep(0.01)
        nsize = item[1]
        width = item[2]
        height = item[3]
        yv12_frame_data = string_at(item[0],nsize)
        # yv12_frame_data = np.array(yv12_frame_data)
        # yv12_frame_data = np.frombuffer(yv12_frame_data, dtype=np.int8)
        yv12_frame_data = np.frombuffer(yv12_frame_data, dtype=np.uint8).reshape((height + height // 2, width))
        # yv12_frame_data = np.array(item)
        # print(type(yv12_frame_data),yv12_frame_data.shape,nsize,height,width)
        bgr_frame = cv2.cvtColor(yv12_frame_data, cv2.COLOR_YUV2BGR_YV12)
        h, w = bgr_frame.shape[:2]
        scale = 0.3
        bgr_frame = cv2.resize(bgr_frame, (int(w * scale), int(h * scale)))
        # rgb_frame = convert_yv12_to_rgb(yv12_frame_data,width,height)
        # queue_YV12_data.task_done()
        cv2.imshow('RGB Image', bgr_frame)
        cv2.waitKey(1)
        # cv2.destroyAllWindows()


consumer_get_queue_data_task = threading.Thread(target=consumer_get_queue_data)
# consumer_get_queue_data_task.setDaemon = True

def convert_yv12_to_rgb(yv12_data, width, height):
    # YV12数据在一个单一的数组中，需要首先将其转换为一个适合cvtColor函数使用的形式
    y_size = width * height
    uv_size = y_size // 4
    # Y分量
    y_plane = yv12_data[0:y_size].reshape((height, width))
    # V分量（注意YV12格式中V分量在U分量之前）
    v_plane = yv12_data[y_size:y_size+uv_size].reshape((height // 2, width // 2))
    # U分量
    u_plane = yv12_data[y_size+uv_size:y_size+2*uv_size].reshape((height // 2, width // 2))
    # OpenCV期望的YUV格式是连续的，Y分量之后紧跟U分量和V分量，且UV分量是交错的。
    # 由于YV12的UV分量是分开的，我们需要重新排列它们。
    uv_plane = cv2.resize(cv2.merge([u_plane, v_plane]), (width, height), interpolation=cv2.INTER_LINEAR)
    # 将Y分量和重新排列的UV分量合并成一个图像
    yuv_img = cv2.merge([y_plane, uv_plane[:,:,0], uv_plane[:,:,1]])
    # 使用cvtColor将YUV转换为RGB
    rgb_img = cv2.cvtColor(yuv_img, cv2.COLOR_YUV2RGB_YV12)
    return rgb_img


cnt=0
# 登录的设备信息
DEV_IP = create_string_buffer(b'192.168.1.221')
DEV_PORT = 8000
DEV_USER_NAME = create_string_buffer(b'admin')
DEV_PASSWORD = create_string_buffer(b'123456789abc')

WINDOWS_FLAG = True
win = None  # 预览窗口
funcRealDataCallBack_V30 = None  # 实时预览回调函数，需要定义为全局的

PlayCtrl_Port = c_long(-1)  # 播放句柄
Playctrldll = None  # 播放库
FuncDecCB = None   # 播放库解码回调函数，需要定义为全局的

# 获取当前系统环境
def GetPlatform():
    sysstr = platform.system()
    print('' + sysstr)
    if sysstr != "Windows":
        global WINDOWS_FLAG
        WINDOWS_FLAG = False

# 设置SDK初始化依赖库路径
def SetSDKInitCfg():
    # 设置HCNetSDKCom组件库和SSL库加载路径
    # print(os.getcwd())
    if WINDOWS_FLAG:
        strPath = os.getcwd().encode('gbk')
        sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
        sdk_ComPath.sPath = strPath
        Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
        Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll'))
        Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'\libssl-1_1-x64.dll'))
    else:
        strPath = os.getcwd().encode('utf-8')
        sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
        sdk_ComPath.sPath = strPath
        Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
        Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'/libcrypto.so.1.1'))
        Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'/libssl.so.1.1'))

def LoginDev(Objdll):
    # 登录注册设备
    device_info = NET_DVR_DEVICEINFO_V30()
    lUserId = Objdll.NET_DVR_Login_V30(DEV_IP, DEV_PORT, DEV_USER_NAME, DEV_PASSWORD, byref(device_info))
    return (lUserId, device_info)

def DecCBFun(nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
    # 解码回调函数
    if pFrameInfo.contents.nType == 3:
        # 解码返回视频YUV数据，将YUV数据转成jpg图片保存到本地
        # 如果有耗时处理，需要将解码数据拷贝到回调函数外面的其他线程里面处理，避免阻塞回调导致解码丢帧
        sFileName = ('../../pic/test_stamp[%d].jpg'% pFrameInfo.contents.nStamp)
        nWidth = pFrameInfo.contents.nWidth
        nHeight = pFrameInfo.contents.nHeight
        nType = pFrameInfo.contents.nType
        dwFrameNum = pFrameInfo.contents.dwFrameNum
        nStamp = pFrameInfo.contents.nStamp
        # print(nWidth, nHeight, nType, dwFrameNum, nStamp, sFileName)
        # print(nSize,nStamp)
        queue_YV12_data.put([pBuf,nSize,nWidth,nHeight])
        # lRet = Playctrldll.PlayM4_ConvertToJpegFile(pBuf, nSize, nWidth, nHeight, nType, c_char_p(sFileName.encode()))
        lRet = 1
        if lRet == 0:
            print('PlayM4_ConvertToJpegFile fail, error code is:', Playctrldll.PlayM4_GetLastError(nPort))
        else:pass
            # print('PlayM4_ConvertToJpegFile success')

def RealDataCallBack_V30(lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
    global cnt
    # 码流回调函数
    if dwDataType == NET_DVR_SYSHEAD:
        # 设置流播放模式
        Playctrldll.PlayM4_SetStreamOpenMode(PlayCtrl_Port, 0)
        # 打开码流，送入40字节系统头数据
        if Playctrldll.PlayM4_OpenStream(PlayCtrl_Port, pBuffer, dwBufSize, 1024*1024):
            # 设置解码回调，可以返回解码后YUV视频数据
            global FuncDecCB
            FuncDecCB = DECCBFUNWIN(DecCBFun)
            Playctrldll.PlayM4_SetDecCallBackExMend(PlayCtrl_Port, FuncDecCB, None, 0, None)
            # 开始解码播放
            if Playctrldll.PlayM4_Play(PlayCtrl_Port, cv.winfo_id()):
                print(u'播放库播放成功')
            else:
                print(u'播放库播放失败')
        else:
            print(u'播放库打开流失败')
    elif dwDataType == NET_DVR_STREAMDATA:
        # print("NET_DVR_STREAMDATA",cnt)
        cnt=cnt+1
        Playctrldll.PlayM4_InputData(PlayCtrl_Port, pBuffer, dwBufSize)
    else:
        print (u'其他数据,长度:', dwBufSize)

def OpenPreview(Objdll, lUserId, callbackFun):
    '''
    打开预览
    '''
    preview_info = NET_DVR_PREVIEWINFO()
    preview_info.hPlayWnd = 0
    preview_info.lChannel = 1  # 通道号
    preview_info.dwStreamType = 0  # 主码流
    preview_info.dwLinkMode = 0  # TCP
    preview_info.bBlocked = 1  # 阻塞取流

    # 开始预览并且设置回调函数回调获取实时流数据
    lRealPlayHandle = Objdll.NET_DVR_RealPlay_V40(lUserId, byref(preview_info), callbackFun, None)
    return lRealPlayHandle

def InputData(fileMp4, Playctrldll):
    while True:
        pFileData = fileMp4.read(4096)
        if pFileData is None:
            break

        if not Playctrldll.PlayM4_InputData(PlayCtrl_Port, pFileData, len(pFileData)):
            break

def on_exit():
    exit_event.set()  # 通知线程退出
    consumer_get_queue_data_task.join()  # 等待线程结束
    win.quit()  # 然后退出GUI

if __name__ == '__main__':
    # 创建窗口
    consumer_get_queue_data_task.start()
    win = tkinter.Tk()
    #固定窗口大小
    win.resizable(0, 0)
    win.overrideredirect(True)

    sw = win.winfo_screenwidth()
    # 得到屏幕宽度
    sh = win.winfo_screenheight()
    # 得到屏幕高度

    # 窗口宽高
    ww = 512
    wh = 384
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    win.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

    # 创建退出按键
    b = Button(win, text='退出', command=on_exit)
    b.pack()
    # 创建一个Canvas，设置其背景色为白色
    cv = tkinter.Canvas(win, bg='white', width=ww, height=wh)
    cv.pack()

    # 获取系统平台
    GetPlatform()

    # 加载库,先加载依赖库
    if WINDOWS_FLAG:
        os.chdir(r'./lib/win')
        Objdll = ctypes.CDLL(r'./HCNetSDK.dll')  # 加载网络库
        Playctrldll = ctypes.CDLL(r'./PlayCtrl.dll')  # 加载播放库
    else:
        os.chdir(r'./lib/linux')
        Objdll = cdll.LoadLibrary(r'./libhcnetsdk.so')
        Playctrldll = cdll.LoadLibrary(r'./libPlayCtrl.so')

    SetSDKInitCfg()  # 设置组件库和SSL库加载路径

    # 初始化DLL
    err = Objdll.NET_DVR_Init()
    print(err)
    # 启用SDK写日志
    Objdll.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)
   
    # 获取一个播放句柄
    if not Playctrldll.PlayM4_GetPort(byref(PlayCtrl_Port)):
        print(u'获取播放库句柄失败')

    # 登录设备
    (lUserId, device_info) = LoginDev(Objdll)
    if lUserId < 0:
        err = Objdll.NET_DVR_GetLastError()
        print('Login device fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
        # 释放资源
        Objdll.NET_DVR_Cleanup()
        exit()

    # 定义码流回调函数
    funcRealDataCallBack_V30 = REALDATACALLBACK(RealDataCallBack_V30)
    # 开启预览
    lRealPlayHandle = OpenPreview(Objdll, lUserId, funcRealDataCallBack_V30)
    if lRealPlayHandle < 0:
        print ('Open preview fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
        # 登出设备
        Objdll.NET_DVR_Logout(lUserId)
        # 释放资源
        Objdll.NET_DVR_Cleanup()
        exit()

    #show Windows
    win.mainloop()

    # # 开始云台控制
    # lRet = Objdll.NET_DVR_PTZControl(lRealPlayHandle, PAN_LEFT, 0)
    # if lRet == 0:
    #     print ('Start ptz control fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
    # else:
    #     print ('Start ptz control success')

    # # 转动一秒
    # sleep(1)

    # # 停止云台控制
    # lRet = Objdll.NET_DVR_PTZControl(lRealPlayHandle, PAN_LEFT, 1)
    # if lRet == 0:
    #     print('Stop ptz control fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
    # else:
    #     print('Stop ptz control success')
    
    print("dddddddddddddddddddd")
    # sleep(1000)
    print("sleep over")
    # 关闭预览
    Objdll.NET_DVR_StopRealPlay(lRealPlayHandle)

    # 停止解码，释放播放库资源
    if PlayCtrl_Port.value > -1:
        Playctrldll.PlayM4_Stop(PlayCtrl_Port)
        Playctrldll.PlayM4_CloseStream(PlayCtrl_Port)
        Playctrldll.PlayM4_FreePort(PlayCtrl_Port)
        PlayCtrl_Port = c_long(-1)

    # 登出设备
    Objdll.NET_DVR_Logout(lUserId)

    # 释放资源
    Objdll.NET_DVR_Cleanup()

