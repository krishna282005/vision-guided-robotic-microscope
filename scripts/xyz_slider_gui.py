#!/usr/bin/env python3
import tkinter as tk
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class Slider(Node):
    def __init__(self):
        super().__init__('xyz_slider_gui')
        self.pub=self.create_publisher(Float64MultiArray,'/stage_velocity_controller/commands',10)
        self.x=self.y=self.z=0.0

    def publish(self):
        m=Float64MultiArray(); m.data=[self.x,self.y,self.z]; self.pub.publish(m)

def main():
    rclpy.init()
    node=Slider()
    root=tk.Tk(); root.title('XYZ GANTRY DEBUGGER'); root.geometry('420x300')
    def axis(label,lo,hi,attr):
        row=tk.Frame(root); row.pack(fill='x',padx=12,pady=8)
        tk.Label(row,text=label,width=5).pack(side='left')
        scale=tk.Scale(row,from_=lo,to=hi,resolution=0.001,orient='horizontal',length=280,
                       command=lambda v:setattr(node,attr,float(v)) or node.publish())
        scale.pack(side='left'); scale.set(0.0)
    axis('X',-0.10,0.10,'x')
    axis('Y',-0.08,0.08,'y')
    axis('Z',0.00,0.05,'z')
    def tick():
        rclpy.spin_once(node,timeout_sec=0)
        root.after(20,tick)
    root.after(20,tick)
    root.mainloop()
    node.destroy_node(); rclpy.shutdown()

if __name__=='__main__': main()
