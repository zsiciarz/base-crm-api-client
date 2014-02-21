import urllib
import urllib2
import logging

import json

logger = logging.getLogger(__name__)

CONTACT_PARAMS = {
    'name': '',
    'last_name': '',
    'first_name': '',
    'is_organisation': '',
    'contact_id': '',
    'email': '',
    'phone': '',
    'mobile': '',
    'twitter': '',
    'skype': '',
    'facebook': '',
    'linkedin': '',
    'address': '',
    'city': '',
    'country': '',
    'title': '',
    'description': '',
    'industry': '',
    'website': '',
    'fax': '',
    'tag_list': '',
    'private': '',
}

DEAL_PARAMS = {
    'name': '',
    'entity_id': '',
    'scope': '',
    'hot': 'false',
    'deal_tags': '',
    'contact_ids': '',
    'source_id': '',
    'stage': '',
}

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
        auth_url = '/authentication.json'
        params = urllib.urlencode({
            'email': email,
            'password': password,
        })

        try:
            data = urllib2.urlopen(self.resource['sales'] + auth_url, params).read()
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
    # Accounts Functions
    ##########################
    def get_accounts(self):
        """
        Get current account.
        """
        account_url = '/account' + self.format

        url = self.resource['sales'] + account_url

        req = urllib2.Request(url, headers=self.header)
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    ##########################
    # Helper Functions
    ##########################
    def _get_data(self, full_url):
        """
        This function submits the url using GET and returns the data for the requested URL.  If the format is set to
        'native', the function assumes the URL is set to json and converts the response using loads()
        """
        print 'Loading URL %s' % (full_url)
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
        req = urllib2.Request(full_url, data=params, headers=self.header)
        response = urllib2.urlopen(req)
        data = response.read()
        if self.convert_to_native:
            data = json.loads(data)
        return data

    def _put_data(self, full_url, params):
        """
        This function submits the params to the url using PUT and returns the data for the requested URL.  If the format
        is set to 'native', the function assumes the URL is set to json and converts the response using loads()
        """
        req = urllib2.Request(full_url, data=params, headers=self.header)
        req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()
        if self.convert_to_native:
            data = json.loads(data)
        return data

    def _format_url(self, url, format=None):
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
    def _build_deal_url(self, deal_id=None, contact_id=None, format=None):
        """
        Returns a URL to obtain either all deals (deal_id=None) or a specific deal (deal_id=integer). For a list of
        deals nested under another object, do not include a deal_id and include one (and only one) of the following
        parent identifiers:
         - contact_id
        If this is the terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
        """
        if contact_id is not None:
            url = self._build_contact_url(contact_id)
        else:
            url = self.resource['sales']
        url += '/deals'
        if deal_id is not None:
            url += '/%s' % (deal_id)
        return self._format_url(url, format)

    def _build_lead_url(self, lead_id = None, format=None):
        """
        Returns a URL to obtain either all leads (lead_id=None) or a specific lead (lead_id=integer). If this is the
        terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
        """
        url = self.resource['leads'] + '/leads'
        if lead_id is not None:
            url += '/%s' % (lead_id)
        return self._format_url(url, format)

    def _build_contact_url(self, contact_id = None, company_id = None, deal_id = None, format=None):
        """
        Returns a URL to obtain either all contacts (contact_id=None) or a specific contact (contact_id=integer). For a
        list of contacts nested under another object, do not include a contact_id and include one (and only one) of the
        following parent identifiers:
         - company_id (technically, this is the ID of the BaseCRM contact object for the company)
         - deal_id
        If this is the terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
        """
        if deal_id is not None:
            url = self._build_deal_url(deal_id)
        elif company_id is not None:
            url = self._build_contact_url(company_id)
        else:
            url = self.resource['sales'] + '/contacts'
        # Build URL through nested checks
        if contact_id is not None:
            if company_id is None:
                url += '/%s' % (contact_id)
            else:
                raise ValueError("Cannot include both a contact and company ID.")
        return self._format_url(url, format)

    def _build_note_url(self, note_id=None, contact_id=None, lead_id=None, deal_id=None, format=None):
        """
        Returns a URL to obtain either all notes (note_id=None) or a specific note (note_id=integer). For a
        list of notes nested under another object, do not include a note_id and include one (and only one) of the
        following parent identifiers:
         - contact_id
         - lead_id
         - deal_id
        If this is the terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
        """
        if contact_id is not None:
            url = self._build_contact_url(contact_id)
        elif lead_id is not None:
            url = self._build_lead_url(lead_id)
        elif deal_id is not None:
            url = self._build_deal_url(deal_id)
        else:
            raise ValueError("Notes URL constructor requires a valid object (lead, contact, deal).")
        # Add note data
        url += '/notes'
        if note_id is not None:
            url += '/%s' % (note_id)
        return self._format_url(url, format)

    def _build_reminder_url(self, reminder_id=None, contact_id=None, lead_id=None, deal_id=None, format=None):
        """
        Returns a URL to obtain either all reminders (reminder_id=None) or a specific reminder (reminder_id=integer).
        For a list of reminders nested under another object, do not include a reminder_id and include one (and only one)
        of the following parent identifiers:
         - contact_id
         - lead_id
         - deal_id
        If this is the terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
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
        return self._format_url(url, format)

    def _build_tags_url(self, tag_id=None, format=None):
        """
        Returns a URL to obtain either all tags (tag_id=None) or a specific tag (tag_id=integer). If this is the
        terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
        """
        url = self.resource['tags']
        url += '/taggings'
        if tag_id is not None:
            url += '/%s' % (tag_id)
        return self._format_url(url, format)

    def _build_sources_url(self, source_id=None, contact_id=None, lead_id=None, deal_id=None, format=None):
        """
        Returns a URL to obtain either all sources (source_id=None) or a specific source (source_id=integer). If this is
        the terminal object, include a format:
         - '.json'
         - '.xml'
         - 'native'
        """
        url = self.resource['sales']
        url += '/sources'
        if source_id is not None:
            url += '/%s' % (source_id)
        return self._format_url(url, format)

    ##########################
    # Deals Functions
    ##########################
    def get_deals(self, page=1, stage='incoming'):
        """
        Gets deal objects in batches of 20.
        Arguments:
            page = the set of deals to return. 1 (default) returns the first 20.
            stage = the stage of deals to return - see DEAL_STAGES list for details.
        """
        url = self._build_deal_url(format=self.format)
        # Append parameters
        params = urllib.urlencode({
            'page': page,
            'stage': stage,
            })
        full_url = url + '?' + params
        return self._get_data(full_url)

    def get_deal(self, deal_id):
        """
        Gets the deal with the given deal_id. Returns the deal info.
        """
        full_url = self._build_deal_url(deal_id=deal_id, format=self.format)
        return self._get_data(full_url)

    def create_deal(self, deal_info):
        """
        Creates a new deal in base, given proper deal parameters in deal_info argument.
        Proper parameters are shown in the DEAL_PARAMS dictionary.
        Returns a json or xml reponse.
        """
        return self._upsert_deal(deal_info=deal_info)

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
        deal_data = self._get_deal(deal_id=deal_id, force_json=True)
        deal_data_dict = json.loads(deal_data)
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

    def _upsert_deal(self, deal_info={}, deal_id=None):
        """
        PRIVATE FUNCTION:
        Creates a new deal if deal_id = None.
        Otherwise, edits the deal with the given deal_id.
        """
        deals_url = '/deals'
        if deal_id != None:
            deals_url += '/%s' % str(deal_id)
        deals_url += self.format

        url = self.resource['sales'] + deals_url

        if deal_info == {} or (('name' not in deal_info.keys() \
                or 'entity_id' not in deal_info.keys()) and deal_id == None):
            return "Missing required attributes 'name' or 'entity_id'"

        final_params = {}

        for key in deal_info.keys():
            if key not in DEAL_PARAMS.keys():
                return "%s is not a legal deal attribute" % key
            else:
                final_params[key] = deal_info[key]

        params = urllib.urlencode(_unicode_dict(final_params))

        req = urllib2.Request(url, data=params, headers=self.header)
        if deal_id != None:
            req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    def get_deal_notes(self, deal_id, page=0):
        """
        Gets deal notes.
        """
        url = self._build_note_url(deal_id=deal_id, format=self.format)
        # Append parameters
        params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + params
        return self._get_data(full_url)

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
        url_base_template += self.format

        url = self.resource['sales'] + url_base_template

        params = urllib.urlencode({'note[content]': unicode(note_content).encode('utf-8')})

        req = urllib2.Request(url, data=params, headers=self.header)
        if note_id != None:
            req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    ##########################
    # Contact Functions
    ##########################
    def get_contacts(self, page=1):
        """
        Gets contact objects in batches of 20.
        Arguments:
            page = the set of contacts to return. 1 (default) returns the first 20.
        """
        url = self._build_contact_url(format=self.format)
        # Append parameters
        params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + params
        return self._get_data(full_url)

    def get_contact(self, contact_id):
        """
        Gets the contact with the given contact_id. Returns the contact info.
        """
        full_url = self._build_contact_url(contact_id=contact_id, format=self.format)
        return self._get_data(full_url)

    def create_contact(self, contact_info, person=True):
        """
        Creates a new contact based on contact_info with fields shown in CONTACT_PARAMS.
        Assumes the contact is a person.  If the contact is a company, use person=False
        Returns a json or xml response.
        """
        return self._upsert_contact(contact_info=contact_info, contact_id=None, person=person)

    def create_contact_new(self, contact_info, person=True):
        """
        Creates a new contact based on contact_info with fields shown in CONTACT_PARAMS.
        Assumes the contact is a person.  If the contact is a company, use person=False
        Returns a json or xml response.
        """
        return self._upsert_contact_new(contact_info=contact_info, contact_id=None, person=person)

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

    def _upsert_contact(self, contact_info={}, contact_id=None, person=True):
        """
        Creates a new contact if contact_id == None.
        Otherwise, edits contact with the given id.
        """
        contacts_url = '/contacts'
        if contact_id != None:
            contacts_url += '/%s' % str(contact_id)
        contacts_url += self.format

        url = self.resource['sales'] + contacts_url

        CONTACT_PARAMS['is_organisation'] = 'false'
        if not person:
            CONTACT_PARAMS['is_organisation'] = 'true'

        # If we are creating a new contact, we must have name and last_name parameters
        # and we always must have some parameter
        if contact_info == {} or \
                (contact_id == None and 'name' not in contact_info.keys() and
                'last_name' not in contact_info.keys()):
            return

        final_params = {}

        for key in contact_info.keys():
            if key not in CONTACT_PARAMS.keys():
                return
            else:
                final_params['contact[' + key + ']'] = contact_info[key]

        params = urllib.urlencode(_unicode_dict(final_params))

        req = urllib2.Request(url, data=params, headers=self.header)

        if contact_id != None:
            req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    def _upsert_contact_new(self, contact_info={}, contact_id=None, person=True):
        """
        Creates a new contact if contact_id == None.
        Otherwise, edits contact with the given id.
        """
        full_url = self._build_contact_url(contact_id=contact_id, format=self.format)

        CONTACT_PARAMS['is_organisation'] = 'false'
        if not person:
            CONTACT_PARAMS['is_organisation'] = 'true'

        # If we are creating a new contact, we must have name and last_name parameters
        # and we always must have some parameter
        if contact_info == {} or\
           (contact_id == None and 'name' not in contact_info.keys() and
            'last_name' not in contact_info.keys()):
            return

        final_params = {}

        for key in contact_info.keys():
            if key not in CONTACT_PARAMS.keys():
                return
            else:
                final_params['contact[' + key + ']'] = contact_info[key]

        params = urllib.urlencode(_unicode_dict(final_params))

        if contact_id is None:
            return self._post_data(full_url, params)
        else:
            return self._put_data(full_url, params)

    def get_contact_notes(self, contact_id, page=0):
        """
        Gets contact notes.
        """
        url = self._build_note_url(contact_id=contact_id, format=self.format)
        # Append parameters
        params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + params
        return self._get_data(full_url)

    def get_contact_note(self, contact_id, note_id):
        """
        Gets contact object.
        """
        full_url = self._build_note_url(note_id=note_id, contact_id=contact_id, format=self.format)
        return self._get_data(full_url)

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

    def _upsert_contact_note(self, note_content='', contact_id, note_id=None):
        """
        PRIVATE FUNCTION
        Creates a new note for a given contact_id with content note_content, if note_id == None.
        Otherwise, edits the note with the given note_id.
        """

        url_base_template = '/contacts/%s/notes' % str(contact_id)
        if note_id != None:
            url_base_template += '/%s' % str(note_id)
        url_base_template += self.format

        url = self.resource['sales'] + url_base_template

        params = urllib.urlencode({'note[content]': unicode(note_content).encode('utf-8')})

        req = urllib2.Request(url, data=params, headers=self.header)
        if note_id != None:
            req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        data = response.read()

        return data

    ##########################
    # Lead Functions
    ##########################
    def get_leads(self, page=0):
        """
        Gets lead objects in batches of 20.
        Arguments:
            page = the set of deals to return. 0 (default) returns the first 20.
        """
        url = self._build_lead_url(format=self.format)
        # Append parameters
        params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + params
        return self._get_data(full_url)

    def get_lead(self, lead_id):
        """
        Gets the deal with the given deal_id. Returns the deal info.
        """
        full_url = self._build_lead_url(lead_id=lead_id, format=self.format)
        return self._get_data(full_url)

    def get_lead_notes(self, lead_id, page=0):
        """
        Gets lead notes.
        """
        url = self._build_note_url(lead_id=lead_id, format=self.format)
        # Append parameters
        params = urllib.urlencode({
            'page': page,
            })
        full_url = url + '?' + params
        return self._get_data(full_url)

    def get_lead_note(self, lead_id, note_id):
        """
        Gets lead object.
        """
        full_url = self._build_note_url(note_id=note_id, lead_id=lead_id, format=self.format)
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
        sources_url = '/sources' + self.format
        url = self.resource['sales'] + sources_url
        if other == 1:
            params = urllib.urlencode({
                'other': other,
            })
        else:
            params = ''
        # Append parameters
        full_url = url + '?' + params

        req = urllib2.Request(full_url, headers=self.header)
        response = urllib2.urlopen(req)
        data = response.read()

        return data

