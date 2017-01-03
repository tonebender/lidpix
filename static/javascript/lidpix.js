$(document).ready(function() {
    
    $('#dir_dropdown_btn').click(function() {
        $('#directory_form').fadeToggle('fast');
    });
    
    $('#gridbutton1').click(function() {
        $('ul.rig').removeClass('columns-4 columns-10');
        $('ul.rig').addClass('columns-1');
    });
    $('#gridbutton4').click(function() {
        $('ul.rig').removeClass('columns-1 columns-10');
        $('ul.rig').addClass('columns-4');
    });
    $('#gridbutton10').click(function() {
        $('ul.rig').removeClass('columns-1 columns-4');
        $('ul.rig').addClass('columns-10');
    });
});
