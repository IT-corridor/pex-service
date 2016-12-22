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
    /* ----------------------- */

});

/* for flight alert dialog */
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
