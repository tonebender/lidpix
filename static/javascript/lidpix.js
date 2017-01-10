$(document).ready(function() {
    
    // When the folder button next to 'Lidpix' is clicked, show the directory 
    // field and change the folder button itself
    $('#folder_button').click(function() {
        if ( $('#dir_field').css('visibility') == 'hidden' )
            $('#dir_field').css('visibility','visible');
        else
            $('#dir_field').css('visibility','hidden');
        $('#folder_icon').toggleClass('fa-folder-open-o');
        $('#folder_icon').toggleClass('fa-folder-o');
    });
    
    // Buttons for choosing the grid format of the thumbnails
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
    
    
    $.urlParam = function(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null) {
           return null;
        }
        else {
           return results[1] || 0;
        }
    }
    
    
    var imagedir = $.urlParam('imagedir');
    
    // When user clicks "Load images", get the thumbs urls (as json)
    $('#loadimages').click(function() {
        load_thumbs(imagedir);
    });
    
    

});

function load_thumbs(imagedir) {
    // Show progress message
    $('#loadimages').html('Loading images ...');
    console.log(imagedir);

    $.ajax({
        type: 'GET',
        url: 'http://localhost:5080/supplythumbs',
        data: 'imagedir=' + imagedir,
        success:function(feed) {
            console.log(feed);
            $('#testdiv').html('BLA');
        },
        dataType: 'json'
    });
}


/*
    function resizeInput() {
        $(this).attr('size', $(this).val().length);
    }

    // The directory text input changes width according to content
    $('#directory_form > input[type="text"]')
        // event handler
        .keyup(resizeInput)
        // resize on page load
        .each(resizeInput);
*/
