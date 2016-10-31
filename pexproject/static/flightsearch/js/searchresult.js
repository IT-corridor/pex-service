$('#nodata-msg').empty();
var data_status = false;
var datalist = data0;

if (datalist.length > 0) {
    data_status = true;
}

$(function() {

    $('#departuredate').datepicker({
        minDate: 0,
        onSelect: function() {
            setTimeout(function function_name(argument) {
                $('#return').focus();
            }, 200);

        },
        onClose: function(selectedDate) {
            // Set the minDate of 'to' as the selectedDate of 'from'
            $("#return").datepicker("option", "minDate", selectedDate);
        }
    });
    $('#return').datepicker({
        minDate: 0,
        onSelect: function() {
            /*  setTimeout(function function_name (argument) {
             $('#cabintab').focus();
             },50);
             */
        },
    });
});

$(".flight-search-show").click(function() {
    $(".flight-search-panel").toggleClass('in');
});

$('#passenger').change(function() {
    $('#traveller').val($('#passenger').val());
});

$(document).ready(function() {

    if (request_returnkey == '') {
        //$('.travelers-down-menu').addClass('full-width-res');
        $('.travelers-down-menu').css("left", "-=122");
    }
});

$(document).ready(function() {
    if (($('.chk-airlines').length) != ($('.chk-airlines:checked').length)) {
        $("#selectairline").prop('checked', false);
    } else {
        $("#selectairline").prop('checked', true);
    }

    if (($('.chk-stoppage').length) != ($('.chk-stoppage:checked').length)) {
        $("#selectallstop").prop('checked', false);
    } else {
        $("#selectallstop").prop('checked', true);
    }

});

//@@@ SELECT ALL CABIN@@@@@@@@@
$(document).ready(function() {

    $("#checkallcabin").on("click", function() {
        if ($(this).is(':checked')) {
            $(".chk").each(function() {
                this.checked = true;

            });
        } else {
            $(".chk").each(function() {
                this.checked = false;
            });
        }
    });
    $(".chk").on("click", function() {
        if (!$(this).is(':checked')) {
            $("#checkallcabin").attr('checked', false);
        }
    });

    //@@@@ SELECT ALL AIRLINES @@@@@@@@@
    //var airlines = {};
    $("#selectairline").on("click", function() {
        if ($(this).is(':checked')) {
            $(".chk-airlines").each(function() {
                this.checked = true;

            });
        } else {
            $(".chk-airlines").each(function() {
                this.checked = false;
            });
        }
    });
    $(".chk-airlines").on("click", function() {
        if (!$(this).is(':checked')) {
            $("#selectairline").attr('checked', false);
        }
    });

    //@@@@ SELECT ALL STOPPAGE @@@@@@@@@

    $("#selectallstop").on("click", function() {
        if ($(this).is(':checked')) {
            $(".chk-stoppage").each(function() {
                this.checked = true;

            });
        } else {
            $(".chk-stoppage").each(function() {
                this.checked = false;
            });
        }
    });
    $(".chk-stoppage").on("click", function() {
        if (!$(this).is(':checked')) {
            $("#selectallstop").attr('checked', false);
        }
    });

});
//  ==  ==  ==  ==  ==  ==  ==  ==  ==  == = time slider ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == =

var deptmintime;
var arivemintime;
var deptmaxtime;
var arivemaxtime;

var process_status = 'complete';

function timeconversion(time) {
    var val = time;
    var hour;
    ampm = val.split(' ');
    mindepature = ampm[0].split(':');
    hour = mindepature[0];

    if ($.trim(ampm[1]) != "p.m." && $.trim(ampm[1]) != "PM") {

        if (parseInt(hour) > 11) {
            hour = 0;
        }
    } else {
        if (parseInt(hour) < 12) {
            hour = parseInt(hour) + 12;
        } else {
            hour = 0 + 12;
        }

    }
    minute = mindepature[1];
    deptmin = (hour * 60);
    if (minute) {
        deptmin = parseInt(deptmin) + parseInt(minute);
    }

    return deptmin;

}

