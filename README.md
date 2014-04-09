Introduction
============

The [original BaseCRM API Client (for Python)](http://github.com/npinger/base-crm-api-client) focused on replicating the [Base API Documentation](http://dev.futuresimple.com/api/overview) and an enhanced version of this branch can be found under the "OfficialSupport" branch.  If FutureSimple expands their official API, we may port the relevant feature into this branch.

In early 2014, it became clear that FutureSimple was not regularly updating their API documents:

 - Zapier was able to detect New Objects (Contacts, Deals, Leads) and changes in Deal Stages.  While it was possible to detect these by brute force (e.g. pulling down all of these objects), it seemed unlikely that this approach was used.
 - @claytondaley contacted FutureSimple to find out if searching was available through the API and was provided a URL example for an undocumented search capability.
 - In light of this undocuented feature, @claytondaley reviewed the messages exchanged by the BaseCRM web interface and identified calls for lots of additional features:
   - Count functions for various object types (avoiding the need to return a huge results document to check the metadata)
   - Activities (emails, calls, tasks)
   - Email Integration (inbox, sent, archived, and untracked emails)
   - Lists of existing values for Cities, Regions, Countries, Zip_Codes, Stages, Loss Reasons, Currencies, and Statuses
   - Calls that return a list of fields that are sortable and filterable
   - Additional views for Deals like top_deals, total_pipeline, and deals/by_ids (supporting multiple ids)
   - Configuration checks like integration status, voice and email preferences, etc.
 
FutureSimple made it clear that the search functionality was not set in stone and the same likely applies to these additional features.  Users desiring officially supported features should download and use the [client from the original repo] (https://github.com/npinger/base-crm-api-client) (or the OfficialSupport branch here).  Users willing to risk intermittent issues to take advantage of a more advanced feature set should use master.

NOTE:  IF YOU ARE USING THE EXPANDED CLIENT, TAKE FULL ADVANTAGE OF THE FUNCTION DOCS.  IN SOME CASES (ESPECIALLY PAGING) THE CLIENT USES INTERFACES THAT DO NOT COMPLY WITH THE DEV.FUTURESIMPLE.COM SPECIFICATION.

How it works
============

This client give access to GET/POST/PUT/DELETE API calls through user-friendly functions like get_contacts().

To set up a connection to base, simply run:

    from base_client import BaseAPIService
    base_conn = BaseAPIService(email="YOUR_EMAIL", password="YOUR_PASSWORD")

    # This will set up a service that returns Python native (i.e. dict or list) responses.  To return json or xml, add the argument format='json' or format='xml'.
    
Alternatively, supply an API token:
    
    base_conn = BaseAPIService(token="YOUR_API_TOKEN")
    
(You can find your API token in Settings -> Manage Account.)

Then you can start working with base objects immediately.  Examples (assuming you have instantiated `base_conn` as above).

Examples of getting objects:

    # Return the first page of incoming deals (output will be a python dict)
    base_conn.get_deals(page=1, stage='incoming')

    # Return the first page of contacts (output will be a python list)
    base_conn.get_contacts(page=1)

Example creation and modification of contact:

    # Create a new contact (dict object will be stored as a response)
    response = base_conn.create_contact(contact_info={'first_name': 'John', 'last_name': 'Doe'})

    # Get the id of the new contact
    contact_id = response['contact']['id']

    # Update the contact's phone number
    base_conn.update_contact(contact_info={'phone': '555-555-5555'}, contact_id=contact_id)

Important Variables:
* CONTACT_PARAMS - a list of legal parameters for a contact in the `contact_info` argument.  See the [base api documentation](http://dev.futuresimple.com/api/overview) for required parameters.
* CONTACT_FILTERS - a list of legal parameters for searching contacts
* CONTACT_SORTS - a list of legal parameters for sorting contacts
* DEAL_PARAMS - a list of legal parameters for a deal in `deal_info` argument.  See the [base api documentation](http://dev.futuresimple.com/api/overview) for required parameters.
* DEAL_STAGES - legal options for stage argument in get_deals
* DEAL_FILTERS - a list of legal parameters for searching deals
* DEAL_SORTS - a list of legal parameters for sorting deals
* LEAD_PARAMS - a list of legal parameters for a lead in the `lead_info` argument.  See the [base api documentation](http://dev.futuresimple.com/api/overview) for required parameters.
* LEAD_FILTERS - a list of legal parameters for searching leads
* LEAD_SORTS - a list of legal parameters for sorting leads

Available methods:
==================
Please see the code itself for documentation - function headers are reasonably descriptive.  The biggest feature missing from the current implementation is the ability to delete objects.

Accounts Functions:
* get_accounts()

Contacts Functions:
* get_contacts(contact_ids, page, per_page)
* get_deal_contacts(deal_id, page, per_page)
* get_contact(contact_id)
* search_contacts(filters, sort_by, sort_order, tags_exclusivity, page)
* create_contact(self, contact_info)
* update_contact(self, contact_info, contact_id)

Deals Functions:
* get_deals(page, stage)
* get_deal(deal_id)
* search_deals(filters, sort_by, sort_order, tags_exclusivity, page)
* create_deal(deal_info)
* update_deal(deal_info, deal_id)
(Deal) Sources Functions:
* get_sources(type)
* get_source(source_id)

Leads Functions:
* get_leads(page, per_page)
* get_lead(lead_id)
* search_leads(filters, sort_by, sort_order, tags_exclusivity, page, per_page)
* create_lead(lead_info)
* update_lead(lead_info, lead_id)

Feed (i.e. Activity) Functions
* get_feed(type)
* get_contact_feed(contact_id)
* get_contact_feed_emails(contact_id)
* get_contact_feed_notes(contact_id)
* get_contact_feed_calls(contact_id)
* get_contact_feed_tasks_completed(contact_id)
* get_deal_feed(deal_id)
* get_deal_feed_emails(deal_id)
* get_deal_feed_notes(deal_id)
* get_deal_feed_calls(deal_id)
* get_deal_feed_tasks_completed(deal_id)
* get_lead_feed(lead_id)
* get_lead_feed_emails(lead_id)
* get_lead_feed_notes(lead_id)
* get_lead_feed_calls(lead_id)
* get_lead_feed_tasks_completed(lead_id)

Tags Functions:
* get_tags(type, page)
* get_tag(tag_id)
* get_contact_tags(page)
* get_contact_tags_alt(page)
* get_deal_tags(page)
* get_lead_tags(page)
* tag_contacts(tag_list, contact_ids)
* untag_contacts(tag, contact_ids)
* retag_contact(tag_list, contact_id)
* update_contact_tags(taglist_contact_id)
* tag_deals(tag_list, deal_ids)
* untag_deals(tag, deal_ids)
* retag_deal(tag_list, deal_id)
* update_deal_tags(taglist_deal_id)
* tag_leads(tag_list, lead_ids)
* untag_leads(tag, lead_ids)
* retag_lead(tag_list, lead_id)
* update_lead_tags(taglist_lead_id)

Notes
* get_notes(page)
* get_note(note_id)
* update_note(content, note_id)
* get_contact_notes(contact_id,  page=0)
* create_contact_note(self, contact_id, note_content)
* update_contact_note(self, contact_id, note_content, note_id)
* get_deal_notes(deal_id, page=0)
* create_deal_note(deal_id, note_content)
* update_deal_note(self, deal_id, note_content, note_id)
* get_lead_notes(lead_id, page=0)

Tasks
* get_tasks(status, due, page)
* get_tasks_by_date_range(due_from, due_to, status, page)
* get_task(task_id)
* get contact_tasks(contact_id)
* get deal_tasks(deal_id)
* get lead_tasks(lead_id)

Reminders
* get_contact_reminders(contact_id)
* get_deal_reminders(deal_id)

Ongoing Development:
====================
Because we are not using the official API specification, the client could cease to function at any time.  If you're actively using the client, we encourage you to work with us to ensure it stays functional.

There are also opportunities for enhancement:
* Naming Conventions - As the API has expanded, some of the calls (in particular tags) don't fit as cleanly in the original naming scheme.  A standard naming scheme should be established and documented with due consideration given to not-yet-implemented API calls.
* Error handling - There is presently no effort to catch and handle errors during the API call and only transient efforts to check types and values.
* Optional arguments - Several optional arguments (like per_page) may work on more functions than currently implemented.  We should generate a document to keep track of which parameters have been tested against which calls to avoid unnecesarry duplication of tests.
* Metadata - Some of the get and search calls return metadata that could be processed and cached (or used to support functions returning exclusively metadata).  In other cases, summary data (e.g. counts) are supported through special API calls.
* Unimplemented Data Fields - To populate the BaseCRM UI, there are a variety of identified calls that return lists of cities, states (i.e. "regions"), countries, and zip codes.
* Unimplemented Types - API calls to several object types (emails, calls) have been identified but not implemented

We welcome issue reports and pull requests.
