/**
 * Backend JavaScript
 * Bsexy
 *
 * Copyright (c) 2016. by Way2CU, http://way2cu.com
 * Authors: Mladen Mijatov
 */

var Caracal = Caracal || new Object();


Caracal.handle_shop_window_open = function(shop_window) {
	// make sure we are working with the right window
	if (shop_window.id !== 'shop_item_add')
		return true;

	// get fields
	var expiration_field = shop_window.container.find('input[name=expires]');
	expiration_field.val(Date.now() + (30 * 24 * 60 * 60));
};


$(function() {
	Caracal.window_system.events.connect('window-open', Caracal.handle_shop_window_open);
})
