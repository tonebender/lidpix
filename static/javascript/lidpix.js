// Jquery
$(document).ready(function() {
  
    // Global variables, or shall we call them aliases ...
    var base_url = 'http://localhost:5080';
    var serveimage_url = base_url + '/serveimage?image=';
    var servethumb_url = base_url + '/servethumb?image=';
    var fobs; // Array that will hold all file objects
    
    
    // Facebook crap
    $.ajaxSetup({ cache: true });
    $.getScript('//connect.facebook.net/en_US/sdk.js', function(){
        FB.init({
            appId: '1650430888594943',
            version: 'v2.7' // or v2.1, v2.2, v2.3, ...
        });
        $('#loginbutton,#feedbutton').removeAttr('disabled');
        //FB.getLoginStatus(updateStatusCallback);
        /*
        FB.ui({
            method: 'share_open_graph',
            action_type: 'og.likes',
            action_properties: JSON.stringify({
            object:'https://developers.facebook.com/docs/',
            })
        }, function(response) {
        // Debug response (optional)
        console.log(response);
        }); */
    });
    (function(d, s, id){
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) {return;}
        js = d.createElement(s); js.id = id;
        js.src = "//connect.facebook.net/en_US/sdk.js";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
    
    
    /**
     * Get the value of the URL parameter 'name'
     * 
     * @param name The name of the parameter
     * @param defaultvalue This is returned if no value is found
     */
    function urlParam(name, defaultvalue) {
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
     * @param filetype A string containing the file extension, e.g. 'jpg'
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
    function render_thumb(imagedir, id, thumbsize) {
        var real_file_url = serveimage_url + imagedir + '/' + fobs[id].name;
        return '<li id="' + id + '">' +
                    '<a href="' + real_file_url + '">' +
                        '<img src="' + servethumb_url + imagedir + '/' + fobs[id].name + 
                            '&thumbsize=' + thumbsize + '">' +
                        '<div class="icon">' +                 // Icon is only used when image is hidden
                            '<span class="' + fa_icon(fobs[id].filetype) +'"></span>' +
                        '</div>' +
                    '</a>' +
                    '<p>' + fobs[id].name + '</p>' +
               '</li>';
    }
    
    /**
     * Return HTML for an icon, based on a bunch of variables ...
     * This is used for files (non-images) that don't have thumbnails
     */
    function render_icon(imagedir, id) {
        var real_file_url = '#';
        if (fobs[id].filetype == 'DIR') {
            real_file_url = base_url + '/folder?imagedir=' + imagedir + '/' + fobs[id].name;
        }
        return '<li class="icon" id="' + id + '">' +
                    '<a href="' + real_file_url + '">' +
                        '<div>' +
                            '<span class="' + fa_icon(fobs[id].filetype) +'"></span>' +
                        '</div>' +
                    '</a>' +
                    '<p>' + fobs[id].name + '</p>' +
                '</li>';
    }
    
    /**
     * Return HTML for a file menu
     */
    function render_menu(id) {
        return '<div class="menu">' +
                    '<a href="#"><span class="fa fa-bars"></span></a>' +
                    '<div class="dropdown-content">' +
                        '<a href="#" id="' + id + '" class="menuitem facebook">' +
                           '<span class="fa fa-facebook-official"></span> ' + 
                           'Upload to Facebook</a>' +
                        '<a href="#" id="' + id + '" class="menuitem info">' +
                        '<span class="fa fa-info-circle"></span> Image info</a>' +
                        //'<a href="#">Link 3</a>' +
                    '</div>' +
                '</div>';
    }
    
    /**
     * Get ajax/json content and add to the page (thumbs and whatnot)
     * 
     * @param imagedir (string) The path for the files
     * @param thumbsize (string) Geometry for thumbnails (e.g. "200x")
     */
    function get_dir(imagedir, thumbsize) {
        
        var file_id = 0;
        
        $('#status_field').html('Loading directory ...');
        
        $.getJSON({
            type: 'GET',
            url: 'http://localhost:5080/getdir',
            data: 'imagedir=' + imagedir,
            success:function(feed) {
                var real_file_url = '';
                fobs = feed; // Save all file objects to global var (!)
                feed.forEach(function(entry) {  // Put thumbs on page
                    if (is_image(entry.filetype)) {              // Thumb
                        $('#thumbs_area').append(render_thumb(imagedir, file_id, thumbsize));
                        $('#thumbs_area li').last().find('a').after(render_menu(file_id)); // Menu
                    } else {                                     // or Icon
                        $('#thumbs_area').append(render_icon(imagedir, file_id));
                    }
                    file_id++;
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
        $('#thumbs_area li div.icon').hide();
        $('#thumbs_area img').show();
    }
    
    
    /**
     * Show the file upload dialog
     *
    function upload_dialog() {
        
    } */
    
    
    function upload_to_facebook(id) {
        console.log(fobs[id].name);
    }
    

    (function init() {
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
        
        $('#gridbutton_icon').click(function() { // Hide thumbs and show icons instead
            $('#thumbs_area img').toggle();
            $('#thumbs_area li div.icon').toggle();
        });
        
        $('#settingsbutton').click(function() {
            $('#settingsdialog').show();
        });
        
        $('#settingsclosebutton').click(function() {
            $('#settingsdialog').hide();
        });
        
        
        $('div#dir_field').css('visibility', 'hidden');  // If JS is disabled, it will remain shown
        
        
        var imagedir = urlParam('imagedir', null);
        var thumbsize = urlParam('thumbsize', '200x');
            
        get_dir(imagedir, thumbsize);
        
        
        // Add click event to menu buttons on all thumbs
        $(document).on('click', '.menu', function() {
            $(this).find('.dropdown-content').toggle();
        });
        
        // Add click event to all facebook menu items
        $(document).on('click', '.menuitem, .facebook', function() {
            upload_to_facebook($(this).prop('id'));
        });
    })();
    
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
