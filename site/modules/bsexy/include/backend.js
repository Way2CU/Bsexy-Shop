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
	if (shop_window.id != 'shop_item_add')
		return true;

	// set expiration date a month from today
	var expiration_field = shop_window.container.find('input[name=expires]');
	var date = new Date();
	date.setMonth(date.getMonth() + 1);
	var value = date.getUTCFullYear() + '-' + date.getMonth() + '-' + date.getDate() + 'T00:00';
	expiration_field.val(value);
};


$(function() {
	Caracal.window_system.events.connect('window-content-load', Caracal.handle_shop_window_open);
})
