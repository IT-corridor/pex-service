$(document).ready(function() {
    var max_fields = 6; //maximum input boxes allowed
    var add_button = $(".add_field_button"); //Add button ID
    var x = 1; //initlal text box count
    $(add_button).click(function(e) {

        e.preventDefault();

        if (x < max_fields) { //max input box allowed
            x++; //text box increment
            $('.addmore').append('<div><input type="text" name="mytext[]"/><a href="#" class="remove_field">X</a></div>'); //add input box
        }
    });

    $('.addmore').on("click", ".remove_field", function(e) { //user click on remove text
        e.preventDefault();
        $(this).parent('div').remove();
        x--;
    });
});
