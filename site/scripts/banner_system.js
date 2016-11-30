/**
 * Banner system JavaScript
 * Bsexy site
 *
 * Copyright (c) 2016. by Way2CU, http://way2cu.com
 * Authors: Tal Reznic
 */

// create or use existing site scope
var Site = Site || {};

Site.BannerSystem = function(items, banners, increament_size, position) {
	var self = this;

	self.items = document.querySelectorAll(items);
	self.items_container = null;
	self.banners = document.querySelectorAll(banners);
	self.start_position = position;
	self.increament_size = increament_size;

	self._init = function() {
		// check if there are items
		if(self.items.length > 0)
			self.items_container = self.items[0].parentElement;

		// check if there are banners and remove container of banners
		if(self.banners.length > 0)
			self.banners[0].parentElement.remove();

		// insert banners after two items
		for(var i = 0; i < self.banners.length; i++) {
			self.items_container.insertBefore(self.banners[i], self.items_container.childNodes[self.start_position]);
			self.start_position += self.increament_size;
		}
	}

	// initialize object
	self._init();
}

$(function() {
	if (Site.is_mobile()) {
		if(window.location.pathname == "/") {
			Site.home_page_banners = new Site.BannerSystem('a.category', 'a.add_link', 5, 0);
		} else {
			Site.banner_system = new Site.BannerSystem('div.item', 'a.add_link', 3, 2);
		}
	}
})