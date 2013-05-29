#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MediaInfo parser for PyAacGUI
Requires: Unix MediaInfo program
'''
import os
import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element
import subprocess

__author__ = "Joker Qyou"

# 最终返回结果的容器
info = {
	"album": "",
	"artist": "",
	"title": "",
	"writer": "",
	"year": "",
	"genre": "",
	"track": "",
	"totaltracks": "",
	"comment": "",
	"composer": ""
}

# 外部 MediaInfo 程序返回的 XML 提取的属性与 Nero AAC Codec 的标准属性之间的对照
_tagPair = {
	"Album": "album",
	"Performer": "artist",
	"Track_name": "title",
	"Album_Performer": "writer",
	"Recorded_date": "year",
	"Genre": "genre",
	"Track_name_Position": "track",
	"Track_name_Total": "totaltracks",
	"Comment": "comment",
	"Composer": "composer"
	}

def _xml2dict(element):
	'''
	将 XML Element 转换为字典
	Code from: dingyaguang117 ( https://github.com/dingyaguang117 )
	'''
	assert isinstance(element, Element) 
	ret = {}
	for child in list(element):
		# print child.tag, child.text
		if len(child) != 0:
			value = _xml2dict(child)
		else:
			value = child.text
		if child.tag in ret:
			if type(ret[child.tag]) != list:
				ret[child.tag] = [ret[child.tag]]
			ret[child.tag].append(value)
		else:
			ret[child.tag] = value
	return ret


def getInfo(filePath):
	'''
	调用外部 MediaInfo 程序获取指定文件的媒体属性
	Args:
		filePath: 指定文件的完整路径
	Returns:
		包含 Nero AAC 标准属性的字典
	'''
	# 将直接修改这个模块的全局变量 info
	global info
	if not os.path.exists(filePath):
		# 文件不存在，则直接返回空的属性字典
		return info
	else:
		# 调用 MediaInfo 获取属性
		_infoPopen = subprocess.Popen(["mediainfo",\
									"--output=xml",\
									filePath],\
									stdout = subprocess.PIPE)
		_infoPopen.wait()
		# MediaInfo 会输出 XML 格式的属性列表
		_infoStr = _infoPopen.stdout
		_infoXML = ElementTree.parse(_infoStr)
		_infoXMLRoot = _infoXML.getroot()
		_infoDict = _xml2dict(_infoXMLRoot)
		_infoDict = _infoDict["File"]
		for _dict in _infoDict["track"]:
			if _dict.has_key("Complete_name"):
				_tagDict = _dict
		# 参考标准属性对照 _tagPair ，填充标准属性
		for _key in _tagDict:
			if _tagPair.has_key(_key):
				_tagValue = _tagDict[_key]
				_tagKey = _tagPair[_key]
				info.update({_tagKey: _tagValue})
		return info
