from pymongo import MongoClient

client = MongoClient()
db = client['zhaopin']
lagou_cate = db.lagou_category
data = lagou_cate.find()
cate_list = []
for i in data :
    cate_list.append(i['detail_category'])
cate_list1= set(cate_list)
print(len(cate_list1))
print(cate_list1)
