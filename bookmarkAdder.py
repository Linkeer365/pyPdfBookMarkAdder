from collections import namedtuple
import os

from PyPDF2 import PdfFileReader,PdfFileWriter

import numpy as np
import pandas as pd
import xlrd
import xlwt



bookmark_fields=["content","layer","page_num"]
Bookmark=namedtuple("Bookmark",bookmark_fields)

txt_dir="D:/pdf书签处理总站"

def bookmark_print(some_bookmark:Bookmark):
    for key,val in some_bookmark._asdict().items():
        print("{}: {}".format(key,val))
    print("One bookmark is printed!")

def file2lines(file_name:str,encoding_type:str):
    assert file_name.endswith(".txt")
    if txt_dir!=os.getcwd():
        os.chdir(txt_dir)
    if not encoding_type=="utf-16-le":
        print("Not utf-16-le as usual!")
    with open(file_name,"r",encoding=encoding_type) as f:
        return f.readlines()

def add_base_page_num(old_page_num,base_page_num):
    return old_page_num+base_page_num


def getToken_oneline(one_line:str,line_cnt:int,base_page_num:int):
    # 默认格式必须是/t开头（或者没有/t），再以/t结尾

    cur_idx=0
    cur_char=''
    one_line_len=len(one_line)
    one_line_layer=-1
    content_startat=-1
    while cur_idx!=one_line_len:
        cur_char=one_line[cur_idx]
        if cur_char!='\t':
            one_line_layer=cur_idx+1
            content_startat=cur_idx
            break
        cur_idx+=1

    one_line_content: str
    one_line_page_num_old: str
    one_line_content,one_line_page_num_old=(one_line[content_startat:]).rsplit("\t",maxsplit=1)
    one_line_page_num_old=one_line_page_num_old.replace("\n","")
    base_page_num:int
    one_line_page_num:str
    one_line_page_num=str(add_base_page_num(int(one_line_page_num_old),base_page_num))
    format_one_line_content="  ".join(one_line_content.split())

    one_line_y_position=704

    if one_line_layer==1:
        one_line_color="red"
    elif one_line_layer==2:
        one_line_color="blue"
    elif one_line_layer==3:
        one_line_color="mise"
    elif one_line_layer>3:
        one_line_color="black"


    # line_cnt 此处删去，若后面需要则加在第一个位子上
    one_line_tokens=[format_one_line_content,one_line_layer,one_line_page_num,one_line_y_position,one_line_color]

    print("Line Cnt:{}\nContent:{}\nLayer:{}\nPage_num:{}\nColor:{}\nn".format(line_cnt,format_one_line_content,one_line_layer,one_line_page_num,one_line_color))
    return one_line_tokens

def write2xls(one_file_tokens:[[]],file_name:str,fathers:[int]):

    # full 是我自己的
    # 普通的bookmark是给pdfb.exe 软件的

    writer=pd.ExcelWriter("{}.xls".format(file_name))
    writer2=pd.ExcelWriter("full_{}.xls".format(file_name))
    # https://zhuanlan.zhihu.com/p/28119708
    # 原先是下面这行，因为一开始把Level和Layer，还有Content之类的混了，现在注释掉，大家也知道大致是什么意思
    # data_flame=pd.DataFrame(data=one_file_tokens,columns=["Line Cnt","Content","Layer","Pagenum","Y position"])
    data_flame=pd.DataFrame(data=one_file_tokens,columns=["Bookmark","Level","Page","Y position","Color"])
    data_flame.to_excel(writer,"sheet1",index=False,columns=["Bookmark","Level","Page","Y position"])

    new_fathers=[]

    for father in fathers:
        if father=="null":
            new_father=father
        elif isinstance(father,int):
            new_father="第{}行".format(str(father+2))
        new_fathers.append(new_father)


    data_flame["Father"]=new_fathers

    data_flame.to_excel(writer2,"sheet1",index=False,columns=["Bookmark","Level","Page","Father","Color"])


    writer.save()
    writer2.save()
    print("Write done.")

