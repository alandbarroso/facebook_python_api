from facebook_api.core import FacebookCoreAPI

import json

import logging

class FacebookPageAPI(FacebookCoreAPI):
	_USER_URI = "https://graph.facebook.com/v2.1/me"
	_ACCOUNT_PAGE_URI = "https://graph.facebook.com/v2.1/%(user_id)s/accounts"

	_PAGE_URI = "https://graph.facebook.com/v2.1/%(page_id)s"

	_PAGE_FEED_URI = "/feed"
	_PAGE_PHOTOS_URI = "/photos"
	
	POST_FILTER = "/posts"
	TAGGED_FILTER = "/tagged"
	PROMOTABLE_FILTER = "/promotable_posts"
	
	UPLOADED_FILTER = "/uploaded"

	BACKDATE_YEAR = 'year'
	BACKDATE_MONTH = 'month'
	BACKDATE_DAY = 'day'
	BACKDATE_HOUR = 'hour'
	BACKDATE_MINUTE = 'minute'

	def __init__(self, user_storage, page_storage, page_id=None, http=None):
		super(FacebookPageAPI, self).__init__(storage=page_storage, http=http)

		self.logger = logging.getLogger('FacebookPageAPI')

		# Page id
		self.page_id = page_id
		self._PAGE_URI = self._PAGE_URI % {'page_id': self.page_id}

		# Storages
		self.user_storage = user_storage
		self.page_storage = page_storage

	def list_pages(self):
		old_storage = self.storage
		self.storage = self.user_storage

		self.logger.debug('Getting user id')
		response = self.get(self._USER_URI)
		self.user_id = response['id']
		self._ACCOUNT_PAGE_URI = self._ACCOUNT_PAGE_URI % {'user_id': self.user_id}
		self.logger.debug('User id %s' % self.user_id)

		list_url = self._ACCOUNT_PAGE_URI
		response = self.get(list_url)
		
		self.storage = old_storage
		
		return response['data']

	def _get_page_access_token(self):
		# Getting the user id
		self.storage = self.user_storage

		self.logger.debug('Getting user id')
		response = self.get(self._USER_URI)
		self.user_id = response['id']
		self._ACCOUNT_PAGE_URI = self._ACCOUNT_PAGE_URI % {'user_id': self.user_id}
		self.logger.debug('User id %s' % self.user_id)

		list_url = self._ACCOUNT_PAGE_URI
		response = self.get(list_url)
		pages = response['data']
		
		page_access_token = None
		for page in pages:
			if page['id'] == self.page_id:
				self.logger.debug('Page found! Registering access_token')
				page_access_token = page['access_token']

		if not page_access_token:
			raise Exception("The page id %s doesn't belong to the user with the current access token")

		self.page_storage.save(page_access_token)
		self.storage = self.page_storage

	def set_page_id(self, page_id):
		self.logger.debug('Page found! Registering access_token')
		self.page_id = page_id

		self._PAGE_URI = self._PAGE_URI % {'page_id': self.page_id}	

		self._get_page_access_token()

	def get_page_information(self):
		page_url = self._PAGE_URI
		response = self.get(page_url)
		
		return response

	def set_page_information(self, about=None, 
							company_overview=None, 
							description=None, 
							general_info=None,
							is_permanently_closed=None, 
							country=None, city=None, longitude=None, zip_code=None, state=None, street_address=None, located_in=None, latitude=None,
							mission=None,
							street=None, lot=None, valet=None,
							phone=None,
							price_range=None,
							website=None,
							cover=None, offset_y=None, no_feed_story=None, no_notification=None):
		page_url = self._PAGE_URI

		params = dict()
		
		if about:
			params['about'] = about
		if company_overview:
			params['company_overview'] = company_overview
		if description:
			params['description'] = description
		if general_info:
			params['general_info'] = general_info
		if is_permanently_closed:
			params['is_permanently_closed'] = is_permanently_closed
		if mission:
			params['mission'] = mission
		if phone:
			params['phone'] = phone
		if price_range:
			params['price_range'] = price_range
		if website:
			params['website'] = website

		if cover:
			params['cover'] = cover
		if offset_y:
			params['offset_y'] = offset_y
		if no_feed_story:
			params['no_feed_story'] = no_feed_story
		if no_notification:
			params['no_notification'] = no_notification

		if country or city or longitude or zip_code or state or street or located_in or latitude:
			location = dict()

			if country:
				location['country'] = country
			if city:
				location['city'] = city
			if longitude:
				location['longitude'] = longitude
			if zip_code:
				location['zip'] = zip_code
			if state:
				location['state'] = state
			if street_address:
				location['street'] = street_address
			if located_in:
				location['located_in'] = located_in
			if latitude:
				location['latitude'] = latitude

			params['location'] = json.dumps(location)

		if street or lot or valet:
			parking = dict()

			if street:
				parking['street'] = street
			if lot:
				parking['lot'] = lot
			if valet:
				parking['valet'] = valet

			params['parking'] = json.dumps(parking)

		response = self.post(page_url, params)

		return response

	def get_news_feed(self, post_filter=None):
		page_url = self._PAGE_URI

		feed_url = page_url
		if not post_filter:
			feed_url = feed_url + self._PAGE_FEED_URI
		else:
			feed_url = feed_url + post_filter

		response = self.get(feed_url)
		while response['data']:
			yield response['data']

			if 'paging' in response.keys():
				next_page = response['paging']['next']

				response = self.get(next_page)

	def post_news_feed(self, 
						message=None,
						link=None, picture=None, name=None, caption=None, description=None,
						actions=None,
						place=None,
						tags=None,
						object_attachment=None,
						published=True,
						scheduled_publish_time=None,
						backdated_time=None,
						backdated_time_granularity=None):
		page_url = self._PAGE_URI

		feed_url = page_url + self._PAGE_FEED_URI

		params = dict()

		if message:
			params['message'] = message
		if link:
			params['link'] = link
		if picture:
			params['picture'] = picture
		if name:
			params['name'] = name
		if caption:
			params['caption'] = caption
		if description:
			params['description'] = description
		if actions:
			params['actions'] = actions
		if place:
			params['place'] = place
		if tags:
			params['tags'] = tags
		if object_attachment:
			params['object_attachment'] = object_attachment
		if published:
			params['published'] = "true"
		else:
			params['published'] = "false"
		if scheduled_publish_time:
			params['scheduled_publish_time'] = scheduled_publish_time
		if backdated_time:
			params['backdated_time'] = backdated_time
		if backdated_time_granularity:
			params['backdated_time_granularity'] = backdated_time_granularity

		response = self.post(feed_url, params)
		return response['id']

	def get_photos(self, uploaded_filter=False):
		page_url = self._PAGE_URI

		photos_url = page_url + self._PAGE_PHOTOS_URI
		if uploaded_filter:
			photos_url = photos_url + self.UPLOADED_FILTER

		response = self.get(photos_url)
		while response['data']:
			yield response['data']

			if 'paging' in response.keys():
				next_page = response['paging']['next']

				response = self.get(next_page)

	def post_photo(self,
					source=None,
					url=None,
					message=None,
					place=None,
					no_story=False,
					published=True,
					scheduled_publish_time=None):
		page_url = self._PAGE_URI

		photos_url = page_url + self._PAGE_PHOTOS_URI
		
		params = dict()
		files = dict()

		if source:
			files['source'] = source

		if url:
			params['url'] = url
		if message:
			params['message'] = message
		if place:
			params['place'] = place
		if no_story:
			params['no_story'] = "true"
		else:
			params['no_story'] = "false"
		if published:
			params['published'] = "true"
		else:
			params['published'] = "false"
		if scheduled_publish_time:
			params['scheduled_publish_time'] = scheduled_publish_time

		self.logger.debug(params)

		response = self.post(photos_url, params, files)

		return response