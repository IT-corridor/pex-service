$(document).ready(function() {
    $('[type=submit]').attr('disabled', true);
    $('#id_term').prop('checked', false);

    $('#id_term').change(function() {
        // console.log($('#id_term').prop('checked'));
        $('[type=submit]').attr('disabled', !$('#id_term').prop('checked'));        
    });

    $('[submit=submit]').click(function(e) {
        var num_queries = $('#id_queries').val();

        if (num_queries < 50) {
            e.preventDefault();
            alert('Please specify valid number of searches over 50!');
            $('#id_queries').focus();
        }
    });
});    
