let data_clear_track = new Data_Clear_Track()
update_interval = 30 //ms

/*
When we run our server it will render html template then calls load parameters function.
Load parameters function loads default values on first startup, if we refresh the page
sam thing happens but load parameters function will load stored values.

We setting interval for updating client side indicators according to data we received.

*/

function load_parameters(outputs){
  for (const [key, value] of Object.entries(outputs)) {
    data_clear_track.outputs[key] = value
    console.log(key, value);
  }
  update_client_side()
  setInterval(function() {update_indicators()}, update_interval)
}

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
  
  function update_graph(name){
    data_clear_track.Update_Graph_Mode(name, 1)
    get_graph_data()
  }

  function get_graph_data(){
    fetch("graph")
    .then(response => response.json())
    .then(receive => {
      data_clear_track.Update_Graph_Data(receive)
    })
    .then(function(){data_clear_track.Update_Graph_Display()})
  }

document.getElementById("Stop").addEventListener("dblclick", function() {data_clear_track.Update_Select_List({Stop: 0})})
document.getElementById("Stop").addEventListener("click", function() {data_clear_track.Update_Select_List({Stop: 1})})

document.getElementById("Taxi").addEventListener("dblclick", function() {data_clear_track.Update_Select_List({Taxi: 0})})
document.getElementById("Taxi").addEventListener("click", function() {data_clear_track.Update_Select_List({Taxi: 1})})


// If double click to arrow container direction will be none
document.getElementById("Arrow_Container").addEventListener("dblclick", function() {data_clear_track.Update_Select_List({Direction: null})})

document.getElementById("Left_Arrow").addEventListener("click", function() {data_clear_track.Update_Select_List({Direction: "Left"})})
document.getElementById("Forward_Arrow").addEventListener("click", function() {data_clear_track.Update_Select_List({Direction: "Forward"})})
document.getElementById("Right_Arrow").addEventListener("click", function() {data_clear_track.Update_Select_List({Direction: "Right"})})

document.getElementById("Left_Lane").addEventListener("click", function() {data_clear_track.Update_Select_List({Lane: "Left"})})
document.getElementById("Right_Lane").addEventListener("click", function() {data_clear_track.Update_Select_List({Lane: "Right"})})
document.getElementById("Emergency_Button").addEventListener("click", function() {data_clear_track.Emergency_Stop()})

document.getElementById('C_Color_Image').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Color_Image")})
document.getElementById('C_Depth_Image').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Depth_Image")})
document.getElementById('C_Object_Detection_Image').addEventListener("click", function() {data_clear_track.Update_Camera_Mode("Object_Detection_Image")})

document.getElementById('G1_Steering').addEventListener("click", function() {update_graph("Steering")})
document.getElementById('G1_Throttle').addEventListener("click", function() {update_graph("Throttle")})
document.getElementById('G1_Speed').addEventListener("click", function() {update_graph("Speed")})
document.getElementById('G1_IMU_Accel_X').addEventListener("click", function() {update_graph("IMU_Accel_X")})
document.getElementById('G1_IMU_Accel_Y').addEventListener("click", function() {update_graph("IMU_Accel_Y")})
document.getElementById('G1_IMU_Accel_Z').addEventListener("click", function() {update_graph("IMU_Accel_Z")})
document.getElementById('G1_IMU_Gyro_X').addEventListener("click", function() {update_graph("IMU_Gyro_X")})
document.getElementById('G1_IMU_Gyro_Y').addEventListener("click", function() {update_graph("IMU_Gyro_Y")})
document.getElementById('G1_IMU_Gyro_Z').addEventListener("click", function() {update_graph("IMU_Gyro_Z")})

// We detecting click and hold
document.getElementById('Progress_Bar').addEventListener("mousedown", function(e){
  // If we pres mouse button moving bar into that area
  bar_move(e)
  // And we starting to listen mause movement if we not mouseup (detecting the click and hold)
  document.getElementById('Progress_Bar').addEventListener("mousemove", bar_move)
  }
)
// If we click and release mouse button we are not moving bar according to mouse position
document.getElementById('Progress_Bar').addEventListener("mouseup", function(){
  document.getElementById('Progress_Bar').removeEventListener("mousemove", bar_move)
})

