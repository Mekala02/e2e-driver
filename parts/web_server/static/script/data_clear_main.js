let data_clear_track = new Data_Clear_Track()
update_interval = 30 //ms

function update_client_side(){
  for (const key in data_clear_track.outputs){
      eval(`data_clear_track.Update_${key}(undefined, 1)`)
  }
  get_graph_data()
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
    .then(function(){data_clear_track.Update_Graph_Display()})
  }

function load_parameters(outputs){
    for (const [key, value] of Object.entries(outputs)) {
        data_clear_track.outputs[key] = value
        console.log(key, value);
      }
      update_client_side()
      setInterval(function() {update_indicators()}, update_interval)
}

function update_graph(name){
  data_clear_track.Update_Graph_Mode(name, 1)
  get_graph_data()
}

function bar_move(e){
  index = e.offsetX * data_clear_track.outputs["Data_Lenght"] / data_clear_track.Progress_Bar_Width
  data_clear_track.Update_Data_Index(Math.round(index))
}

document.getElementById("Emergency_Button").addEventListener("click", function() {data_clear_track.Emergency_Stop()})

document.getElementById('C_RGB').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("RGB")})
document.getElementById('C_Depth').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Depth")})
document.getElementById('C_Object_Detection').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Object_Detection")})

document.getElementById('G1_Steering').addEventListener("click", function() {update_graph("Steering")})
document.getElementById('G1_Throttle').addEventListener("click", function() {update_graph("Throttle")})
document.getElementById('G1_Speed').addEventListener("click", function() {update_graph("Speed")})

document.getElementById('G1_IMU_Accel_X').addEventListener("click", function() {update_graph("IMU_Accel_X")})
document.getElementById('G1_IMU_Accel_Y').addEventListener("click", function() {update_graph("IMU_Accel_Y")})
document.getElementById('G1_IMU_Accel_Z').addEventListener("click", function() {update_graph("IMU_Accel_Z")})
document.getElementById('G1_IMU_Gyro_X').addEventListener("click", function() {update_graph("IMU_Gyro_X")})
document.getElementById('G1_IMU_Gyro_Y').addEventListener("click", function() {update_graph("IMU_Gyro_Y")})
document.getElementById('G1_IMU_Gyro_Z').addEventListener("click", function() {update_graph("IMU_Gyro_Z")})

document.getElementById('Progress_Bar').addEventListener("mousedown", function(e){
  bar_move(e)
  document.getElementById('Progress_Bar').addEventListener("mousemove", bar_move)
  }
)
document.getElementById('Progress_Bar').addEventListener("mouseup", function(){
  document.getElementById('Progress_Bar').removeEventListener("mousemove", bar_move)
})

document.getElementById('Mark_Left_Button').addEventListener("click", function() {data_clear_track.Update_Left_Marker(data_clear_track.outputs["Data_Index"])})
document.getElementById('Mark_Right_Button').addEventListener("click", function() {data_clear_track.Update_Right_Marker(data_clear_track.outputs["Data_Index"])})
document.getElementById('Delete_Button').addEventListener("click", function() {data_clear_track.Update_Select_List(["Delete"])})

document.getElementById('Progress_Bar').addEventListener("dblclick", function(e){
  index = Math.round(e.offsetX * data_clear_track.outputs["Data_Lenght"] / data_clear_track.Progress_Bar_Width)
  for (const dict of data_clear_track.outputs["Select_List"]){
    if(dict["Indexes"][0] < index && index < dict["Indexes"][1]){
      data_clear_track.Update_Left_Marker(dict["Indexes"][0])
      data_clear_track.Update_Right_Marker(dict["Indexes"][1])
    }
  }
})

document.getElementById('Unselect_Button').addEventListener("click", function() {
  left_marker = data_clear_track.outputs["Left_Marker"]
  right_marker = data_clear_track.outputs["Right_Marker"]
  for (const dict of data_clear_track.outputs["Select_List"]){
    if(dict["Indexes"][0] == left_marker && dict["Indexes"][1] == right_marker){
      const index = data_clear_track.outputs["Select_List"].indexOf(data_clear_track.outputs["Select_List"])
      data_clear_track.outputs["Select_List"].splice(index, 1)
      data_clear_track.send_data({Select_List: data_clear_track.outputs["Select_List"]})
      data_clear_track.Update_Select_List(undefined, 1)
      return
    }
  }
})
