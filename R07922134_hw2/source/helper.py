last_names = set("陳林黃張李王吳劉蔡楊許鄭謝洪郭邱曾廖賴徐周葉蘇莊呂江何蕭羅高潘簡朱鍾彭游詹胡施沈余盧梁趙顏柯翁魏孫戴范方宋鄧杜傅侯曹薛丁卓馬阮董唐温藍蔣石古紀姚連馮歐程湯黄田康姜汪白鄒尤巫鐘黎涂龔嚴韓袁金童陸夏柳凃邵")

def is_chinese(string):
    for chart in string:
        if chart < u'\u4e00' or chart > u'\u9fff':
            return False
    return True

def isName(term):
    if len(term) < 2 or len(term) > 4 or (not is_chinese(term)):
        return False

    if term[0] in last_names:
        return True