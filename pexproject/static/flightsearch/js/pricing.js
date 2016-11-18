$(document).ready(function() {
    $('[type=image]').attr('src', '/static/flightsearch/img/paypal.png');
    $('[type=image]').attr('disabled', true);

    $('#id_term').change(function() {
        console.log($('#id_term').prop('checked'));
        $('[type=image]').attr('disabled', !$('#id_term').prop('checked'));        
    });

    $('[name=submit]').click(function(e) {
        var num_queries = $('#id_queries').val();

        if (num_queries >= 50) {
            $('#id_quantity').val(num_queries);
        } else {
            e.preventDefault();
            alert('Please specify valid number of searches over 50!');
            $('#id_queries').focus();
        }
    });
});    
