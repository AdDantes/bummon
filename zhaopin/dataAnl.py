from pyecharts import Pie, TreeMap, Bar, WordCloud
from pymongo import MongoClient
import math
import jieba
import jieba.analyse
import re
from time import time
from concurrent.futures import ThreadPoolExecutor


position = input('请输入职位名称:')
city = '北京'

class DataAnalysis():
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.zhaopin
        self.lagou = self.db.lagou
        self.position = position
        self.city = city
        self.filename = 'D:\GIT\zhaopin\stopwords.txt'
        self.search_name = list(self.lagou.find({'search_name': self.position}))


    def salary(self):
        print('{}:薪资占比图 正在生成中。。。。。。。。。。。'.format(self.position))
        values = [0, 0, 0, 0, 0, 0]
        for i in self.search_name:
            salary_list = re.findall('\d+', i['salary'])
            if len(salary_list) > 1:
                ave = (int(salary_list[0]) + int(salary_list[1])) / 2

            else:
                ave = int(salary_list[0])

            ave_salary = math.ceil(ave)
            if ave_salary < 5:
                values[0] += 1
            elif ave_salary in range(5, 10):
                values[1] += 1
            elif ave_salary in range(10, 20):
                values[2] += 1
            elif ave_salary in range(20, 30):
                values[3] += 1
            elif ave_salary in range(30, 40):
                values[4] += 1
            else:
                values[5] += 1
        key = ['5k以下', '5k-10k', '10k-20k', '20k-30k', '30k-40k', '40k以上']
        pie = Pie("{}薪资比例".format(self.position), title_pos='center', width=900)
        pie.add("salary", key, values, center=[40, 50], is_random=True, radius=[30, 75], rosetype="area",
                is_legend_show=False, is_label_show=True, is_more_utils=True)
        pie.render('{}_薪资.html'.format(self.position))

    def education(self):
        print('{}:学历占比图 正在生成中。。。。。。。。。。。'.format(self.position))
        edu = ['本科', '大专', '应届毕业生', '硕士', '博士']
        data = []
        # search_name = lagou.find({'search_name':position})
        for i in edu:
            edu_count = self.lagou.count({'education': i, 'search_name': self.position})
            # print(edu_count)
            data.append({'value': edu_count, 'name': i})
        tree_map = TreeMap("{}学历要求".format(self.position), width=1200, height=600)
        tree_map.add('学历水平', data, is_label_show=True, label_pos='inside')
        tree_map.render('{}_学历.html'.format(self.position))

    def city_salary(self):
        """
        各城市职位薪资情况对比
        :return:
        """
        print('{}:城市薪资对比 正在生成中。。。。。。。。。。。'.format(self.position))
        cities = []
        for i in self.search_name:
            cities.append(i['city'])
        cities = list(set(cities))
        city_salary = []
        city_name = []
        for city in cities:
            city_infor = self.lagou.find({'search_name': self.position,'city':city})
            ave_salary = 0
            j=0
            for infor in city_infor:
                salary = infor['salary']
                salary_list = re.findall('\d+', salary)
                if len(salary_list) > 1:
                    ave = (int(salary_list[0]) + int(salary_list[1])) / 2
                else:
                    ave = int(salary_list[0])
                ave = math.ceil(ave)
                ave_salary += ave
                j+=1
            if j >= 10:
                city_name.append(city)
                ave_salary = math.ceil(ave_salary / j)
                city_salary.append(ave_salary)

        bar = Bar(self.position, '城市薪资对比')
        bar.add('{}:城市薪资对比'.format(self.position), city_name, city_salary, is_label_show=True, is_more_utils=True)
        bar.render('{}_城市薪资对比.html'.format(self.position))

    def work_years(self):
        print('{}:工作年限图 正在生成中。。。。。。。。。。。'.format(self.position))
        work_years = ['应届毕业生', '1年以下', '1-3年', '3-5年', '5-10年', '不限']
        data = []
        for i in work_years:
            year_count = self.lagou.count({'workYear': i})
            data.append(year_count)
        bar = Bar(self.position, '工作经验要求')
        bar.add('工作年限', work_years, data, is_label_show=True, is_more_utils=True)
        bar.render('{}_工作年限.html'.format(self.position))

    def run(self):
        self.city_salary()
        self.salary()
        self.education()
        self.work_years()


class Getkeyword(DataAnalysis):
    def write_work_duty(self):
        work_duty = ''
        for i in self.search_name:
            work_duty = work_duty + i['work_duty'] + '/'
        duty_path = '{}_岗位职责.txt'.format(self.position)
        with open(duty_path, 'a', encoding='utf8') as f:
            f.write(work_duty)
        self.get_keywords(duty_path)

    def write_work_requirement(self):
        work_requirement = ''
        for i in self.search_name:
            work_requirement = work_requirement + i['work_requirement'] + '/'
        requirement_path = '{}_职业要求.txt'.format(self.position)
        with open(requirement_path, 'a', encoding='utf8') as f:
            f.write(work_requirement)
        self.get_keywords(requirement_path)

    # 创建停用词list
    def stopwordslist(self, filepath):
        stopwords = [line.strip() for line in open(filepath, 'r').readlines()]
        return stopwords

    def seg_sentence(self, sentence):
        sentence_seged = jieba.cut(sentence.strip())
        stopwords = self.stopwordslist(self.filename)  # 这里加载停用词的路径
        outstr = ''
        for word in sentence_seged:
            if word not in stopwords:
                if word != '\t':
                    outstr += word
                    outstr += " "
        return outstr  # 返回

    def get_keywords(self, path):
        duty_req = re.findall('_(.*?).txt', path)[0]
        with open(path, 'r', encoding='utf8') as f:
            inputs = f.read()
            content = self.seg_sentence(inputs)
            keywords = jieba.analyse.extract_tags(content, topK=100, withWeight=True)
            name = []
            value = []
            for item in keywords:
                name.append(item[0])
                value.append(item[1])
        self.word_cloud(name, value, duty_req)

    def word_cloud(self, name, value, duty_req):
        wordcloud = WordCloud(width=1300, height=620)
        wordcloud.add("", name, value, word_size_range=[20, 100])
        wordcloud.render('{}_{}.html'.format(self.position, duty_req))

    def run(self):
        print('{}:岗位职责云词图 正在生成中。。。。。。。。。。。'.format(self.position))
        self.write_work_duty()
        print('{}:职业需求云词图 正在生成中。。。。。。。。。。。'.format(self.position))
        self.write_work_requirement()


if __name__ == '__main__':
    start = time()
    anal = DataAnalysis()
    anal.run()
    key = Getkeyword()
    key.run()
    end = time()
    print(end - start)
