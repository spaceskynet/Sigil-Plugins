#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# By: SpaceSkyNet

from lxml import etree
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QPushButton, QComboBox,
                             QLabel, QApplication, QVBoxLayout)
from PyQt5.QtCore import Qt
import sys, os

lang_lists = ['简体到繁体（OpenCC标准）', '繁体（OpenCC标准）到简体', '简体到繁体（中国台湾）', '繁体（中国台湾）到简体', '简体到繁体（中国香港）', '繁体（中国香港）到简体', '简体到繁体（中国台湾，包括常用词汇）', '繁体（中国台湾）到简体（包括常用词汇）', '繁体（OpenCC标准）到繁体（中国台湾）', '繁体（中国香港）到繁体（OpenCC 标准）', '繁体（OpenCC标准）到繁体（中国香港）', '繁体（OpenCC标准，旧字体）到日文新字体', '日文新字体到繁体（OpenCC 标准，旧字体）', '繁体（中国台湾）到繁体（OpenCC 标准）', ]
select_lang_json = ['s2t.json', 't2s.json', 's2tw.json', 'tw2s.json', 's2hk.json', 'hk2s.json', 's2twp.json', 'tw2sp.json', 't2tw.json', 'hk2t.json', 't2hk.json', 't2jp.json', 'jp2t.json', 'tw2t.json', ]
target_langcode_lists = ['zh-CHT', 'zh-CN', 'zh-TW', 'zh-CN', 'zh-HK', 'zh-CN', 'zh-TW', 'zh-CN', 'zh-TW', 'zh-CHT', 'zh-HK', 'ja-JP', 'zh-CHT', 'zh-CHT']

class askSetting(QDialog):

    def __init__(self,
                 app=None,
                 parent=None,
                 bk=None,
                 items=None):

        super(askSetting, self).__init__(parent)

        self.app = app
        self.items = items

        self.setWindowIcon(QIcon(os.path.join(bk._w.plugin_dir, 's2t-t2s', 'plugin.png')))
        global lang_lists
        self.choice_list = lang_lists
        
        layout = QVBoxLayout()

        choice_info = '选择转换方式：'
        layout.addWidget(QLabel(choice_info))
        self.lang_combobox = QComboBox(self)
        self.lang_combobox.addItems(self.choice_list)
        self.lang_combobox.setCurrentIndex(items['current_index'])
        layout.addWidget(self.lang_combobox)
        self.lang_combobox.currentIndexChanged.connect(lambda: self.on_combobox_func())
        #print('UI', items)
        self.btn = QPushButton('确定', self)
        self.btn.clicked.connect(lambda: (self.bye(items)))
        self.btn.setFocusPolicy(Qt.StrongFocus)

        layout.addWidget(self.btn)

        self.setLayout(layout)
        self.setWindowTitle(' 简繁转换设置 ')
    def on_combobox_func(self):
        self.items['current_index'] = self.lang_combobox.currentIndex()

    def bye(self, items):
        self.close()
        self.app.exit(1)

def convLang(bk):
    items = {'current_index': 0}
    
    app = QApplication(sys.argv)
    ask = askSetting(app=app, items=items, bk=bk)
    ask.show()
    rtnCode = app.exec_()
    if rtnCode != 1:
        print('User abort by closing Setting dialog')
        return -1
    try:
        import opencc
    except:
        print('Please install the OpenCC Lib!')
        return -1
    
    global lang_lists, select_lang_json, target_langcode_lists
    
    c_index = items['current_index']
    print("Selected:", lang_lists[c_index])
    converter = opencc.OpenCC(select_lang_json[c_index])
    
    # convert html/xhtml files
    for (file_id, _) in bk.text_iter():
        file_href = bk.id_to_href(file_id)
        file_basename = bk.href_to_basename(file_href)
        file_mime = bk.id_to_mime(file_id)
        html_original = bk.readfile(file_id)
        html_original_conv = converter.convert(html_original)
        bk.writefile(file_id, html_original_conv)
        print('Changed:', file_basename, file_mime) 
    
    # convert ncx file
    NCX_id = bk.gettocid()
    if not NCX_id:
        print('ncx file is not exists!')
        return -1
    
    NCX_mime = bk.id_to_mime(NCX_id)
    NCX_href = bk.id_to_href(NCX_id)
    NCX_original = bk.readfile(NCX_id)
    NCX_original = converter.convert(NCX_original)
    bk.writefile(NCX_id, NCX_original)
    print('Changed:', NCX_href, NCX_mime)
    
    # convert opf file
    OPF_basename = 'content.opf'
    OPF_mime = 'application/oebps-package+xml'
    metadata = bk.getmetadataxml()
    metadata_xml = etree.XML(metadata)
    
    for i in metadata_xml.xpath('//child::*'): 
        if 'language' in i.tag: 
            i.text = target_langcode_lists[c_index]

    metadata_conv = converter.convert(etree.tostring(metadata_xml, encoding="utf-8", xml_declaration=True).decode('utf8'))
    bk.setmetadataxml(metadata_conv)
    
    guide = bk.getguide()
    guide_conv = []
    for i in range(len(guide)):
        guide_conv.append([])
        for j in range(len(guide[i])):
            guide_conv[i].append(converter.convert(guide[i][j]))
    bk.setguide(guide_conv)
    print('Changed:', OPF_basename, OPF_mime)
    
    print("Success!")
    return 0

def run(bk):
    return convLang(bk)