var record_timer = 0
var stop_timer = 0

class Status {
    constructor(){
        this.xhr = new XMLHttpRequest()
        this.button_clicked_color = "#912020"
        this.indicator_color = "red"
        // this.outputs = {pilot: "Manuel", route: "Manuel", motor_power: 0, record: 0,
        // speed_factor: 1, camera_mode: "RGB", graph1_mode: [], graph2_mode: []}
        this.outputs = {}

        this.not_record_style = document.getElementById("Record").style

        this.graph = {Steering: [], Throttle: [], Speed: [], Timestamp: [],
            IMU_Accel_X: [], IMU_Accel_Y: [], IMU_Accel_Z: [], IMU_Gyro_X: [], IMU_Gyro_Y: [], IMU_Gyro_Z: []}
    }

    send_data(data){
        this.xhr.open("POST", "/outputs", true)
        this.xhr.setRequestHeader('Content-Type', 'application/json');
        this.xhr.send(JSON.stringify(data))
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
            this.unactivated_color("Stop", this.indicator_color)
            stop_timer = 0
            document.getElementById("Arrow_Container").style.visibility = "visible"
            document.getElementById("Stop_Timer").style.display = "none"
            clearInterval(this.Print_Stop_Timer_Interval)
        }
        else if (stopped == 1){
            if (stop_time != 0){
                document.getElementById("Arrow_Container").style.visibility = "hidden"
                document.getElementById("Stop_Timer").style.display = "flex"
                document.getElementById("Stop_Timer").innerHTML = stop_time
                stop_timer = stop_time
                this.Print_Stop_Timer_Interval = setInterval(this.Print_Stop_Timer, 1000)
            }
            this.activated_color("Stop", this.indicator_color)
        }
        this.Stop = stopped
        // console.log("Stop:", this.stop)
    }

    Update_Taxi(pull_over){
        if (pull_over == 0)
            this.unactivated_color("Taxi", this.indicator_color)
        else if (pull_over == 1)
            this.activated_color("Taxi", this.indicator_color)
        this.Taxi = pull_over
        // console.log("Taxi:", this.taxi)
    }

    turn_signal(direction){
        var arrow = document.getElementById(direction+"_Arrow")
        var arrow_stick = document.getElementById(direction+"_Arrow_Stick")
        if (arrow.style.borderColor == "white"){
            arrow.style.borderColor = "#ffb700"
            arrow_stick.style.backgroundColor = "#ffb700"
        }
        else{
            arrow.style.borderColor = "white"
            arrow_stick.style.backgroundColor = "white"
        }
    }

    Update_Direction(direction){
        if (this.Direction != direction){
            try{
                document.getElementById(this.Direction+"_Arrow").style.borderColor = "white"
                document.getElementById(this.Direction+"_Arrow_Stick").style.backgroundColor = "white"
            }
            catch{}
            clearInterval(this.turn_signal_interval)
            if (direction == "Forward"){
                document.getElementById(direction+"_Arrow").style.borderColor = "#ffb700"
                document.getElementById(direction+"_Arrow_Stick").style.backgroundColor = "#ffb700"
            }
            else{
                this.turn_signal_interval = setInterval(this.turn_signal, 500, direction)
            }
        }
        this.Direction = direction
        // console.log("Direction:", this.Direction)
    }

    Update_Lane(lane){
        try{document.getElementById(this.Lane+"_Lane").style.visibility = "hidden"}
        catch{}
        this.Lane = lane
        document.getElementById(this.Lane+"_Lane").style.visibility = "visible"
        // console.log("Lane:", this.lane)
    }

    Emergency_Stop(){
        alert("Emergency Stop")
    }
    
    Update_Camera_Mode(mode, synchronize=0){
        if (synchronize == 0){
            this.unactivated_color("C_"+this.outputs["Camera_Mode"])
            this.outputs["Camera_Mode"] = mode
            this.send_data({Camera_Mode: this.outputs["Camera_Mode"]})
        }
        this.activated_color(`C_${this.outputs["Camera_Mode"]}`, this.button_clicked_color)
    }

    Update_FPS(fps){
        document.getElementById("Fps").innerHTML = fps
    }

    Update_Graph_Mode(mode, graph=0, synchronize=0){
        // If we synchronizing we only activating the colors on client side
        if (synchronize == 0){
            // If clicked button already selected we turning off it and deleting from list
            if (this.outputs[`Graph${graph}_Mode`].includes(mode)){
                this.unactivated_color(`G${graph}_${mode}`)
                const index = this.outputs[`Graph${graph}_Mode`].indexOf(mode)
                this.outputs[`Graph${graph}_Mode`].splice(index, 1)
            }
            else{
                this.activated_color(`G${graph}_${mode}`, this.button_clicked_color)
                this.outputs[`Graph${graph}_Mode`].push(mode)
            }
            // Finaly sending list to the server
            if (graph == 1){
                const dict = {}
                dict["test"] = this.outputs["Graph1_Mode"]
                // console.log(dict["test"])
                this.send_data({Graph1_Mode: this.outputs["Graph1_Mode"]})
            }
            else if(graph == 2)
                // console.log({graph2_mode: this.outputs["graph2_mode"]})
                this.send_data({Graph2_Mode: this.outputs["Graph2_Mode"]})
        }
        else{
            for (let value of this.outputs[`Graph${graph}_Mode`]) {
                this.activated_color(`G${graph}_${value}`, this.button_clicked_color)
              }
        }
    }

    Update_Graph1_Mode(mode, synchronize=0){
        this.Update_Graph_Mode(mode, 1, synchronize)
    }

    Update_Graph2_Mode(mode, synchronize=0){
        this.Update_Graph_Mode(mode, 2, synchronize)
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

    Update_Speed_Factor(speed_factor, synchronize=0){
        if (synchronize == 0){
            this.outputs["Speed_Factor"] = speed_factor / 50
            document.getElementById("Speed_Slider").title = this.outputs["Speed_Factor"]
            this.send_data({Speed_Factor: this.outputs["Speed_Factor"]})
        }
        else
            document.getElementById("Speed_Slider").value = this.outputs["Speed_Factor"] * 50
        // console.log(this.outputs["Speed_Factor"])
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

    Update_Record(mode=undefined, synchronize=0){
        if (synchronize == 0){
            if (this.outputs["Record"] == 0)
                this.outputs["Record"] = 1
            else if (this.outputs["Record"] == 1)
                this.outputs["Record"] = 0
                this.send_data({Record: this.outputs["Record"]})
                // console.log("Record:", this.outputs["Record"])
        }
        this.record_style_change(this.outputs["Record"])
    }

    Update_Motor_Power(mode=undefined, synchronize=0){
        if (synchronize == 0){
            if (this.outputs["Motor_Power"] == 1)
                this.outputs["Motor_Power"] = 0
            else if (this.outputs["Motor_Power"] == 0)
                this.outputs["Motor_Power"] = 1
                this.send_data({Motor_Power: this.outputs["Motor_Power"]})
                // console.log("Motor_Power:", this.outputs["motor_power"])
        }
        if (this.outputs["Motor_Power"] == 1)
            this.activated_color("Go", "red")
        else if(this.outputs["Motor_Power"] == 0)
            this.unactivated_color("Go")
    }
    
    Update_Pilot_Mode(mode, synchronize=0){
        if (synchronize == 0)
        {
            this.unactivated_color("Pilot_"+this.outputs["Pilot_Mode"])
            this.outputs["Pilot_Mode"] = mode
            this.send_data({Pilot_Mode: this.outputs["Pilot_Mode"]})
        }
        this.activated_color(`Pilot_${this.outputs["Pilot_Mode"]}`, this.button_clicked_color)
        // console.log("Pilot:", this.outputs["Pilot"])
    }
    
    Update_Route_Mode(mode, synchronize=0){
        if (synchronize == 0){
            this.unactivated_color("Route_"+this.outputs["Route_Mode"])
            this.outputs["Route_Mode"] = mode
            this.send_data({Route_Mode: this.outputs["Route_Mode"]})
        }
        this.activated_color(`Route_${this.outputs["Route_Mode"]}`, this.button_clicked_color)
        // console.log("Route:", this.outputs["Route"])
    }
    
    update_client_side(){
        for (const key in outputs){
            eval(`this.Update_${key}(undefined, 1)`)
        }

        // eval("this.Update_Pilot_Mode(undefined, 1)")
        // this.Update_Route_Mode(undefined, 1)
        // this.Update_Camera_Mode(undefined, 1)
        // this.Update_Speed_Factor(undefined, 1)
        // this.Update_Motor_Power(undefined, 1)
        // this.Update_Record(undefined, 1)

        // this.Update_Graph_Mode(undefined, 1, 1) // First 1 is graph no second 1 is syncronize mode on
        // this.Update_Graph_Mode(this.outputs["Graph2_Mode"], 2, 1)
    }

    update_indicators(){
        fetch("inputs")
        .then(response => response.json())
        .then(inputs => {
            Track.Update_Stop(inputs["Stop"])
            Track.Update_Taxi(inputs["Taxi"])
            Track.Update_Direction(inputs["Direction"])
            Track.Update_Lane(inputs["Lane"])

            Track.Update_Steering(inputs["Steering"])
            Track.Update_Throttle(inputs["Throttle"])
            Track.Update_Speed(inputs["Speed"])

            Track.Update_FPS(inputs["Fps"])


            for (const key in Track.graph) {
                    Track.graph[key].push(inputs[key])
            }
            // Track.graph["Steering"].push(inputs["Steering"])
            // Track.graph["Throttle"].push(inputs["Throttle"])
            // Track.graph["Speed"].push(inputs["Speed"])
            // Track.graph["Timestamp"].push(inputs["Timestamp"] / 10**24)
            // Track.graph["IMU_Accel_X"].push(inputs["IMU_Accel_X"])
            // Track.graph["IMU_Accel_Y"].push(inputs["IMU_Accel_Y"])
            // Track.graph["IMU_Accel_Z"].push(inputs["IMU_Accel_Z"])
            // Track.graph["IMU_Gyro_X"].push(inputs["IMU_Gyro_X"])
            // Track.graph["IMU_Gyro_Y"].push(inputs["IMU_Gyro_Y"])
            // Track.graph["IMU_Gyro_Z"].push(inputs["IMU_Gyro_Z"])
        })
    }
}