if (timedata_) {

    var dept = mindept_;
    if (dept != "None") {
        deptmintime = timeconversion(dept);
    } else {
        deptmintime = 0;
    }

    var arive = minarival_;
    if (arive != "None") {
        arivemintime = timeconversion(arive);
    } else {
        arivemintime = 0;
    }
    var maxdeparture = maxdept_;
    if (maxdeparture != "None") {
        deptmaxtime = timeconversion(maxdeparture);
    } else {
        deptmaxtime = 1439;
    }

    var maxarivaltime = maxarival_;

    if (maxarivaltime != "None") {

        arivemaxtime = timeconversion(maxarivaltime);

    } else {
        arivemaxtime = 1439;
    }
} else {
    deptmintime = 0;
    arivemintime = 0;
    deptmaxtime = 1439;
    arivemaxtime = 1439;

}
/*************************** SLIDER DECTION  ******************************/

$("#depart").slider({
    range: true,
    min: 0,
    max: 1439,
    values: [deptmintime, deptmaxtime],
    slide: function(e, ui) {
        var hours0 = Math.floor(ui.values[0] / 60);
        var minutes0 = ui.values[0] - (hours0 * 60);
        var hours1 = Math.floor(ui.values[1] / 60);
        var minutes1 = ui.values[1] - (hours1 * 60);
        start = getTime(hours0, minutes0);
        end = getTime(hours1, minutes1);
        $('#depaturemin').val(start);
        $('#depaturemax').val(end);
        depaturemin = start;
        depaturemax = end;
        $("#time").text(start + ' - ' + end);
    }

});

var depaturemin = $('#depaturemin').val();
var depaturemax = $('#depaturemax').val();
var arivalmin = $('#arivalmin').val();
var arivalmax = $('#arivalmax').val();

function slideTime1(event, ui) {
    var val0 = $("#depart").slider("values", 0),
        val1 = $("#depart").slider("values", 1),
        hours0 = Math.floor(val0 / 60);
    minutes0 = val0 - (hours0 * 60);
    hours1 = Math.floor(val1 / 60);
    minutes1 = val1 - (hours1 * 60);
    start = getTime(hours0, minutes0);
    end = getTime(hours1, minutes1);
    $('#depaturemin').val(start);
    $('#depaturemax').val(end);
    depaturemin = start;
    depaturemax = end;
    $("#time").text(start + ' - ' + end);
}

$("#arive").slider({
    range: true,
    min: 0,
    max: 1439,
    values: [arivemintime, arivemaxtime],
    slide: function(e, ui) {
        hours0 = Math.floor(ui.values[0] / 60);
        minutes0 = ui.values[0] - (hours0 * 60);
        hours1 = Math.floor(ui.values[1] / 60);
        minutes1 = ui.values[1] - (hours1 * 60);
        startTime = getTime(hours0, minutes0);
        $('#arivalmin').val(startTime);
        endTime = getTime(hours1, minutes1);
        $('#arivalmax').val(endTime);
        arivalmin = startTime;
        arivalmax = endTime;
        $("#arivaltime").text(startTime + ' - ' + endTime);
    }
});

function slideTime(event, ui) {

    var val0 = $("#arive").slider("values", 0),
        val1 = $("#arive").slider("values", 1),
        hours0 = Math.floor(val0 / 60);
    minutes0 = val0 - (hours0 * 60); //parseInt(val0 % 60, 10),
    hours1 = Math.floor(val1 / 60);
    minutes1 = val1 - (hours1 * 60); //parseInt(val1 % 60, 10),

    startTime = getTime(hours0, minutes0);
    $('#arivalmin').val(startTime);
    endTime = getTime(hours1, minutes1);
    $('#arivalmax').val(endTime);
    arivalmin = startTime;
    arivalmax = endTime;
    $("#arivaltime").text(startTime + ' - ' + endTime);
}

