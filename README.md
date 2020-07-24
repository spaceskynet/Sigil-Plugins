# Sigil Plugins By SpaceSkyNet

There are some sigil plugins written by me.

一些 Sigil 插件。

## s2t - t2s (简繁中文转换)

使用 OpenCC 库进行转换，使用前请先在Python环境上安装OpenCC，或者将`s2t-t2s`文件夹下的`opencc.zip`解压放入Sigil程序目录的`Lib\site-packages`下。

![s2t - t2s](https://i.loli.net/2020/07/24/AMsH1bY2S5VctD6.png)

## AliasReplace (别名替换)

解决译制小说中存在的译名不统一的问题，需要提供一张`csv`对照表。

格式如下（可提供多行）:

`id, target_name, origin_name_1, origin_name_2 ...`

**Ex:** `1, Bob, Pop, Pob, Bop`

默认读取插件目录下的`NameMap.csv`。

![AliasReplace](https://i.loli.net/2020/07/24/e3ikV8blvNsZGEA.png)

## ChapterInspection (分章检查)

检查各章节的字数是否符合集中趋势，不符合输出`异常`。

![ChapterInspection](https://i.loli.net/2020/07/24/gQlXOP1zVauoqxG.png)
