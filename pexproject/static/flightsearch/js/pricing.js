$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();   
    
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

    $('#id_queries').change(function() {
        set_enable_acct_alaska();
    });

    $('.cycle_option input').click(function() {
        set_enable_acct_alaska();
    });
});    

function set_enable_acct_alaska() {
    var option = $('input[name=cycle]:checked').val();
    var num_queries = $('#id_queries').val() * 1;

    if (option == 'O' && num_queries >= 3500 || option == 'M' && num_queries >= 1250 || option == 'Y' && num_queries >= 1000 ) {
        // console.log(option);
        $('#id_acct_alaska').attr('disabled', false);
    } else {
        $('#id_acct_alaska').attr('disabled', true);
    }
}