function getTime(hours, minutes) {
    var time = null;
    minutes = minutes + "";
    if (hours < 12) {
        time = "AM";
    } else {
        time = "PM";
    }
    if (hours == 0) {
        hours = 12;
    }
    if (hours > 12) {
        hours = hours - 12;
    }
    if (minutes.length == 1) {
        minutes = "0" + minutes;
    }
    return hours + ":" + minutes + " " + time;
}

slideTime();
slideTime1();

// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  end time slider ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 

$(function() {

    $("#from").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
        },
        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
        select: function(event, ui) {
            $('#fromid').val(ui.item.id);
        },
    });
    $("#to").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
        },
        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
        select: function(event, ui) {
            $('#toid').val(ui.item.id);
        },
    });
});

$(function() {
    if ($(window).width() < 768) {
        $(".filters-holder").addClass('filters-holder-ht');
        $(".show-filter").click(function() {
            $(this).parent().parent().toggleClass('filters-holder-ht');
        });
    }
    $("#cabintab").focus(function() {
        $(".travelers-holder").addClass('open');
        return false;
    });

    $("#cabintab").click(function() {
        $(".travelers-holder").addClass('open');
        return false;
    });

    $(".form_val").focus(function() {
        if (!$(this).hasClass("cabin_type")) {
            $(".travelers-holder").removeClass('open');
        }
    });
});
$('#apply_traveler').click(function() {
    $(".travelers-holder").removeClass('open');
});

$(document).ready(function() {
    $(".alert-warning").hide();
    var tno = '';
    if (passenger_) {
        tno = passenger_;
    } else {
        tno = passenger__;
    }
    $('#adults').val(tno);
    $('#traveller').val(tno);
    //$('#passenger').val(tno);
    travelinfo();
});

var total;

//@@increase decrease on buttom click
$(function() {
    $('.add').on('click', function() {
        total = tatalpassenger();
        if (total < 6) {
            var $qty = $(this).closest('p').find('.qty');
            var currentVal = parseInt($qty.val());
            if (!isNaN(currentVal)) {
                $qty.val(currentVal + 1);
            }
            travelinfo();
        }
    });
    $('.minus').on('click', function() {
        total = tatalpassenger();
        if (total > 0) {
            var $qty = $(this).closest('p').find('.qty');
            var currentVal = parseInt($qty.val());
            if (!isNaN(currentVal) && currentVal > 0) {
                $qty.val(currentVal - 1);
            }

            travelinfo();
        }
    });

});
$('#cabintype').on('change', function() {
    travelinfo();
});
//@@@Cabin select@@@@


function travelinfo() {
    total = tatalpassenger();
    $('#passenger').val(total);
    var text;
    if (total == 1) {
        text = "traveler";
    } else {
        text = "travelers";
    }
    var selectedcabin = $("#cabintype option:selected").text();
    var html = "<span id='travelar'>" + total + " " + text + ", " + selectedcabin + "</span>";
    $('#travelar').replaceWith(html);
    if (total == 0) {
        var msg = '';
        $('#submitid').prop('disabled', true);
        $(".alert-warning").empty();
        msg = "You must select atleast one traveler";
        $(".alert-warning").append(msg);
        $(".alert-warning").show();
    } else {
        $('#submitid').prop('disabled', false);
        $(".alert-warning").hide();
    }
}

//@@@Total Passenger@@@@
function tatalpassenger() {
    var sum = 0;
    $('.numberHolder').each(function() {
        sum += parseFloat($(this).val());
    });
    return sum;
};

//@@not close on click dropdown

$('.dropdown-menu .down-menu-block').click(function(e) {
    e.stopPropagation();
});

$('#loading_img').hide();
//@@---------------------- pagination -------------------------------------
var call_sent = "completed";
var pagecount = 2;
var is_data = 1;

