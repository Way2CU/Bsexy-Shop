#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import urllib2
import codecs
import pymysql
import warnings
import base64
import hashlib

from Queue import Queue, Empty as EmptyQueue
from threading import Thread, Event, active_count as thread_count, Lock


class Worker(Thread):
	def __init__(self, index, queue, stop_event):
		Thread.__init__(self, name='{}-{}'.format(self.__class__.__name__, index))

		self._index = index
		self._queue = queue
		self._stop_event = stop_event

	def log(self, text):
		"""Print text out to console with thread name."""
		Import.log('{}: {}'.format(self.name, text))


class Downloader(Worker):
	DESTINATION = './gallery/images/'

	def run(self):
		"""Download specified images."""
		count = 0
		self.log('Waiting for data.')

		# process data
		while not self._stop_event.is_set():
			try:
				# try getting the data from the main queue
				url, file_name = self._queue.get(True, 1)

			except EmptyQueue:
				# there's still nothing in the queue, wait a bit more
				time.sleep(2)

			else:
				# download image
				if self.download(url, file_name):
					count += 1

		self.log('Stopping! {} images downloaded.'.format(count))

	def download(self, url, file_name):
		"""Download specified URL and store it to default directory."""
		result = False

		if not Import.get_option('download'):
			Inserter.add_image((
					file_name,
					-1
				))
			return True

		# try to download data
		try:
			remote_file = urllib2.urlopen(url)
			data = remote_file.read()

		except urllib2.URLError:
			self.log('Error opening {}'.format(url))

		else:
			full_path = os.path.join(os.path.abspath(self.DESTINATION), file_name)
			with open(full_path, 'wb') as local_file:
				local_file.write(data)
				result = True

			# add image for processing
			Inserter.add_image((
					file_name,
					len(data)
				))

			self.log('Downloaded: {}'.format(file_name))

		return result


