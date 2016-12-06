import os

p = '/path/to/some/dir'

def get_paths(pathname):
	
	""" If pathname is the string '/path/to/dir', this returns
	the list ['/path', '/path/to', '/path/to/dir'] """
	
	#functools.reduce(lambda a, b: a+[a[-1]+b+'/'], '/path/to/some/dir'.split('/'), [''])
	#[dir.rsplit("/",n)[0] for n in range(dir.count("/")-1,0,-1)]
	
	subpath = os.path.dirname(pathname)
	if subpath != '/':
		return get_paths(subpath) + [pathname]
	else:
		return [pathname]
		
paths = get_paths(p)
paths = [[p, os.path.basename(p)] for p in paths]
print paths
