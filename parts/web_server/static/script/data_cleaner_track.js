var record_timer = 0
var stop_timer = 0

class Data_Clear_Track extends Main_Track {
    constructor(){
        // This Class inherits for Data_Clear_Track Class
        super()
        // Getting progress bars width we will need it for some calculations
        this.Progress_Bar_Width = document.getElementById('Progress_Bar').clientWidth
        // For keeping track of selected lists div
        this.selected_between_div = 0
        // Graphs trace
        this.traces = []
        // Searchlists results list
        this.search_results_list = []
        // For keeping track of searchlists results div
        this.search_results_divs = []
    }

    Update_Graph_Data(receive){
        // Getting graph plot datas
        for (const key in receive) {
            this.graph[key] = JSON.parse(JSON.stringify(receive[key]))
          }
    }

    Update_Graph_Index(){
        // This is for vertical line on the graph according to data index
        this.graph_layout["shapes"] = [
            {
                type: 'line',
                x0: this.outputs["Data_Index"],
                y0: this.y_min_value-1,
                x1: this.outputs["Data_Index"],
                y1: this.y_max_value+1,
                line: {
                    color: 'white',
                    width: 3
                }
            }]
        Plotly.react("Graph1", this.traces, this.graph_layout, {displayModeBar: false})
      }

    Update_Graph_Display(){
        // Ploting the graph
        this.traces = []
        this.y_max_value = -Infinity
        this.y_min_value = Infinity
        for (let mode of this.outputs["Graph1_Mode"]){
            this.traces.push({
            x: this.graph["Data_Id"],
            y: this.graph[mode],
            name: mode,
            type:'line',
            line: {
            width: 4
            }})
            // We calculating y axis max and min values to determine vertical lines border (Using in Update_Graph_Index)
            this.y_max_value = Math.max(this.y_max_value, Math.max(...this.graph[mode]))
            this.y_min_value = Math.min(this.y_min_value, Math.min(...this.graph[mode]))
        }
        this.Update_Graph_Index()
      }

    Update_Data_Folder(folder, synchronize=0){
        if (synchronize == 0){
        // For now we are not using this becouse wedont have a way to change data folder inside
        // of an web interface
        this.outputs["Data_Folder"] = folder
        this.send_data({Data_Folder: this.outputs["Data_Folder"]})
        }
        document.getElementById("Data_Folder").innerHTML = this.outputs["Data_Folder"]
    }

    Update_Data_Lenght(lenght, synchronize=0){
        // For now we are not using this becouse wedont have a way to change data folder inside
        // of an web interface
        if (synchronize == 0){
            this.outputs["Data_Lenght"] = lenght
            this.send_data({Data_Lenght: this.outputs["Data_Lenght"]})
        }
    }

    Update_Data_Index(index, synchronize=0){
        if (synchronize == 0){
            if (index < this.outputs["Data_Lenght"] && index >= 0){
                this.outputs["Data_Index"] = index
                this.send_data({Data_Index: this.outputs["Data_Index"]})
            }
        }
        // Updates Data_Index indicator accordingly
        document.getElementById("Data_Index").innerHTML = this.outputs["Data_Index"]
        // Updates progress bars indicator accordingly
        // We are converting index to % of a bars lenght
        document.getElementById("Bar_Data_Index").style.left = `${this.outputs["Data_Index"]/this.outputs["Data_Lenght"]*100}%`
    }

    add_between_mark(div, start, finish, color){
        // Adds mark between start and finish %
        if (start <= finish){
            div.style.position = "absolute"
            div.style.height = "100%"
            div.style.width = "auto"
            div.style.left = start + "%"
            if (start == finish)
                // If they are in same position we making div little larger for better visualization
                div.style.right = 99.99 - finish + "%"
            else
                div.style.right = 100 - finish + "%"
            div.style.backgroundColor = color
            // Makes div unselectable on hover
            div.style.pointerEvents = "none"
        }
    }