class Inserter(Worker):
	image_queue = Queue()
	item_galleries = {}
	item_images = {}

	category_index = {
			22: 'apartments',
			16: 'apartments',
			15: 'vip',
			1:  'escort',
			6:  'massage',
			12: 'spa',
			13: 'transgender',
			9:  'gays',
			8:  'sado',
			14: 'required'
			}
	category_map = {}

	location_index = {
			1: ('tel_aviv', 'ramat_gan', 'lod', 'bat_yam', 'petah_tikva', 'rishon',
				'givataim', 'holon', 'hadera', 'natanya', 'herzeliya', 'ramat_hasharon',
				'rannana', 'kefar_saba', 'hod_hasharon'),
			5: ('eilat',),
			4: ('rehovot', 'ashdod', 'ashkelon', 'bear_sheva', 'dimona'),
			2: ('haifa', 'krayot', 'akko', 'nahariya', 'galil', 'tiberius', 'carmiel', 'north_settelment'),
			3: ('jerusalem', 'modiin')
			}

	def run(self):
		"""Insert data to database."""
		# create database connection
		count = 0
		connection = pymysql.connect(
				host='localhost',
				user='root',
				password='caracal',
				db='web_engine',
				charset='utf8'
				)

		self.remove_tags = re.compile('<.*?>')

		# collect existing data
		self.log('Connected to database. Collecting existing data...')
		cursor = connection.cursor()

		sql = 'SELECT `id`, `text_id` FROM `shop_categories`;'
		cursor.execute(sql)
		data = cursor.fetchall()

		for category_id, category_text_id in data:
			if len(category_text_id.strip()) == 0: continue  # only categories with text_id
			self.category_map[category_text_id] = category_id

		cursor.close()

		# process data
		self.log('Waiting for data.')
		while not self._stop_event.is_set():
			# insert data
			try:
				# try getting the data from the main queue
				data = self._queue.get(True, 1)
				had_data = True

			except EmptyQueue:
				# there's still nothing in the queue, wait a bit more
				had_data = False

			else:
				# download image
				self.insert(connection, data)

			# insert images
			try:
				# get data from the image queue
				file_name, size = self.image_queue.get(True, 1)
				had_image = True

			except EmptyQueue:
				# image queue is empty check if we should terminate or continue
				had_image = False

			else:
				# insert image to the database
				self.insert_image(connection, file_name, size)
				count += 1

			# wait for data
			if not had_data and not had_image:
				if active_count() <= 2:
					break

				time.sleep(2)

		# clean up
		connection.close()
		self.log('Database connection closed!')

	def insert(self, connection, data):
		"""Insert data into database."""
		cursor = connection.cursor()

		# create gallery
		gallery_sql = 'INSERT INTO `gallery_groups`(`name_he`, `name_en`) VALUES (%s, %s);'
		name_he = data['name_he'] if 'name_he' in data else ''
		name_en = data['name_en'] if 'name_en' in data else ''

		cursor.execute(gallery_sql, (name_he, name_en))
		gallery_id = cursor.lastrowid

		# create shop item
		item_sql = (
				'INSERT INTO `shop_items`(`uid`, `name_he`, `name_en`, `description_he`, `description_en`, `gallery`) '
				'VALUES (%s, %s, %s, %s, %s, %s);'
				)
		description_he = self.remove_tags.sub('', data['description_he']) if 'description_he' in data else ''
		description_en = self.remove_tags.sub('', data['description_en']) if 'description_en' in data else ''
		uid = hashlib.new('sha1', str(data['id'])).hexdigest()

		cursor.execute(item_sql, (uid, name_he, name_en, description_he, description_en, gallery_id))
		item_id = cursor.lastrowid

		# create phone number property
		phone_number = data['phone'] if 'phone' in data else ''
		phone_numbers = phone_number.split('|')

		for index, phone_number in enumerate(phone_numbers, 1):
			phone_sql = (
					'INSERT INTO `shop_item_properties`(`item`, `text_id`, `type`, `name_he`, `name_en`, `name_ru`, `name_ar`, `value`) '
					'VALUES (%s, %s, "text", "Phone number", "Phone number", "Phone number", "Phone number", %s);'
					)
			field_name = 'phone{}'.format(index)
			phone_number = phone_number.strip()
			field_value = 's:{}:"{}";'.format(len(phone_number), phone_number)

			cursor.execute(phone_sql, (item_id, field_name, field_value))

		# add other properties
		properties = {
				'age': 'number',
				'height': 'number',
				'breast_size': 'text',
				'language': 'text',
				'origin': 'text'
				}

		for property_name, field_type in properties.items():
			sql = (
					'INSERT INTO `shop_item_properties`(`item`, `text_id`, `type`, `name_he`, `name_en`, `name_ru`, `name_ar`, `value`) '
					'VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
					)
			field_name = property_name.replace('_', ' ').capitalize()
			field_value = 's:0:"";'

			cursor.execute(sql, (item_id, property_name, field_type, field_name, field_name, field_name, field_name, field_value))

		# assign item to categories
		location_id = int(data['location']) if 'location' in data else None
		service_id = int(data['category']) if 'category' in data else None

		# assign location cateogry
		if location_id is not None and self.location_index.has_key(location_id):
			location_text_ids = self.location_index[location_id]
			location_text_ids = filter(lambda text_id: text_id in self.category_map, location_text_ids)

			for location_text_id in location_text_ids:
				category_id = self.category_map[location_text_id]
				category_sql = 'INSERT INTO `shop_item_membership`(`category`, `item`) VALUES (%s, %s)'
				cursor.execute(category_sql, (category_id, item_id))

		# assign service category
		if service_id is not None and service_id in self.category_index:
			service_text_id = self.category_index[service_id]

			if service_text_id in self.category_map:
				category_id = self.category_map[service_text_id]
				category_sql = 'INSERT INTO `shop_item_membership`(`category`, `item`) VALUES (%s, %s)'
				cursor.execute(category_sql, (category_id, item_id))

		# store gallery association for easy access later on
		self.item_galleries[item_id] = gallery_id

		# store image file names associated with this item
		for image in Import.images_to_download:
			image_file = image.lower()
			if image_file in data:
				self.item_images[data[image_file]] = item_id

		# commit transaction
		cursor.close()

	def insert_image(self, connection, file_name, size):
		"""Insert image to database."""
		if file_name not in self.item_images:
			return  # we don't know to which item this image is associated

		# get the gallery id we need to add image to
		item_id = self.item_images[file_name]
		gallery_id = self.item_galleries[item_id]

		# make sure gallery is valid
		if gallery_id is None:
			return

		# prepare for insertion
		cursor = connection.cursor()
		image_sql = 'INSERT INTO `gallery`(`group`, `size`, `filename`) VALUES (%s, %s, %s);'

		if size == -1:
			size = os.path.getsize(os.path.abspath(os.path.join(Downloader.DESTINATION, file_name)))

		# insert data
		cursor.execute(image_sql, (gallery_id, size, file_name))
		cursor.close()

	@classmethod
	def add_image(self, data):
		"""Append image data for insertion later."""
		self.image_queue.put_nowait(data)