$(window).scroll(function() {
    var doch = ($(document).height() - 200);
    var winh = ($(window).height() + 200);
    if ($(window).scrollTop() >= doch - winh) {
        if (is_data > 0) {
            if (call_sent == "completed") {
                loadArticle(pagecount);
                pagecount++;
            }
        }
    }
});

var urls = (get_full_path_);

function loadArticle(pageNumber) {
    call_sent = "in_progress";
    $('#loading_img').show();
    var airline = new Array();
    var stoppage = new Array();
    var fareCodes = new Array();
    var min_prc_param = "";
    var max_prc_param = "";
    var row_val = "";

    if ($('#minPriceMile').val() != '')
        min_prc_param = "&minPriceMile=" + parseInt($('#minPriceMile').val());
    if ($('#maxPriceMile').val() != '')
        max_prc_param = "&maxPriceMile=" + parseInt($('#maxPriceMile').val());

    if ($('#rowid').length)
        row_val = "&rowid=" + $('#rowid').val();

    $(".chk-airlines:checked").each(function() {
        airline.push($(this).val());
    });

    $(".farecode:checked").each(function() {
        fareCodes.push($(this).val());
    });

    $(".chk-stoppage:checked").each(function() {
        stoppage.push($(this).val());
    });

    var multicity = '';
    var multicity1 = multicity_;

    if (multicity1 != '')
        multicity = "&multicity=" + multicity1;

    var stoplenght = stoppage.length;
    var airlinelenght = airline.length;

    $.ajax({
        url: urls,
        type: 'POST',
        data: "action=" + encodeURI('infinite_scroll') + min_prc_param + max_prc_param + "&page_no=" + encodeURI(pageNumber) + "&loop_file=loop&csrfmiddlewaretoken=" + csrf_token + "&depaturemin=" + depaturemin + "&depaturemax=" + depaturemax + "&arivalmin=" + arivalmin + "&arivalmax=" + arivalmax + "&airlines=" + airline + "&fareCodes=" + fareCodes + "&stoppage=" + stoppage + row_val + multicity,
        success: function(html) {
            $("#content").append(html);
            call_sent = "completed";
            $('#loading_img').hide();
            if ($("#nodata").length)
                is_data = 0;
        }
    });
    return false;
}

$(document).ready(function() {

    // hide #back-top first
    $("#back-top").hide();
    $('.btn-balances').hide();
    // fade in #back-top
    $(function() {
        $(window).scroll(function() {
            if ($(this).scrollTop() > 100) {
                $('#back-top').fadeIn();
                $('.btn-balances').fadeIn();
            } else {
                $('#back-top').fadeOut();
                $('.btn-balances').fadeOut();
            }
        });

        // scroll body to 0px on click
        $('#back-top a').click(function() {
            $('body,html').animate({
                scrollTop: 0
            }, 800);
            return false;
        });
    });

});

//  ==  ==  ==  ==  == show/hide details ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == =
$(document.body).on('click', '.show-details', function() {
    //$('.show-details').on('click',function () {
    var collapse_content_selector = $(this).attr('href');
    var toggle_switch = $(this);
    $(collapse_content_selector).slideToggle(function() {
        $(this).is(':visible') ? toggle_switch.text('HIDE DETAILS') : toggle_switch.text('SHOW DETAILS');
    });
});

var record;
var tweet1;
var tweetcontent;
var fulltext;
var fbcontent;
$(document.body).on('click', '.share', function() {
    var record = $(this).attr("id");
    $('#recorid').val(record);
    tweetcontent = $(this).siblings("input[type='hidden']").val();
    var flight_price = $(this).siblings("input[type='hidden']").attr('class');
    var fbtext = "Miles " + flight_price + dis_string1;
    $('#fbtitle').empty();
    $('#fbtitle').append(fbtext);
    $('#social_share').attr('href', function() {
        fbcontent = this.href + '%26share_recordid=' + record;

    });
    $('#twitter_share').attr('href', function() {
        var fbcontent1 = fbcontent.split("?u=");
        fbcontent1 = tweetcontent + fbcontent1[1];
        var tweet = this.href;
        tweet1 = tweet.split('status=');
        var tweeturl = tweet1[1];
        $('#twitter_content').val(fbcontent1);
        fulltext = tweet1[0] + 'status=' + fbcontent1;
        return this.href = tweet1[0] + 'status=' + fbcontent1;
    });
});
$('#social_share').click(function() {
    window.open(fbcontent, 'newwindow', 'width=600, height=250');
    return false;
});

