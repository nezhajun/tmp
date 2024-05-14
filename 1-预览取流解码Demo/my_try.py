import os
from ctypes import *
from HCNetSDK import *
import platform
import tkinter
import logging
from sdk_types import *

# 创建Logger对象
logger = logging.getLogger('my_try_logger')



def logger_config(logger_obj: logging.Logger):
    logger_obj.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG
    file_handler = logging.FileHandler('my_try.log',encoding="utf-8") # 创建FileHandler，设置日志文件名
    file_handler.setLevel(logging.DEBUG)     # 设置FileHandler的日志级别（可选）

    # 创建Formatter，设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - \
        [%(filename)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # 创建StreamHandler，用于输出到控制台
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # 设置StreamHandler的日志级别

    # 将Formatter添加到FileHandler
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 将FileHandler添加到Logger
    logger_obj.addHandler(file_handler)
    logger_obj.addHandler(stream_handler)


def sdk_config():
    strPath = os.getcwd().encode("gbk")
    sdk_err_r = c_bool(True) # 0 = FALSE
    local_sdk_path = NET_DVR_LOCAL_SDK_PATH()
    local_sdk_path.sPath = strPath
    sdk_err_r = Objdll.NET_DVR_SetSDKInitCfg(c_int(2),byref(local_sdk_path))
    if sdk_err_r == False:
        logger.error("local_sdk_path set err...")
    sdk_err_r = Objdll.NET_DVR_SetSDKInitCfg(c_int(3),create_string_buffer(strPath + b"\libcrypto-1_1-x64.dll"))
    if sdk_err_r == False:
        logger.error("libcrypto-1_1-x64.dll set err...")    
    sdk_err_r = Objdll.NET_DVR_SetSDKInitCfg(c_int(4),create_string_buffer(strPath + b"\libssl-1_1-x64.dll"))
    if sdk_err_r == False:
        logger.error("libssl-1_1-x64.dll set err...")

def log_dev(objdll):
    device_info = NET_DVR_DEVICEINFO_V30()
    lUserId = objdll.NET_DVR_Login_V30()
    return (lUserId,device_info)
    
if __name__ == '__main__':
    logger_config(logger)
    
    logger.info("device start running...")
    
    Objdll = CDLL(r"./lib/win/HCNetSDK.dll")
    playctrldll = CDLL(r'./lib/win/PlayCtrl.dll')
    
    sdk_config()
    
    sdk_err_r = Objdll.NET_DVR_Init()
    if sdk_err_r == NET_DVR_NOERROR:
        logger.info("NET_DVR_Init() okay...")
    elif sdk_err_r == NET_DVR_ALLOC_RESOURCE_ERROR:
        logger.error("NET_DVR_ALLOC_RESOURCE_ERROR")
    elif sdk_err_r == NET_DVR_ALLOC_RESOURCE_ERROR:
        logger.error("NET_DVR_GETLOCALIPANDMACFAIL")
    else:logger.error("NET_DVR_Init() error... err_code:%d",sdk_err_r)
    
    

    
    