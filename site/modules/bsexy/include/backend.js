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


/**
 * Automatically add phone properties to the new item.
 */
Caracal.add_properties = function(shop_window) {
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
	var day = date.getDate();
	if (day.length == 1)
		day = '0' + day;

	var value = date.getUTCFullYear() + '-' + month + '-' + day + 'T00:00';
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

/**
 * Update tags entry for before item data is saved.
 *
 * @param object window
 */
Caracal.update_tags = function(shop_window) {
	var handled_windows = ['shop_item_add', 'shop_item_change'];

	// handle only specific windows
	if (handled_windows.indexOf(shop_window.id) == -1)
		return true;

	// find elements
	var tags = shop_window.container.find('input[name=tags]').eq(0);
	var categories = shop_window.container.find('input[type=checkbox][name^=category_id]');
	var selected = new Array();

	for (var i=0, count=categories.length; i<count; i++) {
		var category = categories.eq(i);

		if (!category.is(':checked'))
			continue;

		var data = category.data('text-id');
		if (data)
			selected.push(data);
	}

	// update tags container
	tags.val(JSON.stringify(selected));
};


/**
 * Attach additional handler for shop categories checkbox. This
 * handler will select child categories as well when parent one
 * is checked.
 *
 * @param object shop_window
 */
Caracal.attach_category_click_handler = function(shop_window) {
	var handled_windows = ['shop_item_add', 'shop_item_change'];

	// handle only specific windows
	if (handled_windows.indexOf(shop_window.id) == -1)
		return true;

	// find all checkboxes
	var categories = shop_window.container.find('input[type=checkbox][name^=category_id]');
	var exclude_list = ['escort', 'apartments', 'massage', 'private', 'vip'];

	categories.on('change', function(event) {
		var category = $(this);
		var container = category.closest('div.list_item').find('div.children');
		var children = container.find('input[type=checkbox][name^=category_id]');
		var text_id = category.data('text-id');

		if (exclude_list.indexOf(text_id) == -1)
			children.each(function(index) {
				var current = $(this);
				current.prop('checked', category.is(':checked'));
			});
	});
};


$(function() {
	Caracal.window_system.events.connect('window-content-load', Caracal.add_properties);
	Caracal.window_system.events.connect('window-content-load', Caracal.attach_category_click_handler);
	Caracal.window_system.events.connect('window-before-submit', Caracal.update_tags);
	Caracal.window_system.events.connect('window-close', Caracal.handle_shop_window_close);
});
