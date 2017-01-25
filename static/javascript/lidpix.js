$(document).ready(function() {

    var base_url = 'http://localhost:5080';
    var serveimage_url = base_url + '/serveimage?image=';
    var thumbs_dir = '/.lidpixthumbs/';
    
    $.urlParam = function(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null) {
           return null;
        }
        else {
           return results[1] || 0;
        }
    }
    
    function load_thumbs(imagedir, showthumbs) {
        
        /* Get thumbnails for the images in imagedir and add them to the page */
        
        $('#status_field').html('Loading directory ...');
    
        $.getJSON({
            type: 'GET',
            url: 'http://localhost:5080/supplythumbs',
            data: 'imagedir=' + imagedir,
            success:function(feed) {
                feed.forEach(function(entry) {  // Put thumbs on page
                    $('#thumbs_area').append(
                        '<a href="' + serveimage_url +
                            imagedir + entry.name + '">' +
                        '<li>' +
                            '<img src="' + serveimage_url + imagedir +
                                thumbs_dir + entry.name +
                            '">' +
                            '<p>' + entry.name + '</p>' +
                            '<p>' + entry.datetime + '</p>' +
                        '</li>'
                    );
                });
                $('#status_field').html(''); // Remove "loading" message
            },
        });
    }

    // When the folder button right of 'Lidpix' is clicked, show the directory 
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
    $('#grid_buttons a').click(function() {
        $('#grid_buttons a').removeClass('grid_btn_selected');
        $('ul.rig').removeClass('columns-1 columns-4 columns-10');
    });
    $('#gridbutton1').click(function() {
        $('#gridbutton1').addClass('grid_btn_selected');
        $('ul.rig').addClass('columns-1');
    });
    $('#gridbutton4').click(function() {
        $('#gridbutton4').addClass('grid_btn_selected');
        $('ul.rig').addClass('columns-4');
    });
    $('#gridbutton10').click(function() {
        $('#gridbutton10').addClass('grid_btn_selected');
        $('ul.rig').addClass('columns-10');
    });
    
    
    var imagedir = $.urlParam('imagedir');
    var showthumbs = $.urlParam('showthumbs');
    
    load_thumbs(imagedir, showthumbs);
    
});


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
