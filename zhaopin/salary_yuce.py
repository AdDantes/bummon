from pymongo import MongoClient
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import re
import math

"""职业薪资预测"""
client = MongoClient()
db = client['zhaopin']
# city = input('请输入城市名称:')
# education = input('请输入学历:')
position = '爬虫工程师'
# workYear = input('请输入工作年限')
lagou = db.lagou
lagou_data = lagou.find({'search_name': position})
data = pd.DataFrame(list(lagou_data))

del data['_id']

salary = []
for i in data['salary']:
    salary_list = re.findall('\d+', i)
    if len(salary_list) > 1:
        ave = (int(salary_list[0]) + int(salary_list[1])) / 2
    else:
        ave = int(salary_list[0])
    ave_salary = math.ceil(ave)

    if ave_salary < 5:
        j = '5k以下'
    elif ave_salary in range(5, 10):
        j = '5k-10k'
    elif ave_salary in range(10, 20):
        j = '10k-20k'
    elif ave_salary in range(20, 30):
        j = '20k-30k'
    elif ave_salary in range(30, 40):
        j = '30k-40k'
    else:
        j = '40k以上'
    salary.append(j)

# print(data.columns)
x = data[['city', 'education', 'search_name', 'workYear']]
y = salary

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
dv = DictVectorizer()
x_train = x_train.to_dict(orient='records')
# x_test = {'city':city, 'education':education,'search_name':position, 'workYear':workYear}
x_test = x_test.to_dict(orient='records')
x_train = dv.fit_transform(x_train)
x_test = dv.transform(x_test)
rf = RandomForestClassifier(max_depth=10, n_estimators=10)
rf.fit(x_train, y_train)
pre = rf.predict(x_test)
print(y_test)
score = rf.score(x_test, y_test)
print(pre)
print(score)

gs = GridSearchCV(rf, param_grid={'n_estimators': [5, 10, 15, 20, 25, 30]}, cv=5)
gs.fit(x_train, y_train)
y_predict = gs.predict(x_test)
print('使用随机森林并网格搜索优化参数后的精准度为：', gs.score(x_test, y_test))
print('在交叉验证中得到的最好结果：', gs.best_score_)
# print('每次交叉验证的结果：', gs.cv_results_)
print('最好的参数模型', gs.best_estimator_)
