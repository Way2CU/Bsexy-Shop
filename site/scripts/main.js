/**
 * Main JavaScript
 * Site Name
 *
 * Copyright (c) 2015. by Way2CU, http://way2cu.com
 * Authors:
 */

// create or use existing site scope
var Site = Site || {};

// make sure variable cache exists
Site.variable_cache = Site.variable_cache || {};


/**
 * Check if site is being displayed on mobile.
 * @return boolean
 */
Site.is_mobile = function() {
	var result = false;

	// check for cached value
	if ('mobile_version' in Site.variable_cache) {
		result = Site.variable_cache['mobile_version'];

	} else {
		// detect if site is mobile
		var elements = document.getElementsByName('viewport');

		// check all tags and find `meta`
		for (var i=0, count=elements.length; i<count; i++) {
			var tag = elements[i];

			if (tag.tagName == 'META') {
				result = true;
				break;
			}
		}

		// cache value so next time we are faster
		Site.variable_cache['mobile_version'] = result;
	}

	return result;
};

/**
 * Handler function for view control links
 */
Site.handle_view_controls = function() {
	var self = this;
	var view = self.getAttribute('data-id');
	var view_controls = document.querySelectorAll('div.display a');
	var items = document.querySelectorAll('div.item');

	self.classList.add('active');
	for(var i = 0,count = view_controls.length; i <count; i++) {
		if(self != view_controls[i]) {
			view_controls[i].classList.remove('active');
		}
	}

	if(view == "gallery") {
		for(var i = 0, count = items.length; i < count; i++) {
			items[i].classList.add('gallery');
		}
	} else {
		for(var i = 0, count = items.length; i < count; i++) {
			items[i].classList.remove('gallery');
		}
	}
}

/**
 * Function called when document and images have been completely loaded.
 */
Site.on_load = function() {
	if (Site.is_mobile())
		Site.mobile_menu = new Caracal.MobileMenu();

	// create function for displaying category items view
	var view_controls = document.querySelectorAll('div.display a');
	for(var i = 0,count = view_controls.length; i <count; i++) {
		view_controls[i].addEventListener('click', Site.handle_view_controls);
	}
};


// connect document `load` event with handler function
$(Site.on_load);