function bar_move(px=0, index=0){
  // If we passed position in px converting it to index
  if (px)
    index = px.offsetX * data_clear_track.outputs["Data_Lenght"] / data_clear_track.Progress_Bar_Width
  data_clear_track.Update_Data_Index(Math.round(index))
  // Updating graphs horizontal line
  data_clear_track.Update_Graph_Index()
}

var searchBar = document.getElementById('Search_Box')
// Listening for search query
searchBar.addEventListener("keydown", (e) => {
  // If we pres enter and query is not none
  if (e.key == "Enter" && searchBar.value != "") {
      searchQuery = Search_Box.value
      data_clear_track.mark_search_results(searchQuery)
  }
})

// Updating left marker and making changes div invisible and delete its content
document.getElementById('Mark_Left_Button').addEventListener("click", function() {data_clear_track.Update_Left_Marker(data_clear_track.outputs["Data_Index"])
  data_clear_track.update_display_changes(undefined, 1)})
document.getElementById('Mark_Right_Button').addEventListener("click", function() {data_clear_track.Update_Right_Marker(data_clear_track.outputs["Data_Index"])
  data_clear_track.update_display_changes(undefined, 1)})
document.getElementById('Unselect_Button').addEventListener("click", function() {data_clear_track.unselect()
  data_clear_track.update_display_changes(undefined, 1)})
document.getElementById('Delete_Button').addEventListener("click", function() {data_clear_track.Update_Select_List({Delete: true})})
document.getElementById('Save_Button').addEventListener("click", function() {data_clear_track.save_changes()})
document.getElementById('Apply_Button').addEventListener("click", function() {data_clear_track.apply_changes()})


// Listening for double click onte selected mark
document.getElementById('Progress_Bar').addEventListener("dblclick", function(e){
  // Converting px to index
  index = Math.round(e.offsetX * data_clear_track.outputs["Data_Lenght"] / data_clear_track.Progress_Bar_Width)
  // Searching for selected list that matches left, right index
  for (const dict of data_clear_track.outputs["Select_List"]){
    if(dict["Indexes"][0] < index && index < dict["Indexes"][1]){
      data_clear_track.Update_Left_Marker(dict["Indexes"][0])
      data_clear_track.Update_Right_Marker(dict["Indexes"][1])
      // Making visible the changes div
      data_clear_track.update_display_changes(dict["Changes"])
    }
  }
  // Same thing for search result divs
  for (const between of data_clear_track.search_results_list){
    if(between[0] < index && index < between[1]){
      data_clear_track.Update_Left_Marker(between[0])
      data_clear_track.Update_Right_Marker(between[1])
    }
  }
})

var endTime = 0
var startTime = 0
var counter = 0

// This is for wind or rewind the data index with arrow keys
addEventListener('keydown', function(e){
  // If our counter <= 5 that means we only presed for once so we winding our data
  // only one index but if we pres and hold counter will be greater then 5 in that
  // case we are winding or rewinding the video according to real speed
  if (counter > 5){
    // For mesuring time difference between this function
    endTime = performance.now()
    // Incrementing according to fps and clien side speed
    increment = Math.round((endTime - startTime) * data_clear_track.Fps / 1000)
  }
  else
    increment = 1
  if (e.code == "ArrowRight"){
    bar_move(0, data_clear_track.outputs["Data_Index"] + increment)
  }
  else if (e.code == "ArrowLeft"){
    bar_move(0, data_clear_track.outputs["Data_Index"] - increment)
  }
  startTime = performance.now()
  counter ++
})

// When we keyup reseting the counter becouse that means we are not presing it anymore
addEventListener('keyup', function(e){
  if (e.code == "ArrowRight"  || e.code == "ArrowLeft"){
    counter = 0
  }
})