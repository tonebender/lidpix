


// Jquery
$(document).ready(function() {

    var base_url = 'http://localhost:5080';
    var serveimage_url = base_url + '/serveimage?image=';
    var servethumb_url = base_url + '/servethumb?image=';
    
    /**
     * Get the value of the URL parameter 'name'
     * 
     * @param name The name of the parameter
     * @param defaultvalue This is returned if no value is found
     */
    $.urlParam = function(name, defaultvalue) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null) {
           return defaultvalue;
        } else {
           return results[1] || 0;
        }
    }
    
    /**
     * Return the width and height of the browser viewport
     */
    function getViewport() {
        
        var viewPortWidth;
        var viewPortHeight;
        
        // The more standards compliant browsers (mozilla/netscape/opera/IE7) 
        // use window.innerWidth and window.innerHeight
        if (typeof window.innerWidth != 'undefined') {
          viewPortWidth = window.innerWidth,
          viewPortHeight = window.innerHeight
        }
        
        // IE6 in standards compliant mode (i.e. with a valid doctype as the 
        // first line in the document)
         else if (typeof document.documentElement != 'undefined'
         && typeof document.documentElement.clientWidth !=
         'undefined' && document.documentElement.clientWidth != 0) {
            viewPortWidth = document.documentElement.clientWidth,
            viewPortHeight = document.documentElement.clientHeight
         }
        
         // older versions of IE
         else {
           viewPortWidth = document.getElementsByTagName('body')[0].clientWidth,
           viewPortHeight = document.getElementsByTagName('body')[0].clientHeight
         }
         return [viewPortWidth, viewPortHeight];
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
        else if (is_image(ft))
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
     * Return true if extension is one of predefined image extensions,
     * otherwise false
     */
    function is_image(extension) {
        return ('jpeg jpg gif gifv png tiff bmp xcf psd pcx'.
                indexOf(extension.toLowerCase()) > -1);
    }
    
    /**
     * Return HTML for a thumbnail, based on a bunch of variables ...
     */
    function render_thumb(imagedir, filename, filetype, datetime, thumbsize) {
        var real_file_url = serveimage_url + imagedir + '/' + filename;
        return '<li>' +
                    '<a href="' + real_file_url + '">' +
                        '<img src="' + servethumb_url + imagedir + '/' + filename + 
                            '&thumbsize=' + thumbsize + '">' +
                    '</a>' +
                    render_menu(imagedir, filename, filetype, datetime) +  // Menu!
                    '<p>' + filename + '</p>' +
               '</li>';
    }
    
    /**
     * Return HTML for an icon, based on a bunch of variables ...
     */
    function render_icon(imagedir, filename, filetype, datetime) {
        var real_file_url = '#';
        if (filetype == 'DIR') {
            real_file_url = base_url + '/folder?imagedir=' + imagedir + '/' + filename;
        }
        return '<li class="icon">' +
                    '<a href="' + real_file_url + '">' +
                        '<div>' +
                            '<span class="' + fa_icon(filetype) +'"></span>' +
                        '</div>' +
                    '</a>' +
                    '<p>' + filename + '</p>' +
                '</li>';
    }
    
    function render_menu(imagedir, filename, filetype, datetime) {
        return '<div class="menu">' +
                    '<a href="#"><span class="fa fa-bars"></span></a>' +
                    '<div class="dropdown-content">' +
                        '<a href="#">Link 1</a>' +
                        '<a href="#">Link 2</a>' +
                        '<a href="#">Link 3</a>' +
                    '</div>' +
                '</div>';
    }
    
    /**
     * Get ajax/json content and add to the page. Maybe create thumbnails.
     * 
     * @param imagedir (string) The path for the files
     * @param thumbsize (string) Geometry for thumbnails (e.g. "200x")
     */
    function get_dir(imagedir, thumbsize) {
        
        $('#status_field').html('Loading directory ...');
        
        $.getJSON({
            type: 'GET',
            url: 'http://localhost:5080/getdir',
            data: 'imagedir=' + imagedir,
            success:function(feed) {
                var real_file_url = '';
                feed.forEach(function(entry) {  // Put thumbs on page
                    if (is_image(entry.filetype)) {              // Thumb
                        $('#thumbs_area').append(render_thumb(imagedir, 
                        entry.name, entry.filetype, entry.datetime, thumbsize));
                    } else {                                     // or Icon
                        $('#thumbs_area').append(render_icon(imagedir, 
                        entry.name, entry.filetype, entry.datetime));
                    }
                    /* $('li').last().append(render_menu(imagedir,   // Menu
                        entry.name, entry.filetype, entry.datetime)); */
                });
                $('#status_field').html(''); // Remove "loading" message
            },
        });
    }
    
    /**
     * Change the src attribute of the img tags inside #thumbs_area so they
     * display different sized thumbnails
     * 
     * @param thumbsize (string) Geometry for thumbnail (e.g. "200x") to use
     */
    function change_thumbs(thumbsize) {
        var src, new_src;
        $('#thumbs_area img').each(function(index, elem) {
            src = $(elem).attr('src');
            new_src = src.replace(/&thumbsize=[x\d]+/, '&thumbsize=' + thumbsize);
            $(elem).attr('src', new_src);
        });
    }


    // When the folder button right of 'Lidpix' is clicked, show the directory 
    // field and change the folder button itself
    $('#folder_button').click(function() {
        if ($('#dir_field').css('visibility') == 'hidden')
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
    $('#gridbutton1').click(function() {  // This one chooses huge thumbs sized
        var vw, vh;                       // 10px narrower than viewport,
        [vw, vh] = getViewport();         // but not larger than 800x
        if (vw > 800)
            vw = 810;
        change_thumbs((vw - 10) + 'x');
        $('#gridbutton1').addClass('grid_btn_selected');
        $('ul.rig').addClass('columns-1');
    });
    $('#gridbutton4').click(function() {
        change_thumbs('400x');
        $('#gridbutton4').addClass('grid_btn_selected');
        $('ul.rig').addClass('columns-4');
    });
    $('#gridbutton10').click(function() {
        change_thumbs('200x');
        $('#gridbutton10').addClass('grid_btn_selected');
        $('ul.rig').addClass('columns-10');
    });
    
    var imagedir = $.urlParam('imagedir', null);
    var thumbsize = $.urlParam('thumbsize', '200x');
    
    get_dir(imagedir, thumbsize);
    
    // Add click event to menu buttons on all thumbs - shows menus
    $(document).on('click', '.menu', function() {
        $(this).find('.dropdown-content').toggle();
    });
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
