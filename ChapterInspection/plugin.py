#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# By: SpaceSkyNet

import re
from lxml import etree
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QPushButton, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView,
                             QProgressBar, QApplication, QHBoxLayout, QVBoxLayout, QTableWidget)
from PyQt5.QtCore import Qt
import sys, os

styleSheet = '''
#BlueProgressBar {
    margin: 2px;
    text-align: center;
    border: 2px solid #A9A9A9;
    background-color: #FFFFFF;
}
#BlueProgressBar::chunk {
    background-color: #2196F3;
}
'''

class askSetting(QDialog):

    def __init__(self,
                 app=None,
                 parent=None,
                 bk=None,
                 items=None):

        super(askSetting, self).__init__(parent)

        self.app = app
        self.items = items
        
        self.setWindowIcon(QIcon(os.path.join(bk._w.plugin_dir, 'ChapterInspection', 'plugin.png')))
        
        V_layout = QVBoxLayout()     
        H_layout = QHBoxLayout()
        self.chapter_table = QTableWidget(self)
        self.chapter_table = self.setChapterTable(self.chapter_table, bk)
        
        V_layout.addWidget(self.chapter_table)
        H_layout.addStretch(0)
        self.recheck_btn = QPushButton('重新检查', self)
        self.recheck_btn.clicked.connect(lambda: (self.recheckChapter(bk)))
        self.recheck_btn.setFocusPolicy(Qt.StrongFocus)
        H_layout.addWidget(self.recheck_btn)
        
        H_layout.addStretch(1)
        self.exit_btn = QPushButton('关闭', self)
        self.exit_btn.clicked.connect(lambda: (self.bye(items)))
        self.exit_btn.setFocusPolicy(Qt.StrongFocus)

        H_layout.addWidget(self.exit_btn)
        V_layout.addLayout(H_layout)
        self.setLayout(V_layout)
        self.setWindowTitle(' 分章检查 ')
        self.setFixedSize(900, 500)
    
    def setChapterTable(self, chapter_table, bk):
        chapter_check = checkChapter(bk)
        chapters_len = len(chapter_check)
        chapter_table.setRowCount(chapters_len)
        chapter_table.setColumnCount(3)
        chapter_table.setColumnWidth(0, 300)
        chapter_table.setColumnWidth(1, 450)
        chapter_table.setColumnWidth(2, 50)
        chapter_table.horizontalHeader().setStretchLastSection(True)
        chapter_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        chapter_table.verticalHeader().setDefaultSectionSize(15)
        chapter_table.setHorizontalHeaderLabels(['章节标题', '章节长度', '结果'])
        max_chapter_len = max([chapter_len for _, chapter_len, _ in chapter_check])
        for row in range(chapters_len):
            chapter_name, chapter_len, chapter_result = chapter_check[row]
            chapter_result = '异常' if chapter_result else ''
            chapter_table.setItem(row, 0, QTableWidgetItem(chapter_name))
            pbar = QProgressBar(self, textVisible=True, objectName="BlueProgressBar")
            pbar.setMinimum(0)
            pbar.setMaximum(max_chapter_len)
            pbar.setValue(chapter_len)
            pbar.setFormat("%v")
            chapter_table.setCellWidget(row, 1, pbar)
            chapter_table.setItem(row, 2, QTableWidgetItem(chapter_result))
        chapter_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return chapter_table
    
    def recheckChapter(self, bk):
        self.chapter_table = self.setChapterTable(self.chapter_table, bk)
        QMessageBox.information(self, '提示信息', '重新检查完毕！', QMessageBox.Ok)      
        
    
    def bye(self, items):
        self.close()
        self.app.exit(1)

def getChapterInfo(bk):
    NCX_id = bk.gettocid()
    if not NCX_id:
        print('ncx file is not exists!')
        os._exit(-1)
    
    NCX_original = bk.readfile(NCX_id)
    NCX_original_xml = etree.XML(NCX_original.encode(encoding = "utf-8"))
    chapter_info = []
    for i in NCX_original_xml.xpath("//*"):
        chapter_name, chapter_href = '', ''
        if "navPoint" in i.tag:
            for j in i.xpath('*'):
                if 'content' in j.tag:
                    for key, value in j.items():
                        if key == 'src':
                            chapter_href = value
                elif 'navLabel' in j.tag:
                    chapter_name = j.xpath('*')[0].text
            chapter_info.append((chapter_name, chapter_href))
    #print(chapter_info)
    return chapter_info
    
