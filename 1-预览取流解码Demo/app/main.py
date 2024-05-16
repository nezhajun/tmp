import sys

# 添加新的路径
new_path = r'C:\Users\徐旭\Desktop\HIK\tmp\1-预览取流解码Demo'
if new_path not in sys.path:
    sys.path.append(new_path)

from HkSDK.camera.camera_adapter import CameraAdapter,CameraWidget



if __name__ == '__main__':

    cWidget = CameraWidget(480,360)
    cWidget.create_canvas(lwidth=480,lheight=360,lrow=0,lcolumn=0)
    cWidget.create_canvas(lwidth=480,lheight=360,lrow=0,lcolumn=1)
    cWidget.create_canvas(lwidth=480,lheight=360,lrow=0,lcolumn=2)


    camera01 = CameraAdapter("camera01")
    camera02 = CameraAdapter("camera02")

    camera01.set_window(cWidget.get_canvas_id(0))
    camera02.set_window(cWidget.get_canvas_id(1))
    camera01.login(b'192.168.1.221',8000,b'admin',b'123456789abc')
    camera02.login(b'192.168.1.222',8000,b'admin',b'123456789abc')
    
    def on_exit():
        camera01.logout()
        camera02.logout()
        exit()
        
    cWidget.create_bottom("exit",on_exit)
    camera01.start_preview()
    camera02.start_preview()
    print(camera01.camera_id)
    print(camera01.camera_info)
    # print(camera02.camera_id)
    # print(camera02.camera_info)
    
    
    cWidget.loop()

    print("dddddddddddddddddddd")
    # sleep(1000)
    print("sleep over")
    camera01.logout()
    camera02.logout()





