sfHover = function() {

	if (!document.getElementsByTagName) return false;

	var sfEls = document.getElementById("nav1").getElementsByTagName("li");

	// if you only have one main menu - delete the line below //

	var sfEls2 = document.getElementById("nav2").getElementsByTagName("li");

	//

	for (var i=0; i<sfEls.length; i++) {

		sfEls[i].onmouseover=function() {

			this.className+=" sfhover";

		}

		sfEls[i].onmouseout=function() {

			this.className=this.className.replace(new RegExp(" sfhover\\b"), "");

		}

	}

	for (var i=0; i<sfEls2.length; i++) {

		sfEls2[i].onmouseover=function() {

			this.className+=" sfhover";

		}

		sfEls2[i].onmouseout=function() {

			this.className=this.className.replace(new RegExp(" sfhover\\b"), "");

		}

	}

	//

}

if (window.attachEvent) window.attachEvent("onload", sfHover);