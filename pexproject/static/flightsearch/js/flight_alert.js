$('.delete_button').click(function(e) {
    e.preventDefault();
    var link = $(this).attr('href');
    bootbox.confirm("Are you sure you want to delete this FLight Price Alerts?", function(result) {
        if (result == true) {
            document.location.href = link;
        }
    });
});

$('#flight_alert_link').click(function() {
    $('.modelform').trigger("reset");
    $('#passenger').val("1");
    //$(':input').not(':button, :submit, :reset, :hidden, :checkbox, :radio').val('');
    //$(':checkbox, :radio').prop('checked', false);
    $("#returndatediv").show();
    $('#save_button').text('Save');
    travelinfo();
});

$("#oneWay").click(function() {
    if ($("#oneWay").prop('checked') == true) {
        $("#returndatediv").hide();
        $('#alt_return').val('');
    } else {

        $("#returndatediv").show();
    }

});

$("#roundTrip").click(function() {
    if ($("#roundTrip").prop('checked') == true) {
        $("#returndatediv").show();
    } else {
        $("#returndatediv").hide();
        $('#alt_return').val('');
    }

});

$(function() {
    $("#alt_from").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
            $('#alt_fromid').val('');
        },
        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
        // appendTo: ".modelform",
        select: function(event, ui) {
            $('#alt_fromid').val(ui.item.id);
        },
    });

    $("#alt_to").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
            $('label[class=error]').remove();
            $('#alt_to').css('border-color', '');
            $('#alt_toid').val('');
        },

        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
        appendTo: ".modelform",
        select: function(event, ui) {
            $('#alt_toid').val(ui.item.id);
        },
    });
});


$(function() {

    $('#alt_depart').datepicker({
            dateFormat: 'yy-mm-dd',
            minDate: 0,
            onSelect: function() {
                setTimeout(function function_name(argument) {
                    $('#alt_return').focus();
                }, 200);

            },
            onClose: function(selectedDate) {
                // Set the minDate of 'to' as the selectedDate of 'from'
                if (selectedDate != '') {
                    $("#alt_return").datepicker("option", "minDate", selectedDate);
                    $("#alt_expire").datepicker("option", "maxDate", selectedDate, "minDate", 0);
                } else {
                    $("#alt_return").datepicker("option", "minDate", 0);
                    $("#alt_expire").datepicker("option", "minDate", 0);
                }

            }
        }

    );
    $('#alt_return').datepicker({
        dateFormat: 'yy-mm-dd',
        minDate: 0,
    });
    $('#alt_expire').datepicker({
        minDate: 0,
        dateFormat: 'yy-mm-dd',
    });
});

var total;
$('.action').click(function() {
    var recordid = $(this).attr('id');

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/flightAlert/",
        data: {
            "alertid": recordid,
            "csrfmiddlewaretoken": csrf_token
        }
    }).done(function(data) {
        $('#flight-model-alert').modal('show');
        if (data['returndate'] != 'None') {
            $('#roundTrip').prop('checked', true);
            $("#returndatediv").show();
            $("#alt_return").val(data['returndate']);
        } else {
            $('#oneWay').prop('checked', true);
            $("#returndatediv").hide();
            $('#alt_return').val('');
        }
        $('#alt_from').val(data['from_airport']);
        $('#alt_to').val(data['to_airport']);
        $('#alt_toid').val(data['destination_airportid']);
        $('#alt_fromid').val(data['source_airportid']);
        $('#alt_depart').val(data['departdate']);
        $('#price_mile').val(data['maxprice']);
        $('#alertid').val(data['alertid']);
        $('#passenger').val(data['traveller']);
        $('#adults').val(data['traveller']);
        total = data['traveller'];
        $('#cabintype').val(data['cabin']);

        if (data['annual_repeat'] == 'True') {
            $('#annual_repeat').prop('checked', true);
        }
        travelinfo();
        $('#save_button').text('Update');
    });

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

$(document).ready(function() {
    $('#passenger').val('1');
    $(".alert-warning").hide();
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
