/**
 * Read More JavaScript
 * Bsexy Site
 *
 * Copyright (c) 2017. by Way2CU, http://way2cu.com
 * Authors: Mladen Mijatov
 */

// create or use existing site scope
var Site = Site || new Object();


Site.ReadMore = function(container) {
	var self = this;

	self.container = container;
	self.control = null;

	/**
	 * Complete object initialization.
	 */
	self._init = function() {
		self.control = document.createElement('a');
		self.control.classList.add('read-more');
		self.control.addEventListener('click', self.handle_click);

		// configure container
		self.container.classList.add('has-read-more');
		self.container.appendChild(self.control);
	};

	/**
	 * Handle clicking on more button.
	 * @param object event
	 */
	self.handle_click = function(event) {
		event.preventDefault();
		if (self.container.classList.contains('active'))
			self.container.classList.remove('active'); else
			self.container.classList.add('active');
	};

	// finalize object
	self._init();
}
