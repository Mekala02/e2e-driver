# E2E Driver
End To End Self Driving Car

<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/car_1.jpg" title="Web_Interface" alt="Web_Interface"/>&nbsp;

This is a ongoing project!

Using Jetson Xavier JetPack 5.0.2 --- r35.1.0</br>
Pull docker image:
```bash
sudo docker pull mekala02/e2e-driver:developer
```
Run docker image:
```
nvidia-docker run -it --rm --privileged --network host --ipc=host -v $(pwd):/root mekala02/e2e-driver:developer
```

<h1>Features</h1>

Easy to use modular architecture.<br/>
High speed, all parts can run min @100 FPS.<br/>
Web interface.<br/>

Web Interface For Live Data:

<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/web_interface.gif" title="Web_Interface" alt="Web_Interface"/>&nbsp;

Web Interface For Editing Data:

<img src="https://github.com/Mekala02/e2e-driver/blob/main/docs/data_edit_web_interface.gif" title="Data_Edit_Web_Interface" alt="Data_Edit_Web_Interface"/>&nbsp;
