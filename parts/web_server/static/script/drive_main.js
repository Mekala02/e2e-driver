let track = new Main_Track()
update_interval = 30 //ms

/*
When we run our server it will render html template then calls load parameters function.
Load parameters function loads default values on first startup, if we refresh the page
sam thing happens but load parameters function will load stored values.

We setting interval for updating client side indicators according to data we received.
*/

function load_parameters(outputs){
    for (const [key, value] of Object.entries(outputs)) {
        track.outputs[key] = value
        console.log(key, value);
    }
    update_client_side()
    setInterval(function() {update_indicators()}, update_interval)
}

function update_client_side(){
    for (const key in track.outputs){
        eval(`track.Update_${key}(undefined, 1)`)
    }
}

function update_indicators(){
    fetch("inputs")
    .then(response => response.json())
    .then(inputs => {
        track.Update_Stop(inputs["Stop"])
        track.Update_Taxi(inputs["Taxi"])
        track.Update_Direction(inputs["Direction"])
        track.Update_Lane(inputs["Lane"])
        track.Update_Steering(inputs["Steering"])
        track.Update_Throttle(inputs["Throttle"])
        track.Update_Speed(inputs["Speed"])
        track.Update_FPS(inputs["Fps"])
        for (const key in track.graph) {
            track.graph[key].push(inputs[key])
        }
        // If there is overwrite, Overwrites the outputs then updates
        for (const key in inputs["overwrite"]){
            value = inputs["overwrite"][key]
            // If overwrite value different then our value overwriting
            if (track.outputs[key] != value)
                eval(`track.Update_${key}("${value}")`)
        }
    })
}

setInterval(function(){track.update_graph(1)}, update_interval)
setInterval(function(){track.update_graph(2)}, update_interval)

document.getElementById("Emergency_Button").addEventListener("click", function() {track.Emergency_Stop()})

document.getElementById('C_Color_Image').addEventListener("click", function() {track.Update_Camera_Mode("Color_Image")});
document.getElementById('C_Depth_Image').addEventListener("click", function() {track.Update_Camera_Mode("Depth_Image")});
document.getElementById('C_Object_Detection_Image').addEventListener("click", function() {track.Update_Camera_Mode("Object_Detection_Image")});

document.getElementById('G1_Steering').addEventListener("click", function() {track.Update_Graph_Mode("Steering", 1)});
document.getElementById('G1_Target_Speed').addEventListener("click", function() {track.Update_Graph_Mode("Target_Speed", 1)});
document.getElementById('G1_Throttle').addEventListener("click", function() {track.Update_Graph_Mode("Throttle", 1)});
document.getElementById('G1_IMU_Accel_X').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Accel_X", 1)});
document.getElementById('G1_IMU_Accel_Y').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Accel_Y", 1)});
document.getElementById('G1_IMU_Accel_Z').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Accel_Z", 1)});
document.getElementById('G1_IMU_Gyro_X').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Gyro_X", 1)});
document.getElementById('G1_IMU_Gyro_Y').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Gyro_Y", 1)});
document.getElementById('G1_IMU_Gyro_Z').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Gyro_Z", 1)});
document.getElementById('G1_Speed').addEventListener("click", function() {track.Update_Graph_Mode("Speed", 1)});

// document.getElementById('G1_IMU_Mode_Select').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Mode_Select", 1)});

document.getElementById('G2_Steering').addEventListener("click", function() {track.Update_Graph_Mode("Steering", 2)});
document.getElementById('G2_Target_Speed').addEventListener("click", function() {track.Update_Graph_Mode("Target_Speed", 2)});
document.getElementById('G2_Throttle').addEventListener("click", function() {track.Update_Graph_Mode("Throttle", 2)});
document.getElementById('G2_IMU_Accel_X').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Accel_X", 2)});
document.getElementById('G2_IMU_Accel_Y').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Accel_Y", 2)});
document.getElementById('G2_IMU_Accel_Z').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Accel_Z", 2)});
document.getElementById('G2_IMU_Gyro_X').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Gyro_X", 2)});
document.getElementById('G2_IMU_Gyro_Y').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Gyro_Y", 2)});
document.getElementById('G2_IMU_Gyro_Z').addEventListener("click", function() {track.Update_Graph_Mode("IMU_Gyro_Z", 2)});
document.getElementById('G2_Speed').addEventListener("click", function() {track.Update_Graph_Mode("Speed", 2)});

const  speed_slider = document.getElementById("Speed_Slider")
speed_slider.addEventListener("input", function() {track.Update_Speed_Factor(speed_slider.value)})

document.getElementById("Go").addEventListener("click", function() {track.Update_Motor_Power()})
document.getElementById("Record").addEventListener("click", function() {track.Update_Record()})

document.getElementById("Pilot_Full_Auto").addEventListener("click", function() {track.Update_Pilot_Mode("Full_Auto")})
document.getElementById("Pilot_Angle").addEventListener("click", function() {track.Update_Pilot_Mode("Angle")})
document.getElementById("Pilot_Manuel").addEventListener("click", function() {track.Update_Pilot_Mode("Manuel")})

document.getElementById("Route_Route").addEventListener("click", function() {track.Update_Route_Mode("Route")})
document.getElementById("Route_Random").addEventListener("click", function() {track.Update_Route_Mode("Random")})
document.getElementById("Route_Manuel").addEventListener("click", function() {track.Update_Route_Mode("Manuel")})