def stripHtmlTags(content):
    re_h = re.compile('</?\w+[^>]*>')
    content = re_h.sub('', content)
    return content

def intervalRecursion(L, R, max_frequency, interval, sum, all_sum, max_index):
    if max_frequency >= 1.0 or R - L == max_index: return (0, max_index)
    if sum / all_sum >= max_frequency: return (L, R)
    if L > 0 and R < max_index:
        i_L, i_R = interval[L - 1], interval[R + 1]
        if i_L > i_R:
            if (sum + i_R) / all_sum >= max_frequency: return (L, R + 1)
            elif (sum + i_L) / all_sum >= max_frequency: return (L - 1, R)
        else:
            if (sum + i_L) / all_sum >= max_frequency: return (L - 1, R)
            elif (sum + i_R) / all_sum >= max_frequency: return (L, R + 1)
        if (sum + i_L + i_R) / all_sum >= max_frequency: return (L - 1, R + 1)
        return intervalRecursion(L - 1, R + 1, max_frequency, interval, sum + i_L + i_R, all_sum, max_index)
    elif L == 0:
        index_R = min(R + 1, max_index)
        i_R = interval[index_R]
        if (sum + i_R) / all_sum >= max_frequency: return (L, R + 1)
        return intervalRecursion(L, R + 1, max_frequency, interval, sum + i_R, all_sum, max_index)
    else:
        index_L = max(L - 1, 0)
        i_L = interval[index_L]
        if (sum + i_L) / all_sum >= max_frequency: return (L - 1, R)
        return intervalRecursion(L - 1, R, max_frequency, interval, sum + i_L, all_sum, max_index)
        

def maxFrequencyInterval(interval, key, max_frequency = 0.8, parts = 10):
    Min, Max = key(interval[0]), key(interval[-1])
    Max = Max + 10 - (Max - Min) % 10
    part_interval_lens = []
    i, cnt = 0, 0
    for num in interval:
        num = key(num)
        p_R = Min + i * (Max - Min) // parts
        if num <= p_R: 
            cnt += 1
        else: 
            i += 1
            part_interval_lens.append(cnt)
            cnt = 1
    part_interval_lens.append(cnt)
    #print(part_interval_lens, len(part_interval_lens))
    max_len, max_pos = max(part_interval_lens), 0
    for i in range(len(part_interval_lens)):
        if part_interval_lens[i] == max_len:
            max_pos = i
            break
    #print(i, i, max_frequency, part_interval_lens, max_len, len(interval), len(part_interval_lens) - 1)
    L, R = intervalRecursion(i, i, max_frequency, part_interval_lens, max_len, len(interval), len(part_interval_lens) - 1)
    return (Min + (L - 1) * (Max - Min) // parts, Min + R * (Max - Min) // parts)
    

def checkChapter(bk):
    chapter_info = getChapterInfo(bk)
    chapter_check = []
    for i, (chapter_name, chapter_href) in enumerate(chapter_info):
        pos = chapter_href.find('#')
        if pos != -1: chapter_href = chapter_href[:pos]
        chapter_id = bk.href_to_id(chapter_href)
        #print(chapter_href, chapter_id)
        chapter_content = bk.readfile(chapter_id)
        chapter_len = len(stripHtmlTags(chapter_content))
        chapter_check.append([i, chapter_len, False])
    key=lambda x: x[1]
    chapter_check.sort(key = key)
    L, R = maxFrequencyInterval(chapter_check, key)
    chapter_check.sort(key = lambda x: x[0])
    for i in range(len(chapter_check)):
        chapter_check[i][0] = chapter_info[i][0]
        if key(chapter_check[i]) < L or key(chapter_check[i]) > R:
            chapter_check[i][2] = True
    #print(L, R, chapter_check)
    print('All is Checked!')
    #os.system('pause')
    return chapter_check

def checkChapterRunner(bk):
    #chapter_check = checkChapter(bk)
    items = {'max_frequency': 0.8, 'parts': 10}
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)
    ask = askSetting(app=app, items=items, bk=bk)
    ask.show()
    rtnCode = app.exec_()
    
    print("Success!")
    return 0

def run(bk):
    return checkChapterRunner(bk)