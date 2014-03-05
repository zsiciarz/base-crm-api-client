Introduction
============

The original BaseCRM API Client focused on replicating the [Base API Documentation](http://dev.futuresimple.com/api/overview) and an enhanced version of this branch can be found under the "OfficialSupport" branch.  If FutureSimple expands their official API, we may port the relevant feature into this branch.

In early 2014, it became clear that FutureSimple was not keeping the API documents up to date:

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
 
FutureSimple made it clear that the search function was not set in stone and the same likely applies to these additional features.  Users desiring officially supported features should download and use the limited OfficialSupport branch.  Users willing to risk intermittent issues to take advantage of these advanced features should use master.

NOTE:  IF YOU ARE USING THE EXPANDED CLIENT, TAKE FULL ADVANTAGE OF THE FUNCTION DOCS.  IN SOME CASES (ESPECIALLY PAGING) THE CLIENT USES INTERFACES THAT DO NOT COMPLY WITH THE DEV.FUTURESIMPLE.COM SPECIFICATION.

How it works
============

This client give access to GET/POST/PUT/DELETE API calls through user-friendly functions like get_contacts().

To set up a connection to base, simply run:

    from base_client import BaseAPIService
    base_conn = BaseAPIService(email="YOUR_EMAIL", password="YOUR_PASSWORD")

    # This will set up a service that returns Python native (usually dict) responses.  To return json or xml, add the argument format='json' or format='xml'

Then you can start working with base objects immediately.  Examples (assuming you have instantiated `base_conn` as above).

Examples of getting objects:

    # Return the first page of incoming deals (output will be a json response)
    base_conn.get_deals(page=1, stage='incoming')

    # Return the first page of contacts (output will be a json response)
    base_conn.get_contacts(page=1)

Example creation and modification of contact:

    # Create a new contact (json object will be stored as a response)
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
* LEAD_FILTERS - a list of legal parameters for searching leads
* LEAD_SORTS - a list of legal parameters for sorting leads


Available methods:
==================
Please see the code itself for documentation - function headers are reasonably descriptive.  Currently, the module has limited functionality.

Accounts Functions:
* get_accounts()

Contacts Functions:
* get_contacts(page=1)
* get_contact(contact_id)
* search_contacts(filters, sort_by, sort_order, tags_exclusivity, page)
* create_contact(self, contact_info, person=True)
* update_contact(self, contact_info, contact_id, person=True)
* update_contact_tags(contact_id, tags, action='add') (other actions are "remove" or "replace")
* get_contact_notes(contact_id,  page=0)
* get_contact_note(contact_id, note_id)
* create_contact_note(self, contact_id, note_content)
* update_contact_note(self, contact_id, note_content, note_id)

Deals Functions:
* get_deals(page=1, stage='incoming')
* get_deal(deal_id)
* search_deals(filters, sort_by, sort_order, tags_exclusivity, page)
* create_deal(deal_info)
* update_deal(deal_info, deal_id)
* update_deal_tags(deal_id, tags, action='add') (other actions are "remove" or "replace")
* get_deal_notes(deal_id, page=0)
* get_deal_note(deal_id, note_id)
* create_deal_note(deal_id, note_content)
* update_deal_note(self, deal_id, note_content, note_id)

Leads Functions:
* get_leads(page=0)
* get_lead(lead_id)
* search_leads(filters, sort_by, sort_order, tags_exclusivity, page)
* get_lead_notes(lead_id, page=0)
* get_lead_note(lead_id, note_id)

Sources Functions:
* get_sources(self, other=0)

Tags Functions:
* get_tags(page=0)

Ongoing Development:
====================
This was put together relatively quickly.  There are a couple of areas where improvements will be necessary:
* Error handling
* Filling out methods to deal with all types of objects

Feel free to get involved if you want.