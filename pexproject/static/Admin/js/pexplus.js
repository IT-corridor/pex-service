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
    $('#id_search_history_from').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_search_history_to").datepicker("option", "minDate", selectedDate);
            search_history();
        }
    });

    $('#id_search_history_to').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_search_history_from").datepicker("option", "maxDate", selectedDate);
            search_history();
        }
    });    
    // --------------------------------------------------------------------- // 
    $('#id_search_avg_from').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_search_avg_to").datepicker("option", "minDate", selectedDate);
            search_avg();
        }
    });

    $('#id_search_avg_to').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_search_avg_from").datepicker("option", "maxDate", selectedDate);
            search_avg();
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

    $('#id_user_signup_from').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_user_signup_to").datepicker("option", "minDate", selectedDate);
            user_signup_activity();
        }
    });

    $('#id_user_signup_to').datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd",
        onClose: function(selectedDate) {
            $("#id_user_signup_from").datepicker("option", "maxDate", selectedDate);
            user_signup_activity();
        }
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
    _price_history_num([[],[]]);
    var start_date = new Date();
    start_date.setMonth(start_date.getMonth()-1);
    $('#id_user_signup_from').val(get_formatted_date(start_date));
    $('#id_user_signup_to').val(get_formatted_date(new Date()));
    user_signup_activity();
    search_activity();
});

get_formatted_date = function(_date) {
    var dd = _date.getDate();
    var mm = _date.getMonth()+1; //January is 0!
    var yyyy = _date.getFullYear();

    if(dd<10) {
        dd='0'+dd
    } 

    if(mm<10) {
        mm='0'+mm
    } 

    return yyyy+'-'+mm+'-'+dd;
}

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

    $.post('/stats/signup_activity/', 
        {'_from':_from, '_to':_to}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        stat_user_signup_activity = JSON.parse(data);
        var result = '';
        for(idx in stat_user_signup_activity) {
            var no = idx*1 + 1;
            result += '<tr><td>'+no+'</td><td>'+stat_user_signup_activity[idx][0]+'</td><td>'+stat_user_signup_activity[idx][1]+'</td></tr>';
        }
        $('#id_user_signup_table_body').html(result);
    });    
}

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

search_history = function() {
    var _from = $('#id_search_history_from').val();
    var _to = $('#id_search_history_to').val();

    if (_from == '' || _to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/stats/search_history/', 
        {'_from':_from, '_to':_to}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        data = JSON.parse(data);

        $.plot("#id_search_history_chart", data, {
            yaxis: {
                tickFormatter: function (val, axis) {
                    return Math.ceil(val) + " ";
                },    
            },
            xaxis: {
                mode: "time"
            }
        });  
    });
}


search_avg = function() {
    var _from = $('#id_search_avg_from').val();
    var _to = $('#id_search_avg_to').val();

    if (_from == '' || _to == '')
        return false;
    
    $('.page-loader').show();    

    $.post('/stats/search_avg/', 
        {'_from':_from, '_to':_to}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        data = JSON.parse(data);

        $.plot("#id_search_avg_chart", data, {
            series: {
                lines: { show: true },
                points: { show: true }
            },            
            grid: { hoverable: true, clickable: true },            
            yaxis: {
                tickFormatter: function (val, axis) {
                    // return Math.ceil(val) + " ";
                    return parseFloat(Math.round(val * 100) / 100).toFixed(2);
                },    
            },
            xaxis: {
                mode: "time"
            }
        });  

        $("#id_search_avg_chart").bind("plothover", function (event, pos, item) {
            if (item) {
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                var date = new Date(item.datapoint[0]);
                x = date.toString("MMM dd"); // "Dec 20"
                $(".flot-tooltip").html(item.series.label + " : " + y + " on " + x).css({top: item.pageY+5, left: item.pageX+5}).show();
            }
            else {
                $(".flot-tooltip").hide();
            }
        });
        
        $("<div class='flot-tooltip' class='chart-tooltip'></div>").appendTo("body");

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

    $.post('/stats/price_history/', 
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

    $.post('/stats/price_history_period/', 
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

    $.post('/stats/price_history_num/', 
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

    console.log(JSON.stringify(data[0]));
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


search_activity = function() {
    var mode = $('#id_user_search_activity').val();
    $('.page-loader').show();    

    $.post('/stats/search_activity/', 
        {'mode': mode}
    ).success(function(data) {
        $('.page-loader').fadeOut();
        $('#panel_user_search_activity').html(data);
    });
}
