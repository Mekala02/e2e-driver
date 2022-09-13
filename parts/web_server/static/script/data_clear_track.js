var record_timer = 0
var stop_timer = 0

class Data_Clear_Track extends Main_Track {
    constructor(){
        super()
    }
    
    Update_Data_Folder(){

    }

    Update_Data_Position(){
        
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
            console.log(mode)
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

}