class Import:
	"""
	Main application class which is used to parse, download and insert
	data into final database.
	"""
	AD_IMAGE_URL_TEMPLATE = 'http://bsexy.co.il/images/pics/{}'
	THREAD_COUNT = 10

	stdout_lock = Lock()
	images_to_download = (
			'image_main',
			'image_1',
			'image_2',
			'image_3',
			'image_4',
			'image_5',
			'image_6',
			'image_7',
			'image_8'
			)
	config = None

	def __init__(self):
		# create queues for communicating with other threads
		self._image_queue = Queue()
		self._data_queue = Queue()

		# create events for controlling threads
		self._stop_event = Event()

		# create regular expression for matching data
		match_item = re.compile(
				'^INSERT \[dbo\]\.\[sx_ads\] \([^\)]+\) VALUES \('             # table
				'(?P<id>\d+),\s*'                                              # id
				'(?P<category>\d+),\s*'                                        # category id
				'(?P<location>\d+),\s*'                                        # location id
				'(?P<sex>\d+),\s*'                                             # sex
				'(?P<promoted>\d+),\s*'                                        # item is promoted
				'(?:N\'(?P<name_he>.{0,100}?(?=\',\s))\'|NULL),\s+'            # name in hebrew
				'(?:N\'(?P<name_en>.{0,150}?(?=\',\s))\'|NULL),\s+'            # name in english
				'(?:N\'(?P<description_he>.{0,1000}?(?=\',\s))\'|NULL),\s+'    # description in hebrew
				'(?:N\'(?P<description_en>.{0,1500}?(?=\',\s))\'|NULL),\s+'    # description in english
				'(?:N\'(?P<phone>.{0,50}?(?=\',\s))\'|NULL),\s+'               # phone number

				'(?:N\'(?P<icon>.{0,50}?(?=\',\s))\'|NULL),\s+'                # icon file
				'(?:N\'(?P<image_main>.{0,255}?(?=\',\s))\'|NULL),\s+'         # main image file
				'(?:N\'(?P<image_1>.{0,255}?(?=\',\s))\'|NULL),\s+'            # rest of the images
				'(?:N\'(?P<image_1_small>.{0,255}?(?=\',\s))\'|NULL),\s+'
				'(?:N\'(?P<image_2>.{0,255}?(?=\',\s))\'|NULL),\s+'
				'(?:N\'(?P<image_2_small>.{0,255}?(?=\',\s))\'|NULL),\s+'
				'(?:N\'(?P<image_3>.{0,255}?(?=\',\s))\'|NULL),\s+'
				'(?:N\'(?P<image_3_small>.{0,255}?(?=\',\s))\'|NULL),\s+'
				'(?:N\'(?P<image_4>.{0,255}?(?=\',\s))\'|NULL),\s+'
				'(?:N\'(?P<image_4_small>.{0,255}?(?=\',\s))\'|NULL),\s+'

				'(?:N\'(?P<call_to_action_he>.{0,1000}?(?=\',\s))\'|NULL),\s+' # call to action text in hebrew
				'(?:N\'(?P<call_to_action_en>.{0,1500}?(?=\',\s))\'|NULL),\s+' # call to action text in english
				'.+?(?=\d)(?P<status>\d+),\s+'                                 # status

				'(?:N\'(?P<image_5>.{0,255}?(?=\',\s))\'|NULL),\s+'            # fifth image
				'(?:N\'(?P<image_5_small>.{0,255}?(?=\',\s))\'|NULL),\s+'      # thumbnail for fifth image
				'(?:N\'(?P<image_6>.{0,255}?(?=\',\s))\'|NULL),\s+'            # sixth image
				'(?:N\'(?P<image_6_small>.{0,255}?(?=\',\s))\'|NULL),\s+'      # thumbnail for sixth image
				'(?:N\'(?P<image_7>.{0,255}?(?=\',\s))\'|NULL),\s+'            # seventh image
				'(?:N\'(?P<image_7_small>.{0,255}?(?=\',\s))\'|NULL),\s+'      # thumbnail for seventh image
				'(?:N\'(?P<image_8>.{0,255}?(?=\',\s))\'|NULL),\s+'            # eighth image
				'(?:N\'(?P<image_8_small>.{0,255}?(?=\',\s))\'|NULL),'         # thumbnail for eighth image

				'[^\)]*\)',                                                    # match the rest of the query
				re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL
				)

		# create threads
		self.create_threads()

		# parse the file
		file_name = 'dump.sql'
		Import.log('Opening file {}...'.format(file_name))

		dump = '';
		with open(file_name, 'rb') as raw_file:
			dump = raw_file.read()

		Import.log('Parsing...')
		for match in match_item.finditer(dump):
			data = match.groupdict()
			data = dict(filter(lambda item: item[1] is not None, data.items()))

			# add complete data set for inserter to pick up
			self._data_queue.put_nowait(data)

			# add all the images
			for group_name in self.images_to_download:
				# make sure specified data exists
				if not group_name in data or data[group_name] is None:
					continue

				# add data to the queue
				file_name = data[group_name]
				url = self.AD_IMAGE_URL_TEMPLATE.format(file_name)
				self._image_queue.put_nowait((url, file_name.lower()))

		Import.log('Parsing complete. Waiting for threads to finish.')

		# wait for threads to process data
		try:
			while thread_count() > 1:
				time.sleep(1)

		except KeyboardInterrupt:
			self._stop_event.set()
			Import.log('Keyboard interrupt. Stopping threads...')

	def create_threads(self):
		"""Create all the worker threads."""
		for index in xrange(self.THREAD_COUNT):
			Downloader(index, self._image_queue, self._stop_event).start()

		Inserter(0, self._data_queue, self._stop_event).start()

	@classmethod
	def log(cls, text):
		"""Print text to console and flush it."""
		cls.stdout_lock.acquire()
		print text
		cls.stdout_lock.release()

	@classmethod
	def set_config(cls, config):
		"""Set configuration."""
		cls.config = config

	@classmethod
	def get_option(cls, name):
		"""Return option name."""
		assert name in cls.config
		return cls.config[name]


if __name__ == '__main__':
	Import.set_config({
		'download': True
		})

	Import()
