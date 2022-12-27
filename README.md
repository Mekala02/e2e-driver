# E2E Driver (Self Driving Library)
This is an ongoing project!</br>

Currently Using:
* Custom 3D Printed Body on top of modified Wltoys 124017 chassis</br>
* Jetson AGX Xavier JetPack 5.0.2 --- r35.1.0</br>
* ZED Mini Stereo Camera</br>
* Arduino Nano</br>
* HC-020K Optical Encoder</br>
* Turnigy Evolution Radio Control System</br>

<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/car_1.jpg" title="Web_Interface" alt="Web_Interface"/>&nbsp;

<h1>Features</h1>
Modular architecture. New parts can be added easily<br/>
Parts can work threaded and multithreaded.<br/>
High speed, all parts can run min @100 FPS.<br/>
Easy to setup and configure.<br/>
Fast data saving.<br/>
DAgger(Dataset Aggregation)<br/>
Data Augmentation<br/>
Cruise Control<br/>
Merge multiple datasets<br/>
Reduced fps sampling<br/>
Depth input<br/>
Imu, encoder input<br/>
Tensorrt<br/>
Tensorboard<br/>
Fast inferance<br/>
Fast training<br/>
Early stoping<br/>
Web interface<br/>
<br/>
<h3>Low Latency Live Data:</h3>
<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/16.jpg" title="Web_Interface" alt="Web_Interface"/>&nbsp;

<h3>User finedly Data Editing:</h3>
<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/data_edit_web_interface.gif" title="Data_Edit_Web_Interface" alt="Data_Edit_Web_Interface"/>&nbsp;

<h1>Getting Started</h1>

Pull docker image:
```bash
sudo docker pull mekala02/e2e-driver:developer
```
Run docker image:
```
nvidia-docker run -it --rm --privileged --network host --ipc=host -v $(pwd):/root mekala02/e2e-driver:developer
```
