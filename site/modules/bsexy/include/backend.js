/**
 * Backend JavaScript
 * Bsexy
 *
 * Copyright (c) 2016. by Way2CU, http://way2cu.com
 * Authors: Mladen Mijatov
 */

var Caracal = Caracal || new Object();

Caracal.add_property_row = function(property_id, data, container) {
	// add two phone numbers by default
	var row = $('<div>');
	row
		.addClass('list_item')
		.appendTo(container);

	// update field name
	data['text_id'] += property_id.toString();

	// create data field
	var data_field = $('<input>');
	data_field
		.attr('type', 'hidden')
		.attr('name', 'property_data_' + property_id)
		.val(JSON.stringify(data))
		.appendTo(row);

	// create columns
	var column_name = $('<span class="column">');
	var column_type = $('<span class="column">');
	var column_options = $('<span class="column">');

	column_name
		.html(data.name[language_handler.current_language])
		.attr('style', 'width: 250px')
		.appendTo(row);

	column_type
		.html(data.type)
		.attr('style', 'width: 60px')
		.appendTo(row);

	column_options.appendTo(row);

	// create options
	var option_remove = $('<a>');
	var option_change = $('<a>');
	var space = document.createTextNode(' ');

	option_change
		.on('click', Caracal.Shop.edit_property)
		.appendTo(column_options);

	column_options.append(space);

	option_remove
		.on('click', Caracal.Shop.delete_property)
		.appendTo(column_options);

	// load language constants for options
	language_handler.getTextArrayAsync(null, ['delete', 'change'], function(data) {
			option_remove.html(data['delete']);
			option_change.html(data['change']);
		});
};


Caracal.handle_shop_window_open = function(shop_window) {
	// make sure we are working with the right window
	if (shop_window.id != 'shop_item_add')
		return true;

	// set expiration date a month from today
	var expiration_field = shop_window.container.find('input[name=expires]');
	var date = new Date();
	date.setMonth(date.getMonth() + 1);
	var month = (date.getMonth() + 1).toString();
	if (month.length == 1)
		month = '0' + month;
	var value = date.getUTCFullYear() + '-' + month + '-' + date.getDate() + 'T00:00';
	expiration_field.val(value);

	// data to add
	var data = {
			text_id: 'phone',
			name: {
				'he': 'Phone number',
				'en': 'Phone number'
				},
			type: 'text',
			value: ''
		};

	// get container
	var container = shop_window.container.find('div#item_properties.list_content');

	// add two phone numbers
	data2 = data;
	Caracal.add_property_row(1, data, container);
	Caracal.add_property_row(2, data2, container);
};

/**
 * Reload item list when shop items are added or changed.
 *
 * @param object shop_window
 * @return boolean
 */
Caracal.handle_shop_window_close = function(shop_window) {
	var handled_windows = ['shop_item_add', 'shop_item_change'];

	// handle only specific windows
	if (handled_windows.indexOf(shop_window.id) == -1)
		return true;

	var bsexy_window = Caracal.window_system.getWindow('bsexy_items');
	if (bsexy_window)
		bsexy_window.loadContent();
}

/**
 * Update item management window when filters change.
 *
 * @param object sender
 */
Caracal.update_bsexy_item_list = function(sender) {
	var items_window = Caracal.window_system.getWindow('bsexy_items');
	var manufacturer = items_window.container.find('select[name=manufacturer]');
	var category = items_window.container.find('select[name=category]');

	// prepare data to send to server
	var data = {
			manufacturer: manufacturer.val(),
			category: category.val()
		};

	// save original url for later use
	if (items_window.original_url == undefined)
		items_window.original_url = items_window.url;

	// reload window
	items_window.loadContent(items_window.original_url + '&' + $.param(data));
};


$(function() {
	Caracal.window_system.events.connect('window-content-load', Caracal.handle_shop_window_open);
	Caracal.window_system.events.connect('window-close', Caracal.handle_shop_window_close);
})
