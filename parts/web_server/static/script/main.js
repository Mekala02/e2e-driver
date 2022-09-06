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
document.getElementById('G1_IMU').addEventListener("click", function() {Track.Update_Graph_Mode("IMU", 1)});

document.getElementById('G2_Steering').addEventListener("click", function() {Track.Update_Graph_Mode("Steering", 2)});
document.getElementById('G2_Throttle').addEventListener("click", function() {Track.Update_Graph_Mode("Throttle", 2)});
document.getElementById('G2_Speed').addEventListener("click", function() {Track.Update_Graph_Mode("Speed", 2)});
document.getElementById('G2_IMU').addEventListener("click", function() {Track.Update_Graph_Mode("IMU", 2)});

document.getElementById("Speed_Slider").addEventListener("input", function() {Track.Update_Speed_Factor()})

document.getElementById("Go").addEventListener("click", function() {Track.Update_Motor_Power()})
document.getElementById("Record").addEventListener("click", function() {Track.Update_Record()})

document.getElementById("Pilot_Full_Auto").addEventListener("click", function() {Track.Update_Pilot_Mode("Full_Auto")})
document.getElementById("Pilot_Angle").addEventListener("click", function() {Track.Update_Pilot_Mode("Angle")})
document.getElementById("Pilot_Manuel").addEventListener("click", function() {Track.Update_Pilot_Mode("Manuel")})

document.getElementById("Route_Route").addEventListener("click", function() {Track.Update_Route_Mode("Route")})
document.getElementById("Route_Random").addEventListener("click", function() {Track.Update_Route_Mode("Random")})
document.getElementById("Route_Manuel").addEventListener("click", function() {Track.Update_Route_Mode("Manuel")})

function getData() {
  return Math.random();
}  

var layout1 = {
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
  yaxis: {showticklabels: false}
};

var trace1 = {
  x: [],
  y: [],
  type:'line',
  line: {
  color: 'red',
  width: 4
}}

Plotly.react('Graph1', [trace1], layout1, {displayModeBar: false});

var length1 = 0

setInterval(function(){
  length1 = Track.graph["timestamp"].length
  trace1["x"] = Track.graph["timestamp"].slice(Math.max(0, length1 - 500), length1 - 1)
  trace1["y"] = Track.graph["steering"].slice(Math.max(0, length1 - 500), length1 - 1)
  layout1["xaxis"]["range"] = [trace1["x"][0], trace1["x"][500]]
  Plotly.relayout('Graph1', layout1);
}, update_interval);


var layout2 = JSON.parse(JSON.stringify(layout1))

var trace2 = {
  x:[],
  y:[],
  type:'line',
  line: {
  color: 'blue',
  width: 4
}}

Plotly.react('Graph2', [trace2], layout2, {displayModeBar: false});

var length2 = 0

setInterval(function(){
  length2 = Track.graph["timestamp"].length
  trace2['x'] = Track.graph["timestamp"].slice(Math.max(0, length2 - 500), length2 - 1)
  trace2["y"] = Track.graph["throttle"].slice(Math.max(0, length2 - 500), length2 - 1)
  layout2["xaxis"]["range"] = [trace2["x"][0], trace2["x"][500]]
  Plotly.relayout('Graph2', layout2);
}, update_interval);