$('#twitter_content').change(function() {
    var text = $('#twitter_content').val();
    $('#twitter_share').attr('href', function() {
        fulltext = '';
        fulltext = tweet1[0] + 'status=' + text;
    });

});
$('#twitter_share').click(function() {
    window.open(fulltext, 'newwindow', 'width=600, height=250');
    return false;

});

var dataurls = (get_full_path_);
var multicity1 = multicity_;
var searchid = keyid_;
var returnid = request_returnkey;
var cabin = cabin_;
var airline = new Array();
var stoppage = new Array();
var row_val = "";
var refreshIntervalId = '';

$('#progress_hidden_val').val(progress_value_);

if ($('#rowid').length)
    row_val = "&rowid=" + $('#rowid').val();

$(".chk-airlines:checked").each(function() {
    airline.push($(this).val());
});

$(".chk-stoppage:checked").each(function() {
    stoppage.push($(this).val());
});

refresh_airline = setInterval(loading, 3000);

var airlines = ["Delta", "United", "Etihad", "S7", "Virgin Atlantic", "Virgin America", "Virgin Australia", "Jetblue", "American", "Aeroflot", "AirChina"];

i = 0;

function loading() {
    $('#loading-info').empty();
    $('#loading-info').append('Searching  ' + airlines[i] + ' Airlines ...');
    i = (i + 1) % airlines.length;
}

var progess_width = 0;
var timecompleted = true;
var callrunning = false;

if (!data_status) // there is no data
{
    $("#loading-model").modal('show');

    if (parseInt($('#progress_hidden_val').val()) > 185) // after data is loaded
    {
        $("#loading-model").modal('hide');
        $('.progress').hide();
        $('.filters-holder').removeClass('xs-filters-holder-ht');
        isprocess();
    } else {
        $('.filters-holder').addClass('xs-filters-holder-ht');
        refreshIntervalId = setInterval(updateTime, 2000);
    }
} else {
    $('.progress').hide();
    $('.filters-holder').removeClass('xs-filters-holder-ht');
    get_post_search_data();
    getflexData();
    //isprocess();
}

//  ==  ==  ==  ==  ==  ==  ==  ==  ==  == = price slider  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == =
function priceMileslider(event, ui) {
    var min_miles = $("#miles_slider").slider("values", 0);
    var max_miles = $("#miles_slider").slider("values", 1);
    $('#minPriceMile').val(min_miles);
    $('#maxPriceMile').val(max_miles);
    $("#miles_value").text('Miles ' + min_miles + ' - Miles ' + max_miles);
}

function initialisePriceRange() {
    var minPriceMile = parseInt($('#minPriceMile').val());
    var maxPriceMile = parseInt($('#maxPriceMile').val());
    if (minpricemile_ != 0) {
        minPriceMile = minpricemile_;
        maxPriceMile = maxpricemile_;
    }
    var fix_min_price;
    var fix_max_price;
    if ($('#fix_min_price').val() != 'undefined') {
        fix_min_price = parseInt($('#fix_min_price').val());
        fix_max_price = parseInt($('#fix_max_price').val());
    } else {
        fix_min_price = minPriceMile;
        fix_max_price = maxPriceMile;
    }
    $("#miles_slider").slider({
        range: true,
        min: fix_min_price,
        max: fix_max_price,
        values: [minPriceMile, maxPriceMile],
        slide: function(priceRange, ui) {
            $('#minPriceMile').val(ui.values[0]);
            $('#maxPriceMile').val(ui.values[1]);
            $("#miles_value").text('Miles ' + ui.values[0] + ' -  Miles ' + ui.values[1]);
        }
    });
    priceMileslider();
}

