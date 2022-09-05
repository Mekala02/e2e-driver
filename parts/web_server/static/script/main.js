let Track = new Status()

function load_parameters(outputs){
    for (const [key, value] of Object.entries(outputs)) {
        Track.outputs[key] = value
        console.log(key, value);
      }
      Track.update_client_side()
      setInterval(Track.update_indicators, update_interval)
}

document.getElementById("Emergency_Button").addEventListener("click", function() {Track.Emergency_Stop()})

document.getElementById('Camera_Mode').addEventListener('change', function() {Track.Update_Camera_Mode(this.value)});
document.getElementById('Graph_Mode').addEventListener('change', function() {Track.Update_Graph_Mode(this.value)});

document.getElementById("Speed_Slider").addEventListener("input", function() {Track.Update_Speed_Factor()})

document.getElementById("Go").addEventListener("click", function() {Track.Update_Motor_Power()})
document.getElementById("Record").addEventListener("click", function() {Track.Update_Record()})

document.getElementById("Pilot_Full_Auto").addEventListener("click", function() {Track.Update_Pilot_Mode("Full_Auto")})
document.getElementById("Pilot_Angle").addEventListener("click", function() {Track.Update_Pilot_Mode("Angle")})
document.getElementById("Pilot_Manuel").addEventListener("click", function() {Track.Update_Pilot_Mode("Manuel")})

document.getElementById("Route_Route").addEventListener("click", function() {Track.Update_Route_Mode("Route")})
document.getElementById("Route_Random").addEventListener("click", function() {Track.Update_Route_Mode("Random")})
document.getElementById("Route_Manuel").addEventListener("click", function() {Track.Update_Route_Mode("Manuel")})
