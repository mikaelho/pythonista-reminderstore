# coding: utf-8
import reminders
import json

class ReminderStore():
	
	def __init__(self, namespace = 'Pythonista', to_json = False):
		self.json = to_json
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
		list_reminders = reminders.get_reminders(self.list_calendar)
		self.items = {}
		for item in list_reminders:
			self.items[item.title] = item
			
	def refresh(self, diff = False):
		print 'syart'
		prev = {}
		delta = { "added": set(), "deleted": set(), "changed": set() }
		has_delta = False
		if diff:
			for key in self.items:
				prev[key] = self.items[key].notes
		list_reminders = reminders.get_reminders(self.list_calendar)
		self.items = {}
		for item in list_reminders:
			self.items[item.title] = item
			print item.title
			if diff:
				if not item.title in prev:
					has_delta = True
					delta['added'].add(item.title)
				else:
					if item.notes <> prev[item.title].notes:
						has_delta = True
						delta['changed'].add(item.title)
					del prev[item.title]
		if diff and len(prev) > 0:
			has_delta = True
			for key in prev:
				delta['deleted'].add(key)
		return delta if has_delta else None		
			
	def __setitem__(self, id, content):
		id = self.effective_id(id)
		r = self.items[id] if id in self.items else reminders.Reminder(self.list_calendar)
		r.title = id
		r.notes = json.dumps(content, ensure_ascii=False) if self.json else content
		self.items[id] = r
		r.save()
		
	def __getitem__(self, id):
		id = self.effective_id(id)
		if id in self.items:
			content = self.items[id].notes
			return json.loads(content) if self.json else content
		else:
			return None
			
	def __delitem__(self, id):
		id = self.effective_id(id)
		if id in self.items:
			success = reminders.delete_reminder(self.items[id])
			del self.items[id]
			if not success:
				raise KeyError
		else:
			raise KeyError
			
	def effective_id(self, id):
		return id if isinstance(id, basestring) else str(id)
			
	def __len__(self):
		return len(self.items)
	
	def __str__(self):
		printable = {}
		for key in self:
			printable[key] = self[key]
		return str(printable)
			
	def __iter__(self):
		return iter(self.items.keys())
					
class DictDiff():
	def __init__(self, current_dict, past_dict):
		self.current_dict, self.past_dict = current_dict, past_dict
		self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
		self.intersect = self.set_current.intersection(self.set_past)
		self.has_changed = len(self.unchanged()) == len(self.set_current)
	def added(self):
		return self.set_current - self.intersect 
	def removed(self):
		return self.set_past - self.intersect 
	def changed(self):
		return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
	def unchanged(self):
		return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
					
if __name__ == "__main__":
					
	content = '''# ReminderStore
	
## Intro

ReminderStore is a [Pythonista](http://omz-software.com/pythonista/) persistence provider. It uses the ```reminders``` module to store the values in a specific list in the iOS Reminders app. If you set that list to be distributed across your iOS devices, you get a free cloud-based for your app data, suitable for prototyping different distributed use cases.

## Usage

See the end of the file for a simple example of storing and retrieving values in the store.

First argument to the constructor is the name of the list to be created in the Reminders app. Stored items are assumed to be unicode text, to be stored as-is. You can provide an optional ```to_json=True``` parameter for the constructor to store more complex items as JSON.
'''
						
	store = ReminderStore('Testing ReminderStore')
	id = 'item_id'
	store[id] = content
	print 'Items in store: ' + str(len(store))
	print store
	for key in store:
		print 'Key: ' + key
		print store[key]
	del store[id]
	print 'Items in store: ' + str(len(store))
