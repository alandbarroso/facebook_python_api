from facebook_api.core import FacebookCoreAPI

# For logging purposes
import logging

# For hashing email or phone numbers
import hashlib

# To use on parameters
import json

class FacebookCustomAudiencesAPI(FacebookCoreAPI):
	_ACCOUNT_AUDIENCES_URI = "https://graph.facebook.com/v2.1/act_%(account_id)s/customaudiences"
	
	_AUDIENCE_URI = "https://graph.facebook.com/v2.1/%(audience_id)s"
	_AUDIENCE_USERS_URI = "https://graph.facebook.com/v2.1/%(audience_id)s/users"
	_AUDIENCE_ACCOUNTS_URI = "https://graph.facebook.com/v2.1/%(audience_id)s/adacounts"

	# Types of schema
	UID = 'UID'
	EMAIL = 'EMAIL_SHA256'
	PHONE = 'PHONE_SHA256'

	def __init__(self, account_id, storage, http=None):
		super(FacebookCustomAudiencesAPI, self).__init__(storage=storage, http=http)
		
		self.account_id = account_id
		self._ACCOUNT_AUDIENCES_URI = self._ACCOUNT_AUDIENCES_URI % {'account_id': self.account_id}

		self.logger = logging.getLogger('FacebookCustomAudiencesAPI')

	def create_audience(self, name, description=None, opt_out_link=None):
		create_params = dict()
		create_params['name'] = name

		if description:
			create_params['description'] = description
		if opt_out_link:
			create_params['opt_out_link'] = opt_out_link

		create_url = self._ACCOUNT_AUDIENCES_URI
		response = self.post(create_url, create_params)

		# Returns the id of the created custom audience
		return response['id']

	def update_audience(self, name, description=None, opt_out_link=None):
		update_params = dict()
		update_params['name'] = name

		if description:
			update_params['description'] = description
		if opt_out_link:
			update_params['opt_out_link'] = opt_out_link

		update_url = self._AUDIENCE_URI % {'audience_id': audience_id}
		response = self.post(update_url, update_params)

		# Returns the id of the created custom audience
		return response

	def hash_data(self, data):
		return [hashlib.sha256(item.lower().strip(" \t\r\n\0\x0B.")).hexdigest() for item in data]

	def upload_users(self, audience_id, schema, data):
		users_url = self._AUDIENCE_USERS_URI % {'audience_id': audience_id}

		if schema == self.EMAIL or schema == self.PHONE:
			data = self.hash_data(data)

		payload = {'schema':schema,
					'data':data}
		payload = json.dumps(payload)

		upload_parametes = {'payload':payload}

		return self.post(users_url, upload_parametes)

	def delete_users(self, audience_id, schema, data):
		users_url = self._AUDIENCE_USERS_URI % {'audience_id': audience_id}

		if schema == self.EMAIL or schema == self.PHONE:
			data = self.hash_data(data)

		payload = {'schema':schema,
					'data':data}
		payload = json.dumps(payload)

		delete_parametes = {'payload':payload}

		return self.delete(users_url, delete_parametes)

	def list_audiences(self):
		list_url = self._ACCOUNT_AUDIENCES_URI
		params = {'fields': 'id, name'}
	
		response = self.get(list_url, params)
		while response['data']:
			yield response['data']

			params = {'after': response['paging']['cursors']['after']}
			response = self.get(list_url, params)