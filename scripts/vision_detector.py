#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float64MultiArray
from cv_bridge import CvBridge

TOPIC='/world/xyz_test/model/morphle_xy_axis/link/base_link/sensor/microscope_camera/image'

class VisionDetector(Node):
    def __init__(self):
        super().__init__('vision_detector')
        self.bridge=CvBridge()
        self.pub=self.create_publisher(Float64MultiArray,'/stage_velocity_controller/commands',10)
        self.sub=self.create_subscription(Image,TOPIC,self.cb,10)
        self.kp_x=0.00009; self.ki_x=0.0; self.kd_x=0.000025
        self.kp_y=0.00009; self.ki_y=0.0; self.kd_y=0.000025
        self.max_velocity=0.03; self.deadband=5.0
        self.prev_x=self.prev_y=0.0
        self.last_t=self.get_clock().now()
        self.get_logger().info('Vision-guided microscope detector started.')

    def cb(self,msg):
        try: frame=self.bridge.imgmsg_to_cv2(msg,'bgr8')
        except Exception as e:
            self.get_logger().error(str(e)); return
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        masks=[
            cv2.inRange(hsv,np.array([0,100,80]),np.array([10,255,255])),
            cv2.inRange(hsv,np.array([170,100,80]),np.array([180,255,255])),
            cv2.inRange(hsv,np.array([95,80,60]),np.array([135,255,255]))]
        mask=masks[0]|masks[1]|masks[2]
        n,_,stats,cent=cv2.connectedComponentsWithStats(mask)
        best=None
        for i in range(1,n):
            if stats[i,cv2.CC_STAT_AREA] >= 100:
                if best is None or stats[i,cv2.CC_STAT_AREA] > best[0]:
                    best=(stats[i,cv2.CC_STAT_AREA],cent[i])
        h,w=frame.shape[:2]; cx=w/2; cy=h/2
        if best is None:
            self.publish(0.0,0.0); return
        tx,ty=best[1]; ex=tx-cx; ey=ty-cy
        if abs(ex)<self.deadband: ex=0.0
        if abs(ey)<self.deadband: ey=0.0
        now=self.get_clock().now()
        dt=max((now-self.last_t).nanoseconds/1e9,1e-3)
        dx=(ex-self.prev_x)/dt; dy=(ey-self.prev_y)/dt
        vx=self.kp_x*ex+self.kd_x*dx
        vy=-(self.kp_y*ey+self.kd_y*dy)
        vx=float(np.clip(vx,-self.max_velocity,self.max_velocity))
        vy=float(np.clip(vy,-self.max_velocity,self.max_velocity))
        self.publish(vx,vy)
        self.prev_x=ex; self.prev_y=ey; self.last_t=now

    def publish(self,vx,vy):
        m=Float64MultiArray(); m.data=[float(vx),float(vy),0.0]; self.pub.publish(m)

def main(args=None):
    rclpy.init(args=args); node=VisionDetector()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    node.destroy_node(); rclpy.shutdown()

if __name__=='__main__': main()
