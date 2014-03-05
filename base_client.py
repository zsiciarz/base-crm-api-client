import urllib
import urllib2
import logging
import json

logger = logging.getLogger(__name__)

def _unicode_dict(d):
    new_dict = {}
    for k, v in d.iteritems():
        new_dict[k] = unicode(v).encode('utf-8')
    return new_dict


def _list_to_tags(l):
    new_tags = ''
    for elem in l:
        if elem != '':
            new_tags += elem + ','

    if new_tags == '':
        return ''
    else:
        return new_tags[:-1]


"""

Current API paging:

                    Page
                    0                   1
Contacts (API)      duplicates 1        beginning
Deals (API)         404                 beginning
Leads (API)         beginning           2nd page
Contacts (search)   beginning           2nd page
Leads (search)      beginning           2nd page
Deals (search)      duplicates 1        beginning

Tags                duplicates 1        beginning
Notes               duplicates 1        beginning
Feed                TBD                 TBD
Emails              TBD                 TBD

"""

class BaseAPIService(object):

    def __init__(self, email, password, format='native'):
        """
        Gets a login token for base, and set the format for response objects.
        format =    'native' (default)
                    'json'
                    'xml'
        """

        self.resource = dict()
        self.resource['app'] = 'https://app.futuresimple.com/api/v1'
        self.resource['common'] = 'https://common.futuresimple.com/api/v1'
        self.resource['core'] = 'https://core.futuresimple.com/api/v1'
        self.resource['crm'] = 'https://crm.futuresimple.com/api/v1'
        self.resource['leads'] = 'https://leads.futuresimple.com/api/v1'
        self.resource['sales'] = 'https://sales.futuresimple.com/api/v1'

        if format == 'native':
            self.format = 'native'
        if format == 'json':
            self.format = '.json'
        elif format == 'xml':
            self.format = '.xml'

        # Get token
        status, self.token = self._get_login_token(email=email, password=password)
        if status == "ERROR":
            # If we get an error, return it.
            logger.error(self.token)
            self.auth_failed = True
        else:
            # Set URL header for future requests
            self.header = {"X-Pipejump-Auth": self.token, "X-Futuresimple-Token": self.token}
            self.auth_failed = False

    ##########################
    # Token Functions
    ##########################
    def _get_login_token(self, email, password):
        """
        Passes email and password to base api and returns login token.
        """
        auth_url = self._build_resource('sales',1) + '/authentication.json'
        url_params = urllib.urlencode({
            'email': email,
            'password': password,
        })

        try:
            data = urllib2.urlopen(auth_url, url_params).read()
        except urllib2.HTTPError, e:
            return ("ERROR", "HTTP: %s" % str(e))
        except urllib2.URLError, e:
            return ("ERROR", "Error URL: %s" % str(e.reason.args[1]))

        try:
            dict_data = json.loads(data)
            token = dict_data["authentication"]["token"]
        except KeyError:
            return ("ERROR", "Error: No Token Returned")

        return ("SUCCESS", token)

    ##########################
    # Helper Functions
    ##########################
    def _get_data(self, full_url):
        """
        This function submits the url using GET and returns the data for the requested URL.  If the format is set to
        'native', the function assumes the URL is set to json and converts the response using loads()
        """
        print 'GETing URL %s' % (full_url)
        req = urllib2.Request(full_url, headers=self.header)
        response = urllib2.urlopen(req)
        data = response.read()
        if self.format == 'native':
            data = json.loads(data)
        return data

    def _post_data(self, full_url, params):
        """
        This function submits the params to the url using POST and returns the data for the requested URL.  If the
        format is set to 'native', the function assumes the URL is set to json and converts the response using loads()
        """
        print 'POSTing URL %s' % (full_url)
        req = urllib2.Request(full_url, data=params, headers=self.header)
        response = urllib2.urlopen(req)
        data = response.read()
        if self.format == 'native':
            data = json.loads(data)
        return data

    def _put_data(self, full_url, params):
        """
        This function submits the params to the url using PUT and returns the data for the requested URL.  If the format
        is set to 'native', the function assumes the URL is set to json and converts the response using loads()
        """
        print 'PUTing URL %s' % (full_url)
        req = urllib2.Request(full_url, data=params, headers=self.header)
        req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()
        if self.format == 'native':
            data = json.loads(data)
        return data

    def _apply_format(self, url, format=None):
        """
        This function appends an appropriate extension telling the BaseCRM API to respond in a particular format. The
        'native' format uses json.
        """
        if format is not None:
            if format == '.json' or format == 'native':
                url += '%s' % ('.json')
            elif format == '.xml':
                url += '%s' % ('.xml')
        return url

    ##########################
    # URL Builders
    ##########################
    def _build_resource(self, resource, version):
        """
        Builds a URL for a resource using the not-officially-documented:

        app.futuresimple.com/apis/<resource>/api/v<version>
        """
        return 'https://app.futuresimple.com/apis/%s/api/v%d' % (resource, version)

    def _build_deal_url(self, deal_id=None, contact_id=None, format=None):
        """
        Returns a URL to obtain either all deals (deal_id=None) or a specific deal (deal_id=integer). For a list of
        deals nested under another object, do not include a deal_id and include one (and only one) of the following
        parent identifiers:
         - contact_id
        If this is the terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        if contact_id is not None:
            url = self._build_contact_url(contact_id)
        else:
            url = self._build_resource('sales', 1)
        url += '/deals'
        if deal_id is not None:
            url += '/%s' % (deal_id)
        return self._apply_format(url, format)

    def _build_lead_url(self, lead_id = None, format=None):
        """
        Returns a URL to obtain either all leads (lead_id=None) or a specific lead (lead_id=integer). If this is the
        terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        url = self._build_resource('leads', 1) + '/leads'
        if lead_id is not None:
            url += '/%s' % (lead_id)
        return self._apply_format(url, format)

    def _build_contact_url(self, contact_id = None, company_id = None, deal_id = None, format=None):
        """
        Returns a URL to obtain either all contacts (contact_id=None) or a specific contact (contact_id=integer). For a
        list of contacts nested under another object, do not include a contact_id and include one (and only one) of the
        following parent identifiers:
         - company_id (technically, this is the ID of the BaseCRM contact object for the company)
         - deal_id
        If this is the terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        if deal_id is not None:
            url = self._build_deal_url(deal_id)
        elif company_id is not None:
            url = self._build_contact_url(company_id)
        else:
            # https://app.futuresimple.com/apis/crm/api/v1/contacts.json
            url = self._build_resource('crm', 1)
            url += '/contacts'
        # Build URL through nested checks
        if contact_id is not None:
            if company_id is None:
                url += '/%s' % (contact_id)
            else:
                raise ValueError("Cannot include both a contact and company ID.")
        return self._apply_format(url, format)

    def _build_note_url(self, note_id=None, format=None):
        """
        Returns a URL to obtain either all notes (note_id=None) or a specific note (note_id=integer). This call must
        include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        url = self._build_resource('common',1)
        url += '/%s' % 'notes'
        if note_id is not None:
            url += '/%s' % note_id

        return self._apply_format(url, format)

    def _build_reminder_url(self, reminder_id=None, contact_id=None, lead_id=None, deal_id=None, format=None):
        """
        Returns a URL to obtain either all reminders (reminder_id=None) or a specific reminder (reminder_id=integer).
        For a list of reminders nested under another object, do not include a reminder_id and include one (and only one)
        of the following parent identifiers:
         - contact_id
         - lead_id
         - deal_id
        If this is the terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        if contact_id is not None:
            url = self._build_contact_url(contact_id)
        elif lead_id is not None:
            url = self._build_lead_url(lead_id)
        elif deal_id is not None:
            url = self._build_deal_url(deal_id)
            # Add reminder data
        else:
            raise ValueError("Reminders URL constructor requires a valid object (lead, contact, deal).")
        url += '/reminders'
        if reminder_id is not None:
            url += '/%s' % (reminder_id)
        return self._apply_format(url, format)

    def _build_tags_url(self, tag_id=None, format=None):
        """
        Returns a URL to obtain either all tags (tag_id=None) or a specific tag (tag_id=integer). If this is the
        terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        url = self._build_resource('tags',1)
        url += '/tags'
        if tag_id is not None:
            url += '/%s' % (tag_id)
        return self._apply_format(url, format)

    def _build_sources_url(self, source_id=None, contact_id=None, lead_id=None, deal_id=None, format=None):
        """
        Returns a URL to obtain either all sources (source_id=None) or a specific source (source_id=integer). If this is
        the terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        url = self._build_resource('sales',1)
        url += '/sources'
        if source_id is not None:
            url += '/%s' % (source_id)
        return self._apply_format(url, format)

    def _build_feeder_url(self, format=None):
        url = self._build_resource('feeder', 1)
        url += '/feed'
        return self._apply_format(url, format)

    def _build_activity_url(self, contact_id=None, lead_id=None, deal_id=None, format=None):
        """
        Returns a URL to obtain either all activities (type=None) or a specific activity type (only=<type>). Request
        must include one (and only one) of the following parent identifiers:
         - contact_id
         - lead_id
         - deal_id
        Call may include one of the follwing type values:
         - 'Email' returns only emails
         - 'Note' returns only notes
         - 'Call' returns only phone calls
         - 'Task' returns only completed tasks
        If this is the terminal object, include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        url = self._build_feeder_url(None)

        # Add appropriate path and ID
        if contact_id is not None:
            url += "/contact/%d" % contact_id
        elif lead_id is not None:
            url += "/lead/%d" % lead_id
        elif deal_id is not None:
            url += "/deal/%d" % deal_id
        else:
            raise ValueError("Activity URL constructor requires a valid object (lead, contact, deal).")

        return self._apply_format(url, format)

    def _build_search_url(self, type, format):
        if type == 'contact':
            url = self._build_resource('crm',1) + '/contacts'
        elif type == 'lead':
            url = self._build_lead_url()
        elif type == 'deal':
            url = self._build_deal_url()
        else:
            raise ValueError("Invalid search type.")
        url += '/search'
        return self._apply_format(url, format)

    ##########################
    # Accounts Functions
    ##########################
    def get_accounts(self):
        """
        Get current account.
        """
        url = self._build_resource('sales',1)
        url += '/account'
        full_url = self._apply_format(url, self.format)

        return self._get_data(full_url)

    ##########################
    # Tags Functions
    ##########################
    def get_tags(self, app=0, page=1):
        """
        Gets tag objects in batches of 20.
        Arguments:
            page = the set of deals to return. 1 (default) returns the first 20.
        """
        url = self._build_tags_url(format=self.format)
        # Append parameters
        url_params = urllib.urlencode({
            'page': page,
            'app_id': app,
            })
        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def get_contact_tags(self, page=1):
        """
        Contact tags are generated by two values of app_id:

        https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=4
        https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=7

        The difference is unclear so two functions (get_contact_tags and get_contact_tags_alt) are used.
        """
        return self.get_tags(4, page)
    def get_contact_tags_alt(self, page=1):
        return self.get_tags(7, page)
    def get_deal_tags(self, page=1):
        # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=1
        return self.get_tags(1, page)
    def get_lead_tags(self, page=1):
        # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=5
        return self.get_tags(5, page)

    ##########################
    # Notes Functions
    ##########################
    def _get_notes(self, contact_id=None, deal_id=None, lead_id=None, page=1, format=None):
        url = self._build_note_url(format=format)

        final_params = dict()
        if contact_id is not None:
            final_params['noteable_type'] = 'Contact'
            final_params['noteable_id'] = contact_id
        elif deal_id is not None:
            final_params['noteable_type'] = 'Deal'
            final_params['noteable_id'] = deal_id
        elif lead_id is not None:
            final_params['noteable_type'] = 'Lead'
            final_params['noteable_id'] = lead_id
        final_params['page'] = page
        url_params = urllib.urlencode(final_params)

        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def get_note(self, note_id):
        full_url = self._build_note_url(note_id=note_id, format=self.format)
        return self._get_data(full_url)

    def _create_note(self, content, contact_id=None, deal_id=None, lead_id=None, format=None):
        return self._create_note_legacy(content, contact_id=contact_id, deal_id=deal_id, lead_id=lead_id, format=format)

    def _create_note_legacy(self, content, contact_id=None, deal_id=None, lead_id=None, format=None):
        """
        This function uses legacy URLs for note creation.
        """
        pass

    def _create_note_new(self, content, contact_id=None, deal_id=None, lead_id=None, format=None):
        """
        BaseCRM UI POSTs to the URL
            https://app.futuresimple.com/apis/common/api/v1/notes.json
        with the parameters:
            actor_timeline_label: "Clayton Daley"
            content: "test note"
            noteable_id: 7787301 # ID of lead
            noteable_type: "Lead"
            secondary_subject_timeline_label: "Test Lead"
            subject_timeline_label: "test note"
        but this client gets a 500 Internal Server Error like due to either the X-CSRF-Token-Signature or Referer
        """
        final_params = dict()
        final_params['content'] = content
        if contact_id is not None:
            final_params['noteable_type'] = 'Contact'
            final_params['noteable_id'] = contact_id
        elif deal_id is not None:
            final_params['noteable_type'] = 'Deal'
            final_params['noteable_id'] = deal_id
        elif lead_id is not None:
            final_params['noteable_type'] = 'Lead'
            final_params['noteable_id'] = lead_id
        url_params = urllib.urlencode(final_params)

        url = self._build_note_url(format=format)
        return self._post_data(url, url_params)

    ##########################
    # Tasks Functions
    ##########################

    # https://app.futuresimple.com/apis/common/api/v1/tasks.json?status=active&owner=309357&_=1393883617883
    # https://app.futuresimple.com/apis/common/api/v1/tasks.json?taskable_type=Lead&taskable_id=7787301&done=true&_=1393889637145
    # https://app.futuresimple.com/apis/common/api/v1/tasks.json?taskable_type=Contact&taskable_id=40905809&status=active&skip_pagination=true
    # https://app.futuresimple.com/apis/common/api/v1/tasks.json?taskable_type=Deal&taskable_id=1290465&status=active&skip_pagination=true

    ##########################
    # Contact Functions and Constants
    ##########################
    CONTACT_PARAMS = [
        'name',
        'last_name',
        'first_name',
        'is_organisation',
        'contact_id',
        'email',
        'phone',
        'mobile',
        'twitter',
        'skype',
        'facebook',
        'linkedin',
        'address',
        'city',
        'country',
        'title',
        'description',
        'industry',
        'website',
        'fax',
        'tag_list',
        'private',
        ]

    CONTACT_FILTERS = [
        'user_id',
        'city', # All lower
        'region', # All lower
        'zip', # NOT zip_code as listed in aggregate
        'country', # All lower
        'tag_ids', # Comma (%2C) separated in URL
        'tags', # All lower; Comma (%2C) separated in URL
    ]

    CONTACT_SORTS = [
        # Verified not available: organisation_name, mobile, overdue_tasks, phone, unread_emails
        # Included in return list:
        'last_name',
        'first_name',
        'user_id',
        'account_id',
        'title',
        'created_at',
        'is_sales_account',
        'id',
        'is_organisation',
        'email',
        'name',
        # In sort_value if submitted, otherwise not returned:
        'last_activity',
        'calls_to_action,first',
        'calls_to_action,last'
    ]

    # Views
    # https://app.futuresimple.com/apis/crm/api/v1/contacts.json?contact_ids=40905835%2C40905820&per_page=100
    # https://app.futuresimple.com/apis/crm/api/v1/contacts/count.json?page=1&tags_exclusivity=and&crm_list=true&sort_by=calls_to_action%2Cfirst&using_search=false

    # Related Parameters
    # https://app.futuresimple.com/apis/crm/api/v1/custom_fields/cities
    # https://app.futuresimple.com/apis/crm/api/v1/custom_fields/regions
    # https://app.futuresimple.com/apis/crm/api/v1/custom_fields/countries
    # https://app.futuresimple.com/apis/crm/api/v1/custom_fields/zip_codes
    # https://app.futuresimple.com/apis/crm/api/v1/custom_fields.json?filterable=true
    # https://app.futuresimple.com/apis/crm/api/v1/custom_fields.json?sortable=true
    # https://app.futuresimple.com/apis/crm/api/v1/custom_field_values/grouped.json

    # https://app.futuresimple.com/apis/common/api/v1/feed/account_contacts_privacy.json

    # Activities
    # SEE ACTIVITIES SECTION

    def get_contacts(self, page=1):
        """
        Gets contact objects in batches of 20.
        Arguments:
            page = the set of contacts to return. 1 (default) returns the first 20.
        """
        url = self._build_contact_url(format=self.format)
        # Append parameters
        url_params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def get_contact(self, contact_id):
        """
        Gets the contact with the given contact_id. Returns the contact info.
        """
        full_url = self._build_contact_url(contact_id=contact_id, format=self.format)
        return self._get_data(full_url)

    def search_contacts(self, filters=None, sort_by=None, sort_order='asc', tags_exclusivity='and', page=0):
        url = self._build_search_url('contact', self.format)

        valid_params = {'page' : page,}
        if filters is not None:
            for key, value in filters.items():
                if key in self.CONTACT_FILTERS:
                    if key in ['tag_ids','tags']:
                        valid_params[key] = ','.join(value)
                        if tags_exclusivity in ['and','or']:
                            valid_params['tags_exclusivity'] = tags_exclusivity
                        else:
                            raise ValueError("tags_exclusivity must be 'and' or 'or'")
                    else:
                        valid_params[key] = value
                else:
                    raise ValueError("%s is not a valid filter for a Contact search" % (key))
        if sort_by is not None:
            if sort_by in self.CONTACT_SORTS:
                valid_params['sort_by'] = sort_by
            else:
                raise ValueError("%s is not a valid sort field for a Contact search" % (key))
            if sort_order in ['asc','desc']:
                valid_params['sort_order'] = sort_order
            else:
                raise ValueError("%s is not a valid sort order for a Contact search" % (sort_order))

        url_params = urllib.urlencode(valid_params)

        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def _upsert_contact(self, contact_info={}, contact_id=None, person=True):
        """
        Creates a new contact if contact_id == None.
        Otherwise, edits contact with the given id.
        """
        full_url = self._build_contact_url(contact_id=contact_id, format=self.format)

        # If we are creating a new contact, we must have name and last_name parameters
        # and we always must have some parameter
        if contact_info == {} or\
           (contact_id == None and 'name' not in contact_info.keys() and
            'last_name' not in contact_info.keys()):
            return

        final_params = {}

        final_params['is_organisation'] = 'false'
        if not person:
            final_params['is_organisation'] = 'true'

        for key in contact_info.keys():
            if key not in self.CONTACT_PARAMS:
                return
            else:
                final_params['contact[' + key + ']'] = contact_info[key]

        url_params = urllib.urlencode(_unicode_dict(final_params))

        if contact_id is None:
            return self._post_data(full_url, url_params)
        else:
            return self._put_data(full_url, url_params)

    def create_contact(self, contact_info, person=True):
        """
        Creates a new contact based on contact_info with fields shown in CONTACT_PARAMS.
        Assumes the contact is a person.  If the contact is a company, use person=False
        Returns a json or xml response.
        """
        return self._upsert_contact(contact_info=contact_info, contact_id=None, person=person)

    def update_contact(self, contact_info, contact_id, person=True):
        """
        Edits contact with the unique base_id based on contact_info with fields shown in CONTACT_PARAMS.
        Assumes the contact is a person.  If the contact is a company, use person=False
        Returns a json or xml response.
        """
        return self._upsert_contact(contact_info=contact_info, contact_id=contact_id, person=person)

    def update_contact_tags(self, contact_id, tags, action='add'):
        """
        Adds, removes, or replaces tags for a contact.  Returns a json or xml response.
        Arguments:
        contact_id: The base id of the contact that we want to work with
        tags: comma separated string of tags. Eg. 'platinum,trial_period'
        action: one of the following: 'add', 'remove', 'replace'
        """
        contact_data_dict = self._get_data(self._build_contact_url(contact_id=contact_id, format='native'))
        old_tags = contact_data_dict['contact']['tags_joined_by_comma'].split(', ')
        new_tags_list = tags.split(',')

        if action == 'add':
            new_tags = _list_to_tags(list(set(new_tags_list + old_tags)))
        elif action == 'remove':
            for elem in new_tags_list:
                try:
                    old_tags.remove(elem)
                except ValueError:
                    pass
            new_tags = _list_to_tags(old_tags)
        elif action == 'replace':
            new_tags = _list_to_tags(new_tags_list)

        person = not contact_data_dict['contact']['is_organisation']

        return self.update_contact(contact_info={'tag_list': new_tags}, contact_id=contact_id, person=person)

    def _upsert_contact_note(self, note_content, contact_id, note_id=None):
        """
        PRIVATE FUNCTION
        Creates a new note for a given contact_id with content note_content, if note_id == None.
        Otherwise, edits the note with the given note_id.
        """
        url = self._build_note_url(contact_id=contact_id)

        url_params = urllib.urlencode({'note[content]': unicode(note_content).encode('utf-8')})

        if note_id != None:
            return self._put_data(url, url_params)
        else:
            return self._post_data(url, url_params)

    def get_contact_notes(self, contact_id, page=0):
        return self._get_notes(contact_id=contact_id, page=page, format=self.format)

    def create_contact_note(self, contact_id, note_content):
        """
        Creates a note associated with a specific contact (defined by Base's unique contact_id)
        with the content note_content.
        Returns a json or xml response.
        """
        return self._upsert_contact_note(contact_id=contact_id, note_content=note_content)

    def update_contact_note(self, contact_id, note_content, note_id):
        """
        Edits a note (defined by Base's unique contact_id and the note's unique note_id)
        with the content note_content.
        Returns a json or xml response.
        """
        return self._upsert_contact_note(contact_id=contact_id, note_content=note_content, note_id=note_id)

    # Formatted as feed
    def get_contact_feed(self, contact_id):
        return self._get_contact_feed(contact_id, format=self.format)
    def get_contact_feed_emails(self, contact_id):
        return self._get_contact_feed(contact_id, type='Email', format=self.format)
    def get_contact_feed_notes(self, contact_id):
        return self._get_contact_feed(contact_id, type='Note', format=self.format)
    def get_contact_feed_calls(self, contact_id):
        return self._get_contact_feed(contact_id, type='Call', format=self.format)
    def get_contact_feed_tasks_completed(self, contact_id):
        return self._get_contact_feed(contact_id, type='Task', format=self.format )

    def _get_contact_feed(self, contact_id, type=None, params=None, format=None):
        """
        Gets activities (emails, notes, calls, tasks) for a contact by building URL requests like:

        https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2
        https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Email
        https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Note
        https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Call
        https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Task
        """
        # Build base URL
        url = self._build_activity_url(contact_id=contact_id, format=format)

        # Add appropriate parameters
        if params is None:
            final_params = {}
        else:
            final_params = params.copy()

        final_params['api_mailman'] = 2
        if type is not None:
            if type not in ['Email','Note','Call','Task']:
                final_params['only'] = type

        url_params = urllib.urlencode(_unicode_dict(final_params))
        full_url = url + '?' + url_params

        return self._get_data(full_url)

    ##########################
    # Deals Functions and Constants
    ##########################
    DEAL_PARAMS = [
        'name',
        'entity_id',
        'scope',
        'hot',
        'deal_tags',
        'contact_ids',
        'source_id',
        'stage',
        ]

    DEAL_STAGES = [
        'incoming',
        'qualified',
        'quote',
        'custom1',
        'custom2',
        'custom3',
        'closure',
        'won',
        'lost',
        'unqualified',
        ]

    DEAL_FILTERS = [
        'currency',
        'stage',
        'tag_ids',
        # tags (e.g. tag text) not available in deals
        'user_id',
        'hot',
        ]

    DEAL_SORTS = [
        'account_id',
        'added_on',
        'created_at',
        'currency',
        'entity_id',
        'hot',
        'id',
        'last_activity', # Alias for (otherwise not available) updated_at
        'last_stage_change_at',
        'loss_reason_id',
        'name',
        'scope',
        'source_id',
        'stage_code',
        'user_id'
        # In sort_value if submitted, otherwise not returned:
        'source', # Pulls full source record (user_id, name, created_at, updated_at, created_via, deleted_at, id, account_id
    ]

    # Views
    # https://app.futuresimple.com/apis/sales/api/v1/deals/by_ids.json?deal_ids=2049413%2C1283854%2C1283853%2C1283851&per_page=4
    # https://app.futuresimple.com/apis/leads/api/v1/leads.json?ids=7787301&per_page=1
    # https://app.futuresimple.com/apis/sales/api/v1/deals.json?dont_scope_by_stage=true&deal_ids=1276628
    # https://app.futuresimple.com/apis/sales/api/v2/contacts/deals.json?contact_ids=40905809
    # https://app.futuresimple.com/apis/sales/api/v1/deals/top_deals.json
    # https://app.futuresimple.com/apis/sales/api/v2/deals/total_pipeline_worth

    # Related Parameters
    # https://app.futuresimple.com/apis/sales/api/v1/sources.json?all=true
    # https://app.futuresimple.com/apis/sales/api/v1/sources.json?other=true
    # https://app.futuresimple.com/apis/sales/api/v1/sources.json?auto=true

    # https://app.futuresimple.com/apis/sales/api/v1/stages.json?detailed=true

    # https://app.futuresimple.com/apis/sales/api/v1/loss_reasons.json

    # https://app.futuresimple.com/apis/sales/api/v1/deal_custom_fields.json
    # https://app.futuresimple.com/apis/sales/api/v1/deal_custom_fields.json?sortable=true
    # https://app.futuresimple.com/apis/sales/api/v1/custom_field_values/grouped.json

    # https://app.futuresimple.com/apis/sales/api/v2/deals/currencies.json

    # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=1

    # Activities
    # SEE ACTIVITIES SECTION

    def get_deals(self, page=1, stage='incoming'):
        """
        Gets deal objects in batches of 20.
        Arguments:
            page = the set of deals to return. 1 (default) returns the first 20.
            stage = the stage of deals to return - see DEAL_STAGES list for details.
        """
        url = self._build_deal_url(format=self.format)
        # Append parameters
        if stage not in self.DEAL_STAGES:
            raise ValueError("Deal Stage must come from builtin stages list.")
        url_params = urllib.urlencode({
            'page': page,
            'stage': stage,
            })
        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def get_deal(self, deal_id):
        """
        Gets the deal with the given deal_id. Returns the deal info.
        """
        full_url = self._build_deal_url(deal_id=deal_id, format=self.format)
        return self._get_data(full_url)

    def search_deals(self, filters=None, sort_by=None, sort_order='asc', tags_exclusivity='and', page=1):
        url = self._build_search_url('deal', self.format)

        valid_params = {'page' : page,}
        if filters is not None:
            for key, value in filters.items():
                if key in self.DEAL_FILTERS:
                    if key in ['tag_ids','tags']:
                        valid_params[key] = ','.join(value)
                        if tags_exclusivity in ['and','or']:
                            valid_params['tags_exclusivity'] = tags_exclusivity
                        else:
                            raise ValueError("tags_exclusivity must be 'and' or 'or'")
                    else:
                        valid_params[key] = value
                else:
                    raise ValueError("%s is not a valid filter for a deal search" % (key))
        if sort_by is not None:
            if sort_by in self.DEAL_SORTS:
                valid_params['sort_by'] = sort_by
            else:
                raise ValueError("%s is not a valid sort field for a deal search" % (key))
            if sort_order in ['asc','desc']:
                valid_params['sort_order'] = sort_order
            else:
                raise ValueError("%s is not a valid sort order for a deal search" % (sort_order))

        url_params = urllib.urlencode(valid_params)

        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def create_deal(self, deal_info):
        """
        Creates a new deal in base, given proper deal parameters in deal_info argument.
        Proper parameters are shown in the DEAL_PARAMS dictionary.
        Returns a json or xml reponse.
        """
        return self._upsert_deal(deal_info=deal_info)

    def _upsert_deal(self, deal_info={}, deal_id=None):
        """
        PRIVATE FUNCTION:
        Creates a new deal if deal_id = None.
        Otherwise, edits the deal with the given deal_id.
        """
        deals_url = '/deals'
        if deal_id != None:
            deals_url += '/%s' % str(deal_id)
        deals_url = self._apply_format(deals_url, self.format)

        url = self.resource['sales'] + deals_url

        if deal_info == {} or (('name' not in deal_info.keys()\
                                or 'entity_id' not in deal_info.keys()) and deal_id == None):
            return "Missing required attributes 'name' or 'entity_id'"

        final_params = {}

        for key in deal_info.keys():
            if key not in self.DEAL_PARAMS:
                return "%s is not a legal deal attribute" % key
            else:
                final_params[key] = deal_info[key]

        url_params = urllib.urlencode(_unicode_dict(final_params))

        req = urllib2.Request(url, data=url_params, headers=self.header)
        if deal_id != None:
            req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    def update_deal(self, deal_info, deal_id):
        """
        Updates a deal with the given the base deal_id accoring to deal_info parameters.
        Proper parameters are shown in the DEAL_PARAMS dictionary.
        Returns a json or xml response.
        """
        return self._upsert_deal(deal_info=deal_info, deal_id=deal_id)

    def update_deal_tags(self, deal_id, tags, action='add'):
        """
        Adds, removes, or replaces tags for a deal.  Returns a json or xml response.
        Arguments:
        deal_id: The base id of the deal that we want to work with
        tags: comma separated string of tags. Eg. 'platinum,trial_period'
        action: one of the following: 'add', 'remove', 'replace'
        """
        deal_data_dict = self._get_data(self._build_deal_url(deal_id=deal_id, format='.json'))
        old_tags = deal_data_dict['deal']['deal_tags'].split(', ')
        new_tags_list = tags.split(',')

        if action == 'add':
            new_tags = _list_to_tags(list(set(new_tags_list + old_tags)))
        elif action == 'remove':
            for elem in new_tags_list:
                try:
                    old_tags.remove(elem)
                except ValueError:
                    pass
            new_tags = _list_to_tags(old_tags)
        elif action == 'replace':
            new_tags = _list_to_tags(new_tags_list)

        return self.update_deal(deal_info={'deal_tags': new_tags}, deal_id=deal_id)

    def get_deal_notes(self, deal_id, page=0):
        return self._get_notes(deal_id=deal_id, page=page, format=self.format)

    def get_deal_note(self, deal_id, note_id):
        """
        Gets deal object.
        """
        full_url = self._build_note_url(note_id=note_id, deal_id=deal_id, format=self.format)
        return self._get_data(full_url)

    def create_deal_note(self, deal_id, note_content):
        """
        Creates a note associated with a specific deal (defined by Base's unique deal_id)
        with the content note_content.
        Returns a json or xml response.
        """
        return self._upsert_deal_note(deal_id=deal_id, note_content=note_content)

    def update_deal_note(self, deal_id, note_content, note_id):
        """
        Edits a note (defined by Base's unique deal_id and the note's unique note_id)
        with the content note_content.
        Returns a json or xml response.
        """
        return self._upsert_deal_note(deal_id=deal_id, note_content=note_content, note_id=note_id)

    def _upsert_deal_note(self, deal_id, note_content='', note_id=None):
        """
        PRIVATE FUNCTION
        Creates a new note for a given deal_id with content note_content, if note_id == None.
        Otherwise, edits the note with the given note_id.
        """

        url_base_template = 'deals/%s/notes' % str(deal_id)
        if note_id != None:
            url_base_template += '/%s' % str(note_id)
        url_base_template = self._apply_format(url_base_template, self.format)

        url = self.resource['sales'] + url_base_template

        url_params = urllib.urlencode({'note[content]': unicode(note_content).encode('utf-8')})

        req = urllib2.Request(url, data=url_params, headers=self.header)
        if note_id != None:
            req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    def get_deal_feed(self, deal_id):
        return self._get_deal_feed(deal_id, format=self.format)
    def get_deal_feed_emails(self, deal_id):
        return self._get_deal_feed(deal_id, type='Email', format=self.format)
    def get_deal_feed_notes(self, deal_id):
        return self._get_deal_feed(deal_id, type='Note', format=self.format)
    def get_deal_feed_calls(self, deal_id):
        return self._get_deal_feed(deal_id, type='Call', format=self.format)
    def get_deal_feed_tasks_completed(self, deal_id):
        return self._get_deal_feed(deal_id, type='Task', format=self.format)

    def _get_deal_feed(self, deal_id, type=None, url_params=None, format=None):
        """
        Gets activities (emails, notes, calls, tasks) for a deal by building URL requests like:

        https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2
        https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Email
        https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Note
        https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Call
        https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Task
        """

        # Build base URL
        url = self._build_activity_url(deal_id=deal_id, format=format)

        # Add appropriate parameters
        if params is None:
            final_params = {}
        else:
            final_params = params.copy()

        final_params['api_mailman'] = 2
        if type is not None:
            if type not in ['Email','Note','Call','Task']:
                final_params['only'] = type

        url_params = urllib.urlencode(_unicode_dict(final_params))
        full_url = url + '?' + url_params

        return self._get_data(full_url)

    ##########################
    # Sources Functions
    ##########################
    def get_sources(self, other=0):
        """
        Gets contact sources.
        Argument:
            other: default to 0.  If 1, retrieves sources added by other users in the account.
        """
        url = self._build_sources_url(format=self.format)
        if other == 1:
            url_params = urllib.urlencode({
                'other': other,
                })
        else:
            url_params = ''
        # Append parameters
        full_url = url + '?' + url_params
        return self._get_data(full_url)

    ##########################
    # Lead Functions
    ##########################
    LEAD_FILTERS = [
        'tag_ids',
        'owner_id',
        'status_id',
        ]

    LEAD_SORTS = [
        'account_id',
        'added_on',
        'company_name',
        'created_at',
        'first_name',
        'id',
        'last_activity_date',
        'last_activity', # Appears to be alias of last_activity_date
        'last_name',
        'owner_id',
        'state',
        'status_id',
        'title',
        #'tag_ids', # Accepted by API but non-functional
        #'tags', # Accepted by API but non-functional
        'user_id',
        ]

    # Views
    # https://app.futuresimple.com/apis/leads/api/v1/leads.json?sort_by=last_name&sort_order=asc&tags_exclusivity=and&without_unqualified=true&using_search=false&page=0&converting=false
    # https://app.futuresimple.com/apis/leads/api/v1/leads/search.json?sort_by=last_name&sort_order=asc&tags_exclusivity=and&without_unqualified=true

    # Related Parameters
    # https://app.futuresimple.com/apis/leads/api/v1/statuses.json

    # https://app.futuresimple.com/apis/leads/api/v1/custom_fields.json?sortable=true
    # https://app.futuresimple.com/apis/leads/api/v1/custom_fields/filterable.json

    # Activities
    # SEE ACTIVITIES SECTION

    def get_leads(self, page=0):
        """
        Gets lead objects in batches of 20.
        Arguments:
            page = the set of deals to return. 0 (default) returns the first 20.
        """
        url = self._build_lead_url(format=self.format)
        # Append parameters
        url_params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def get_lead(self, lead_id):
        """
        Gets the deal with the given deal_id. Returns the deal info.
        """
        full_url = self._build_lead_url(lead_id=lead_id, format=self.format)
        return self._get_data(full_url)

    def search_leads(self, filters=None, sort_by=None, sort_order='asc', tags_exclusivity='and', page=0):
        url = self._build_search_url('lead', self.format)

        valid_params = {'page' : page,}
        if filters is not None:
            for key, value in filters.items():
                if key in self.LEAD_FILTERS:
                    if key in ['tag_ids','tags']:
                        valid_params[key] = ','.join(value)
                        if tags_exclusivity in ['and','or']:
                            valid_params['tags_exclusivity'] = tags_exclusivity
                        else:
                            raise ValueError("tags_exclusivity must be 'and' or 'or'")
                    else:
                        valid_params[key] = value
                else:
                    raise ValueError("%s is not a valid filter for a Lead search" % (key))
        if sort_by is not None:
            if sort_by in self.LEAD_SORTS:
                valid_params['sort_by'] = sort_by
            else:
                raise ValueError("%s is not a valid sort field for a Lead search" % (key))
            if sort_order in ['asc','desc']:
                valid_params['sort_order'] = sort_order
            else:
                raise ValueError("%s is not a valid sort order for a Lead search" % (sort_order))

        url_params = urllib.urlencode(valid_params)

        full_url = url + '?' + url_params
        return self._get_data(full_url)

    def get_lead_notes(self, lead_id, page=0):
        return self._get_notes(lead_id=lead_id, page=page, format=self.format)

    # Feed formatted
    def get_lead_feed(self, lead_id):
        return self._get_lead_feed(lead_id, format=self.format)
    def get_lead_feed_emails(self, lead_id):
        return self._get_lead_feed(lead_id, type='Email', format=self.format)
    def get_lead_feed_notes(self, lead_id):
        return self._get_lead_feed(lead_id, type='Note', format=self.format)
    def get_lead_feed_notes_alt(self, lead_id):
        return self._get_notes(lead_id=lead_id, format=self.format)
    def get_lead_feed_calls(self, lead_id):
        return self._get_lead_feed(lead_id, type='Call', format=self.format)
    def get_lead_feed_tasks_completed(self, lead_id):
        return self._get_lead_feed(lead_id, type='Task', format=self.format)

    def _get_lead_feed(self, lead_id, type=None, params=None, format=None):
        """
        Gets activities (emails, notes, calls, tasks) for a deal by building URL requests like:

        https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?page=1&api_mailman=v2
        https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Note&page=1&api_mailman=v2
        https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Email&page=1&api_mailman=v2
        https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Call&page=1&api_mailman=v2
        https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Task&page=1&api_mailman=v2
        """

        # Build base URL
        url = self._build_activity_url(lead_id=lead_id, format=format)

        # Add appropriate parameters
        if params is None:
            final_params = {}
        else:
            final_params = params.copy()

        final_params['api_mailman'] = 2
        if type is not None:
            if type not in ['Email','Note','Call','Task']:
                final_params['only'] = type

        url_params = urllib.urlencode(_unicode_dict(final_params))
        full_url = url + '?' + url_params

        return self._get_data(full_url)

    ##########################
    # Email Functions
    ##########################

    # V1
    # https://app.futuresimple.com/apis/mailman/api/v1/email_profile.json
    # https://app.futuresimple.com/apis/mailman/api/v1/email_profiles/check.json

    # V2
    # https://app.futuresimple.com/apis/mailman/api/v2/email_profile.json
    # https://app.futuresimple.com/apis/mailman/api/v2/email_profile.json?postpone=true

    # Inbox
    # https://app.futuresimple.com/apis/mailman/api/v2/synced_emails.json?mailbox=inbox&page=1&fields=items%2Ctotal_count&content=none

    # Sent
    # https://app.futuresimple.com/apis/mailman/api/v2/synced_emails.json?mailbox=outbox&page=1&fields=items%2Ctotal_count&content=none

    # Archived
    # https://app.futuresimple.com/apis/mailman/api/v2/synced_emails.json?mailbox=archived&page=1&fields=items%2Ctotal_count&content=none

    # Untracked
    # https://app.futuresimple.com/apis/mailman/api/v1/synced_emails/other.json?page=1


    ##########################
    # Call Functions
    ##########################

    # https://app.futuresimple.com/apis/voice/api/v1/voice_preferences.json
    # https://app.futuresimple.com/apis/voice/api/v1/call_lists.json
    # https://app.futuresimple.com/apis/voice/api/v1/call_outcomes.json
    # https://app.futuresimple.com/apis/voice/api/v1/call_scripts.json

    ##########################
    # Miscellaneous Functions
    ##########################

    # https://app.futuresimple.com/apis/core/api/v2/startup.json
    # https://app.futuresimple.com/apis/sales/api/v1/dashboard.json
    # https://app.futuresimple.com/apis/core/api/v1/public/currencies.json
    # https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=null
    # https://app.futuresimple.com/apis/voice/api/v1/voice_preferences.json
    # https://app.futuresimple.com/apis/sales/api/v1/integrations_status.json
    # https://app.futuresimple.com/apis/crm/api/v1/mailchimp/status.json