function get_post_search_data() {
    // price matrix
    $.ajax({
        url: '/get_flight_pricematrix',
        type: 'POST',
        data: {
            "csrfmiddlewaretoken": csrf_token,
            "cabin": cabin_,
            "keyid": keyid_,
            "returnkey": request_returnkey,
            "multicity": multicity_
        },
        success: function(html) {
            $('#price_matrix').empty();
            $('#price_matrix').append(html);
        }
    });

    // mile range and farecodes
    $.ajax({
        url: '/get_flight_pricematrix',
        type: 'POST',
        data: {
            "csrfmiddlewaretoken": csrf_token,
            "cabin": cabin_,
            "keyid": keyid_,
            "returnkey": request_returnkey,
            "multicity": multicity_,
            "valuefor": "pricerange"
        },
        success: function(data) {
            $('#minPriceMile').val(data[0]);
            $('#maxPriceMile').val(data[1]);
            $('#fix_min_price').val(data[0]);
            $('#fix_max_price').val(data[1]);
            create_fare_code_filter(data[2]);
            initialisePriceRange();
        }
    });

    // aircrafts filter
    $.ajax({
        url: '/get_aircraft_category',
        type: 'POST',
        data: {
            "csrfmiddlewaretoken": csrf_token,
            "cabin": cabin_,
            "keyid": keyid_,
            "returnkey": request_returnkey,
            "multicity": multicity_,
            "valuefor": "pricerange"
        },
        success: function(data) {
            $('#filter_aircraft').html(data);
        }
    });

}
// ----------- Flex data call ----------------------------------//

function getflexData() {
    var searchtype = searchtype_;
    $.ajax({
        type: "POST",
        url: "/getFlexResult/",
        data: {
            "departkey": searchid,
            "searchtype": searchtype,
            "returnkey": returnid,
            csrfmiddlewaretoken: csrf_token
        },
        success: function(html) {
            //$('#calendarmatix').empty();
            $('#calendarmatix').append(html);
        }
    });
}
var codelen = fareCodelength_;
var codes = fareCodes_;
var code1 = codes.replace(/&quot;/g, '');
code1 = code1.replace('[', '');
code1 = code1.replace(']', '');
code1 = code1.split(',');

function create_fare_code_filter(fareCodeList) {
    var fareCodeDisplay = '';
    for (item = 0; item < fareCodeList.length; item++) {
        codeStatus = '';
        if (codelen > 0)
            for (c = 0; c < codelen; c++)
                if ($.trim(code1[c]) == $.trim(fareCodeList[item]))
                    codeStatus = "checked='checked'";
        fareCodeDisplay = fareCodeDisplay + "<div class='checkbox'><label><input type='checkbox' class='farecode' name='fareCodes' value='" + fareCodeList[item] + "'" + codeStatus + "><span></span>" + fareCodeList[item] + "</label></div>";
    }
    $('#add_fare_code').append(fareCodeDisplay);
}

function updateTime() {
    timecompleted = true;
    if (!callrunning)
        isprocess();
}

