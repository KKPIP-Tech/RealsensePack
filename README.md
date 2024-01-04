# RealsensePack
Intel Realsense Support Pack

当前支持的设备有：
Intel Realsense D430

预设的深度图为 16 位，640x480，30fps
预设的灰度图为 8 位，640x480，30fps

支持的系统及环境：
- Windows 10 及以上
- Ubuntu 20.04 LTS 及以上（其他的 Linux 发行版系统我没测试过）
- Python `3.8`, `3.10`, `3.11`

执行下面的指令安装
```
python setup.py build
python setup.py install
```

样例程序
```python
import cv2
from realsensepack import realsense as RealsenseD430

if __name__ == '__main__':
    Depth_Camera = RealsenseD430(record=False)
    Depth_Camera.start()
    while True:
        Depth_Camera.get_frame()
        irl_frame = Depth_Camera.get_irl_image()
        depth_frame = Depth_Camera.get_depth_image()
        print(Depth_Camera.get_target_depth(depth_pixel=[320, 320]))
        # cv2.namedWindow('IR Example', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('IR Example', depth_frame)
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
```