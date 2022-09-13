let data_clear_track = new Data_Clear_Track()
update_interval = 30 //ms

function update_client_side(){
  for (const key in data_clear_track.outputs){
      eval(`data_clear_track.Update_${key}(undefined, 1)`)
  }
}

function update_indicators(){
  fetch("inputs")
  .then(response => response.json())
  .then(inputs => {
      data_clear_track.Update_Stop(inputs["Stop"])
      data_clear_track.Update_Taxi(inputs["Taxi"])
      data_clear_track.Update_Direction(inputs["Direction"])
      data_clear_track.Update_Lane(inputs["Lane"])

      data_clear_track.Update_Steering(inputs["Steering"])
      data_clear_track.Update_Throttle(inputs["Throttle"])
      data_clear_track.Update_Speed(inputs["Speed"])

      data_clear_track.Update_FPS(inputs["Fps"])

    })
  }
  
  function get_graph_data(){
    fetch("graph")
    .then(response => response.json())
    .then(receive => {
      data_clear_track.Update_Graph_Data(receive)
    })
  }

function load_parameters(outputs){
    for (const [key, value] of Object.entries(outputs)) {
        data_clear_track.outputs[key] = value
        console.log(key, value);
      }
      update_client_side()

      setInterval(function() {update_indicators()}, update_interval)
}

get_graph_data()
// data_clear_track.Update_Graph_Display()

// setInterval(function(){data_clear_track.update_graph(1)}, update_interval)

document.getElementById("Emergency_Button").addEventListener("click", function() {data_clear_track.Emergency_Stop()})

document.getElementById('C_RGB').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("RGB")});
document.getElementById('C_Depth').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Depth")});
document.getElementById('C_Object_Detection').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Object_Detection")});

document.getElementById('G1_Steering').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("Steering", 1)});
document.getElementById('G1_Throttle').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("Throttle", 1)});
document.getElementById('G1_Speed').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("Speed", 1)});

document.getElementById('G1_IMU_Accel_X').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("IMU_Accel_X", 1)});
document.getElementById('G1_IMU_Accel_Y').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("IMU_Accel_Y", 1)});
document.getElementById('G1_IMU_Accel_Z').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("IMU_Accel_Z", 1)});
document.getElementById('G1_IMU_Gyro_X').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("IMU_Gyro_X", 1)});
document.getElementById('G1_IMU_Gyro_Y').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("IMU_Gyro_Y", 1)});
document.getElementById('G1_IMU_Gyro_Z').addEventListener("click", function() {data_clear_track.Update_Graph_Mode("IMU_Gyro_Z", 1)});

