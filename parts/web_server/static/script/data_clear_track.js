var record_timer = 0
var stop_timer = 0

class Data_Clear_Track extends Main_Track {
    constructor(){
        super()
        this.Progress_Bar_Width = document.getElementById('Progress_Bar').clientWidth
        this.selected_between_div = 0
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
        // this.graph_layout["shapes"] = [
        //     //line vertical
        //     {
        //       type: 'line',
        //       x0: 1663084384230,
        //       y0: -1,
        //       x1: 1663084384232,
        //       y1: 1,
        //       line: {
        //         color: 'white',
        //         width: 3
        //       }
        //     }]
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
            // Converting indexes to parent divs %
            var Left = `${this.outputs[`Left_Marker`] / this.outputs["Data_Lenght"] * 100}`
            var Right = `${this.outputs["Right_Marker"] / this.outputs["Data_Lenght"] * 100}`
            if (marker == "Left")
                document.getElementById(`${marker}_Marker`).style.left = `calc(${Left}%)`
            if (marker == "Right")
                document.getElementById(`${marker}_Marker`).style.left = `calc(${Right}% - 3px)`
            this.delete_between_mark(this.selected_between_div)
            this.selected_between_div = document.createElement("div")
            document.getElementById("Progress_Bar").appendChild(this.selected_between_div)
            this.add_between_mark(this.selected_between_div, Left, Right, "rgb(63 81 181 / 70%)")
        }

        Update_Left_Marker(index, synchronize=0){
            this.Update_Marker(index, "Left", synchronize)
        }

        Update_Right_Marker(index, synchronize=0){
            this.Update_Marker(index, "Right", synchronize)
        }

        // Changes is list
        Update_Select_List(changes, synchronize=0){
            if (synchronize == 0){
                for (const dict of this.outputs["Select_List"]){
                    if (dict["Indexes"][0] == this.outputs["Left_Marker"] && dict["Indexes"][1] == this.outputs["Right_Marker"]){
                        for (const element of changes){
                            if (dict["Changes"].includes(element) == 0)
                                dict["Changes"].push(element)
                        }
                        this.send_data({Select_List: this.outputs["Select_List"]})
                        return
                    }
                }
                var tmp_dict = {}
                tmp_dict["Indexes"] = [this.outputs["Left_Marker"], this.outputs["Right_Marker"]]
                tmp_dict["Changes"] = []
                tmp_dict["Div"] = this.selected_between_div
                for (const element of changes)
                    if (tmp_dict["Changes"].includes(element) == 0)
                        tmp_dict["Changes"].push(element)
                this.selected_between_div.style.backgroundColor = "#ff4e4e"
                this.selected_between_div = 0
                this.outputs["Select_List"].push(tmp_dict)
                this.send_data({Select_List: this.outputs["Select_List"]})
            }
            else{
                for (const dict of this.outputs["Select_List"]){
                    console.log(dict["Changes"])
                    // Converting indexes to % of parent div
                    var start = dict["Indexes"][0] / this.outputs["Data_Lenght"] * 100
                    var finish = dict["Indexes"][1] / this.outputs["Data_Lenght"] * 100
                    var color = "#ff4e4e"
                    this.div = document.createElement("div")
                    document.getElementById("Progress_Bar").appendChild(this.div)
                    this.add_between_mark(this.div, start, finish, color)
                }
            }
        }

        unselect(){
            var left_marker = this.outputs["Left_Marker"]
            var right_marker = this.outputs["Right_Marker"]
            for (const dict of this.outputs["Select_List"]){
              if(dict["Indexes"][0] == left_marker && dict["Indexes"][1] == right_marker){
                const index = this.outputs["Select_List"].indexOf(this.outputs["Select_List"])
                this.outputs["Select_List"].splice(index, 1)
                this.delete_between_mark(dict["Div"])
                this.send_data({Select_List: this.outputs["Select_List"]})
                this.Update_Right_Marker(undefined, 1)
                return
              }
            }
        }
}