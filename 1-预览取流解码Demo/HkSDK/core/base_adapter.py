import os
import ctypes


# 海康威视基础类，AI摄像机，通用摄像机，门禁产品，出入口产品通用
class BaseAdapter:
    # 动态sdk文件 .so .dll
    so_list = []

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


    # python 调用 sdk 指定方法
    def call_lib_cpp(self, func_name, *args):
        for so_lib in self.so_list:
            try:
                lib = ctypes.CDLL.LoadLibrary(so_lib)
                try:
                    value = eval("lib.%s" % func_name)(*args)
                    # logging.info("调用的库：" + so_lib)
                    # logging.info("执行成功,返回值：" + str(value))
                    return value
                except:
                    continue
            except:
                # logging.info("库文件载入失败：" + so_lib)
                continue

        # logging.error("没有找到接口！")
        return False


    def init_sdk(self):     # 初始化海康微视 sdk
        init_res = self.call_cpp("NET_DVR_Init")  # SDK初始化
        if init_res:
            # logging.info("SDK初始化成功")
            return True
        else:
            # self.print_error("NET_DVR_GetLastError 初始化SDK失败: the error code is ")
            return False

    def set_sdk_config(self, enumType, sdkPath):     # 设置sdk初始化参数
        # req = base.NET_DVR_LOCAL_SDK_PATH()
        req
        sPath = bytes(sdkPath, "ascii")
        i = 0
        for o in sPath:
            req.sPath[i] = o
            i += 1

        ptr = ctypes.byref(req)
        res = self.call_cpp("NET_DVR_SetSDKInitCfg", enumType, ptr)
        if res < 0:
            self.print_error("NET_DVR_SetSDKInitCfg 启动预览失败: the error code is")
        return res


    def sdk_clean(self):     # 释放sdk
        result = self.call_cpp("NET_DVR_Cleanup")
        # logging.info("释放资源", result)
        

if __name__ == '__main__':
    test_base = BaseAdapter()
    test_base.add_lib(r"C:\Users\徐旭\Desktop\HIK\CH-HCNetSDKV6.1.9.48_build20230410_win64\Demo示例\5- Python开发示例\1-预览取流解码Demo\lib\win",".dll")
    print(test_base.so_list)