$(function() {
    $('#id_price_history_from').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_price_history_to").datepicker("option", "minDate", selectedDate);
            price_history();
        }
    });

    $('#id_price_history_to').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_price_history_from").datepicker("option", "maxDate", selectedDate);
            price_history();
        }
    });    
    // --------------------------------------------------------------------- // 
    $('#id_price_history_from_period').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_price_history_to_period").datepicker("option", "minDate", selectedDate);
            price_history_period();
        }
    });

    $('#id_price_history_to_period').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_price_history_from_period").datepicker("option", "maxDate", selectedDate);
            price_history_period();
        }
    });    
    // --------------------------------------------------------------------- // 

    $('#id_price_history_from_num').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_price_history_to_num").datepicker("option", "minDate", selectedDate);
            price_history_num();
        }
    });

    $('#id_price_history_to_num').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_price_history_from_num").datepicker("option", "maxDate", selectedDate);
            price_history_num();
        }
    });    

    // --------------------------------------------------------------------- // 

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
    _price_history(stat_price_history);
    _price_history_period(stat_price_history_period);
    _price_history_num([[],[]]);
});

_update_line_info = function(data) {
    var airlines = [['SU', 'Aeroflot'], ['CA', 'Air China'], ['AA', 'American'], ['DL', 'Delta'], ['EY', 'Etihad'], ['B6', 'JetBlue'], ['S7', 'S7'], ['UA', 'United'], ['VX', 'Virgin America'], ['DJ', 'virgin australia'],['VS', 'Virgin Atlantic']];

    var idx = 1;
    if ($(window).width() < 768) 
        idx = 0;

    var rdata = [];
    for(i=0; i < airlines.length; i++)
        rdata.push([airlines[i][idx], data[i]]);

    $.plot("#bar-chart", [ rdata ], {
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
    var _from = $('#id_airline_info_from').val();
    var _to = $('#id_airline_info_to').val();
    
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
    var r_from = $('#id_price_history_route_from').val();
    var r_to = $('#id_price_history_route_to').val();
    var aggregation = $('#id_price_history_aggregation').val();

    if (_from == '' || _to == '')
        return false;

    if (r_from == '' || r_to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/customer/stats/price_history/', 
        {'_from':_from, '_to':_to, 'airline':airline, 'r_from':r_from, 'r_to':r_to, 'aggregation':aggregation}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        stat_price_history = JSON.parse(data);
        _price_history(stat_price_history);
    });
}

price_history_period = function() {
    var _from = $('#id_price_history_from_period').val();
    var _to = $('#id_price_history_to_period').val();
    var airline = $('#id_price_history_airline_period').val();
    var r_from = $('#id_price_history_route_from_period').val();
    var r_to = $('#id_price_history_route_to_period').val();
    var aggregation = $('#id_price_history_aggregation_period').val();
    // time before departure date
    var period = $('#id_price_history_period').val();

    if (_from == '')
        return false;

    if (r_from == '' || r_to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/customer/stats/price_history_period/', 
        {'_from':_from, '_to':_to, 'airline':airline, 'r_from':r_from, 'r_to':r_to, 'aggregation':aggregation, 'period': period}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        stat_price_history = JSON.parse(data);
        _price_history_period(stat_price_history);
    });
}

price_history_num = function() {
    var _from = $('#id_price_history_from_num').val();
    var _to = $('#id_price_history_to_num').val();
    var airline = $('#id_price_history_airline_num').val();
    var r_from = $('#id_price_history_route_from_num').val();
    var r_to = $('#id_price_history_route_to_num').val();
    var aggregation = $('#id_price_history_aggregation_num').val();

    if (_from == '')
        return false;

    if (r_from == '' || r_to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/customer/stats/price_history_num/', 
        {'_from':_from, '_to':_to, 'airline':airline, 'r_from':r_from, 'r_to':r_to, 'aggregation':aggregation}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        stat_price_history = JSON.parse(data);
        _price_history_num(stat_price_history);
        console.log(stat_price_history);
    });
}

_price_history_num = function(data) {
    var i = 0;
    $.each(data, function(key, val) {
        val.color = i;
        ++i;
    });

    // console.log(JSON.stringify(data[0]));
    $.plot("#id_price_history_chart_num", data[0], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return Math.ceil(val) + " miles";
            },    
        },
        xaxis: {
            ticks: data[2]  // [[1,1],[2,2]]        
        }
    });  

    if (data[1].length > 0)
        $('#id_price_history_chart_tax_num').css('margin-left','18px');

    $.plot("#id_price_history_chart_tax_num", data[1], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return "   $"+val.toFixed(2);
            },    
        },
        xaxis: {
            ticks: data[2]  // [[1,1],[2,2]]
        }
    });      
}

_price_history_period = function(data) {
    var i = 0;
    $.each(data, function(key, val) {
        val.color = i;
        ++i;
    });

    // console.log(JSON.stringify(data[0]));
    $.plot("#id_price_history_chart_period", data[0], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return Math.ceil(val) + " miles";
            },    
        },
        xaxis: {
            mode: "time"
        }
    });  

    if (data[1].length > 0)
        $('#id_price_history_chart_tax_period').css('margin-left','18px');

    $.plot("#id_price_history_chart_tax_period", data[1], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return "   $"+val.toFixed(2);
            },    
        },
        xaxis: {
            mode: "time"
        }
    });      
}

_price_history = function(data) {
    var i = 0;
    $.each(data, function(key, val) {
        val.color = i;
        ++i;
    });

    // console.log(JSON.stringify(data[0]));
    $.plot("#id_price_history_chart", data[0], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return Math.ceil(val) + " miles";
            },    
        },
        xaxis: {
            mode: "time"
        }
    });  

    if (data[1].length > 0)
        $('#id_price_history_chart_tax').css('margin-left','18px');

    $.plot("#id_price_history_chart_tax", data[1], {
        yaxis: {
            tickFormatter: function (val, axis) {
                return "   $"+val.toFixed(2);
            },    
        },
        xaxis: {
            mode: "time"
        }
    });      
}

update_user_search = function() {
    var period = $('#id_search_result_period').val();
    var r_from = $('#id_search_result_from_route').val();
    var r_to = $('#id_search_result_to_route').val();
    var category = $('#id_search_category').val();

    $('.page-loader').show();    

    $.post('/customer/stats/user_search/', 
        {'period':period, 'r_from':r_from, 'r_to':r_to, 'category':category}
    ).success(function(data) {
        user_searches = JSON.parse(data);
        var result = '';
        for(idx in user_searches) {
            var status = '<button class="btn bgm-gray waves-effect" style="width: 50px;">'+user_searches[idx].num_result+'</button>';
            if (user_searches[idx].num_result > 0)
                status = '<button class="btn bgm-blue waves-effect" style="width: 50px;">'+user_searches[idx].num_result+'</button>';

            result += '<tr><td>'+(idx*1+1)+'</td><td>'+user_searches[idx].source+'->'+user_searches[idx].destination+'</td><td>'+user_searches[idx].scrapetime+'</td><td>'+user_searches[idx].traveldate+'</td><td>'+user_searches[idx].returndate+'</td><td>'+status+'</td></tr>';
        }
        $('#id_user_search_table_body').html(result);
        $('.page-loader').fadeOut();
    });
}