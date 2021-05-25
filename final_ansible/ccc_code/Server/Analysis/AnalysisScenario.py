import couchdb
import threading
import time
import nltk
from Analysis.nltk_analyse import return_keyword,emotion_analyse,relation_analysis,analyse_content
from Analysis.location_analyse import  all_coordinates,all_city,get_location
import json
TWITTEE_DATASET_NAME = 'twittertest'



def connect_to_server():
    counchDB_server = couchdb.Server('http://admin:8888@172.26.132.132:5984/')
    print("The connection to CouchDB is seccessed:"+str(counchDB_server))
    return counchDB_server

'''
Twitter Analyse
'''
def get_twitter_data(dataset_name,view_name):
    return_data ={}
    couchdb_server = connect_to_server()

    try:
        database = couchdb_server[dataset_name]
    except Exception as e:
        print("There is a exception"+str(e))

    view = database.view(view_name, reduce =  False)
    for each in view:
        #view (MapReduce) each.key is _id, each.value is [text,coordinate and place]
        return_data[each.key] = each.value
    #     print(each.key)
    #     print(each.value)
    # print(return_data)
    return database,return_data

def get_user_location():
    #get data from couchDB
    user_result = {}
    couchdb_server =  connect_to_server()
    try:
        user_dataset = couchdb_server['user']
    except Exception as e:
        print("There is a exception" + str(e))

    view = user_dataset.view('view/user',reduce =False)
    for each in view:
        #each users' ID, and the location
        user_result[each.key] = each.value


    filename = 'user_information.json'
    with open(filename, 'w') as file_obj:
        json.dump(user_result, file_obj)

    return user_result


def get_user_cityname(coordinate,place,user_ID,user_location):

    # get the city's name
    city_name = None
    if coordinate != 'None' and coordinate != None:
        city_name = get_location(coordinate)
    elif place != None and place != 'None':
        for each_city_name in all_city:
            if each_city_name.lower() in place.lower():
                city_name = each_city_name.lower()
    else:
        # TODO:use the users's location as the city_name
        print("use the user's location")
        if user_ID in user_location:
            # user's location is not None, and also in the list of all city's name
            if user_location[user_ID] != None and user_location[user_ID] != 'None':
                for each_city_name in all_city:
                    if each_city_name.lower() in user_location[user_ID].lower():
                        city_name = each_city_name.lower()
    return city_name



