$('#confirm_password').change(function(e) {
    console.log("test");
    if ($('#confirm_password').val() != $('#newpassword').val()) {
        alert("Password mismatch");
        $('#newpassword').val('');
        $('#confirm_password').val('');
        $('#newpassword').focus();
        e.preventDefault();
    }
});
