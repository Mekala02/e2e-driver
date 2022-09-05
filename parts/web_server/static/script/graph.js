function getData() {
    return Math.random();
}  

var layout = {
    autosize: true,
    margin: {
        l: 25,
        r: 25,
        b: 25,
        t: 25,
        pad: 0
    },
    paper_bgcolor: '#222222',
    plot_bgcolor: '#222222',
    yaxis: {tickfont: {size:15}},
    xaxis: {tickfont: {size:15}}
};

trace = {
    y:[getData()],
    type:'line',
    line: {
    color: 'red',
    width: 3
}}

Plotly.newPlot('Graph1', [trace], layout, {displayModeBar: false});

var cnt = 0;

setInterval(function(){

    Plotly.extendTraces('Graph1',{ y:[[getData()]]}, [0]);
    cnt++;
    if(cnt > 500) {
        Plotly.relayout('Graph1',{
            xaxis: {
                range: [cnt-500,cnt]
            }
        });
    }
},15);

Plotly.newPlot('Graph2', [trace], layout, {displayModeBar: false});

var cnt2 = 0;

setInterval(function(){

    Plotly.extendTraces('Graph2',{ y:[[getData()]]}, [0]);
    cnt2++;
    if(cnt > 500) {
        Plotly.relayout('Graph2',{
            xaxis: {
                range: [cnt-500,cnt]
            }
        });
    }
},15);