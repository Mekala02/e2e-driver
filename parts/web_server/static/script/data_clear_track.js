var record_timer = 0
var stop_timer = 0

class Data_Clear_Track extends Main_Track {
    constructor(){
        super()
        this.Progress_Bar_Width = document.getElementById('Progress_Bar').clientWidth
        this.selected_between_div = 0
        this.traces = []
        this.search_results_list = []
        this.search_results_divs = []
    }

    Update_Graph_Data(receive){
        for (const key in receive) {
            this.graph[key] = JSON.parse(JSON.stringify(receive[key]))
          }
    }

    Update_Graph_Index(){
        this.graph_layout["shapes"] = [
            //line vertical
            {
                type: 'line',
                x0: this.outputs["Data_Index"],
                y0: -1,
                x1: this.outputs["Data_Index"],
                y1: 1,
                line: {
                color: 'white',
                width: 3
                }
            }]
        Plotly.react("Graph1", this.traces, this.graph_layout, {displayModeBar: false})
      }

    Update_Graph_Display(){
        // this.axis_length = this.graph["Timestamp"].length
        this.traces = []
        for (let mode of this.outputs["Graph1_Mode"]){
            this.traces.push({
            x: this.graph["Img_Id"],
            y: this.graph[mode],
            name: mode,
            type:'line',
            line: {
            width: 4
            }})
        }
        this.Update_Graph_Index()
        // Plotly.react("Graph1", this.traces, this.graph_layout, {displayModeBar: false})
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
                if (start == finish)
                    div.style.right = 99.99 - finish + "%"
                else
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
                        if (dict["Changes"].includes("Delete"))
                            dict["Div"].style.backgroundColor = "#ff4e4e"
                        else
                            dict["Div"].style.backgroundColor = "yellow"
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
                if (changes.includes("Delete"))
                    this.selected_between_div.style.backgroundColor = "#ff4e4e"
                else
                    this.selected_between_div.style.backgroundColor = "yellow"
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
                    if (dict["Changes"].includes("Delete"))
                        var color = "#ff4e4e"
                    else
                        var color = "yellow"
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

        mark_search_results(search_phrase){
            this.xhr.open("POST", "/search", true)
            this.xhr.setRequestHeader('Content-Type', 'application/json');
            this.xhr.send(JSON.stringify(search_phrase))
            fetch("search_results")
            .then(response => response.json())
            .then(inputs => {
                // Cleaning previous searched divs (if there is any)
                for (const div of this.search_results_divs)
                    this.delete_between_mark(div)
                this.search_results_divs = []
                this.search_results_list = []
                var start_index = inputs[0]
                // Squeezing values into [start, stop] continious list
                for (var i = 0; i < inputs.length; i++){
                    if(inputs[i] + 1 != inputs[i+1]){
                        this.search_results_list.push([start_index, inputs[i]])
                        start_index = inputs[i+1]
                    }
                }
                // Marking search results
                for (const between of this.search_results_list){
                    var div = document.createElement("div")
                    document.getElementById("Progress_Bar").appendChild(div)
                    this.search_results_divs.push(div)
                    // Converting indexes to % of parent div
                    var start = between[0] / this.outputs["Data_Lenght"] * 100
                    var finish = between[1] / this.outputs["Data_Lenght"] * 100
                    this.add_between_mark(div, start, finish, "#ffbf00")
                }
              })
        }
}