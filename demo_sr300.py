import cv2
from time import time
from realsensepack import RealSenseSR300, SR300_OUTPUT

if __name__ == "__main__":
    
    RS = RealSenseSR300()
    RS.start()
    
    while True:
        st = time()
        output:None|SR300_OUTPUT = RS.get_data()
        
        if output is None: continue
        
        cv2.imshow("BGR Frame", output.ir_frame)
        cv2.waitKey(1)
        print(1 / (time()-st))
        
        