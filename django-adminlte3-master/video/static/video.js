
$(document).ready(function () {
    // loadVids();

    function loadVids() {

    	var key = "AIzaSyCTkZNgBB6yo3-OXl2DzbFj0aZMyWNMlOA";
	    // var playlistId = 'PLfr5N_DIRx0Ni4hkPwWzhiMGBd9tV_1nr';
	    // var playlistId = '{{PlaylistId}}';
	    var URL = 'https://www.googleapis.com/youtube/v3/playlistItems';


	    var options = {
	        part: 'snippet',
	        key: key,
	        maxResults: 20,
	        playlistId: playlistId
	    }


        $.getJSON(URL, options, function (data) {
            var id = data.items[0].snippet.resourceId.videoId;

	        var thumb=data.items[0].snippet.thumbnails.maxres.url;

	        var title=data.items[0].snippet.title;

	        createplayer(id,title);
	             
            // resultsLoop(data);
            // progress(count);
            $("#replay").css({"background-image":"url("+thumb+")"});
            
            // console.log(data);

        });

        function resultsLoop(data) {
    	console.log(data);


        $.each(data.items, function (i, item) {

          count = i;


            var thumb = item.snippet.thumbnails.medium.url;
            var title = item.snippet.title;
            var desc = item.snippet.description.substring(0, 100);
            var vid = item.snippet.resourceId.videoId;

            // $("replay").css('background-image','url('${thumb}')');


            $('main').append(`
                            <article class="item" data-key="${vid}">

                                <img src="${thumb}" alt="" class="thumb">
                                <div class="details">
                                    <span class='title'>${title}</span>
                                    
                                </div>

                            </article>
                        `);
        });
    }
    }

	    // CLICK EVENT
    
        
// createplayer();
var player;
	window.onYouTubePlayerAPIReady =function (){
    var id=document.getElementsByTagName('article')[0].getAttribute('data-key');
    var title=document.getElementsByClassName('title')[0].innerText;
    var thumb=document.getElementsByClassName('thumb')[0].getAttribute('src');
    console.log(thumb);
    var link="url('"+thumb+"')";
    
		var tag = document.createElement('script');

		tag.src = "https://www.youtube.com/iframe_api";
		var firstScriptTag = document.getElementsByTagName('script')[0];
		firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

		
		player = new YT.Player('video', {
			height: '390',
	      	width: '640',
	      	videoId: id,
	      	rel: '0',
	      	events: {
	        	'onReady': onPlayerReady,
	        	'onStateChange': onPlayerStateChange
	      	}
	    });

	    $("#title").text(title);
      // console.log(link);
      // console.log($("#thumb"));
      $("#replay").css({'background-image':link});
      progress();

	}

      
      function onPlayerReady(event) {
        // event.target.playVideo();
      }

      
      var done = false;
      function onPlayerStateChange(event) {
        if (event.data == YT.PlayerState.PLAYING && !done) {
          setTimeout(stopVideo, 6000);
          done = true;
        }
        if (event.data == YT.PlayerState.ENDED || event.data == YT.PlayerState.PAUSED) {
          if (window.innerWidth>600) {
            $('#replay').removeClass("hide");
            $("#video").addClass("hide");
          }
        
    	}
      }
      function stopVideo() {
        player.stopVideo();
      }
      function playVideo() {
        player.playVideo();
      }
      function load(id) {
      	player.loadVideoById(id, 0, "large");
      	
      }

      $("#replay").click(function() {
        $("#replay").toggleClass("hide");
      	$("#video").toggleClass("hide");
      	playVideo();
      })

});