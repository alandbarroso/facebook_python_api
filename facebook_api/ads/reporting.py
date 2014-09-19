from facebook_api.core import FacebookCoreAPI

# For logging purposes
import logging

# To do sleep
from time import sleep

class FacebookAdsReportingAPI(FacebookCoreAPI):
	_REPORT_URI = "https://graph.facebook.com/v2.1/act_%(account_id)s/reportstats"
	_ASYNC_REPORT_URI = "https://graph.facebook.com/v2.1/%(report_id)s"

	# PRESET TIMES
	TODAY = 'today'
	YESTERDAY = 'yesterday'
	THIS_WEEK = 'this_week'
	LAST_WEEK = 'last_week'
	LAST_7DAYS = 'last_7_days'
	LAST_14DAYS = 'last_14_days'
	LAST_728AYS = 'last_28_days'
	LAST_30DAYS = 'last_30_days'
	LAST_90DAYS = 'last_90_days'
	THIS_MONTH = 'this_month'
	LAST_MONTH = 'last_month'
	LAST_3MONTHS = 'last_3_months'

	# TIME INCREMENTS
	MONTHLY = 'monthly'
	ALL_DAYS = 'all_days'

	# FORMATS
	JSON_FORMAT = 'json'
	XLS_FORMAT = 'xls'
	CSV_FORMAT = 'csv'

	def __init__(self, account_id, storage, http=None):
		super(FacebookAdsReportingAPI, self).__init__(storage=storage, http=http)

		self.account_id = account_id

		self._REPORT_URI = self._REPORT_URI % {'account_id': self.account_id}

		self.logger = logging.getLogger('FacebookAdsReportingAPI')

	# IMPORTANT!!!!!!!!!!
	# NO FILTER IMPLEMENTED YET
	def get_report(self, 
					start_date=None, end_date=None, date_preset=None, 
					time_increment=None, 
					data_columns=None,
					actions_group_by=None,
					sort_by=None,
					sort_dir=None,
					summary=None,
					report_format=None,
					offset=None,
					limit=None):
		report_params = dict()

		if not start_date and not end_date and not date_preset:
			raise Exception('Missing date_preset or time interval')

		if date_preset:
			report_params['date_preset'] = date_preset
		else:
			if not start_date:
				raise Exception('Missing start_date')
			if not end_date:
				raise Exception('Missing end_date')

			day_start = """{'year':'%(year)d', 'month':'%(month)d', 'day':'%(day)d'}""" % {
									'year':start_date.year,
									'month':start_date.month,
									'day':start_date.day,
								}

			day_stop = """{'year':'%(year)d', 'month':'%(month)d', 'day':'%(day)d'}""" % {
									'year':end_date.year,
									'month':end_date.month,
									'day':end_date.day,
								}

			report_params['time_interval'] = """{'day_start':%(day_start)s, 'day_stop':%(day_stop)s}""" % {
									'day_start':day_start,
									'day_stop':day_stop
								}

		if time_increment:
			report_params['time_increment'] = time_increment

		if not data_columns:
			raise Exception('Misssing data_columns')
		if type(data_columns) == list or type(data_columns) == tuple:
			report_params['data_columns'] = '[' + ','.join(['"' + column + '"' for column in data_columns]) + ']'
		else:
			report_params['data_columns'] = '["' + data_columns + '"]'

		if actions_group_by:
			if type(actions_group_by) == list or type(actions_group_by) == tuple:
				report_params['actions_group_by'] = '[' + ','.join(['"' + column + '"' for column in actions_group_by]) + ']'
			else:
				report_params['actions_group_by'] = '["' + actions_group_by + '""]'

		if sort_by:
			report_params['sort_by'] = sort_by

		if sort_dir:
			report_params['sort_dir'] = sort_dir
		
		if summary:
			report_params['summary'] = summary
				
		if report_format:
			report_params['format'] = report_format

		if offset:
			report_params['offset'] = offset

		if limit:
			report_params['limit'] = limit

		report_params['async'] = True

		acc_url = self._REPORT_URI

		self.logger.debug('Url: ' + acc_url)
		self.logger.debug('Params: ' + str(report_params))

		response = self.post(acc_url, report_params)
		
		report_id = response['id']
		self.logger.debug('Report Id: %s' % report_id)

		self.logger.info('Waiting for report %s to be created.' % report_id)
		async_job_url = self._ASYNC_REPORT_URI % {'report_id':report_id}
		completion = 0
		while completion != 100:
			response = self.get(async_job_url)

			completion = response['async_percent_completion']

			sleep(3)
			self.logger.info('Waiting...')

		self.logger.info('Report %s Done!' % report_id)

		has_next = True
		if not offset:
			offset = 0
		
		report_run_params = {'report_run_id':report_id, 'offset':offset}
		while has_next:
			response = self.get(acc_url, report_run_params)

			if not limit:
				limit = response['limit']

			if response['data']:
				yield response['data']
			else:
				self.logger.debug('No more values in data!')
				has_next = False

			offset = offset + limit
			report_run_params = {'report_run_id':report_id, 'offset':offset}
		
		self.logger.info('Deleting report %s.' % report_id)
		response = self.delete(async_job_url)
		
		self.logger.info('Report %s deleted.' % report_id)