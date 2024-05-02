import cv2
from realsensepack import RealsenseD430

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
    pass