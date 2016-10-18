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