$(document).ready(function() {
    $('#textarea').hide();
    var option1 = "";
    var option2 = "<p><b></b>Note you may have booked on another site</p><p>It's possible that you may have searched on PEX+ but booked through another provider. Check your email inbox for your booking receipt. If you completed the booking on another site, contact the provider. You can also find the provider by checking your credit card statement.</p><p>If you did complete your booking through PEX+, you can look-up your booking online by confirmation number or email address.</p>";
    var option3 = "<p>We could not find any recent fares from your click history.  Please provide details in the 'Comment' field below.</p>";
    var option4 = "<p>Everything you need to know to get started and/or enhance your hotel's listing in PEX+. You can update your hotel's information, learn how to get listed in PEX+ core results, or advertise your hotel as a featured result.</p>";
    var option5 = "";
    $('#feedback_option').change(function() {
        $('#textarea').empty();
        $('#textarea').hide();
        var val = $(this).children(":selected").attr("id");
        if (val == 2) {
            $('#text').val(option2);
            $('#textarea').append(option2);
            $('#message').hide();
            $('#textarea').show();
        }
        if (val == 1) {
            $('#message').show();
            $('#textarea').hide();
        }
        if (val == 4) {
            $('#text').val(option4);
            $('#textarea').append(option4);
            $('#message').hide();
            $('#textarea').show();
        }
        if (val == 3) {
            $('#text').val(option3);
            $('#textarea').append(option3);
            $('#message').show();
            $('#textarea').show();
        }
    });
});