	jQuery(document).ready(function () {

	var cookie, enabled, hideAbout;

	// Get the PageDim cookie
	cookie = jQuery.cookie('page-dim-enabled');

	//console.log("Got cookie: "+cookie);
	
	// Cookie doesn't exist, so we create one
	if(cookie == 0) {
		enabled = 0;
		//console.log('Cookie was 0');
	} else {
		if (cookie == null) {
			jQuery.cookie('page-dim-enabled', 1, { path: '/', domain: 'newsevolved.com'});
			//console.log('Cookie didnt exist');
		}
		enabled = 1;
	}	
	
	hideAbout = false;

	function aboutDimTheLights() {
	
		if(!jQuery('#about-dim-the-lights').length) {
		
			var article = jQuery('.article');
			
			var positionLeft = article.position().left + article.outerWidth(true);
			//console.log('positionLeft: '+ positionLeft);
			
			var about = jQuery('<div></div>')
							.html("<p>Don't mind us, we're just dimming the lights a little to help you read.</p><p>To exit the Dim mode, click anywhere on the dimmed area.</p><p>Don't like it?</p>")
							.attr('id', 'about-dim-the-lights')
							.css({
								'z-index': '100',
								'position': 'absolute',
								'left': positionLeft
								})
							.vCenter()
							;
							
			var disableBtn = jQuery('<button></button>')
								.text('Turn off DimTheLights')
								.bind('click', disableDim)
								.css('display', 'block')
								.appendTo(about)
								;
			
			var dontShowAbout = jQuery('<input type="checkbox" />')
									.attr('id','dont-show-about')
									.bind('click', function() {hideAbout = true; jQuery('#about-dim-the-lights').remove(); })
									.appendTo(about)
									;
			var dontShowAboutLbl = jQuery('<label></label>')
									.attr('for', 'dont-show-about')
									.text('Don\'t show this box again')
									.appendTo(about)
									;
			
			jQuery('body').append(about);
		} else {
			jQuery('#about-dim-the-lights').show();
		}
	}


	function dimTheLights() {
	
		//console.log("hideAbout: "+ hideAbout);
		
		if(!hideAbout) {
			aboutDimTheLights();
		}
		
		jQuery('.article').css('position','relative');
		jQuery('.article').css('background','#fff');
		jQuery('.article').css('zIndex',100);
		jQuery("#pagedimmer").fadeIn("slow");
	
	}
	function raiseTheLights() {
		jQuery('#pagedimmer').fadeOut('slow');
		jQuery('#about-dim-the-lights').remove();
	}

	function disableDim() {
		raiseTheLights();
		
		// Set the cookie to disable
		jQuery.cookie('page-dim-enabled',0, { path: '/', domain: 'newsevolved.com'});
		
		// Unbind events to disable dimming
		$('.article').unbind('mouseenter').unbind('mouseleave');
		
		enabled = false;
		
		//console.log('just disabled DimTheLights');
	}
	
	if(enabled) {
		// Add mouseover event to dim the lights; activates in 2 seconds
		jQuery('.article').bind('mouseenter', function() {
			myTimeout = window.setTimeout(function() {
				dimTheLights();
			}, 2000);  // <-- 2 seconds
		});
		
		// Remove timeout event
		$('.article').bind("mouseleave",function() {
			window.clearTimeout(myTimeout);
		});
		
		// Add click event to end dim
		jQuery('#pagedimmer').click(raiseTheLights);

		// Set the height of the #pagedimmer element		
		jQuery('#pagedimmer').css('height', jQuery('body').outerHeight(true)+jQuery('#toppanel').outerHeight(true));
		
		// Set the width of the #pagedimmer element
		jQuery('#pagedimmer').css('width', jQuery('body').outerWidth(true));
	}

});


/** Plugins used for DimTheLights **/

// Minified jquery.vcenter.js, orgiinally found here: http://test.learningjquery.com/scripts/jquery.vcenter.js
(function($){$.fn.vCenter=function(options){var pos={sTop:function(){return window.pageYOffset||document.documentElement&&document.documentElement.scrollTop||document.body.scrollTop;},wHeight:function(){return window.innerHeight||document.documentElement&&document.documentElement.clientHeight||document.body.clientHeight;}};return this.each(function(index){if(index==0){var $this=$(this);var elHeight=$this.height();var elTop=pos.sTop()+(pos.wHeight()/2)-(elHeight/2);$this.css({position:'absolute',marginTop:'0',top:elTop});}});};})(jQuery);

/** Cookie plugin | Copyright (c) 2006 Klaus Hartl (stilbuero.de) | Dual licensed under the MIT and GPL licenses | http://www.opensource.org/licenses/mit-license.php | http://www.gnu.org/licenses/gpl.html */
jQuery.cookie=function(name,value,options){if(typeof value!='undefined'){options=options||{};if(value===null){value='';options.expires=-1;}
var expires='';if(options.expires&&(typeof options.expires=='number'||options.expires.toUTCString)){var date;if(typeof options.expires=='number'){date=new Date();date.setTime(date.getTime()+(options.expires*24*60*60*1000));}else{date=options.expires;}
expires='; expires='+date.toUTCString();}
var path=options.path?'; path='+(options.path):'';var domain=options.domain?'; domain='+(options.domain):'';var secure=options.secure?'; secure':'';document.cookie=[name,'=',encodeURIComponent(value),expires,path,domain,secure].join('');}else{var cookieValue=null;if(document.cookie&&document.cookie!=''){var cookies=document.cookie.split(';');for(var i=0;i<cookies.length;i++){var cookie=jQuery.trim(cookies[i]);if(cookie.substring(0,name.length+1)==(name+'=')){cookieValue=decodeURIComponent(cookie.substring(name.length+1));break;}}}
return cookieValue;}};