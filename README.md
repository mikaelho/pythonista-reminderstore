# ReminderStore

Key-value store using iOS Reminders for persistence and distribution across iOS devices.

## Introduction

ReminderStore is a [Pythonista](http://omz-software.com/pythonista/) persistence provider. It uses the `reminders` module to store the values in a specific list in the iOS Reminders app. If you set that list to be distributed across your iOS devices, you get a free cloud-based storage for your app data, suitable for prototyping different distributed use cases.

## API

Create a store object providing the name of the Reminders list to be created/used:

`store = ReminderStore(namespace, to_json=False, cache=False)`

Using the store API is similar to using a dict:

* Store values: `store['key'] = 'value'`
* Retrieve values: `store['key']`
* Iterate through all items: `for key in store: print store[key]`
* Delete items: `del store['key']`
* Count of items in store: `len(store)`
* Check existence: `'key' in store`
* Print all contents: `print str(store)`

A convenience method `new_item(value='')` creates a new item in the store and returns an 8-character random key for it.

If you want to store structures instead of plain strings, set `to_json=True`. Store and retrieval operations will then serialize and restore the values to and from JSON.

Setting `cache=True` reduces direct access to the Reminders app. Use the `refresh_cache()` method to refresh the cache and get information on any background changes. See Notes below for more details.

## Notes

* Key is stored as the title of the reminder, and value in the notes field.
* Reminder titles are not unique, but ReminderStore uses an intermediate dict to enforce uniqueness. Results are likely to be unproductive if you create duplicate titles manually. 
* Key is used as-is if it is a plain or unicode string. Otherwise `str()` is called on key before using it.
* By default, ReminderStore goes to the Reminders app to get the latest information. This is somewhat inefficient since checking for new items always requires loading the full list. There are two cases where you might to prefer to activate the intermediate caching instead:
  * If you have no-one making any updates remotely, cache will be more efficient and will never need manual refreshing.
  * If you want to get more control over when any background changes are applied in your app, use the caching and call `refresh_cache` to check and process changes. The method returns None if there are no changes, or a dict with `added`, `deleted` and `changed` sets if there are changes. Each set contains the keys of the stored items that were inserted, deleted or had their contents modified, respectively. You can use this info to e.g. remove deleted items from the UI, or inform the user of a conflict and let them decide which version to keep.
* Note that iOS Reminders app provides no support for complex atomic transactions or referential integrity between items.