    delete_between_mark(div){
        // We are trying becouse someimes div doesnt exist
        try{div.remove()} catch{}
    }

    Update_Marker(index, marker, synchronize=0){
        // Updates left or right markers position and adds or modifies between div accordingly
        if (synchronize == 0){
            this.outputs[`${marker}_Marker`] = index
            if (marker == "Right")
                this.send_data({Right_Marker: this.outputs["Right_Marker"]})
            if (marker == "Left")
                this.send_data({Left_Marker: this.outputs["Left_Marker"]})
        }
        // Converting indexes to progress bars lenght %
        var Left = `${this.outputs[`Left_Marker`] / this.outputs["Data_Lenght"] * 100}`
        var Right = `${this.outputs["Right_Marker"] / this.outputs["Data_Lenght"] * 100}`
        if (marker == "Left")
            // Updating position of marker
            document.getElementById("Left_Marker").style.left = `calc(${Left}%)`
        if (marker == "Right")
            // -3px becouse there is thickness of marker indicator
            document.getElementById("Right_Marker").style.left = `calc(${Right}% - 3px)`
        // Deletes old between mark
        this.delete_between_mark(this.selected_between_div)
        // Creates new div for making it new between mark
        this.selected_between_div = document.createElement("div")
        // Appends div to the progress bar
        document.getElementById("Progress_Bar").appendChild(this.selected_between_div)
        this.add_between_mark(this.selected_between_div, Left, Right, "rgb(63 81 181 / 70%)")
    }

    Update_Left_Marker(index, synchronize=0){
        this.Update_Marker(index, "Left", synchronize)
    }

    Update_Right_Marker(index, synchronize=0){
        this.Update_Marker(index, "Right", synchronize)
    }

    update_display_changes(changes, ifdelete=0){
        // Updates the changes div
        if (ifdelete == 1){
            // If we dont have selected changes we are making this div invisible and cleaning inside
            document.getElementById("Display_Changes").innerHTML = ""
            document.getElementById("Data_Folder").style.display = "flex"
            document.getElementById("Display_Changes").style.display = "none"
        }
        else{
            var inner = ""
            // We are making string for adding to inner html
            // Br is a new line on html
            for (const key in changes){
                inner = inner.concat(String(key) + ": ")
                inner = inner.concat(changes[key])
                inner = inner.concat("<br>")
            }
            document.getElementById("Display_Changes").innerHTML = inner
            document.getElementById("Data_Folder").style.display = "none"
            document.getElementById("Display_Changes").style.display = "flex"
        }
    }

