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
    $('#fa_passenger').val("1");
    //$(':input').not(':button, :submit, :reset, :hidden, :checkbox, :radio').val('');
    //$(':checkbox, :radio').prop('checked', false);
    $("#returndatediv").show();
    $('#fa_save_button').text('Save');
    fa_travelinfo();
});

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
        $('#fa_passenger').val(data['traveller']);
        $('#fa_adults').val(data['traveller']);
        fa_total = data['traveller'];
        $('#fa_cabintype').val(data['cabin']);

        if (data['annual_repeat'] == 'True') {
            $('#annual_repeat').prop('checked', true);
        }
        fa_travelinfo();
        $('#fa_save_button').text('Update');
    });

});
