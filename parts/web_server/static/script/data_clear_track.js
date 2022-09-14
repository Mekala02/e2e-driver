var record_timer = 0
var stop_timer = 0

class Data_Clear_Track extends Main_Track {
    constructor(){
        super()
        this.Progress_Bar_Width = document.getElementById('Progress_Bar').clientWidth
        this.between_divs = {}
    }

    Update_Graph_Data(receive){
        for (const key in receive) {
            this.graph[key] = JSON.parse(JSON.stringify(receive[key]))
          }
    }

    Update_Graph_Display(){
        // this.axis_length = this.graph["Timestamp"].length
        var traces = []
        for (let mode of this.outputs["Graph1_Mode"]){
            traces.push({
            x: this.graph["Timestamp"],
            y: this.graph[mode],
            name: mode,
            type:'line',
            line: {
            width: 4
            }})
        }
        Plotly.react("Graph1", traces, this.graph_layout, {displayModeBar: false})
      }

      Update_Data_Folder(folder, synchronize=0){
          if (synchronize == 0){
              this.outputs["Data_Folder"] = index
              this.send_data({Data_Index: this.outputs["Data_Folder"]})
            }
            document.getElementById("Data_Folder").innerHTML = this.outputs["Data_Folder"]
        }

        Update_Data_Lenght(lenght, synchronize=0){
          if (synchronize == 0){
              this.outputs["Data_Lenght"] = lenght
              this.send_data({Data_Index: this.outputs["Data_Lenght"]})
          }
        }
  
        Update_Data_Index(index, synchronize=0){
          if (synchronize == 0){
              this.outputs["Data_Index"] = index
              this.send_data({Data_Index: this.outputs["Data_Index"]})
          }
          document.getElementById("Data_Index").innerHTML = this.outputs["Data_Index"]
          document.getElementById("Bar_Data_Index").style.left = `${this.outputs["Data_Index"]/this.outputs["Data_Lenght"]*100}%`
        }

        add_between_mark(div, start, finish, color){
            if (start <= finish){
                div.style.position = "absolute"
                div.style.height = "100%"
                div.style.width = "auto"
                div.style.left = start + "%"
                div.style.right = 100 - finish + "%"
                div.style.backgroundColor = color
                div.style.pointerEvents = "none"

            }
        }

        delete_between_mark(div){
            try{div.remove()} catch{}
        }

        Update_Marker(index, marker, synchronize=0){
            if (synchronize == 0){
                this.outputs[`${marker}_Marker`] = index
                if (marker == "Right")
                    this.send_data({Right_Marker: this.outputs[`${marker}_Marker`]})
                if (marker == "Left")
                    this.send_data({Left_Marker: this.outputs[`${marker}_Marker`]})
            }
            else{
                
            }
            var Left = `${this.outputs[`Left_Marker`]/this.outputs["Data_Lenght"]*100}`
            var Right = `${this.outputs["Right_Marker"]/this.outputs["Data_Lenght"]*100}`
            if (marker == "Left")
                document.getElementById(`${marker}_Marker`).style.left = `calc(${Left}%)`
            if (marker == "Right")
                document.getElementById(`${marker}_Marker`).style.left = `calc(${Right}%)`
            this.delete_between_mark(this.between_divs["Marker_Between_Div"])
            this.between_divs["Marker_Between_Div"] = document.createElement("div")
            document.getElementById("Progress_Bar").appendChild(this.between_divs["Marker_Between_Div"])
            this.add_between_mark(this.between_divs["Marker_Between_Div"], Left, Right, "rgb(0 255 0 / 70%)")
        }

        Update_Left_Marker(index, synchronize=0){
            this.Update_Marker(index, "Left", synchronize)
        }

        Update_Right_Marker(index, synchronize=0){
            this.Update_Marker(index, "Right", synchronize)
        }

        Update_Delete_List(right_left_list, synchronize=0){

        }
}