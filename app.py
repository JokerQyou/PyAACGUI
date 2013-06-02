#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
GUI program for PyAac
'''
import wx
import cfg
import time
import random
import os
import sys
import tempfile
import threading
import subprocess

__author__ = "Joker Qyou"

class App(wx.App):
	'''
	Customized App class for PyAac GUI
	'''
	def __init__(self, redirect = True, filename = cfg.APP_LOG_FILE):
		wx.App.__init__(self, redirect, filename)

	def OnInit(self):
		frame = MainFrame()
		frame.Show(True)
		return True

class MainFrame(wx.Frame):
	'''
	Customized Frame class for PyAac GUI
	'''
	def __init__(self):
		wx.Frame.__init__(self, None, -1, cfg.APP_NAME, size = (cfg.APP_START_WIDTH, cfg.APP_START_HEIGHT), style = wx.DEFAULT_FRAME_STYLE)
		self.SetMinSize((cfg.APP_START_WIDTH, cfg.APP_START_HEIGHT))
		sizer = wx.GridSizer(rows = 3, cols = 1, hgap = 20, vgap = 20)
		# mainPanel = wx.Panel(self, -1)
		# 用于存放队列文件路径
		self.filePath = []

		# Set menu bar items
		# Menu bar
		mainMenu = wx.MenuBar()
		# Menu item: File
		menuFile = wx.Menu()
		mainMenu.Append(menuFile, "文件")
		# Menu item: File > Open
		menuFileOpen = addMenuItem(self, menuFile, wx.ID_OPEN, "添加", event = wx.EVT_MENU, handler = self.OnFileOpen)
		# Menu item: Separator
		menuFile.AppendSeparator()
		# Menu item: File > Convert
		menuFileConvert = addMenuItem(self, menuFile, wx.NewId(), "转换", event = wx.EVT_MENU, handler = self.OnFileConvert)
		#Menu item: Separator
		menuFile.AppendSeparator()
		# Menu item: File > Exit
		menuFileQuit = addMenuItem(self, menuFile, wx.ID_EXIT, "退出", event = wx.EVT_MENU, handler = self.OnFileQuit)
		# Menu item: Help
		menuHelp = wx.Menu()
		# Menu item: Help > About
		menuHelpAbout = addMenuItem(self, menuHelp, wx.ID_ABOUT, "关于", event = wx.EVT_MENU, handler = self.OnHelpAbout)
		mainMenu.Append(menuHelp, "帮助")
		self.SetMenuBar(mainMenu)

		# Set tool bar items
		toolBar = self.CreateToolBar(wx.TB_VERTICAL)
		toolBarOpen = addSimpleTool(self, toolBar, wx.ID_OPEN, wx.Bitmap("icons/add.png"), "添加文件")
		toolBarQuit = addSimpleTool(self, toolBar, wx.ID_EXIT, wx.Bitmap("icons/quit.png"), "退出")
		toolBarConvert = addSimpleTool(self, toolBar, wx.NewId(), wx.Bitmap("icons/circle.png"), "转换", event = wx.EVT_TOOL, handler = self.OnFileConvert)
		toolBar.EnableTool(toolBarConvert.GetId(), False)
		toolBarAbout = addSimpleTool(self, toolBar, wx.ID_ABOUT, wx.Bitmap("icons/info.png"), "关于")
		self.toolBar = toolBar
		self.toolBarConvert = toolBarConvert

		# List Control
		self.list = wx.ListCtrl(self, -1, style = wx.LC_REPORT | wx.LC_HRULES)
		self.list.InsertColumn(0, "序号", format = wx.LIST_FORMAT_LEFT, width = 40)
		self.list.InsertColumn(1, "文件来源", format = wx.LIST_FORMAT_LEFT, width = 400)
		self.list.InsertColumn(2, "状态", format = wx.LIST_FORMAT_LEFT, width = 80)
		# Add list control to grid sizer so we dont have to manage it
		sizer.Add(self.list, 0, flag = wx.EXPAND | wx.ALL, border = 10)
		self.SetSizer(sizer)
		self.Fit()

	def OnHelpAbout(self, event):
		aboutInfo = wx.AboutDialogInfo()
		# aboutInfo.SetIcon(wx.Icon("icons/icon.png", wx.BITMAP_TYPE_PNG))
		aboutInfo.SetName(cfg.APP_NAME)
		aboutInfo.SetVersion(cfg.APP_VERSION)
		aboutInfo.SetDescription(cfg.APP_DESCRIPTION)
		aboutInfo.SetLicense(cfg.APP_LICENSE)
		aboutInfo.SetCopyright(cfg.APP_COPYRIGHT)
		aboutInfo.SetWebSite(cfg.APP_WEBSITE)
		for developer in cfg.APP_DEVELOPERS:
			aboutInfo.AddDeveloper(developer)
		for artist in cfg.APP_ARTISTS:
			aboutInfo.AddArtist(artist)
		dlgAbout = wx.AboutBox(aboutInfo)

	def OnFileOpen(self, event):
		defaultDir = os.path.expanduser('~')
		defaultFile = ""
		fileFilters = "Free Lossless Audio Codec (*.flac)|*.flac|WAVE audio (*.wav)|*.wav|Monkey's Audio (*.ape)|*.ape|Wave pack (*.wv)|*.wv|TTA audio (*.tta)|*.tta|TAK audio (*.tak)|*.tak|All files (*.*)|*.*"
		dlgFileOpen = wx.FileDialog(None, "Select an audio file", defaultDir, defaultFile, fileFilters, wx.OPEN | wx.MULTIPLE)
		if dlgFileOpen.ShowModal() == wx.ID_OK:
			fileSelected = dlgFileOpen.GetPaths()
			print "Selected file(s): %s ---- %s" % (fileSelected, time.asctime())
			self.filePath += fileSelected[:]
			self.filePath = rmDuplicates(self.filePath)
			if self.filePath:
				self.toolBar.EnableTool(self.toolBarConvert.GetId(), True)
			initFileList(self.filePath, self.list)
		dlgFileOpen.Destroy()

	def OnFileConvert(self, event):
		import string
		if not self.filePath:
			dlgAlert = wx.MessageDialog(None, "请先选择至少一个音频文件", "没有选择文件", wx.OK | wx.ICON_ERROR)
			dlgAlert.ShowModal()
			dlgAlert.Destroy()
		else:
			self.list.SetStringItem(0, 2, "转换中")
			self.progress = wx.ProgressDialog("文件转换进度", "正在处理... 共 %d 个文件, 来自 %s" % (len(self.filePath), os.path.dirname(self.filePath[0].encode(sys.getfilesystemencoding()))), len(self.filePath), style = wx.PD_AUTO_HIDE)
			self.convertor = Convertor(self)
			self.convertor.start()

	def successAttention(self):
		dlgSuccess = wx.MessageDialog(None, "所有文件转换完毕", "文件队列处理完毕", wx.OK | wx.ICON_INFORMATION)
		dlgSuccess.ShowModal()
		dlgSuccess.Destroy()

	def updateProgress(self, current, newmsg):
		self.list.SetStringItem(current - 1, 2, "完成")
		self.list.SetStringItem(current, 2, "转换中")
		self.flag = self.progress.Update(current, newmsg = newmsg)

	def OnFileQuit(self, event):
		wx.Exit()

class Convertor(threading.Thread):
	'''
	Customized Thread class for PyAac
	'''
	def __init__(self, caller):
		threading.Thread.__init__(self)
		self.caller = caller
		
	def run(self):
		for singleFile in self.caller.filePath:
			currentFile = singleFile.encode(sys.getfilesystemencoding())
			currentProgress = self.caller.filePath.index(singleFile) + 1
			if not os.path.splitext(currentFile)[1] == "wav":
				'''
				先转换为 WAVE 格式的临时文件，
				再将 WAVE 格式的临时文件转换为 AAC 格式的目标文件，
				然后对目标文件写入音频标签，
				最后删除临时文件。
				TODO: 使用 neroAacTag 程序写入音频文件标签
				'''
				tempFile = os.path.join(cfg.TEMP_DIR, randomStr(12) + ".wav")
				toWave = subprocess.Popen(["mplayer",\
										  "-vo", "null",\
										  "-ao", "pcm:file=" + tempFile,\
										  currentFile]).wait()
				if toWave == 0:
					targetFile = os.path.splitext(currentFile)[0] + ".m4a"
					print targetFile
					toAac = subprocess.Popen(["neroAacEnc",\
											 "-br", str(cfg.AAC_BITRATE),\
											 "-2pass",\
											 "-ignorelength",\
											 "-lc",\
											 "-if", tempFile,\
											 "-of", targetFile], stdin = subprocess.PIPE)
					while not toAac.returncode == 0:
						toAac.poll()
					rmTempFile = os.remove(tempFile)
					#Media info tags operations
					import mediainfo
					mediaTags = mediainfo.getInfo(currentFile)
					AACTag = ["neroAacTag", targetFile]
					for _tagKey in mediaTags:
						if mediaTags[_tagKey].strip():
							AACTag.append("-meta:" + _tagKey + "=" + mediaTags[_tagKey])
					print AACTag
					writeAACTag = subprocess.Popen(AACTag)
					while not writeAACTag.returncode == 0:
						writeAACTag.poll()
					wx.CallAfter(self.caller.updateProgress, currentProgress, "正在处理... %d / %d, 来自 %s" % (currentProgress, len(self.caller.filePath), os.path.dirname(currentFile)))
					print "%s converted ---- %s" % (currentFile, time.asctime())
			else:
				'''
				对于 WAVE 格式的源文件无需生成临时文件。
				并且 WAVE 格式文件不携带任何音频标签。
				'''
				targetFile = os.path.splitext(currentFile)[0] + ".m4a"
				toAac = subprocess.Popen(["neroAacEnc",\
										 "-br", str(cfg.AAC_BITRATE),\
										 "-2pass",\
										 "-ignorelength",\
										 "-lc",\
										 "-if", currentFile,\
										 "-of", targetFile], stdin = subprocess.PIPE)
				while not toAac.returncode == 0:
					toAac.poll()
				wx.CallAfter(self.caller.updateProgress, currentProgress, "正在处理... %d / %d, 来自 %s" % (currentProgress, len(self.caller.filePath), os.path.dirname(currentFile)))
				print "%s converted ---- %s" % (currentFile, time.asctime())
		wx.CallAfter(self.caller.successAttention)

def addMenuItem(self, parent, id, text, event = None, handler = None):
	'''
	为指定菜单创建菜单项
	Args:
		self: wx.Frame 对象
		parent: 所属的菜单
		id: 菜单项的 ID
		text: 菜单项上的文本
		event: 要监听的事件
		handler: 处理器
	Returns:
		生成的菜单项对象
	'''
	_menuItem = parent.Append(id, text)
	if event and handler:
		self.Bind(event, handler, _menuItem)
	return _menuItem

def addSimpleTool(self, parent, id, bitmap, text, event = None, handler = None):
	'''
	为指定工具栏添加工具
	Args:
		self: wx.Frame 对象
		parent: 所属的工具栏
		id: 工具的 ID
		bitmap: Bitmap 对象, 工具上的图像
		text: 工具栏的提示文本
		event: 要监听的事件
		handler: 处理器
	Returns:
		menu item
	'''
	_toolBarItem = parent.AddSimpleTool(id, bitmap, text)
	if event and handler:
		self.Bind(event, handler, _toolBarItem)
	return _toolBarItem

def initFileList(fileList, listCtrl):
	'''
	使用给定的列表初始化列表控件
	Args:
		fileList: 包含所有文件路径的列表
		listCtrl: wx.ListCtrl 对象
	Returns:
		None
	'''
	# 清空列表控件中的项目
	listCtrl.DeleteAllItems()
	for _file in fileList:
		_i = fileList.index(_file)
		_index = listCtrl.InsertStringItem(_i, str(_i + 1))
		listCtrl.SetStringItem(_index, 1, _file)
		listCtrl.SetStringItem(_index, 2, "等待")

def rmDuplicates(inputList):
	'''
	列表去重
	Args:
		inputList: 要处理的列表
	Returns:
		处理后的列表
	'''
	return list(set(inputList))

def randomStr(length):
	'''
	提供指定长度的随机字符串
	Args:
		length: int, 随机字符串的长度
	Returns:
		生成的随机字符串
	'''
	return "".join(random.sample(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "Z", "Y", "X", "W", "V", "U", "T", "S", "R", "Q", "P", "O", "N", "M", "L", "K", "J", "I", "H", "G", "F", "E", "D", "C", "B", "A", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], length)).replace(" ","")


def main():
	if not cfg.TEMP_DIR:
		cfg.TEMP_DIR = tempfile.gettempdir()
	app = App(True)
	print "%s ---- %s" % ("App launched.", time.asctime())
	app.MainLoop()

if "__main__" == __name__:
	main()
