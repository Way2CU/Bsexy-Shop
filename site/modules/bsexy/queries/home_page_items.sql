SELECT
	shop_items.id
FROM
	shop_items,
	shop_item_membership,
	shop_categories
WHERE
	shop_items.id = shop_item_membership.item AND
	shop_categories.id = shop_item_membership.category AND
	shop_categories.text_id IN ('escort', 'apartments', 'massage', 'private', 'vip');
