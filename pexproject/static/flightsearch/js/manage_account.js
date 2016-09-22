$(document).ready(function() {
    var message = request_status_;
    if (message != '') {
        alert(message);
    }

    $('.edit').hide();

});
$('#prefrence').click(function() {
    $('#edit_prefrenceinfo').show();
    $('#prefrenceinfo').hide();

});
$('#accountinfo').click(function() {
    $('#edit_infodiv').show();
    $('#infodiv').hide();

});
$('.cancel_info').click(function() {
    location.reload();
    //$('#edit_infodiv').hide();
    //$('#infodiv').show();

});
$('.cancel_preference').click(function() {
    location.reload();
    //$('#edit_prefrenceinfo').hide();
    //$('#prefrenceinfo').show();

});
$('.mailchimp').click(function() {
    var user_email = user_email_;
    var fname = user_first_name_;
    var lname = user_last_name_;

    $.ajax({
        type: "POST",
        dataType: "text",
        url: "mailchimp",
        data: "&csrfmiddlewaretoken=" + csrf_token + "&email=" + encodeURI(user_email) + "&fname=" + encodeURI(fname) + "&lname=" + encodeURI(lname),
        success: function(data) {
            console.log(data);
            $("#hello1").addClass("alert-warning");
            $("#hello1").empty();
            $("#hello1").append(data);
            setTimeout(function() {
                $('#hello1').fadeOut();
            }, 8000);
        }
    });

});
$('#password_change').click(function() {
    var user_email = user_email_;
    //$(".password_block").show();
    $.ajax({
        type: "POST",
        dataType: "text",
        url: "forgotPassword",
        data: "&csrfmiddlewaretoken="+csrf_token + "&email=" + encodeURI(user_email),
        success: function(data) {
            console.log(data);
            $("#hello").addClass("alert-success");
            $("#hello").empty();
            $("#hello").append(data);
            setTimeout(function() {
                $('#hello').fadeOut();
            }, 5000);
        }
    });
});
$('.saveinfo').click(function() {
    if ($('.password_block').is(':hidden')) {
        $('.pass').prop("disabled", true);
        //$('#confirm_password').prop("disabled", true);
    }
});

$('#dob').datepicker({
    dateFormat: 'yy-mm-dd',
    changeYear: true,
    yearRange: "1930:2030"
});
$("#airport").autocomplete({
    open: function(event, ui) {
        $('.ui-autocomplete').off('menufocus hover mouseover');
    },
    autoFocus: true,
    source: "/get_airport/",
    minLength: 2,
    //appendTo:".modelform",

});

$("#id_country").autocomplete({
    open: function(event, ui) {
        $('.ui-autocomplete').off('menufocus hover mouseover');
    },
    autoFocus: true,
    source: "/get_countryname/",
    minLength: 2,
});