function redirecttosearchpage(scraperStatus) {
    $.ajax({
        url: dataurls,
        type: 'POST',
        data: "csrfmiddlewaretoken=" + csrf_token + "&depaturemin=" + depaturemin + "&depaturemax=" + depaturemax + "&airlines=" + airline + "&stoppage=" + stoppage + row_val + "&scraperStatus=" + scraperStatus,
        success: function(html) {
            $('.filters-holder').addClass('xs-filters-holder-ht');
            $("#content1").empty();
            $(".contentdiv").remove();
            $("#content1").append(html);

            progess_width = $('#progressbar').width();
            $('#progress_hidden_val').val(progess_width);

            if (progess_width < 195)
                progess_width = parseInt(progess_width) + 12;

            $('#progressbar').width(progess_width);
            // needs to reload the data
            is_data = 1;
            pagecount = 2;
            $('#content').empty();

            if (scraperStatus == 'complete') {
                $('#progressbar').css("width", "100%");
                $('#progress_hidden_val').val('195');
                //clearInterval(refreshIntervalId);
                $('#progressbar').text('');
                $('.progress').hide();
                $("#loading-model").modal('hide');
                $('.filters-holder').removeClass('xs-filters-holder-ht');

                if ($('#nodata').length > 0 && $('#datafound').length <= 0)
                    $('#nodata-msg').append("Oops, looks like there aren't any flight results for your filtered search. Try to broaden your search criteria for better results.");
            }
        }
    });
}

var dataCheckCount = 0;
var timeCount = 0;
var isDataComplete = '';
var multicity = '';
var multicity1 = multicity_;

function isprocess() {
    callrunning = true;
    timecompleted = false;
    var temp = '';

    if (returnid != '')
        var temp = "&returnkey=" + encodeURI(returnid);

    if (multicity1 != '')
        multicity = "&multicity=" + encodeURI(multicity1);

    $.ajax({
        type: "POST",
        url: "/checkData/",
        data: "keyid=" + encodeURI(searchid) + "&csrfmiddlewaretoken=" + csrf_token + "&cabin=" + encodeURI(cabin) + temp + multicity,
        success: function(data) {
            callrunning = false;

            if (timeCount >= 9 && data[0] != 'onprocess') // after 2 * 9 seconds hide the dialog
                $("#loading-model").modal('hide');
            else
                timeCount = parseInt(timeCount) + 1;

            if (timecompleted && data[1] != 'completed')
                isprocess();

            if (data[1] == 'key_expired') {
                clearInterval(refreshIntervalId);
                $('changebtnid').click();

                setSearchData();
            }

            if (data[1] == 'completed' || dataCheckCount > 60) {
                clearInterval(refreshIntervalId);
                redirecttosearchpage('complete');
                get_post_search_data();
                getflexData();
            } else if (data[0] != 'onprocess' && dataCheckCount % 3 == 0) {
                redirecttosearchpage('onprocess');
            }

            dataCheckCount++;
        },
    });
}

$('#subscribe').click(function() {
    var is_checked = '';
    var subscription_email = $('#subscription_email').val();
    if (subscription_email != '') {
        if ($('#pexdeals').is(':checked')) {
            $.ajax({
                type: "POST",
                dataType: "text",
                url: "/mailchimp/",
                data: "email=" + encodeURI(subscription_email) + "&csrfmiddlewaretoken=" + csrf_token,
                success: function(resp) {
                    $('#subs_msg').empty();
                    $('#subs_msg').append(resp);
                    setTimeout(function() {
                        $('#subs_msg').fadeOut();
                    }, 8000);
                }
            });
        } else {
            alert("please click on news and deals from PEX+");
        }
    } else {
        alert("please enter your valid email");
    }
});

var CSRF_TOKEN = csrf_token;
var triptype = '';
var destinationid = '';
var sourceid = '';
var returndateval = '';
var departdateval = '';
var rdtrip = '';
var trip = '';
var cabintypeval = '';
var searchidval = '';
var returnidval = '';
$("#changebtnid").click(function(event) {
    //event.preventDefault();
    return setSearchData();
});

