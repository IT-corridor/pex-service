$(function() {
    $('#id_price_history_from').datetimepicker({
        viewMode: 'years',
        format: "YYYY-MM-DD",
        minDate: 0,
    });

    $('#id_price_history_to').datetimepicker({
        viewMode: 'years',
        format: "YYYY-MM-DD",
        useCurrent: false
    });    

    $("#id_price_history_from").on("dp.change", function (e) {
        $('#id_price_history_to').data("DateTimePicker").minDate(e.date);
        $('#id_price_history_to').focus();
        price_history();
    });
    $("#id_price_history_to").on("dp.change", function (e) {
        $('#id_price_history_from').data("DateTimePicker").maxDate(e.date);
        price_history();
    });    

    $('#id_user_signup_from').datetimepicker({
        format: "YYYY-MM-DD",
        minDate: 0,
    });

    $('#id_user_signup_to').datetimepicker({
        format: "YYYY-MM-DD",
        useCurrent: false
    });    

    $("#id_user_signup_from").on("dp.change", function (e) {
        $('#id_user_signup_to').data("DateTimePicker").minDate(e.date);
        user_signup_activity();
    });
    $("#id_user_signup_to").on("dp.change", function (e) {
        $('#id_user_signup_from').data("DateTimePicker").maxDate(e.date);
        user_signup_activity();
    });      

    $( ".airport_text" ).autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
        },
            
        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
    });    
});


$(document).ready(function(){    
    _update_line_info(stat_num_search);
    _price_history([[],[]]);
});


update_pop_search = function() {
    var period = $('#id_pop_search_period').val();

    $('.page-loader').show();    

    $.post('/stats/popular_search/', 
        {'period':period}
    ).success(function(data) {
        pop_searches = JSON.parse(data);
        var result = '';
        for(idx in pop_searches) {
            var rank = idx*1 + 1;
            result += '<tr><td>'+rank+'</td><td>'+pop_searches[idx].source+'</td><td>'+pop_searches[idx].destination+'</td><td>'+pop_searches[idx].dcount+'</td></tr>';
        }
        $('#id_pop_search_table_body').html(result);
        $('.page-loader').fadeOut();
    });
}

user_signup_activity = function() {
    var _from = $('#id_user_signup_from').val();
    var _to = $('#id_user_signup_to').val();

    if (_from == '' || _to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/stats/user_signup_activity/', 
        {'_from':_from, '_to':_to}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        stat_user_signup_activity = JSON.parse(data);
        var result = '';
        for(idx in stat_user_signup_activity) {
            var no = idx*1 + 1;
            result += '<tr><td>'+no+'</td><td>'+stat_user_signup_activity[idx].username+'</td><td>'+stat_user_signup_activity[idx].date_joined+'</td></tr>';
        }
        $('#id_user_signup_table_body').html(result);
    });    
}

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

price_history = function() {
    var _from = $('#id_price_history_from').val();
    var _to = $('#id_price_history_to').val();
    var airline = $('#id_price_history_airline').val();
    var r_from = $('#id_price_history_from').val();
    var r_to = $('#id_price_history_to').val();
    var aggregation = $('#id_price_history_aggregation').val();

    if (_from == '' || _to == '')
        return false;

    if (r_from == '' || r_to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/stats/price_history/', 
        {'_from':_from, '_to':_to, 'airline':airline, 'r_from':r_from, 'r_to':r_to, 'aggregation':aggregation}
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

    $.plot("#id_price_history_chart", data[0], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return val + " miles";
            },    
        },
        xaxis: {
            mode: "time"
        }
    });  

    if (data[1].length > 0)
        $('#id_price_history_chart_tax').css('margin-left','38px');

    $.plot("#id_price_history_chart_tax", data[1], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return "   $"+val;
            },    
        },
        xaxis: {
            mode: "time"
        }
    });      
}