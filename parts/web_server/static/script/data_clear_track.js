var record_timer = 0
var stop_timer = 0

class Data_Clear_Track extends Main_Track {
    constructor(){
        super()
        self.Data_Index
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

      Update_Data_Folder(folder, synchronize=0){
        if (synchronize == 0){
            this.outputs["Data_Folder"] = index
            this.send_data({Data_Index: this.outputs["Data_Folder"]})
        }
        document.getElementById("Data_Folder").innerHTML = this.outputs["Data_Folder"]
    }
}