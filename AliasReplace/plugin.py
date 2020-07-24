#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# By: SpaceSkyNet

import csv
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtWidgets import (QDialog, QPushButton, QFileDialog,
                             QLabel, QApplication, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
import sys, os

class askSetting(QDialog):

    def __init__(self,
                 app=None,
                 parent=None,
                 bk=None,
                 items=None):

        super(askSetting, self).__init__(parent)

        self.app = app
        self.items = items

        self.setWindowIcon(QIcon(os.path.join(bk._w.plugin_dir, 'AliasReplace', 'plugin.png')))
        
        H_layout = QHBoxLayout()
        V_layout = QVBoxLayout()
        
        choice_filepath = ''
        self.filepath_label = QLabel(choice_filepath)
        #self.filepath_label.setMaximumSize(250, 15)
        H_layout.addWidget(self.filepath_label)
        self.file_btn = QPushButton('选取文件', self)
        self.file_btn.clicked.connect(lambda: (self.open_file(bk)))
        self.file_btn.setFocusPolicy(Qt.StrongFocus)
        H_layout.addStretch(1)
        H_layout.addWidget(self.file_btn)
        V_layout.addLayout(H_layout)
        self.btn = QPushButton('确定', self)
        self.btn.clicked.connect(lambda: (self.bye(items)))
        self.btn.setFocusPolicy(Qt.StrongFocus)
        
        V_layout.addWidget(self.btn)

        self.setLayout(V_layout)
        self.setWindowTitle(' 别名替换 ')
        self.setFixedSize(400, 100)
    def open_file(self, bk):
        filePath, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.path.join(bk._w.plugin_dir, 'AliasReplace'), 
        "Csv file(*.csv)")
        #print(filePath)
        fontWidth = QFontMetrics(self.filepath_label.font())
        elideNote = fontWidth.elidedText(filePath, Qt.ElideMiddle, 250)
     
        self.filepath_label.setText(elideNote)
        self.filepath_label.setToolTip(filePath)

        self.items['choice_filepath'] = filePath
        print('Chosen:', filePath)


    def bye(self, items):
        self.close()
        self.app.exit(1)

def convName(bk):
    items = {'choice_filepath': ''}
    
    app = QApplication(sys.argv)
    ask = askSetting(app=app, items=items, bk=bk)
    ask.show()
    rtnCode = app.exec_()
    if rtnCode != 1:
        print('User abort by closing Setting dialog')
        return -1
    if not items['choice_filepath']:
        filepath = os.path.join(bk._w.plugin_dir, 'NameMap', 'NameMap.csv')
        if os.path.exists(filepath):
            items['choice_filepath'] = filepath
            print('Auto choice the default file!')
        else:
            print('No file is selected!')
            return -1
    
    csv_filepath = items['choice_filepath']
    replace_list = []
    print("Selected:", csv_filepath)
    with open(csv_filepath, encoding = "utf-8") as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            target_name = row[1]
            row = row[2:]
            for origin_name in row:
                if origin_name: replace_list.append((origin_name, target_name))
    
    #print(replace_list)
    
    # convert html/xhtml files
    for (file_id, _) in bk.text_iter():
        file_href = bk.id_to_href(file_id)
        file_basename = bk.href_to_basename(file_href)
        file_mime = bk.id_to_mime(file_id)
        html_original = bk.readfile(file_id)
        for replace_name in replace_list:
            html_original = html_original.replace(*replace_name)
        bk.writefile(file_id, html_original)
        print('Changed:', file_basename, file_mime) 
    
    # convert ncx file
    NCX_id = bk.gettocid()
    if not NCX_id:
        print('ncx file is not exists!')
        return -1
    
    NCX_mime = bk.id_to_mime(NCX_id)
    NCX_href = bk.id_to_href(NCX_id)
    NCX_original = bk.readfile(NCX_id)
    for replace_name in replace_list:
        NCX_original = NCX_original.replace(*replace_name)
    bk.writefile(NCX_id, NCX_original)
    print('Changed:', NCX_href, NCX_mime)
    
    # convert opf file
    OPF_basename = 'content.opf'
    OPF_mime = 'application/oebps-package+xml'
    metadata = bk.getmetadataxml()
    for replace_name in replace_list:
        metadata = metadata.replace(*replace_name)
    bk.setmetadataxml(metadata)
    
    print('Changed:', OPF_basename, OPF_mime)
    
    print("Success!")
    return 0

def run(bk):
    return convName(bk)