# def write2json(one_file_tokens:[[]],file_name):
#     data_flame=pd.DataFrame(data=one_file_tokens,columns=["Bookmark","Level","Page","Y position"])
#     data_json=data_flame.to_json(orient="split",force_ascii=False)
#     print(data_json)

def get_fathers(layers):
    fathers = []
    idx = len(layers) - 1
    while idx >= 0:
        val = layers[idx]
        if val == 1:
            father = "null"
            fathers.append(father)
        else:
            idx2 = idx
            while idx2 != 0:
                val2 = layers[idx2]
                if val2 < val:
                    father = idx2
                    fathers.append(father)
                    break
                idx2 -= 1
        idx -= 1

    fathers = list(reversed(fathers))
    return fathers


def main():
    for each_file in os.listdir(txt_dir):
        if each_file.endswith(".txt"):
            print("文档名字：\t",each_file)
            # print_pagenum=int(input("打印页数:\t"))
            # doc_pagenum=int(input("文档页数:\t"))
            base_page_num=int(input("基页=文档页数-打印页数\n请输入基数:\t"))
            lines=file2lines(each_file,"utf-16-le")
            one_file_tokens=[]

            layers=[]
            page_nums=[]

            for each_idx,each_line in enumerate(lines):
                one_line_tokens=getToken_oneline(each_line,each_idx,base_page_num)
                layer=one_line_tokens[1]
                page_num=one_line_tokens[2]
                layers.append(layer)
                page_nums.append(page_num)

                one_file_tokens.append(one_line_tokens)

            # get father of each line.

            file_name = each_file[:-4]

            fathers=get_fathers(layers)
            # print("--**--")

            # pdf和txt必须同名
            pdf_fd=open(file_name+".pdf","rb")

            pdf_rd=PdfFileReader(pdf_fd)
            pdf_wt=PdfFileWriter()

            print("Whole num:\t",pdf_rd.getNumPages())

            pages=[pdf_rd.getPage(each_idx) for each_idx in range(pdf_rd.getNumPages())]

            print("page_nums:\t",page_nums)

            # pages=list(pdf_rd.pages)
            print(pages)
            # rgb?
            # 他应该是 green, blue, red 这样的顺序

            # https://tug.org/pracjourn/2007-4/walden/color.pdf
            # rgb 没错，只是你没意识到rgb能有0.3，0.2这种表示方法

            red_tup=(1,0,0.7)
            blue_tup=(0.4,0.1,0.7)
            mise_tup=(0.4,0.5,0.4)
            black_tup=(0,0,0)

            colors_tups={}

            colors_tups["red"]=red_tup
            colors_tups["blue"]=blue_tup
            colors_tups["mise"]=mise_tup
            colors_tups["black"]=black_tup

            addbookmark_objs=[None]*10000

            # 写入pdf文档

            for each_page in pages:
                pdf_wt.addPage(each_page)
            for each_idx,one_line_tokens in enumerate(one_file_tokens):
                page_num: str
                bookmark, layer, page_num, y_pos,color=one_line_tokens
                father_idx:str
                father_idx=fathers[each_idx]
                if father_idx=="null":
                    assert layer==1
                    print("Pagenum:\t",page_num)
                    addbookmark_obj=pdf_wt.addBookmark(title=bookmark,pagenum=int(page_num)-1,parent=None,color=red_tup,bold=True)
                    addbookmark_objs[each_idx]=addbookmark_obj
                    continue
                father_obj=addbookmark_objs[int(father_idx)]
                assert layer!=1
                addbookmark_obj = pdf_wt.addBookmark(title=bookmark, pagenum=int(page_num) - 1, parent=father_obj,
                                                     color=colors_tups[color])
                addbookmark_objs[each_idx] = addbookmark_obj

            if txt_dir!=os.getcwd():
                os.chdir(txt_dir)


            if not os.path.exists(file_name):
                os.mkdir(file_name)

            os.chdir(file_name)
            with open("bookmark_"+file_name+".pdf","wb") as f:
                pdf_wt.write(f)
                # print(one_line_tokens)
            write2xls(one_file_tokens,"bookmark_"+file_name,fathers=fathers)
            # write2json(one_file_tokens,file_name)
    print("done.")
            # print("**--**")

if __name__ == '__main__':
    main()








