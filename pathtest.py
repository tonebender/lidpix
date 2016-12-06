import os

p = '/path/to/some/dir'

def get_paths(pathname):
	
	""" If pathname is the string '/path/to/dir', this returns
	the list ['/path', '/path/to', '/path/to/dir'] """
	
	subpath = os.path.dirname(pathname)
	if subpath != '/':
		return get_paths(subpath) + [pathname]
	else:
		return [pathname]
		
s = get_paths(p)
print s
