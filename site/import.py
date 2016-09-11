#!/usr/bin/env python


import os
import re
import sys
import time
import urllib2
import codecs
import pymysql

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

		# try to download data
		try:
			remote_file = urllib2.urlopen(url)
			data = remote_file.read()

		except urllib2.URLError:
			self.log('Error opening {}'.format(url))

		else:
			with open(os.path.join(os.path.abspath(self.DESTINATION), file_name), 'wb') as local_file:
				local_file.write(data)
				result = True

			self.log('Downloaded: {}'.format(file_name))

		return result


class Inserter(Worker):
	def run(self):
		"""Insert data to database."""
		# create database connection
		count = 0
		connection = pymysql.connect(
					host='localhost',
					user='root',
					password='caracal',
					db='web_engine'
				)

		# process data
		self.log('Waiting for data.')
		while not self._stop_event.is_set():
			try:
				# try getting the data from the main queue
				data = self._queue.get(True, 1)

			except EmptyQueue:
				# there's still nothing in the queue, wait a bit more
				time.sleep(2)

			else:
				# download image
				if self.insert(connection, data):
					count += 1

		# clean up
		connection.close()

	def insert(self, connection, data):
		"""Insert data into database."""
		cursor = connection.cursor()

		# create gallery
		gallery_sql = 'INSERT INTO `gallery_group`(`name_he`, `name_en`) VALUES (?, ?);'
		name_he = data['name_he'] if 'name_he' in data else ''
		name_en = data['name_en'] if 'name_en' in data else ''

		cursor.execute(gallery_sql, (name_he, name_en))
		gallery_id = cursor.lastrowid

		# create shop item

		# commit transaction
		cursor.close()


class Import:
	"""
	Main application class which is used to parse, download and insert
	data into final database.
	"""
	AD_IMAGE_URL_TEMPLATE = 'http://bsexy.co.il/images/pics/{}'
	THREAD_COUNT = 20

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

	def __init__(self):
		# create queues for communicating with other threads
		self._image_queue = Queue()
		self._data_queue = Queue()

		# create events for controlling threads
		self._stop_event = Event()

		# create regular expression for matching data
		match_item = re.compile(
					'^INSERT \[dbo\]\.\[sx_ads\] \([^\)]+\) VALUES \('      # table
					'(?P<id>\d+),\s*'                                       # id
					'(?P<category>\d+),\s*'                                 # category id
					'(?P<location>\d+),\s*'                                 # location id
					'(?P<sex>\d+),\s*'                                      # sex
					'(?P<promoted>\d+),\s*'                                 # item is promoted
					'(?:N\'(?P<name_he>.+?(?=\',\s))\'|NULL),\s*'           # name in hebrew
					'(?:N\'(?P<name_en>.+?(?=\',\s))\'|NULL),\s*'           # name in english
					'(?:N\'(?P<description_he>.+?(?=\',\s))\'|NULL),\s*'    # description in hebrew
					'(?:N\'(?P<description_en>.+?(?=\',\s))\'|NULL),\s*'    # description in english
					'(?:N\'(?P<phone>.+?(?=\',\s))\'|NULL),\s*'             # description in english

					'(?:N\'(?P<icon>.+?(?=\',\s))\'|NULL),\s*'              # icon file
					'(?:N\'(?P<image_main>.+?(?=\',\s))\'|NULL),\s*'        # main image file
					'(?:N\'(?P<image_1>.+?(?=\',\s))\'|NULL),\s*'           # first image
					'(?:N\'(?P<image_1_small>[^\']+)\'|NULL),\s*'           # thumbnail for first image
					'(?:N\'(?P<image_2>.+?(?=\',\s))\'|NULL),\s*'           # second image
					'(?:N\'(?P<image_2_small>.+?(?=\',\s))\'|NULL),\s*'     # thumbnail for second image
					'(?:N\'(?P<image_3>.+?(?=\',\s))\'|NULL),\s*'           # third image
					'(?:N\'(?P<image_3_small>.+?(?=\',\s))\'|NULL),\s*'     # thumbnail for third image
					'(?:N\'(?P<image_4>.+?(?=\',\s))\'|NULL),\s*'           # fourth image
					'(?:N\'(?P<image_4_small>.+?(?=\',\s))\'|NULL),\s*'     # thumbnail for fourth image

					'(?:N\'(?P<call_to_action_he>.+?(?=\',\s))\'|NULL),\s*' # call to action text in hebrew
					'(?:N\'(?P<call_to_action_en>.+?(?=\',\s))\'|NULL),\s*' # call to action text in english
                                                                            # 'CAST\(N\'(?P<date_from>[^\']+)\' AS \w+\),\s*'                      # from date
                                                                            # 'CAST\(N\'(?P<date_to>[^\']+)\' AS \w+\),\s*'                        # to date
					'.+?(?=\d)(?P<status>\d+),\s*'                          # status

					'(?:N\'(?P<image_5>.+?(?=\',\s))\'|NULL),\s*'           # fifth image
					'(?:N\'(?P<image_5_small>.+?(?=\',\s))\'|NULL),\s*'     # thumbnail for fifth image
					'(?:N\'(?P<image_6>.+?(?=\',\s))\'|NULL),\s*'           # sixth image
					'(?:N\'(?P<image_6_small>.+?(?=\',\s))\'|NULL),\s*'     # thumbnail for sixth image
					'(?:N\'(?P<image_7>.+?(?=\',\s))\'|NULL),\s*'           # seventh image
					'(?:N\'(?P<image_7_small>.+?(?=\',\s))\'|NULL),\s*'     # thumbnail for seventh image
					'(?:N\'(?P<image_8>.+?(?=\',\s))\'|NULL),\s*'           # eighth image
					'(?:N\'(?P<image_8_small>.+?(?=\',\s))\'|NULL),'        # thumbnail for eighth image

                                                                            # '.+?(?=CAST)(?:CAST\(N\'(?P<date_start>[^\']+)\' AS \w+\)|NULL),\s*' # start date
                                                                            # 'CAST\(N\'(?P<date_end>[^\']+)\' AS \w+\),?\s*'                      # end date
					'[^\)]*\)',                                             # match the rest of the query
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
				self._image_queue.put_nowait((url, file_name))

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
		# for index in xrange(self.THREAD_COUNT):
		# 	Downloader(index, self._image_queue, self._stop_event).start()

		Inserter(0, self._data_queue, self._stop_event).start()

	@classmethod
	def log(cls, text):
		"""Print text to console and flush it."""
		cls.stdout_lock.acquire()
		print text
		cls.stdout_lock.release()


if __name__ == '__main__':
	Import()
