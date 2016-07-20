update_pop_search = function(obj) {
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