function setSearchData() {
    event.preventDefault();
    var appendErrorLabel = '<label id="from-error" class="error" for="from">Please enter a valid airport</label>';
    if ($('#from').val().trim() == '') {
        $('#from').css('border-color', 'red');
        $('label[class=error]').remove();
        $('#from').after(appendErrorLabel);
        event.preventDefault();
        return false;
    }

    if ($('#to').val().trim() == '') {
        $('label[class=error]').remove();
        $('#to').after(appendErrorLabel);
        $('#to').css('border-color', 'red');
        event.preventDefault();
        return false;
    }
    if ($('#to').val().trim() == $('#from').val().trim()) {
        $('label[class=error]').remove();
        $('#to').after('<label id="from-error" class="error" for="from">From and To city cannot be same</label>');
        $('#to').css('border-color', 'red');
        event.preventDefault();
        return false;
    }

    sourceid = $('#from').val();
    destinationid = $('#to').val();
    var isReturndate = '';
    isReturndate = returndate_;
    if (isReturndate != '') {
        returndateval = $('#return').val();
    }
    departdateval = $('#departuredate').val();
    cabintypeval = $('#cabintype option:selected').val();
    searchData();
    return false;
}

function searchData() {
    $('#changebtnid').prop('disabled', true);
    $("#content1").empty();
    var searchtype = searchtype_;

    $.ajax({
        type: "POST",
        url: "/search/",
        data: "returndate=" + encodeURI(returndateval) + "&searchtype=" + encodeURI(searchtype) + "&rndtripkey=" + encodeURI(rdtrip) + "&cabin=" + encodeURI(cabintypeval) + "&triptype=" + encodeURI(trip) + "&fromMain=" + encodeURI(sourceid) + "&toMain=" + encodeURI(destinationid) + "&deptdate=" + encodeURI(departdateval) + "&csrfmiddlewaretoken=" + encodeURI(CSRF_TOKEN),
        success: function(data) {
            searchtype = data['searchtype'];
            multikey = data['departkey']; //data[0];
            searchid1 = multikey.split(',');
            searchid = searchid1[0];
            var returnid = '';

            if (data['returnkey']) {
                returnid = data['returnkey'];
            }
            getsearchresult(searchid, returnid, searchtype);
            //getsearchresult(searchidval, returnidval);
            //refreshIntervalId = setInterval(datacheck, 5000,searchid,returnid);
        },
        error: function(ret) {
            msg = 'You reached the daily flight search limit!';
            if (ret.responseText == "2") {
                msg += '\nPlease sign up and get more access!';
                var r = confirm(msg);
                if (r == true)
                    $('#login-modal').modal();
            } else if (ret.responseText == "1") {
                alert(msg);
            } else if (ret.responseText == "3") {
                alert('You reached the flight search limit!\nPlease purchase more!');
            } else if (ret.responseText == "11") {
                alert('There is no such airport for origin or destination!\n Please check again!');
                $('#changebtnid').prop('disabled', false);
            }

            return false;
        }
    });
}

function getsearchresult(searchidval, returnidval, searchtype) {
    multicity = '';
    if (multikey.indexOf(",") >= 0) {
        multicity = "&multicity=" + encodeURI(multikey);
    }
    if (searchidval != '') {
        $('#searchid').val(searchid);
        var location = "getsearchresult?keyid=" + encodeURI(searchidval) + "&cabin=" + encodeURI(cabintypeval) + "&passenger=" + encodeURI($('#passenger').val()) + multicity;
        if (returnidval != '') {
            location = location + "&returnkey=" + encodeURI(returnidval);
        }
        location = location + "&searchtype=" + encodeURI(searchtype);
        window.location.href = location;
    }
}

function filter_aircraft_dropdown(this_) {
    var stat = $(this_).prop('src');
    if (stat.includes('caret.png')) {
        $(this_).prop('src', '/static/hotelsearch/css/images/caret_up.png');
        $(this_).parent().parent().children('.filter-aircraft-body').show();
    } else {
        $(this_).prop('src', '/static/hotelsearch/css/images/caret.png');
        $(this_).parent().parent().children('.filter-aircraft-body').hide();
    }
}

function filter_aircraft_check(this_) {
    var checked = $(this_).prop('checked');
    console.log(checked);
    $(this_).parent().parent().parent().children('.filter-aircraft-body').each(function() {
        $(this).children('input').prop('checked', checked);
    });
}
