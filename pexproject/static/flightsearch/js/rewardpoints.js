var selected_account_id;

$(function() {
    $('#departMain').datepicker({
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
            }
            filter_history();
        }
    });
    $('#returnMain').datepicker({
        onSelect: function() {
            $('#returnMain').css('border-color', '');           
        },
        onClose: function(selectedDate) {
            filter_history();   
        }
    });
})

function choose_kind(this_) {
	var kind = $(this_).val();

    $.ajax({
        url: '/choose_kind?kind='+kind,
        type: 'GET',
        success: function(html) {
            $("#wallet_table").html(html);
        }
    });	
}

function modify_reward_page_config() {
    $('#config-reward-page-pannel').removeClass('in');
    var config = $('#config-reward-page-form').serialize();
    $.ajax({
        url: '/modify_config?'+config,
        type: 'GET',
        success: function(html) {
            alert('Successfully modified!');
        }
    }); 
}

function filter_history() {
    $.ajax({
        url: '/get_history?accountId='+selected_account_id+'&from='+$('#departMain').val()+'&to='+$('#returnMain').val(),
        type: 'GET',
        success: function(html) {
            $('#history_content').html(html);
        }
    });     
}

function show_history(accountId) {
    $('#departMain').val('');
    $('#returnMain').val('');
    selected_account_id = accountId;

    $.ajax({
        url: '/get_history?accountId='+accountId,
        type: 'GET',
        success: function(html) {
            $('#history_content').html(html);
            $('#history_dialog').modal();
        }
    });     
}