/* skel-baseline v3.0.1 | (c) n33 | skel.io | MIT licensed */

(function() {

	"use strict";

	// Methods/polyfills.

		// addEventsListener
			var addEventsListener = function(o,t,e)
			{
				var n, i = t.split(" ");
				for(n in i)
					o.addEventListener(i[n],e)
			}

		// classList | (c) @remy | github.com/remy/polyfills | rem.mit-license.org
		!function(){function t(t){this.el=t;for(var n=t.className.replace(/^\s+|\s+$/g,"").split(/\s+/),i=0;i<n.length;i++)e.call(this,n[i])}function n(t,n,i){Object.defineProperty?Object.defineProperty(t,n,{get:i}):t.__defineGetter__(n,i)}if(!("undefined"==typeof window.Element||"classList"in document.documentElement)){var i=Array.prototype,e=i.push,s=i.splice,o=i.join;t.prototype={add:function(t){this.contains(t)||(e.call(this,t),this.el.className=this.toString())},contains:function(t){return-1!=this.el.className.indexOf(t)},item:function(t){return this[t]||null},remove:function(t){if(this.contains(t)){for(var n=0;n<this.length&&this[n]!=t;n++);s.call(this,n,1),this.el.className=this.toString()}},toString:function(){return o.call(this," ")},toggle:function(t){return this.contains(t)?this.remove(t):this.add(t),this.contains(t)}},window.DOMTokenList=t,n(Element.prototype,"classList",function(){return new t(this)})}}();

	// Vars.
		var	$body = document.querySelector('body');

	// Breakpoints.
		skel.breakpoints({
			xlarge:	'(max-width: 1680px)',
			large:	'(max-width: 1280px)',
			medium:	'(max-width: 980px)',
			small:	'(max-width: 736px)',
			xsmall:	'(max-width: 480px)'
		});

	// Disable animations/transitions until everything's loaded.
		$body.classList.add('is-loading');

		window.addEventListener('load', function() {
			$body.classList.remove('is-loading');
		});


	// Login.
		var	$login = document.querySelector('#login'),
			$loginToggle = document.querySelector('a[href="#login"]'),
			$loginSubmit = document.querySelector('a[id="loginButton"]'),
			$loginClose;

		// Event: Prevent clicks/taps inside the login from bubbling.
			addEventsListener($login, 'click touchend', function(event) {
				event.stopPropagation();
			});

		// Event: Hide login on body click/tap.
			addEventsListener($body, 'click touchend', function(event) {
				$login.classList.remove('visible');
			});

		// Toggle.

			// Event: Toggle login on click.
				$loginToggle.addEventListener('click', function(event) {
					event.preventDefault();
					event.stopPropagation();
					$login.classList.toggle('visible');
				});

		// Close.
		
			// Create element.
				$loginClose = document.createElement('a');
					$loginClose.href = '#';
					$loginClose.className = 'close';
					$loginClose.tabIndex = 0;
					$login.appendChild($loginClose);

			// Event: Hide on ESC.
				window.addEventListener('keydown', function(event) {
					if (event.keyCode == 27)
						$login.classList.remove('visible');
				});

			// Event: Hide login on click.
				$loginClose.addEventListener('click', function(event) {
					event.preventDefault();
					event.stopPropagation();
					$login.classList.remove('visible');
				});
		
		// Login.
			
			//Event: Login button clicked
			$loginSubmit.addEventListener('click', function(event) {
				$login.classList.remove('visible');
				
			});
			
		
	// Nav.
		var	$nav = document.querySelector('#nav'),
			$navToggle = document.querySelector('a[href="#nav"]'),
			$navClose;

		// Event: Prevent clicks/taps inside the nav from bubbling.
			addEventsListener($nav, 'click touchend', function(event) {
				event.stopPropagation();
			});

		// Event: Hide nav on body click/tap.
			addEventsListener($body, 'click touchend', function(event) {
				$nav.classList.remove('visible');
			});

		// Toggle.

			// Event: Toggle nav on click.
				$navToggle.addEventListener('click', function(event) {
					event.preventDefault();
					event.stopPropagation();
					$nav.classList.toggle('visible');
				});

		// Close.
		
			// Create element.
				$navClose = document.createElement('a');
					$navClose.href = '#';
					$navClose.className = 'close';
					$navClose.tabIndex = 0;
					$nav.appendChild($navClose);

			// Event: Hide on ESC.
				window.addEventListener('keydown', function(event) {
					if (event.keyCode == 27)
						$nav.classList.remove('visible');
				});

			// Event: Hide nav on click.
				$navClose.addEventListener('click', function(event) {
					event.preventDefault();
					event.stopPropagation();
					$nav.classList.remove('visible');
				});
				
	// Table.
		var $TABLE = $('#table');
		var $BTN = $('#export-btn');
		var $EXPORT = $('#export');

		$('.table-add').click(function () {
			var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line');
			$TABLE.find('table').append($clone);
		});

		$('.table-remove').click(function () {
			$(this).parents('tr').detach();
		});

		$('.table-up').click(function () {
			var $row = $(this).parents('tr');
			if ($row.index() === 1) 
				return; // Don't go above the header
			$row.prev().before($row.get(0));
		});

		$('.table-down').click(function () {
			var $row = $(this).parents('tr');
			$row.next().after($row.get(0));
		});

		// A few jQuery helpers for exporting only
		jQuery.fn.pop = [].pop;
		jQuery.fn.shift = [].shift;

		$BTN.click(function () {
			var $rows = $TABLE.find('tr:not(:hidden)');
			var headers = [];
			var data = [];
	  
			// Get the headers (add special header logic here)
			$($rows.shift()).find('th:not(:empty)').each(function () {
				headers.push($(this).text().toLowerCase());
			});
	  
			// Turn all existing rows into a loopable array
			$rows.each(function () {
				var $td = $(this).find('td');
				var h = {};
		
				// Use the headers from earlier to name our hash keys
				headers.forEach(function (header, i) {
					h[header] = $td.eq(i).text();   
				});
				
				data.push(h);
			});
	  
			// Output the result
			$EXPORT.text(JSON.stringify(data));
		});
	
})();
