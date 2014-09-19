from facebook_api.core import FacebookCoreAPI

import json

import logging

class FacebookPhotoAPI(FacebookCoreAPI):
	_PHOTO_URI = "https://graph.facebook.com/v2.1/%(photo_id)s"

	def __init__(self, storage, photo_id=None, http=None):
		super(FacebookPhotoAPI, self).__init__(storage=storage, http=http)

		self.logger = logging.getLogger('FacebookPhotoAPI')

		# Page id
		self.photo_id = photo_id
		self._PHOTO_URI = self._PHOTO_URI % {'photo_id': self.photo_id}

	def get_photo_information(self):
		photo_url = self._PHOTO_URI

		response = self.get(photo_url)

		return response

	def delete_photo(self):
		photo_url = self._PHOTO_URI

		response = self.delete(photo_url)

		return response