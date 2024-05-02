import base64
from io import BytesIO
from time import time
from collections import namedtuple

import numpy as np
from PIL import Image
import pyrealsense2 as rs

RS_OUTPUT = namedtuple("RealSense", 
                       ["rgb_frame","bgr_frame", 
                        "ir_frame", "base64_color_frame",
                        "depth_frame", "depth_array", "depth_colormap",
                        "frame_width", "frame_height", "depth_delay"])

class RealSenseSR300:
    def __init__(self) -> None:
        
        self._pipline = rs.pipeline()
        self._config = rs.config()
        
        # 设置深度图为 16 位，尺寸 640x480，帧率 60
        self._config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        # # 设置灰度图为 8 位，尺寸 640x480，帧率 60
        self._config.enable_stream(rs.stream.infrared, 640, 480, rs.format.y8, 30)
        # 设置彩色图为 8 位，尺寸 640x480，帧率 60
        self._config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        self._colorizer = rs.colorizer()
        self._colorizer.set_option(rs.option.min_distance, 0)  # meter
        self._colorizer.set_option(rs.option.max_distance, 1.2)  # meter
                
        # 深度图向彩色图对其，可以获得彩色图上特定像素对应的深度信息
        self._align = rs.align(rs.stream.infrared)
    
    def start(self) -> RS_OUTPUT | None:
        self._pipline.start(self._config)

    def get_data(self) -> None | RS_OUTPUT:
        
        start_time = time()
        
        realsense_frame = self._pipline.wait_for_frames()
        aligned_rs_frame = self._align.process(realsense_frame)
        del realsense_frame
        
        depth_frame = aligned_rs_frame.get_depth_frame()
        infrared_frame = aligned_rs_frame.get_infrared_frame()
        color_frame = aligned_rs_frame.get_color_frame()
        
        if not depth_frame or not color_frame: return None
        
        frame_width = depth_frame.get_width()
        frame_height = depth_frame.get_height()
        
        depth_array = np.asanyarray(depth_frame.get_data())
        depth_colormap = np.asanyarray(self._colorizer.colorize(depth_frame).get_data())
        ir_frame = np.asanyarray(infrared_frame.get_data())
        bgr_frame = np.asanyarray(color_frame.get_data())
        rgb_frame = np.asanyarray(color_frame.get_data())
        
        base64_color_frame = self._frame2base64(rgb_frame)
        
        time_usage = time() - start_time
        
        return RS_OUTPUT(rgb_frame=color_frame, bgr_frame=bgr_frame, 
                         ir_frame=ir_frame, base64_color_frame=base64_color_frame,
                         depth_frame=depth_frame, depth_colormap=depth_colormap, depth_array=depth_array,
                         frame_width=frame_width, frame_height=frame_height, depth_delay=time_usage)

    @staticmethod
    def _frame2base64(frame):
        """
        将 OpenCV 视频帧编码为 BASE64 编码
        :param frame: OpenCV VideoCapture frame
        :return: base64_img
        """
        img = Image.fromarray(frame)  # 将每一帧转化为 Image
        output_buffer = BytesIO()  # 创建一个 BytesIO
        img.save(output_buffer, format='JPEG')  # 将图像写入 output_buffer
        byte_data = output_buffer.getvalue()  # 在内存中读取
        base64_data = base64.b64encode(byte_data).decode('utf-8')  # 转为 BASE64
        return base64_data  # 转码成功，返回 BASE64 编码
    
    def __del__(self) -> None:
        self._pipline.stop()


        
        