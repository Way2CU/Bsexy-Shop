<?php

/**
 * Bsexy - Support Module
 *
 * This module provides some basic customizations for Bsexy site. Aside
 * from customizations it also provides options for importing shop items to system from CSV
 * sources generated by the Google Documents.
 *
 * Author: Mladen Mijatov
 */
use Core\Module;
use Core\Events;


class bsexy extends Module {
	private static $_instance;
	const LANG = 'he';
	const API = 'hooks.zapier.com/hooks/catch/133542/6p8qqq';

	/**
	 * Constructor
	 */
	protected function __construct() {
		global $section, $action;

		parent::__construct(__FILE__);

		// connect to shop events
		Event::connect('shop', 'item-added', 'handle_item_add', $this);
		Event::connect('shop', 'item-changed', 'handle_item_change', $this);
	}

	/**
	 * Public function that creates a single instance
	 */
	public static function get_instance() {
		if (!isset(self::$_instance))
			self::$_instance = new self();

		return self::$_instance;
	}

	/**
	 * Transfers control to module functions
	 *
	 * @param array $params
	 * @param array $children
	 */
	public function transfer_control($params=array(), $children=array()) {
	}

	/**
	 * Event triggered upon module initialization
	 */
	public function initialize() {
	}

	/**
	 * Event triggered upon module deinitialization
	 */
	public function cleanup() {
	}

	/**
	 * Handle shop item change.
	 *
	 * @param integer $item_id
	 */
	public function handle_item_add($item_id) {
	}

	/**
	 * Handle adding new shop item.
	 *
	 * @param integer $item_id
	 */
	public function handle_item_change($item_id) {
		global $language;

		// get managers
		$item_manager = ShopItemManager::getInstance();

		// get item from the database
		$item = $item_manager->get_item(array('name', 'expires'), array('id' => $item_id));
		if (!is_object($item))
			return;

		$date_time = date('Y-m-d', strtotime($item->expires));
		$color = 9;
		$post_data = array(
				'start' => $date_time,
				'end'   => $date_time,
				'item'  => $item->name[self::LANG],
				'color' => $color
			);
		$post_data = json_encode($post_data);

		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, self::API);
		curl_setopt($ch, CURLOPT_POST, 1);
		curl_setopt($ch, CURLOPT_HTTPGET, true);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		$response = curl_exec($ch);
	}
}

?>
