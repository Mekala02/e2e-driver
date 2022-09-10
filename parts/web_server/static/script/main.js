let Track = new Status()
update_interval = 10 //ms

function load_parameters(outputs){
    for (const [key, value] of Object.entries(outputs)) {
        Track.outputs[key] = value
        console.log(key, value);
      }
      Track.update_client_side()
      setInterval(Track.update_indicators, update_interval)
}

document.getElementById("Emergency_Button").addEventListener("click", function() {Track.Emergency_Stop()})

document.getElementById('C_RGB').addEventListener("click", function() {Track.Update_Camera_Mode("RGB")});
document.getElementById('C_Depth').addEventListener("click", function() {Track.Update_Camera_Mode("Depth")});
document.getElementById('C_Object_Detection').addEventListener("click", function() {Track.Update_Camera_Mode("Object_Detection")});

document.getElementById('G1_Steering').addEventListener("click", function() {Track.Update_Graph_Mode("Steering", 1)});
document.getElementById('G1_Throttle').addEventListener("click", function() {Track.Update_Graph_Mode("Throttle", 1)});
document.getElementById('G1_Speed').addEventListener("click", function() {Track.Update_Graph_Mode("Speed", 1)});

document.getElementById('G1_IMU_Accel_X').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Accel_X", 1)});
document.getElementById('G1_IMU_Accel_Y').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Accel_Y", 1)});
document.getElementById('G1_IMU_Accel_Z').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Accel_Z", 1)});
document.getElementById('G1_IMU_Gyro_X').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Gyro_X", 1)});
document.getElementById('G1_IMU_Gyro_Y').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Gyro_Y", 1)});
document.getElementById('G1_IMU_Gyro_Z').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Gyro_Z", 1)});

// document.getElementById('G1_IMU_Mode_Select').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Mode_Select", 1)});

document.getElementById('G2_Steering').addEventListener("click", function() {Track.Update_Graph_Mode("Steering", 2)});
document.getElementById('G2_Throttle').addEventListener("click", function() {Track.Update_Graph_Mode("Throttle", 2)});
document.getElementById('G2_Speed').addEventListener("click", function() {Track.Update_Graph_Mode("Speed", 2)});
document.getElementById('G2_IMU_Accel_X').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Accel_X", 2)});
document.getElementById('G2_IMU_Accel_Y').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Accel_Y", 2)});
document.getElementById('G2_IMU_Accel_Z').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Accel_Z", 2)});
document.getElementById('G2_IMU_Gyro_X').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Gyro_X", 2)});
document.getElementById('G2_IMU_Gyro_Y').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Gyro_Y", 2)});
document.getElementById('G2_IMU_Gyro_Z').addEventListener("click", function() {Track.Update_Graph_Mode("IMU_Gyro_Z", 2)});

const  speed_slider = document.getElementById("Speed_Slider")
speed_slider.addEventListener("input", function() {Track.Update_Speed_Factor(speed_slider.value)})

document.getElementById("Go").addEventListener("click", function() {Track.Update_Motor_Power()})
document.getElementById("Record").addEventListener("click", function() {Track.Update_Record()})

document.getElementById("Pilot_Full_Auto").addEventListener("click", function() {Track.Update_Pilot_Mode("Full_Auto")})
document.getElementById("Pilot_Angle").addEventListener("click", function() {Track.Update_Pilot_Mode("Angle")})
document.getElementById("Pilot_Manuel").addEventListener("click", function() {Track.Update_Pilot_Mode("Manuel")})

document.getElementById("Route_Route").addEventListener("click", function() {Track.Update_Route_Mode("Route")})
document.getElementById("Route_Random").addEventListener("click", function() {Track.Update_Route_Mode("Random")})
document.getElementById("Route_Manuel").addEventListener("click", function() {Track.Update_Route_Mode("Manuel")})

var layout = {
  autosize: true,
  margin: {
      l: 25,
      r: 25,
      b: 25,
      t: 25,
      pad: 0
  },
  paper_bgcolor: '#222222',
  plot_bgcolor: '#222222',
  xaxis: {showticklabels: false},
  yaxis: {showticklabels: false},
  showlegend: true,
  legend:{
    font:{
      family: "Courier",
      size: 12,
      color: "white",
    },
    bgcolor: "transparent",
    orientation: "h",
    yanchor: "bottom",
    y: 0,
    xanchor: "right",
    x: 1
  }
};

var trace1 = {
  x: [],
  y: [],
  type:'line',
  line: {
  color: 'red',
  width: 4
}}

var length1 = 0
function graph(graph){
  length1 = Track.graph["Timestamp"].length

  var traces = []
  for (let mode of Track.outputs[`Graph${graph}_Mode`]){
    traces.push({
      x: Track.graph["Timestamp"].slice(Math.max(0, length1 - 500), length1 - 1),
      y: Track.graph[mode].slice(Math.max(0, length1 - 500), length1 - 1),
      name: mode,
      type:'line',
      line: {
      // color: 'red',
      width: 4
    }})
  }

  layout["xaxis"]["range"] = [trace1["x"][0], trace1["x"][500]]

  Plotly.react(`Graph${graph}`, traces, layout, {displayModeBar: false})
}

setInterval(function(){graph(1)}, update_interval)
setInterval(function(){graph(2)}, update_interval)