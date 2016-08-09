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
 * Handle combobox option change event
 */
Site.handle_combobox_option = function(event) {
	var select = this;
	var option = select.options[select.selectedIndex].value;
	window.location = option;
}

/**
 * Handle product thumbnail click event
 */
Site.handle_product_thumbnail = function(event) {
	var self = this;
	var index = event.target.dataset.index;
	var thumbnail_images = document.querySelectorAll('img.thumbnail')
	var big_images = document.querySelectorAll('img.big_image');

	for (var i=0, count=big_images.length; i<count; i++) {
		if (index == i) {
			big_images[i].classList.add('visible');
			thumbnail_images[i].classList.add('active');
		} else {
			big_images[i].classList.remove('visible');
			thumbnail_images[i].classList.remove('active');
		}
	}
}

/**
 * Handler function for view control links
 */
Site.handle_view_controls = function() {
	var view = this.getAttribute('data-id');
	var view_controls = document.querySelectorAll('div.display a');
	var items_container = document.querySelector('div.category_items');
	this.classList.add('active');
	for(var i = 0,count = view_controls.length; i <count; i++) {
		if(this != view_controls[i]) {
			view_controls[i].classList.remove('active');
		}
	}

	if(view == "gallery")
			items_container.classList.remove('gallery'); else
			items_container.classList.add('gallery');
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

	// create function for rotating product big image
	if(document.querySelector('section.item_details')) {
		var product_thumbnails = document.querySelectorAll('img.thumbnail');
		var big_image = document.querySelectorAll('img.big_image')[0].classList.add('visible');
		var thumbnail_image = document.querySelectorAll('img.thumbnail')[0].classList.add('active');
		for (var i = 0, count = product_thumbnails.length; i<count; i++) {
			product_thumbnails[i].dataset.index = i;
			product_thumbnails[i].addEventListener('click', Site.handle_product_thumbnail);
		}
	}

	// create function for combobox option elements
	var select_element = document.querySelector('select');
	select_element.addEventListener('change', Site.handle_combobox_option);
};

// connect document `load` event with handler function
$(Site.on_load);