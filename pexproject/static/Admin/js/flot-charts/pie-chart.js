$(document).ready(function(){
    var pieData = [
        {data: 1, color: '#F44336', label: 'Toyota'},
        {data: 2, color: '#03A9F4', label: 'Nissan'},
        {data: 3, color: '#8BC34A', label: 'Hyundai'},
        {data: 4, color: '#FFEB3B', label: 'Scion'},
        {data: 4, color: '#009688', label: 'Daihatsu'},
    ];
    
    /* Pie Chart */
    
    if($('#pie-chart')[0]){
        $.plot('#pie-chart', pieData, {
            series: {
                pie: {
                    show: true,
                    stroke: { 
                        width: 2,
                    },
                },
            },
            legend: {
                container: '.flc-pie',
                backgroundOpacity: 0.5,
                noColumns: 0,
                backgroundColor: "white",
                lineWidth: 0
            },
            grid: {
                hoverable: true,
                clickable: true
            },
            tooltip: true,
            tooltipOpts: {
                content: "%p.0%, %s", // show percentages, rounding to 2 decimal places
                shifts: {
                    x: 20,
                    y: 0
                },
                defaultTheme: false,
                cssClass: 'flot-tooltip'
            }
            
        });
    }    

    // hard-code color indices to prevent them from shifting as
    // countries are turned on/off


    _price_history(stat_price_history);
});

price_history = function() {
    var _from = $('#id_price_history_from').val();
    var _to = $('#id_price_history_to').val();
    var airline = $('#id_price_history_airline').val();
    var route = $('#id_price_history_route').val();
    var aggregation = $('#id_price_history_aggregation').val();

    if (_from == '' || _to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/stats/price_history/', 
        {'_from':_from, '_to':_to, 'airline':airline, 'route':route, 'aggregation':aggregation}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        stat_price_history = JSON.parse(data);
        _price_history(stat_price_history);
    });
}

_price_history = function(data) {
    var i = 0;
    $.each(data, function(key, val) {
        val.color = i;
        ++i;
    });

    $.plot("#id_price_history_chart", data, {
        yaxis: {
            min: 0
        },
        xaxis: {
            tickDecimals: 2
        }
    });    
}