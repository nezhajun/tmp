# coding=utf-8

from ctypes import *
import sys

# 回调函数类型定义
if 'linux' in sys.platform:
    fun_ctype = CFUNCTYPE
else:
    fun_ctype = WINFUNCTYPE

# 定义预览参数结构体
class FRAME_INFO(Structure):
    pass
LPFRAME_INFO = POINTER(FRAME_INFO)
FRAME_INFO._fields_ = [
    ('nWidth', c_uint32),
    ('nHeight', c_uint32),
    ('nStamp', c_uint32),
    ('nType', c_uint32),
    ('nFrameRate', c_uint32),
    ('dwFrameNum', c_uint32)
]

# 显示回调函数
DISPLAYCBFUN = fun_ctype(None, c_long, c_char_p, c_long, c_long, c_long, c_long, c_long, c_long)
# 解码回调函数
DECCBFUNWIN = fun_ctype(None, c_long, POINTER(c_char), c_long, POINTER(FRAME_INFO), c_void_p, c_void_p)


new_path = r'C:\Users\徐旭\Desktop\HIK\tmp\1-预览取流解码Demo'
if new_path not in sys.path:
    sys.path.append(new_path)

from HkSDK.core.base_adapter import get_libcdll

class PlayAdapter():
    def __init__(self) -> None:
        self.PlayCtrl_obj = get_libcdll(2)
    
    def get_port(self):
        self.PlayCtrl_obj.PlayM4_GetPort()
        
    