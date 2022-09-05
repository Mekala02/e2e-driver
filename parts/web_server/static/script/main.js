var update_interval = 10
var xhr = new XMLHttpRequest()
var button_clicked_color = "#912020"
var indicator_color = "red"
var first_color = "#ffb700"
var record_timer = 0
var stop_timer = 0

class Status {
    constructor(){
        this.outputs = {pilot: "Manuel", route: "Manuel", motor_power: 0, record: 0,
        speed_factor: 1, camera_mode: "RGB", graph_mode: "Speed/IMU"}

        this.not_record_style = document.getElementById("Record").style
        this.direction = "Forward"
        this.lane = "Right"
    }

    send_data(data){
        xhr.open("POST", "/outputs", true)
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data))
        // console.log(data)
    }

    activated_color(ID, color){
        document.getElementById(ID).style.backgroundColor = color;
    }

    unactivated_color(ID){
        document.getElementById(ID).style.backgroundColor = "#00000000"
    }
    
    Print_Stop_Timer(){
        stop_timer -= 1
        document.getElementById("Stop_Timer").innerHTML = stop_timer
    }

    Update_Stop(stopped, stop_time=0){
        if (stopped == 0){
            this.unactivated_color("Stop", indicator_color)
            stop_timer = 0
            document.getElementById("Arrow_Container").style.visibility = "visible"
            document.getElementById("Stop_Timer").style.display = "none"
            clearInterval(this.Print_Stop_Timer_Interval)
        }
        else if (stopped == 1){
            this.activated_color("Stop", indicator_color)
            document.getElementById("Arrow_Container").style.visibility = "hidden"
            document.getElementById("Stop_Timer").style.display = "flex"
            document.getElementById("Stop_Timer").innerHTML = stop_time
            stop_timer = stop_time
            this.Print_Stop_Timer_Interval = setInterval(this.Print_Stop_Timer, 1000)
        }
        this.stop = stopped
        // console.log("Stop:", this.stop)
    }

    Update_Taxi(pull_over){
        if (pull_over == 0)
            this.unactivated_color("Taxi", indicator_color)
        else if (pull_over == 1)
            this.activated_color("Taxi", indicator_color)
        this.taxi = pull_over
        // console.log("Taxi:", this.taxi)
    }

    turn_signal(direction){
        var arrow = document.getElementById(direction+"_Arrow")
        var arrow_stick = document.getElementById(direction+"_Arrow_Stick")
        if (arrow.style.borderColor == "white"){
            arrow.style.borderColor = first_color
            arrow_stick.style.backgroundColor = first_color
        }
        else{
            arrow.style.borderColor = "white"
            arrow_stick.style.backgroundColor = "white"
        }
    }

    Update_Direction(direction){
        document.getElementById(this.direction+"_Arrow").style.borderColor = "white"
        document.getElementById(this.direction+"_Arrow_Stick").style.backgroundColor = "white"
        clearInterval(this.turn_signal_interval)
        if (direction == "Forward"){
            document.getElementById(direction+"_Arrow").style.borderColor = first_color
            document.getElementById(direction+"_Arrow_Stick").style.backgroundColor = first_color
        }
        else{
            this.turn_signal_interval = setInterval(this.turn_signal, 500, direction)
        }
        this.direction = direction
        // console.log("Direction:", this.direction)
    }

    Update_Lane(lane){
        document.getElementById(this.lane+"_Lane").style.visibility = "hidden"
        this.lane = lane
        document.getElementById(this.lane+"_Lane").style.visibility = "visible"
        // console.log("Lane:", this.lane)
    }

    Emergency_Stop(){
        alert("Emergency Stop")
    }
    
    Update_Camera_Mode(camera_mode, synchronize=0){
        if (synchronize == 1)
            document.getElementById("Camera_Mode").value = camera_mode
        else{
            this.outputs["camera_mode"] = camera_mode
            this.send_data({camera_mode: this.outputs["camera_mode"]})
            // console.log('Camera Mode: ', this.outputs["camera_mode"]);
        }
    }

    Update_Graph_Mode(graph_mode, synchronize=0){
        if (synchronize == 1)
            document.getElementById("Graph_Mode").value = graph_mode
        else{
            this.outputs["graph_mode"] = graph_mode
            this.send_data({graph_mode: this.outputs["graph_mode"]})
            // console.log('Graph Mode: ', this.outputs["graph_mode"]);
        }
    }

    bar_lengthen(ID, value, center){
        var bar = document.getElementById(ID)
        var calculated_value = 0
        if (value >= 0){
            bar.style.marginLeft = center+"%"
            bar.style.float = "Left"
            calculated_value = value * (100 - center)
        }
        else if (value < 0){
            bar.style.marginRight = (100 - center)+"%"
            bar.style.float = "Right"
            calculated_value = -value * center
        }
        bar.style.width = calculated_value + "%"
    }

    Update_Steering(steering){
        this.steering = steering
        this.bar_lengthen("Steering", this.steering, 50)
        // console.log('Steering: ', this.steering)
    }

    Update_Throttle(throttle){
        this.throttle = throttle
        this.bar_lengthen("Throttle", this.throttle, 33.33)
        // console.log('Throttle: ', this.throttle)
    }

    Update_Speed(speed){
        this.speed = speed
        document.getElementById("Speed").innerHTML = this.speed + " m/s"
        // console.log('You selected: ', this.speed)
    }

    Update_Speed_Factor(synchronize=0){
        if (synchronize == 1)
            document.getElementById("Speed_Slider").value = this.outputs["speed_factor"] * 50
        else{
            this.outputs["speed_factor"] = document.getElementById("Speed_Slider").value / 50
            document.getElementById("Speed_Slider").title = this.outputs["speed_factor"]
            this.send_data({speed_factor: this.outputs["speed_factor"]})
            // console.log(this.outputs["speed_factor"])
        }
    }

    print_record_time(){
        record_timer+= 0.1
        document.getElementById("Record_Timer").innerHTML = (Math.round(record_timer * 100) / 100).toFixed(1)
    }

    record_style_change(style){
        if (style == 0){
            document.getElementById("Record").style = this.not_record_style
            document.getElementById("Record_Timer").style.visibility = "hidden"
            record_timer = 0
            document.getElementById("Record_Timer").innerHTML = 0
            clearInterval(this.print_record_time_interval)
        }
        else if (style == 1){
            var style = document.getElementById("Record").style
            style.height = "60%"
            style.width = "60%"
            style.backgroundColor = "red"
            style.borderStyle = "solid"
            style.borderRadius = "5px"
            document.getElementById("Record_Timer").style.visibility = "visible"
            this.print_record_time_interval = setInterval(this.print_record_time, 100)
        }
    }

    Update_Record(synchronize=0){
        if (synchronize == 0){
            if (this.outputs["record"] == 0)
                this.outputs["record"] = 1
            else if (this.outputs["record"] == 1)
                this.outputs["record"] = 0
                this.send_data({record: this.outputs["record"]})
                // console.log("Record:", this.outputs["record"])
        }
        this.record_style_change(this.outputs["record"])
    }

    Update_Motor_Power(synchronize=0){
        if (synchronize == 0){
            if (this.outputs["motor_power"] == 1)
                this.outputs["motor_power"] = 0
            else if (this.outputs["motor_power"] == 0)
                this.outputs["motor_power"] = 1
                this.send_data({motor_power: this.outputs["motor_power"]})
                // console.log("Motor_Power:", this.outputs["motor_power"])
        }
        if (this.outputs["motor_power"] == 1)
            this.activated_color("Go", "red")
        else if(this.outputs["motor_power"] == 0)
            this.unactivated_color("Go")
    }
    
    Update_Pilot_Mode(mode){
        this.unactivated_color("Pilot_"+this.outputs["pilot"])
        this.outputs["pilot"] = mode
        this.activated_color("Pilot_"+mode, button_clicked_color)
        this.send_data({pilot: this.outputs["pilot"]})
        // console.log("Pilot:", this.outputs["pilot"])
    }
    
    Update_Route_Mode(mode){
        this.unactivated_color("Route_"+this.outputs["route"])
        this.outputs["route"] = mode
        this.activated_color("Route_"+mode, button_clicked_color)
        this.send_data({route: this.outputs["route"]})
        // console.log("Route:", this.outputs["route"])
    }
    
    update_client_side(){
        this.Update_Pilot_Mode(this.outputs["pilot"])
        this.Update_Route_Mode(this.outputs["route"])
        this.Update_Camera_Mode(this.outputs["camera_mode"], 1)
        this.Update_Graph_Mode(this.outputs["graph_mode"], 1)
        this.Update_Speed_Factor(1)
        this.Update_Motor_Power(1)
        this.Update_Record(1)
    }

    update_indicators(){
        fetch("inputs")
        .then(response => response.json())
        .then(inputs => {
        Track.Update_Stop(inputs["stop"])
        Track.Update_Taxi(inputs["taxi"])
        Track.Update_Direction(inputs["direction"])
        Track.Update_Lane(inputs["lane"])
        Track.Update_Steering(inputs["steering"])
        Track.Update_Throttle(inputs["throttle"])
        Track.Update_Speed(inputs["speed"])
        })
    }
}

let Track = new Status()

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

function load_parameters(outputs){
    for (const [key, value] of Object.entries(outputs)) {
        Track.outputs[key] = value
        console.log(key, value);
      }
      Track.update_client_side()
      setInterval(Track.update_indicators, update_interval)
}