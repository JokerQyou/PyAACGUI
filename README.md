PyAACGUI
========

将无损音频文件转换为使用 Nero AAC Codec 编码的高品质音乐。

在使用 Ubuntu 的过程中发现没有顺手的转换器，个人喜欢用 Nero AAC Codec ，但大部分图形界面转换器都不支持；脚本转换批量文件非常不方便，所以就写了这个。

##依赖##

* `MPlayer`
* Nero AAC Codec (包括 `neroAacEnc` 、`neroAacDec` 和 `neroAacTag` )
* `MediaInfo`
* `wxPython`

程序的本质只是透过 wxPython 提供的图形界面将上面这些软件粘合起来而已。

##使用##

现在功能基本可用，虽然比较丑陋（可能还有未发现的 BUG ）。

安装所有需要的程序后下载本项目，解压后运行 `gui` 文件即可。（如果提示没有权限请自行更改 `gui` 文件权限为可执行）

##授权##

BSD License ，见 BSD.license 文件 。

##作者##

[Joker Qyou](http://mynook.info)