$(document).ready(function(){
  $(".tabs").click(function(){
  	if($(this).attr('data')){
  		var data=$(this).attr('data');
  		var link="/video/"+data;
  		console.log(link);
  		location.replace(link);
  	}
  	else{
  		alert("This module is locked");
  	}
  });
  $(".nav-link").click(function(){
  	if($(this).attr('data')){
  		var data=$(this).attr('data');
  		var link="/video/"+data;
  		console.log(link);
  		location.replace(link);
  	}
  	else{
  		alert("This module is locked");
  	}
  });
}); 


$(window).load(function(){
	// alert($(window).width());
	if ($(window).width()>600) {
		// $(".navbar-brand .logo").removeClass("hide");
		$(".menu").css({'height','inherit'})
	}
	else{
		$(".menu").css({'height','max-content'})
	}
  });
$(window).resize(function(){
	// alert($(window).width());
	if ($(window).width()>600) {
		// $(".navbar-brand .logo").removeClass("hide");
		$(".menu").css('height','inherit')
	}
	else{
		// $(".navbar-brand .logo").addClass("hide");
		$(".menu").css('height','max-content')
	}
  });

function filter(){
  	// console.log($("input[name='search']").val());
  	var search=$("input[name='search']").val();
  	console.log(search);
  	// console.log($(".tabs").attr('data').search(search));
  	$(".tabs h4").each(function() {
  		// $(".tabs").hide();
  		console.log($(this).attr("data"));
  		var data=$(this).text();
  		// console.log(data);
  		// console.log(data.toLowerCase().search(search.toLowerCase()));
  		if (search) {
  			if (data.toLowerCase().search(search.toLowerCase())>=0) {
		  		$(this).parent().show();
		  	}
		  	else{
		  		$(this).parent().parent().parent().hide();
		  	}
  		}
  		else{
  			$(".tabs").show();
  		}
	})	
}

  $(".navbar-toggler").click(function(){
  	$("#navbarNavDropdown").toggleClass("collapse");
  });

function setCookie() {
	console.log($("#username").val());
  	var d = new Date();
  	d.setTime(d.getTime() + (7*24*60*60*1000));
  	var expires = "expires="+ d.toUTCString();
  	document.cookie = "username = cvalue; expires = "+expires+" ;path=/";
}