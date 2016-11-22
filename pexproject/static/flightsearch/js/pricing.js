$(document).ready(function() {
    $('#id_upgrade_pp').attr('disabled', true);
    $('#id_term').prop('checked', false);

    $('#id_term').change(function() {
        // console.log($('#id_term').prop('checked'));
        $('#id_upgrade_pp').attr('disabled', !$('#id_term').prop('checked'));        
    });

    $('#id_upgrade_pp').click(function(e) {
        var num_queries = $('#id_queries').val();

        if (num_queries < 50) {
            e.preventDefault();
            alert('Please specify valid number of searches over 50!');
            $('#id_queries').focus();
        }
    });
});    
