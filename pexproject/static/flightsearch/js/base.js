$(function(){
    if (lmsg != '')
    {
        $('#login-modal').modal('show');
        activeLogin();
    }
    if (smsg != '')
    {
        $('#login-modal').modal('show');
        activeSignup(); 
    }
    if(resetpassword != '') {
        $('#forgetpassword').modal('show');
        resetpassword='';
    }
    if(welcome_msg != ''){
        $('#forgetpassword').modal('show');
        $('#forgot_password_form').hide();

        // prepopulate results
        if (welcome_msg.indexOf('registered') != -1) {
            if (typeof get_full_path_ === 'undefined') {
                console.log('Not in flight search page');
            } else {
                $('#alt_from').val($('#from').val());
                $('#alt_to').val($('#to').val());
                $('#alt_fromid').val($('#fromid').val());
                $('#alt_toid').val($('#toid').val());
                $('#alt_depart').val(reformat_date($('#departuredate').val()));

                if (request_returnkey != '') {
                    $("#returndatediv").show();
                    $('#alt_return').val(reformat_date($('#return').val()));
                    $('#roundTrip').attr('checked', 'checked');
                } else {
                    $('#oneWay').attr('checked', 'checked');
                    $("#returndatediv").hide();
                }

                $('#flight-model-alert').modal();                
            }
        }

        setTimeout(function() {$('#forgetpassword').modal('hide');}, 5000);
    }

    /* for flight alert dialog */
    $("#alt_from").autocomplete({
        open: function(event, ui) {
            $('.ui-autocomplete').off('menufocus hover mouseover');
            $('#alt_fromid').val('');
        },
        autoFocus: true,
        source: "/get_airport/",
        minLength: 2,
        appendTo: ".modelform",
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
                } else {
                    $("#alt_return").datepicker("option", "minDate", 0);
                }
            }
        }

    );
    $('#alt_return').datepicker({
        dateFormat: 'yy-mm-dd',
        minDate: 0,
    });    

    $('.fa_add').on('click', function() {
        fa_total = fa_total_passenger();
        if (fa_total < 6) {
            var $qty = $(this).closest('p').find('.qty');
            var currentVal = parseInt($qty.val());
            if (!isNaN(currentVal)) {
                $qty.val(currentVal + 1);
            }
            fa_travelinfo();
        }
    });
    $('.fa_minus').on('click', function() {
        fa_total = fa_total_passenger();
        if (fa_total > 0) {
            var $qty = $(this).closest('p').find('.qty');
            var currentVal = parseInt($qty.val());
            if (!isNaN(currentVal) && currentVal > 0) {
                $qty.val(currentVal - 1);
            }

            fa_travelinfo();
        }
    });

    $('#fa_passenger').val('1');
    $(".alert-warning").hide();

    /* ----------------------- */

});

/* for flight alert dialog */
function reformat_date(str_date) {
    var year_ = str_date.substring(6, 10);
    var day_ = str_date.substring(3, 5);
    var month_ = str_date.substring(0, 2);

    return year_+"-"+month_+"-"+day_;
}

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

var fa_total;

$("#fa_cabintab").focus(function() {
    $(".travelers-holder").addClass('open');
    return false;
});
$("#fa_cabintab").click(function() {
    $(".travelers-holder").addClass('open');
    return false;
});

$(".form_val").focus(function() {
    if (!$(this).hasClass("cabin_type")) {
        $(".travelers-holder").removeClass('open');
    }
});

$('#fa_apply_traveler').click(function() {
    $(".travelers-holder").removeClass('open');
});

//@@increase decrease on buttom click
$('#fa_cabintype').on('change', function() {
    fa_travelinfo();
});

//@@@Cabin select@@@@
function fa_travelinfo() {
    fa_total = fa_total_passenger();

    $('#fa_passenger').val(fa_total);
    var text;
    if (fa_total == 1) {
        text = "traveler";
    } else {
        text = "travelers";
    }
    var selectedcabin = $("#fa_cabintype option:selected").text();
    var html = "<span id='fa_travelar'>" + fa_total + " " + text + ", " + selectedcabin + "</span>";
    $('#fa_travelar').replaceWith(html);
    if (fa_total == 0) {
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
function fa_total_passenger() {
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

/* ----------------------- */

$('#forgot_password').click(function(){
    $('#forgetpassword').modal('show');
    $('#login-modal').modal('hide');
});    

$(".signuplogin").click(function(){
    var which_button_is_clicked=$(this).attr('id');
    if($.trim(which_button_is_clicked)=="loginbtn")
        activeLogin();
    else if($.trim(which_button_is_clicked)=="signupbtn")
        activeSignup();
});

function activeLogin() {
    $('#signup').removeClass('active');
    $('#signuptab').removeClass('active');
    $('#login').addClass('active');
    $('#logintab').addClass('active');
}

function activeSignup() {
    $('#login').removeClass('active');
    $('#logintab').removeClass('active');
    $('#signup').addClass('active');
    $('#signuptab').addClass('active');
}   

$( "#home_airpot" ).autocomplete({
    open: function(event, ui) {
        $('.ui-autocomplete').off('menufocus hover mouseover');
    },
    autoFocus: true,
    source: "/get_airport/",
    minLength: 2,
    appendTo:".modelform",
});

 
$(".pexdeal").click(function(e){
    e.preventDefault();
    $link = $(this);
    var pex_option = confirm("Do you want to subscribe, to receive PEX+ amazing deals?");
    
    if (pex_option == true) 
    {   
        $.ajax({
            type: "POST",
            dataType: "text",
            url: "/index/",
            data: "pexdeals=1&csrfmiddlewaretoken="+encodeURI(csrf)
        }).done(function(data) {
            window.location.href = $link.attr('href');
        }) ;            
    } else {
        window.location.href = $link.attr('href');
    }
});
