$(document).ready(function() {
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
