
$(document).ready(function(){    
    /* Let's create the chart */
    _update_line_info(stat_num_search);
});

_update_line_info = function(data) {
    $.plot("#bar-chart", [ data ], {
        series: {
            bars: {
                show: true,
                barWidth: 0.6,
                align: "center"
            }
        },
        xaxis: {
            mode: "categories",
            tickLength: 0
        }
    });
}

update_line_info = function(obj) {
    var period = $('#id_airline_info_period').val();
    var fare_class = $('#id_airline_info_fare_class').val();
    var _from = $('#id_search_result_from').val();
    var _to = $('#id_search_result_to').val();
    
    if (_from == '' || _to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/stats/airline_info/', 
        {'period':period, 'fare_class':fare_class, '_from':_from, '_to':_to}
    ).success(function(data) {
        stat_num_search = JSON.parse(data);
        _update_line_info(stat_num_search);
        $('.page-loader').fadeOut();
    });
}