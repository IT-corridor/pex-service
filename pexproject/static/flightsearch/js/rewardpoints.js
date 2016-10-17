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