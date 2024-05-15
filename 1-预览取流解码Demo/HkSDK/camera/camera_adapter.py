
from ..core.base_adapter import BaseAdapter,GetPlatform,WINDOWS_FLAG
import ctypes
import HCNetSDK




class CameraAdapter(BaseAdapter):
    def __init__(self, name=None) -> None:
        self.name = name
        self.camera_id = None
        self.camera_info = None
        self.lRealPlayHandle = None
        self.PlayCtrl_Port = ctypes.c_long(-1)
        err = self.sdk_init()

    def login(self,DEV_IP=None,DEV_PORT=8000,DEV_USER_NAME=None,DEV_PASSWORD=None):
        (self.camera_id, self.camera_info) = self.login_dev(\
            ctypes.create_string_buffer(DEV_IP),\
            DEV_PORT,\
            ctypes.create_string_buffer(DEV_USER_NAME),\
            ctypes.create_string_buffer(DEV_PASSWORD) )
        if self.camera_id < 0:
            err = self.get_LastErrorCode()
            print('Login device fail, error code is: %d' % err)
            self.sdk_clean()             # 释放资源

    def logout(self):
        self.logout_dev(self.camera_id)
        err = self.get_LastErrorCode()
        self.sdk_clean() # 释放资源

    def start_preview(self,hPlayWnd=0,lChannel=1,dwStreamType=0,dwLinkMode=0,bBlocked=1):
        if not self.PlayCtrl_obj.PlayM4_GetPort(ctypes.byref(self.PlayCtrl_Port)): # 获取一个播放句柄
            print(u'获取播放库句柄失败')
        preview_info = HCNetSDK.NET_DVR_PREVIEWINFO()
        preview_info.hPlayWnd = hPlayWnd
        preview_info.lChannel = lChannel  # 通道号
        preview_info.dwStreamType = dwStreamType  # 主码流
        preview_info.dwLinkMode = dwLinkMode  # TCP
        preview_info.bBlocked = bBlocked  # 阻塞取流

        # 开始预览并且设置回调函数回调获取实时流数据
        funcRealDataCallBack_V30 = HCNetSDK.REALDATACALLBACK(self.RealDataCallBack_V30)
        self.lRealPlayHandle = self.PlayCtrl_obj.NET_DVR_RealPlay_V40(self.camera_id, ctypes.byref(preview_info), funcRealDataCallBack_V30, None)
        if self.lRealPlayHandle < 0:
            err = self.get_LastErrorCode()
            print ('Open preview fail, error code is: %d' % err)
            self.logout() # 登出设备并释放资源

    def stop_preview(self):
        self.HCNetSDK_obj.NET_DVR_StopRealPlay(self.lRealPlayHandle)

        # 停止解码，释放播放库资源
        if self.PlayCtrl_Port.value > -1:
            self.PlayCtrl_obj.PlayM4_Stop(self.PlayCtrl_Port)
            self.PlayCtrl_obj.PlayM4_CloseStream(self.PlayCtrl_Port)
            self.PlayCtrl_obj.PlayM4_FreePort(self.PlayCtrl_Port)
            self.PlayCtrl_Port = ctypes.c_long(-1)

    def RealDataCallBack_V30(self,lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
        global cnt
        # 码流回调函数
        if dwDataType == HCNetSDK.NET_DVR_SYSHEAD:
            # 设置流播放模式
            self.PlayCtrl_obj.PlayM4_SetStreamOpenMode(self.PlayCtrl_Port, 0)
            # 打开码流，送入40字节系统头数据
            if self.PlayCtrl_obj.PlayM4_OpenStream(self.PlayCtrl_Port, pBuffer, dwBufSize, 1024*1024):
                # 设置解码回调，可以返回解码后YUV视频数据
                global FuncDecCB
                FuncDecCB = DECCBFUNWIN(DecCBFun)
                self.PlayCtrl_obj.PlayM4_SetDecCallBackExMend(self.PlayCtrl_Port, FuncDecCB, None, 0, None)
                # 开始解码播放
                if self.PlayCtrl_obj.PlayM4_Play(self.PlayCtrl_Port, cv.winfo_id()):
                    print(u'播放库播放成功')
                else:
                    print(u'播放库播放失败')
            else:
                print(u'播放库打开流失败')
        elif dwDataType == HCNetSDK.NET_DVR_STREAMDATA:
            # print("NET_DVR_STREAMDATA",cnt)
            cnt=cnt+1
            self.PlayCtrl_obj.PlayM4_InputData(self.PlayCtrl_Port, pBuffer, dwBufSize)
        else:
            print (u'其他数据,长度:', dwBufSize)

    

class DataStream():
    def convert_yv12_to_rgb(self):
        pass
    
    def save_image():
        pass
    
    def save_video():
        pass



if __name__ == '__main__':
    camera01 = CameraAdapter("camera01")
    camera02 = CameraAdapter("camera02")
    camera01.login(b'192.168.1.221',8000,b'admin',b'123456789abc')
    camera01.login(b'192.168.1.223',8000,b'admin',b'123456789abc')

