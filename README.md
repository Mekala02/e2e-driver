# E2E Driver (Self Driving Library)

Using:
* Jetson AGX Xavier JetPack 5.0.2 --- r35.1.0</br>
* Arduino Nano</br>

Configuration 1:
* Custom 3D Printed Body on top of modified Wltoys 124017 chassis</br>
* ZED Mini Stereo Camera</br>
* HC-020K Optical Encoder</br>
* Turnigy Evolution Radio Control System</br>

<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/car_1.jpg" title="Web_Interface" alt="Web_Interface"/>&nbsp;

Configuration 2:
* Traxxas chassis</br>
* ZED Stereo Camera</br>
* Flysky FS-i6X Radio Control System</br>
* VESC</br>

<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/car_itu_1.jpg" title="Web_Interface" alt="Web_Interface"/>&nbsp;

<h1>Features</h1>
- Currently using behavioral cloning for driving autonomously</br>
- Modular architecture. New parts can be added easily<br/>
- Parts works at high speed and low latency thanks to threading and multi threading,<br/>
&ensp;all parts can run min @100 Hz.<br/>
- Easy to set up and configure.<br/>
- Fast training and inferance<br/>
- TensorRT support<br/>
- TensorBoard support<br/>
- DAgger(Dataset Aggregation) support<br/>
- Data Augmentation support<br/>
- Cruise Control<br/>
- Merge multiple datasets with ease<br/>
- Reduced data sampling<br/>
- Early stopping<br/>
- Web interface<br/>
<br/>
<h1>Web Interface</h1>
<h3>Low Latency Live Data:</h3>
<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/16.jpg" title="Web_Interface" alt="Web_Interface"/>&nbsp;

<h3>Data Editing:</h3>
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
