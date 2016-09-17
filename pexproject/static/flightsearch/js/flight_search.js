function searchData() {
    $('#submitid').prop('disabled', true);
    
    if ($("#content1").length > 0)
        $("#content1").empty();

    $.ajax({
        type: "POST",
        url: "/search/",
        data: "returndate=" + encodeURI(returndateval) + "&searchtype=" + encodeURI(searchtype) + "&rndtripkey=" + encodeURI(rdtrip) + "&cabin=" + encodeURI(cabintypeval) + "&triptype=" + encodeURI(trip) + "&fromMain=" + encodeURI(sourceid) + "&toMain=" + encodeURI(destinationid) + "&deptdate=" + encodeURI(departdateval) + "&csrfmiddlewaretoken=" + encodeURI(CSRF_TOKEN),
        success: function (data) {
            searchtype = data['searchtype'];
            multikey = data['departkey']; //data[0];
            searchid1 = multikey.split(',');
            searchid = searchid1[0];
            var returnid = '';

            if (data['returnkey']) {
                returnid = data['returnkey'];
            }
            redirecttosearchpage(searchid, returnid, searchtype);
            //refreshIntervalId = setInterval(datacheck, 5000,searchid,returnid);
        },
        error: function (ret) {
            msg = 'You reached the daily flight search limit!';
            if (ret.responseText == "2") {                  
                msg += '\nPlease sign up and get more access!';
                var r = confirm(msg);
                if (r == true) 
                    $('#login-modal').modal();
            } else if (ret.responseText == "1") {
                alert(msg);
            } else {
                alert('You reached the flight search limit!\nPlease purchase more!');
            }

            return false;
        }
    });
}

function redirecttosearchpage(searchid, returnkey, searchtype) {
    multicity = '';
    if (multikey.indexOf(",") >= 0) {
        multicity = "&multicity=" + encodeURI(multikey);
    }
    if (searchid != '') {
        $('#searchid').val(searchid);
        var location = "getsearchresult?keyid=" + encodeURI(searchid) + "&cabin=" + encodeURI(cabintypeval) + "&passenger=" + encodeURI($('#passenger').val()) + multicity;
        if (returnkey != '') {
            location = location + "&returnkey=" + encodeURI(returnkey);
        }
        location = location + "&searchtype=" + encodeURI(searchtype);
        window.location.href = location;
    }
}
