# -*- coding: utf-8 -*-
"""
功能说明：
获取 D430 相机的画面与景深数据

Author: Kuang Da
Create time: 2023/07/12
Github: https://github.com/Ender-William
"""
import os
import cv2
import pyrealsense2 as rs
import numpy
import time


class RealsenseD430:
    def __init__(self, record=False):
        # Configure depth and grey_frame streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # 设置深度图为16位，尺寸640x480.帧率30
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        # 设置灰度图为8位，尺寸640x480.帧率30
        self.config.enable_stream(rs.stream.infrared, 640, 480, rs.format.y8, 30)
        if record:
            current_path = os.path.dirname(__file__)
            data_time = str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
            config_path = current_path + "/record/record_file_" + data_time + ".bag"
            print(f"RealsenseD430 Data Save Path: \n{config_path}")
            self.config.enable_record_to_file(config_path)

        self.depth_intrin = None  # 深度相机内参
        self.irl_intrin = None  # 红外相机内参

        # 创建对齐对象与infrared流对齐
        align_to = rs.stream.infrared  # align_to 是计划对齐深度帧的流类型
        self.align = rs.align(align_to)  # rs.align 执行深度帧与其他帧的对齐

        self.frames = None  # 单帧
        self.depth_frame = None  # 深度数据单帧
        self.irl_frame = None  # 红外数据单帧
        self.irl_image_frame = None  # 红外相机画面单帧

        # Filter
        self.depth_to_disparity = None
        self.disparity_to_depth = None
        self.decimation = None
        self.spatial = None
        self.temporal = None
        self.hole_filling = None
        self.depth_frame_filter()  # 初始化过滤器

    def start(self):
        # Start streaming
        self.pipeline.start(self.config)

    def stop(self):
        # Stop streaming
        self.pipeline.stop()

    def get_frame(self):
        """get depth and grey frames from realsense pipeline"""
        self.frames = self.pipeline.wait_for_frames()
        self.frames = self.align.process(self.frames)

        # 获取相机数据
        self.depth_frame = self.frames.get_depth_frame()
        self.irl_frame = self.frames.get_infrared_frame(0)  # use left IR Camera

        # 获取相机参数
        self.depth_intrin = self.depth_frame.profile.as_video_stream_profile().intrinsics  # 获取深度参数，用于像素坐标系转换相机坐标系
        self.irl_intrin = self.irl_frame.profile.as_video_stream_profile().intrinsics  # 获取相机内参

    def get_irl_image(self):
        # Convert ir camera data to ndarray for opencv
        self.irl_image_frame = numpy.asanyarray(self.irl_frame.get_data())
        return self.irl_image_frame

    def depth_frame_filter(self):
        """this is a internal function"""
        self.depth_to_disparity = rs.disparity_transform(True)
        self.disparity_to_depth = rs.disparity_transform(False)

        # 创建抽取过滤器
        self.decimation = rs.decimation_filter()
        self.decimation.set_option(rs.option.filter_magnitude, 1)

        # 空间过滤器
        self.spatial = rs.spatial_filter()
        self.spatial.set_option(rs.option.filter_magnitude, 5)
        self.spatial.set_option(rs.option.filter_smooth_alpha, 1)
        self.spatial.set_option(rs.option.filter_smooth_delta, 50)

        self.spatial.set_option(rs.option.holes_fill, 3)

        self.temporal = rs.temporal_filter()
        self.hole_filling = rs.hole_filling_filter()

    def get_depth_image(self):
        """
        Get depth colorizer image
        :return: ndarray frame
        """
        # 初始化着色器
        colorizer = rs.colorizer()

        frame = self.depth_frame
        frame = self.decimation.process(frame)
        frame = self.depth_to_disparity.process(frame)
        frame = self.spatial.process(frame)
        frame = self.temporal.process(frame)
        frame = self.disparity_to_depth.process(frame)
        frame = self.hole_filling.process(frame)

        colorized_depth = numpy.asanyarray(colorizer.colorize(frame).get_data())
        return colorized_depth

    def get_target_depth(self, depth_pixel: [int, int]):
        """
        Get target pixel depth data`
        :param depth_pixel: [X,Y]
        :return: distance, coordinate
        """
        if depth_pixel[0] > 620 or depth_pixel[0] < 1:
            return None, None
        if depth_pixel[1] > 460 or depth_pixel[1] < 1:
            return None, None
        distance = self.depth_frame.get_distance(depth_pixel[0], depth_pixel[1])
        coordinate = rs.rs2_deproject_pixel_to_point(self.depth_intrin, depth_pixel, distance)
        return distance, coordinate

