$('#mc').click(function() {
    var location = "flights?action=mc";
    window.location.href = location;
});

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

$('#apply_traveler').click(function() {
    $(".travelers-holder").removeClass('open');
});

$(document).ready(function() {
    if ($("#ow").prop('checked') == true) {
        $("#return").hide();

    } else {
        $("#return").show();
    }
    if ($("#rt").prop('checked') == true) {
        $("#return").show();
    }
});
$("#ow").click(function() {
    if ($("#ow").prop('checked') == true) {
        $("#return").hide();
        $('.mobile-wt').removeClass('col-xs-6 xs-pr5');
        $('.mobile-wt').addClass('col-xs-12');
        $('#rmv_nomr').removeClass('nomr');

    } else {

        $("#return").show();
    }

});
$("#rt").click(function() {
    if ($("#rt").prop('checked') == true) {
        $("#return").show();
        $('.mobile-wt').removeClass('col-xs-12');
        $('.mobile-wt').addClass('col-xs-6 xs-pr5');
        $('#rmv_nomr').addClass('nomr');
    } else {
        $("#return").hide();
    }

});

$(function() {
    $("#from").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
            $('label[class=error]').remove();
            $('#from').css('border-color', '');
            $('#fromid').val('');
        },

        autoFocus: true,
        source: "/get_airport/",
        minLength: 1,
        select: function(event, ui) {
            $('#fromid').val(ui.item.id);
        },
    });
    $("#to").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
            $('label[id=from-error]').remove();
            $('#to').css('border-color', '');
            $('#toid').val('');
        },

        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
        select: function(event, ui) {
            $('#toid').val(ui.item.id);
        },
    });

    $('#departMain').datepicker({

        minDate: 0,
        onSelect: function() {
            setTimeout(function function_name(argument) {
                $('#returnMain').focus();
                $('#departMain').css('border-color', '');
            }, 200);

        },
        onClose: function(selectedDate) {
            // Set the minDate of 'to' as the selectedDate of 'from'
            if (selectedDate != '') {
                $("#returnMain").datepicker("option", "minDate", selectedDate);
            } else {
                $("#returnMain").datepicker("option", "minDate", 0);
            }

        }
    });
    $('#returnMain').datepicker({
        minDate: 0,
        onSelect: function() {
            $('#returnMain').css('border-color', '');           
        },

    });
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

    // load destination tiles
    // if ($('#add-section').length > 0 ) {
    //     $.ajax({
    //         type: "POST",
    //         url: "/destination_tiles",
    //         data: "",
    //         success: function(data) {
    //             $('#add-section').html(data);
    //         },
    //     });
    // }
});

$('#cabintype').on('change', function() {
    travelinfo();
});

$(document).ready(function() {
    $('#passenger').val('1');
    $(".alert-warning").hide();

    if ($(window).width() > 768)
        $('#exactDate1').attr("checked", "checked");
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


var CSRF_TOKEN = csrf_token;
var triptype = '';
var destinationid = '';
var sourceid = '';
var returndateval = '';
var departdateval = '';
var rdtrip = '';
var trip = '';
var cabintypeval = '';
var searchid = '';
var returnid = '';
var searchtype = '';

$("#submitid").click(function(event) {
    if ( $('#pre_search').css('display') != 'none' ) {
        return false;
    }

    triptype = $("input[type='radio'][name='trip']:checked");
    searchtype = $("input[type='radio'][name='searchtype']:checked").val();
    var current_date = $.datepicker.formatDate('mm/dd/yy', new Date());
    if (triptype.length > 0) {
        triptypeval = triptype.val();
    }
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

    if ($('#departMain').val().length < 1) {
        $('#departMain').focus();
        $('#departMain').css('border-color', 'red');
        event.preventDefault();
        return false;
    }
    if ('roundTripBtn' == triptypeval) {
        if ($('#returnMain').val().length < 1) {
            $('#returnMain').focus();
            $('#returnMain').css('border-color', 'red');
            event.preventDefault();
            return false;
        }
    } else {
        $('#returnMain').val('');
    }
    sourceid = $('#from').val();
    destinationid = $('#to').val();
    returndateval = $('#returnMain').val();
    departdateval = $('#departMain').val();
    cabintypeval = $('#cabintype option:selected').val();

    searchData();
    return false ;
});

function searchData() {
    $('#pre_search').show();
    // $('#submitid').prop('disabled', true);
    if ($("#content1").length > 0)
        $("#content1").empty();

    $.ajax({
        type: "POST",
        url: "/search/",
        data: "returndate=" + encodeURI(returndateval) + "&searchtype=" + encodeURI(searchtype) + "&rndtripkey=" + encodeURI(rdtrip) + "&cabin=" + encodeURI(cabintypeval) + "&triptype=" + encodeURI(trip) + "&fromMain=" + encodeURI(sourceid) + "&toMain=" + encodeURI(destinationid) + "&deptdate=" + encodeURI(departdateval) + "&csrfmiddlewaretoken=" + encodeURI(CSRF_TOKEN),
        success: function (data) {
            searchtype = data['searchtype'];
            multikey = data['departkey']; //data[0];
            searchid1 = multikey.split(',');
            searchid = searchid1[0];
            var returnid = '';

            if (data['returnkey']) {
                returnid = data['returnkey'];
            }

            redirecttosearchpage(searchid, returnid, searchtype);
            //refreshIntervalId = setInterval(datacheck, 5000,searchid,returnid);
        },
        error: function (ret) {
            $('#pre_search').hide();
            msg = 'You reached the daily flight search limit!';
            if (ret.responseText == "2") {                  
                msg += '\nPlease sign up and get more access!';
                var r = confirm(msg);
                if (r == true) 
                    $('#login-modal').modal();
            } else if (ret.responseText == "1") {
                alert(msg);
            } else if (ret.responseText  ==  "3") {
                alert('You reached the flight search limit!\nPlease purchase more!');
            } else if (ret.responseText  ==  "11") {
                alert('There is no such airport for origin or destination!\n Please check again!');
                $('#submitid').prop('disabled', false);
            }

            return false;
        }
    });
}

function redirecttosearchpage(searchid, returnkey, searchtype) {
    multicity = '';
    if (multikey.indexOf(",") >= 0) {
        multicity = "&multicity=" + encodeURI(multikey);
    }
    if (searchid != '') {
        $('#searchid').val(searchid);
        var location = "/getsearchresult?keyid=" + encodeURI(searchid) + "&cabin=" + encodeURI(cabintypeval) + "&passenger=" + encodeURI($('#passenger').val()) + multicity;
        if (returnkey != '') {
            location = location + "&returnkey=" + encodeURI(returnkey);
        }
        location = location + "&searchtype=" + encodeURI(searchtype);
        window.location.href = location;
    }
}
