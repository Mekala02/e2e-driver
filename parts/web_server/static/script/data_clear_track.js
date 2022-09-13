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

    update_graph_display(){
        this.axis_length = this.graph["Timestamp"].length
        var traces = []
        for (let mode of this.outputs["Graph1_Mode"]){
          traces.push({
            x: this.graph["Timestamp"].slice(Math.max(0, this.axis_length - 500), this.axis_length - 1),
            y: this.graph[mode].slice(Math.max(0, this.axis_length - 500), this.axis_length - 1),
            name: mode,
            type:'line',
            line: {
            width: 4
          }})
        }
        this.graph_layout["xaxis"]["range"] = [this.graph_trace["x"][0], this.graph_trace["x"][500]]
        Plotly.react("Graph1", traces, this.graph_layout, {displayModeBar: false})
      }
      
}