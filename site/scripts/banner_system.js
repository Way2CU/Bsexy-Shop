/**
 * Banner system JavaScript
 * Bsexy site
 *
 * Copyright (c) 2016. by Way2CU, http://way2cu.com
 * Authors: Tal Reznic
 */

// create or use existing site scope
var Site = Site || {};

Site.BannerSystem = function(items, banners) {
	var self = this;

	self.items = document.querySelectorAll(items);
	self.items_container = self.items[0].parentElement;
	self.banners = document.querySelectorAll(banners);
	self.step = 2;

	self._init = function() {
		// remove banner container
		self.banners[0].parentElement.remove();

		for(var i = 0; i < self.banners.length; i++) {
			self.items_container.insertBefore(self.banners[i], self.items_container.childNodes[self.step]);
			self.step += 3;
		}
	}

	// initialize object
	self._init();
}

$(function() {
	if (Site.is_mobile())
		Site.banner_system = new Site.BannerSystem('div.item', 'a.add_link');
})