def analysis_twitter(scenario_name):
    user_location = get_user_location()
    print("get the user's information: id and location")

    # get the scenario data set
    start_time = time.time()
    dataset = {}
    if scenario_name == 'scenario1':
        print("get the twitter data :it is secenario 1")
        view_name = 'view/scenario'
        database,dataset = get_twitter_data(TWITTEE_DATASET_NAME,view_name)

    elif scenario_name == 'scenario2':
        print("get the twitter data :it is secenario 2")
        view_name = 'view/scenario'
        database,dataset = get_twitter_data(TWITTEE_DATASET_NAME,view_name)

    elif scenario_name == 'scenario3':
        print("get the twitter data :it is secenario 3")
        view_name = 'view/scenario'
        database,dataset = get_twitter_data(TWITTEE_DATASET_NAME,view_name)
    elif scenario_name == 'unsolved_twitter':
        print("get the twitter data :it is unsolved twitter ")
        dataset_name = 'unsolved_twitter'
        view_name = 'view/scenario'
        #  view (MapReduce) each.key is _id, each.value is [text,coordinate,place and userID]
        database,dataset = get_twitter_data(dataset_name,view_name)

    print("the end time is :"+str(time.time()-start_time))
    # initial the topic relational key word list
    keyword = return_keyword()
    twitter_result = {}
    count = 0
    for each in dataset:
        print(count)
        count += 1
        start_time = time.time()
        coordinate = dataset[each][1]
        place = dataset[each][2]
        user_ID = dataset[each][3]

        # TODO:get the city's name
        city_name = get_user_cityname(coordinate,place,user_ID,user_location)

        # TODO:analyse the twitter content
        if city_name !=  None and city_name != 'None':  # only handle the twitter data with location information
            # initial the twitter analyse result
            if city_name not in twitter_result:
                twitter_result[city_name] = {'total number': 0, 'keyword relation': 0,
                                             'emotion proportion': {'pos': 0, 'neg': 0, 'neu': 0, 'compound': 0}}
            twitter_result[city_name]['total number'] += 1
            # handle each text to get emotion and similarity analysis result
            text = dataset[each][0]
            analyse_emotion, analyse_similarity = analyse_content(text, keyword)  # very slow

            #  handle twitter data
            if analyse_similarity > 0:  # the threshold
                twitter_result[city_name]['keyword relation'] += 1

                if analyse_emotion == 'pos':
                    twitter_result[city_name]['emotion proportion']['pos'] += 1
                elif analyse_emotion == 'neg':
                    twitter_result[city_name]['emotion proportion']['neg'] += 1
                elif analyse_emotion == 'neu':
                    twitter_result[city_name]['emotion proportion']['neu'] += 1
                elif analyse_emotion == 'compound':
                    twitter_result[city_name]['emotion proportion']['compound'] += 1


        if scenario_name == 'unsolved_twitter':
            try:
                database.delete(database[each])
            except:
                pass

    # put the result in the aurin dataset
    scenario_name = 'basic_scenario'
    data = {}
    data["_id"] = scenario_name
    #data["data"] = twitter_result

    server = connect_to_server()
    try:
        dataset = server.create("analysis_scenario")
    except:
        dataset = server["analysis_scenario"]

    try:
        data_doc = dataset[scenario_name]
        get_data = data_doc["data"]
        print("----")
        # update the value in the couchDB
        for each in get_data:
            add_data = {}
            if each == 'australia':
                if 'australia' in twitter_result:
                    add_data = twitter_result['australia']
            elif each == 'melbourne':
                if 'melbourne' in twitter_result:
                    add_data = twitter_result['melbourne']
            elif each == 'sydney':
                if 'sydney' in twitter_result:
                    add_data = twitter_result['sydney']
            elif each == 'brisbane':
                if 'brisbane' in twitter_result:
                    add_data = twitter_result['brisbane']
            elif each == 'perth':
                if 'perth' in twitter_result:
                    add_data = twitter_result['perth']
            elif each == 'adelaide':
                if 'adelaide' in twitter_result:
                    add_data = twitter_result['adelaide']


            if 'total number' in add_data:
                get_data[each]['total number'] += add_data['total number']
            if 'keyword relation' in add_data:
                get_data[each]['keyword relation'] += add_data['keyword relation']
            if 'emotion proportion' in add_data:
                get_data[each]['emotion proportion']['pos'] += add_data['emotion proportion']['pos']
                get_data[each]['emotion proportion']['neg'] += add_data['emotion proportion']['neg']
                get_data[each]['emotion proportion']['neu'] += add_data['emotion proportion']['neu']
                get_data[each]['emotion proportion']['compound'] += add_data['emotion proportion']['compound']



        data_doc["data"] = get_data
        dataset.save(data_doc)
        print('the dataset in couchDB has been restore')
    except:
        _id, _rec = dataset.save(data)
        data_doc = dataset[_id]


    return data_doc




def analysis_scenario(scenario_name):
    thread = threading.Thread(target = analysis_twitter,args = (scenario_name,))
    thread.start()
    return_message = 'scenario1 twitter analysis process is  started'
    return return_message



if __name__ == '__main__':

    scenario_name = 'scenario1'
    analysis_scenario(scenario_name)



'''

关键字在twitter里面，以及emotion

twitter：


情感分：各部分的比率，失业Twitter的比率：
失业推特刷量：总数是多少




aurin：
三个场景：
1。犯罪率
2。公司搬出数量
3。平均教育水平

{
'mel':{
        "totol number":
        "keyword relation":
        "emotion proportion"

        }
}

负面情绪的twitter数量，正面情绪Twitter数量，总twitter数量
失业Twitter数量，总twitter数量


'''


'''
TODO:
1.twitter数据的处理
    a。以user's location作为city name
    b。分析结果的存储
        字典
    ---------------------------
    b。调用的接口
    c。分析所有的twitter数据 


2。aurin数据的处理
    a. aurin的dataset的选取
    b。aurin数据的坐标位置的处理
    c。aurin数据的上传存储
     -------------------------
    d。aurin数据的调用接口

3。报告

'''