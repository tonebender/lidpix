// Initialize the Facebook JS SDK
window.fbAsyncInit = function() {
	FB.init({
		appId      : '1650430888594943',
		xfbml      : true,
		version    : 'v2.8'
	});
	FB.AppEvents.logPageView();
    console.log("Init FB ----");
    
    /* make the API call */
    FB.api(
        "/me/photos",
        "POST",
    {
        access_token: 'EAACEdEose0cBAHzbU1tV5tsHaPrIwfaZBreH3JIKWDgfM9tCZCnD6XcS9SuaoClDsftRiaZA4KZAUepQzVfBVFKqD7esn5QDfMrbDkW6mTxuSuhyZBC9kLMCrZBokOzUZBWJiUYZAFA8ZCqHLZB9V0tZCv7bfn0j1ZA1cOCw4zfBPdbcg4PqdC90DIY4dRcVog2Q714ZD',
        url: "http://farm4.staticflickr.com/3332/3451193407_b7f047f4b4_o.jpg"
    },
    function (response) {
        if (response && !response.error) {
        /* handle the result */
        console.log(response);
        }
        console.log(response.error);
    }
);
    
};

(function(d, s, id){
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) {return;}
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/sdk.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
