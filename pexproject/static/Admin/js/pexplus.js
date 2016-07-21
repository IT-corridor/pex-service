$(function() {
    $('#id_price_history_from').datetimepicker({
        viewMode: 'years',
        format: "YYYY-MM-DD",
        minDate: 0,
    });

    $('#id_price_history_to').datetimepicker({
        viewMode: 'years',
        format: "YYYY-MM-DD",
        useCurrent: false
    });    

    $("#id_price_history_from").on("dp.change", function (e) {
        $('#id_price_history_to').data("DateTimePicker").minDate(e.date);
        $('#id_price_history_to').focus();
        price_history();
    });
    $("#id_price_history_to").on("dp.change", function (e) {
        $('#id_price_history_from').data("DateTimePicker").maxDate(e.date);
        price_history();
    });    
});

update_pop_search = function() {
    var period = $('#id_pop_search_period').val();

    $('.page-loader').show();    

    $.post('/stats/popular_search/', 
        {'period':period}
    ).success(function(data) {
        pop_searches = JSON.parse(data);
        var result = '';
        for(idx in pop_searches) {
            var rank = idx*1 + 1;
            result += '<tr><td>'+rank+'</td><td>'+pop_searches[idx].source+'</td><td>'+pop_searches[idx].destination+'</td><td>'+pop_searches[idx].dcount+'</td></tr>';
        }
        $('#id_pop_search_table_body').html(result);
        $('.page-loader').fadeOut();
    });
}
