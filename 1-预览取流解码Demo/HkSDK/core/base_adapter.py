import os
import platform
import ctypes
import HCNetSDK

WINDOWS_FLAG = True

def GetPlatform():
    sysstr = platform.system()
    print('' + sysstr)
    if sysstr != "Windows":
        global WINDOWS_FLAG
        WINDOWS_FLAG = False


# 海康威视基础类，AI摄像机，通用摄像机，门禁产品，出入口产品通用
class BaseAdapter:
    
    # 动态sdk文件 .so .dll
    so_list = []

    def __init__(self,id=None) -> None:
        self.BaseID = id
        self.HCNetSDK_obj = None
        self.PlayCtrl_obj = None
    
    def set_lib(self, so_list: []): # 设置所有的so文件
        self.so_list = so_list


    def get_lib(self): # 获取所有的so文件列表
        return self.so_list


    def add_lib(self, path, suffix):  # 加载目录下所有so文件
        files = os.listdir(path)

        for file in files:
            if not os.path.isdir(path + file):
                if file.endswith(suffix):
                    self.so_list.append(path + file)
            else:
                self.add_lib(path + file + "/", suffix)


    def set_sdk_config(self, enumType, sdkPath):     # 设置sdk初始化参数
        # 设置HCNetSDKCom组件库和SSL库加载路径
        # print(os.getcwd())
        if WINDOWS_FLAG:
            strPath = os.getcwd().encode('gbk')
            sdk_ComPath = HCNetSDK.NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.HCNetSDK_obj.NET_DVR_SetSDKInitCfg(2, ctypes.byref(sdk_ComPath))
            self.HCNetSDK_obj.NET_DVR_SetSDKInitCfg(3, ctypes.create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll'))
            self.HCNetSDK_obj.NET_DVR_SetSDKInitCfg(4, ctypes.create_string_buffer(strPath + b'\libssl-1_1-x64.dll'))
        else:
            strPath = os.getcwd().encode('utf-8')
            sdk_ComPath = HCNetSDK.NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.HCNetSDK_obj.NET_DVR_SetSDKInitCfg(2, ctypes.byref(sdk_ComPath))
            self.HCNetSDK_obj.NET_DVR_SetSDKInitCfg(3, ctypes.create_string_buffer(strPath + b'/libcrypto.so.1.1'))
            self.HCNetSDK_obj.NET_DVR_SetSDKInitCfg(4, ctypes.create_string_buffer(strPath + b'/libssl.so.1.1'))


    def sdk_init(self):     # 初始化海康微视 sdk 
        if WINDOWS_FLAG == True:
            os.chdir(r'./lib/win')
            self.HCNetSDK_obj = ctypes.CDLL(r'./HCNetSDK.dll')
        else:
            os.chdir(r'./lib/linux')
            self.HCNetSDK_obj = ctypes.cdll.LoadLibrary(r'./libhcnetsdk.so')

        self.set_sdk_config()

        err = self.HCNetSDK_obj.NET_DVR_Init()
        if err:
            # logging.info("SDK初始化成功")
            return True
        else:
            # self.print_error("NET_DVR_GetLastError 初始化SDK失败: the error code is ")
            return False


    def sdk_clean(self):     # 释放sdk
        err = self.HCNetSDK_obj.NET_DVR_Cleanup()
        # logging.info("释放资源", result)
        
    def loginDev(selof)
        

if __name__ == '__main__':
    test_base = BaseAdapter()
    test_base.add_lib(r"C:\Users\徐旭\Desktop\HIK\CH-HCNetSDKV6.1.9.48_build20230410_win64\Demo示例\5- Python开发示例\1-预览取流解码Demo\lib\win",".dll")
    print(test_base.so_list)