from ctypes import *


NET_DVR_NOERROR = 0  # 没有错误。 
NET_DVR_ALLOC_RESOURCE_ERROR = 41 #  SDK资源分配错误。 
NET_DVR_GETLOCALIPANDMACFAIL = 53 # 获得本地PC的IP地址或物理地址失败。 

class NET_DVR_DEVICEINFO_V40(ctypes.Structure):
    _fields_ = [
        ('struDeviceV30', NET_DVR_DEVICEINFO_V30),  # 设备信息
        ('bySupportLock', c_byte),  # 设备支持锁定功能，该字段由SDK根据设备返回值来赋值的。bySupportLock为1时，dwSurplusLockTime和byRetryLoginTime有效
        ('byRetryLoginTime', c_byte),  # 剩余可尝试登陆的次数，用户名，密码错误时，此参数有效
        ('byPasswordLevel', c_byte),  # admin密码安全等级
        ('byProxyType', c_byte),  # 代理类型，0-不使用代理, 1-使用socks5代理, 2-使用EHome代理
        ('dwSurplusLockTime', c_uint32),  # 剩余时间，单位秒，用户锁定时，此参数有效
        ('byCharEncodeType', c_byte),  # 字符编码类型
        ('bySupportDev5', c_byte),  # 支持v50版本的设备参数获取，设备名称和设备类型名称长度扩展为64字节
        ('bySupport', c_byte),   # 能力集扩展，位与结果：0- 不支持，1- 支持
        ('byLoginMode', c_byte),  # 登录模式:0- Private登录，1- ISAPI登录
        ('dwOEMCode', c_uint32),  # OEM Code
        ('iResidualValidity', c_uint32),  # 该用户密码剩余有效天数，单位：天，返回负值，表示密码已经超期使用，例如“-3表示密码已经超期使用3天”
        ('byResidualValidity', c_byte),  # iResidualValidity字段是否有效，0-无效，1-有效
        ('bySingleStartDTalkChan', c_byte),  # 独立音轨接入的设备，起始接入通道号，0-为保留字节，无实际含义，音轨通道号不能从0开始
        ('bySingleDTalkChanNums', c_byte),  # 独立音轨接入的设备的通道总数，0-表示不支持
        ('byPassWordResetLevel', c_byte),  # 0-无效，
        # 1- 管理员创建一个非管理员用户为其设置密码，该非管理员用户正确登录设备后要提示“请修改初始登录密码”，未修改的情况下，用户每次登入都会进行提醒；
        # 2- 当非管理员用户的密码被管理员修改，该非管理员用户再次正确登录设备后，需要提示“请重新设置登录密码”，未修改的情况下，用户每次登入都会进行提醒。
        ('bySupportStreamEncrypt', c_byte),  # 能力集扩展，位与结果：0- 不支持，1- 支持
        # bySupportStreamEncrypt & 0x1 表示是否支持RTP/TLS取流
        # bySupportStreamEncrypt & 0x2 表示是否支持SRTP/UDP取流
        # bySupportStreamEncrypt & 0x4 表示是否支持SRTP/MULTICAST取流
        ('byMarketType', c_byte),  # 0-无效（未知类型）,1-经销型，2-行业型
        ('byRes2', c_byte * 238)  #保留，置为0
    ]
LPNET_DVR_DEVICEINFO_V40 = POINTER(NET_DVR_DEVICEINFO_V40)