    Update_Select_List(changes, synchronize=0){
        // Changes is a dict
        if (synchronize == 0){
            // Slect List contins dicts, thoose dicts contain: Div, Indexes[Right, Left], Changes {}
            for (const current_changes of this.outputs["Select_List"]){
                // Searching for dict that indexes matches with selected indexes
                if (current_changes["Indexes"][0] == this.outputs["Left_Marker"] && current_changes["Indexes"][1] == this.outputs["Right_Marker"]){
                    // If we found that div (if it's exist)
                    for (const key in changes){
                        // Looking to changes dict if that element doesnt exist we adding it to the dict
                        if (key in current_changes["Changes"]){
                            // If that value already exist we removing it from list
                            if (changes[key] == current_changes["Changes"][key])
                                delete current_changes["Changes"][key]
                            else
                            current_changes["Changes"][key] = changes[key]
                            }
                        else
                            current_changes["Changes"][key] = changes[key]
                    }
                    // If that section going to be deleted we marking it with red
                    // Trying becouse if we refresh the page we losing the div so we cant change it color
                    if ("Delete" in current_changes["Changes"])
                        try{current_changes["Div"].style.backgroundColor = "#ff4e4e"} catch{}
                    else
                        try{current_changes["Div"].style.backgroundColor = "yellow"} catch{}
                    // Updating changes list for seing the changes we made
                    this.update_display_changes(current_changes["Changes"])
                    this.send_data({Select_List: this.outputs["Select_List"]})
                    return
                }
            }
            // If there is no selected mark here we make one (left marker has to be <= right marker)
            if (this.outputs["Left_Marker"] <= this.outputs["Right_Marker"]){
                var tmp_dict = {}
                tmp_dict["Indexes"] = [this.outputs["Left_Marker"], this.outputs["Right_Marker"]]
                tmp_dict["Changes"] = {}
                // We are that div for later use
                tmp_dict["Div"] = this.selected_between_div
                for (const key in changes)
                    // If there is duplicates we are not saving same thing twice
                    if (key in tmp_dict["Changes"] == false)
                        tmp_dict["Changes"][key] = changes[key]
                if ("Delete" in changes)
                    this.selected_between_div.style.backgroundColor = "#ff4e4e"
                else
                    this.selected_between_div.style.backgroundColor = "yellow"
                // Tis div is n longer for selected between so we removing it from selected between div
                this.selected_between_div = 0
                this.outputs["Select_List"].push(tmp_dict)
                this.update_display_changes(tmp_dict["Changes"])
                this.send_data({Select_List: this.outputs["Select_List"]})
            }
        }
        else{
            // If we are syncronizing after refresh looping over select list
            for (const dict of this.outputs["Select_List"]){
                // Converting indexes to % of parent div
                var start = dict["Indexes"][0] / this.outputs["Data_Lenght"] * 100
                var finish = dict["Indexes"][1] / this.outputs["Data_Lenght"] * 100
                if ("Delete" in dict["Changes"])
                    var color = "#ff4e4e"
                else
                    var color = "yellow"
                // Creating div
                const div = document.createElement("div")
                document.getElementById("Progress_Bar").appendChild(div)
                this.add_between_mark(div, start, finish, color)
            }
        }
    }

    unselect(){
        // Unselect marked section
        var left_marker = this.outputs["Left_Marker"]
        var right_marker = this.outputs["Right_Marker"]
        for (const dict of this.outputs["Select_List"]){
            // Searching for div
            if(dict["Indexes"][0] == left_marker && dict["Indexes"][1] == right_marker){
                const index = this.outputs["Select_List"].indexOf(this.outputs["Select_List"])
                // Removing that dict from selected list
                this.outputs["Select_List"].splice(index, 1)
                // Deleting the div of that dict
                this.delete_between_mark(dict["Div"])
                this.send_data({Select_List: this.outputs["Select_List"]})
                // We deleting selected list div but we still selecting that section with our
                // Left and Right cursor so in order to add between marker we using update right marker funcition
                // with Syncronize == 1
                this.Update_Right_Marker(undefined, 1)
                return
            }
        }
    }

    mark_search_results(search_phrase){
        this.xhr.open("POST", "/search", true)
        this.xhr.setRequestHeader('Content-Type', 'application/json')
        // Sending search phrase to the server (python)
        this.xhr.send(JSON.stringify(search_phrase))
        // Getting search results from server (python)
        fetch("search_results")
        .then(response => response.json())
        .then(inputs => {
            // Cleaning previous searched divs (if there is any)
            for (const div of this.search_results_divs)
                this.delete_between_mark(div)
            this.search_results_divs = []
            this.search_results_list = []
            var start_index = inputs[0]
            // Search results are a list that contains all indexes that matches with
            // search phrase but our mark between function takes start, finish % so we
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
                // Converting indexes to %
                var start = between[0] / this.outputs["Data_Lenght"] * 100
                var finish = between[1] / this.outputs["Data_Lenght"] * 100
                this.add_between_mark(div, start, finish, "#ffbf00")
            }
            })
    }
    save_changes(){
        this.xhr.open("POST", "/save", true)
        this.xhr.setRequestHeader('Content-Type', 'application/json')
        // Sending search phrase to the server (python)
        this.xhr.send(JSON.stringify(1))
        window.alert("Saved The Changes")
    }

    apply_changes(){
        
    }
}