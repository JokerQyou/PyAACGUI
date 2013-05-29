import json
# -*- coding: utf-8 -*-
'''
Configuration loader for PyAac GUI program
'''
cfgF = file('config.cfg', 'r')
cfgJSON = json.load(cfgF)
cfgF.close()
#Parse each key as a configuration parameter
for key in cfgJSON:
	# value = str(cfgJSON[key])
	if type(cfgJSON[key]) in [str, unicode]:
		value = u'\"%s\"' % cfgJSON[key]
	else:
		value = str(cfgJSON[key])
	exec(key + u'=' + value)
