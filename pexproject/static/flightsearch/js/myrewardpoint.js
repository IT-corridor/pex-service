$('#sync_all_points').click(function() {
    $('#point-loading-model').modal('show');
});
$('#syncform').submit(function() {
    $('#point-loading-model').modal('show');
    $('#syncdata').prop('disabled', true);
});
$(document).ready(function() {
    var action = '';
    var update_action = '';
    update_action = updatemsg;
    action = temp_message;
    if (action == '') {
        $('#addaccount').hide();

    }
    if (update_action == '' || update_action.indexOf("successfully") >= 0) {
        $('#upaccount').hide();
    }

});
$('#add_account').click(function() {
    $('#action').val('add');
    $('#addaccount').show();
    $('#dropdown').show();
    $(this).hide();
});
$(".cancel").click(function() {
    $('#addaccount').hide();
    $('#add_account').show();
    $('#upaccount').hide();
    $('#up_account').show();
});
$('#up_account').click(function() {
    $('#upaccount').show();
    $('#up_account').hide();
});

$('.update').click(function() {
    var html = '';
    var id = ($(this).attr('id'));
    $('#action').val('update');
    var exist = '';
    $('#airline_Select  option').each(function() {
        if (this.value == id) {
            exist = 'true';
        }
    });
    if (exist == '') {
        $('#airline_Select').append('<option value="' + id + '" selected>' + id + '</option>');
    } else {
        $('#airline_Select>option:eq(' + id + ')').attr('selected', true);
    }
    $('#addaccount').show();
});

$('.deactivate').click(function() {
    var airline = $(this).attr('id');
    airlines = airline.split('_');


    var r = confirm("Are You sure, you want to deactivate your account!");
    if (r == true) {
        $("#" + airlines[0] + "_div").hide();
        //$("#"+airline).parent('.rewardpoint').hide();
        $.ajax({
            type: "POST",
            dataType: "text",
            url: "/myRewardPoint/",
            data: "act=" + encodeURI("deactive") + "&csrfmiddlewaretoken=" + encodeURI(csrf_token) + "&acct=" + encodeURI(airlines[0])
        }).done(function(data) {
            $("#" + airlines[0] + "_div").remove();
            $('#airline_Select').append($('<option>', {
                value: airlines[0],
                text: airlines[0]
            }));
        });

    }
});