$(document).ready(function() {

    var base_url = 'http://localhost:5080';
    var serveimage_url = base_url + '/serveimage?image=';
    var thumbs_dir = '/.lidpixthumbs/';
    
    /**
     * Get the value of the URL parameter 'name'
     * 
     * @param name The name of the parameter
     */
    $.urlParam = function(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null) {
           return null;
        }
        else {
           return results[1] || 0;
        }
    }
    
              
    /**
     * Return a Font Awesome css class definition depending on what filetype is.
     * 
     * @param filetype A string containing e.g. 'jpg'
     */
    function fa_icon(filetype) {
        var ft = filetype.toLowerCase();
        if (ft == 'dir')
            return 'fa fa-folder-o';
        else if (ft == 'mnt')
            return 'fa fa-hdd-o';
        else if ('jpeg jpg gif gifv png tiff bmp xcf psd pcx'.indexOf(ft) > -1)
            return 'fa fa-file-image-o';
        else if ('mov avi mpg mpeg mp4 flv wmv mkv ogv vob dv'.indexOf(ft) > -1)
            return 'fa fa-file-video-o';
        else if ('mp3 ogg flac wma wav sid mod xm aiff ra ram rm mid midi m4a shn ape'.indexOf(ft) > -1)
            return 'fa fa-file-audio-o';
        else if ('pdf'.indexOf(ft) > -1)
            return 'fa fa-file-pdf-o';
        else if ('zip tar gz tgz tbz2 bz2 lhz arj xz 7z iso sit sitx lz sz z rar sfark'.indexOf(ft) > -1)
            return 'fa fa-file-archive-o';
        else if ('txt text tex doc docx odt sxw xls xlsx ods rtf rtfd mdb accdb ppt pptx'.indexOf(ft) > -1)
            return 'fa fa-file-text-o';
        else
            return 'fa fa-file-o';
    }
    
    
    /**
     * Get thumbnails for the images in imagedir and add them to the page
     * 
     * @param imagedir (string) The path for the files
     * @param showthumbs Whether to show thumbnails or just icons for images
     */
    function load_thumbs(imagedir, showthumbs) {
        
        $('#status_field').html('Loading directory ...');
    
        $.getJSON({
            type: 'GET',
            url: 'http://localhost:5080/supplythumbs',
            data: 'imagedir=' + imagedir,
            success:function(feed) {
                var address = '';
                feed.forEach(function(entry) {  // Put thumbs on page
                    address = serveimage_url + imagedir + '/' + entry.name;
                    if (entry.thumb) { // Thumb exists
                        $('#thumbs_area').append(
                            '<li>' +
                                '<a href="' + address + '">' +
                                    '<img src="' + 
                                        serveimage_url + imagedir +
                                        thumbs_dir + entry.name +
                                    '">' +
                                    '<p>' + entry.name + '</p>' +
                                    '<p>' + entry.datetime + '</p>' + 
                                '</a>' +
                            '</li>'
                        );
                    } else { // Thumb does not exist - use icon
                        if (entry.filetype == 'DIR') {
                            address = base_url + '/folderjs?imagedir=' +
                                      imagedir + '/' + entry.name;
                        }
                        $('#thumbs_area').append(
                            '<li class="icon">' +
                                '<a href="' + address + '">' +
                                    '<div>' +
                                        '<span class="' + fa_icon(entry.filetype) +
                                        '"></span>' +
                                    '</div>' +
                                    '<p>' + entry.name + '</p>' +
                                '</a>' +
                            '</li>'
                        );
                    }
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
    $('.gb').click(function() {
        $('.gb').removeClass('grid_btn_selected');
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
