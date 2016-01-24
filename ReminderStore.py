# coding: utf-8
import reminders
import json

class ReminderStore():
	
	def __init__(self, namespace = 'Pythonista', to_json = False, cache = False):
		self.json = to_json
		self.cached = cache
		self.cache = {}
		self.list_calendar = None
		all_calendars = reminders.get_all_calendars()
		for calendar in all_calendars:
			if calendar.title == namespace:
				self.list_calendar = calendar
				break
		if not self.list_calendar:
			new_calendar = reminders.Calendar()
			new_calendar.title = namespace
			new_calendar.save()
			self.list_calendar = new_calendar
		self.items = {}
		self._refresh(force = True)
		
	def _refresh(self, force = False):
		if self.cached and not force:
			return
		list_reminders = reminders.get_reminders(self.list_calendar)
		for item in list_reminders:
			self.items[item.title] = item
			if self.cached:
				self.cache[item.title] = item.notes
				
	def refresh_cache(self):
		delta = { "added": set(), "deleted": set(), "changed": set() }
		has_delta = False
		list_reminders = reminders.get_reminders(self.list_calendar)
		self.items = {}
		new_cache = {}
		for item in list_reminders:
			self.items[item.title] = item
			new_cache[item.title] = item.notes
			if not item.title in self.cache:
				has_delta = True
				delta['added'].add(item.title)
			else:
				if item.notes <> self.cache[item.title]:
					has_delta = True
					delta['changed'].add(item.title)
				del self.cache[item.title]
		if len(self.cache) > 0:
			has_delta = True
			for key in self.cache:
				delta['deleted'].add(key)
		self.cache = new_cache
		return delta if has_delta else None	
			
	def __setitem__(self, id, content):
		id = self._effective_id(id)
		r = self.items[id] if id in self else reminders.Reminder(self.list_calendar)
		r.title = id
		r.notes = json.dumps(content, ensure_ascii=False) if self.json else content
		self.items[id] = r
		r.save()
		if self.cached:
			self.cache[id] = r.notes
		
	def __getitem__(self, id):
		id = self._effective_id(id)
		if id in self:
			content = self.cache[id] if self.cached else self.items[id].notes
			return json.loads(content) if self.json else content
		else:
			return None
			
	def __delitem__(self, id):
		id = self._effective_id(id)
		if id in self:
			reminders.delete_reminder(self.items[id])
			del self.items[id]
			if self.cached:
				del self.cache[id]
		else:
			raise KeyError
			
	def _effective_id(self, id):
		return id if isinstance(id, basestring) else str(id)
			
	def __len__(self):
		self._refresh()
		return len(self.items)
	
	def __str__(self):
		printable = {}
		self._refresh()
		for key in self:
			printable[key] = self[key]
		return str(printable)
			
	def __iter__(self):
		self._refresh()
		return iter(self.items.keys())
					
	def __contains__(self, id):
		if not id in self.items:
			self._refresh()
		return id in self.items
					
if __name__ == "__main__":
					
	content = '''ReminderStore is a [Pythonista](http://omz-software.com/pythonista/) persistence provider. It uses the ```reminders``` module to store the values in a specific list in the iOS Reminders app.
'''
						
	namespace = 'ReminderStore Demo'
	store = ReminderStore(namespace)
	
	id = 'intro'
	content = '''ReminderStore is a [Pythonista](http://omz-software.com/pythonista/) persistence provider. It uses the ```reminders``` module to store the values in a specific list in the iOS Reminders app.
'''

	store[id] = content
	print 'ITEMS IN STORE: ' + str(len(store))
	print
	print 'PRINT CONTENTS'
	print store
	print
	if id in store: print 'VALIDATED: ' + id + ' in store'
	print
	print 'ITERATE ALL CONTENTS'
	for key in store:
		print 'Key: ' + key + ' - ' + store[key]
	del store[id]
	
	print

	store = ReminderStore(namespace, to_json=True)
	
	id = { 'not': 'string' }
	content = { 'complex': 'structure serialization' }
	
	store[id] = content
	print 'JSON: ' + store[id]['complex']
	del store[id]
	
	store = ReminderStore(namespace, cache = True)
	
	store['to be deleted'] = 'sample'
	store['to be changed'] = 'sample'
	
	# Simulate changes to the Reminders synced from another device
	
	# Add
	a = reminders.Reminder(store.list_calendar)
	a.title = 'has been added'
	a.notes = 'sample'
	a.save()
	
	# Change
	list_reminders = reminders.get_reminders(store.list_calendar)
	for item in list_reminders:
		if item.title == 'to be changed':
			item.notes = 'new value'
			item.save()
	
	# Delete
	reminders.delete_reminder(store.items['to be deleted'])
	
	diff = store.refresh_cache()
	
	print
	print 'DIFF: ' + str(diff)
	
	del store['to be changed']
	del store['has been added']
	
	print
	print 'ITEMS IN STORE: ' + str(len(store))
	print 