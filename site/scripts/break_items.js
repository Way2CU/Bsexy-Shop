/**
 * Break items JavaScript
 * Bsexy site
 *
 * Copyright (c) 2016. by Way2CU, http://way2cu.com
 * Authors: Tal Reznic
 */

// create or use existing site scope
var Site = Site || {};

Site.BreakItems = function(priority_items) {
	var self = this;

	self.priority_items = document.querySelectorAll(priority_items);
	self.break_tag = document.createElement('br');

	self._init = function() {
		var last_priority_first = self.priority_items[self.priority_items.length - 1];

		// insert line break tag after last item of each priority range
		last_priority_first.parentNode.insertBefore(self.break_tag, last_priority_first.nextSibling);
	}

	// initialize object
	self._init();
}

$(function() {
	new Site.BreakItems('div.item[data-priority^="2"]');
	new Site.BreakItems('div.item[data-priority^="1"]');
})