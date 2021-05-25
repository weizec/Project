

import json
from Analysis.nltk_analyse import return_keyword,emotion_analyse,relation_analysis,analyse_content
from Analysis.AnalysisScenario import get_user_cityname,get_user_location,connect_to_server


FILE_NAME = 'twitter.json'


if __name__ == '__main__':
    user_location = get_user_location()
    keyword = return_keyword()
    twitter_result = {}

    fileReader = open(FILE_NAME, 'r', encoding='utf-8')
    default_count = 0
    count = 0

    for line in fileReader:
        if count>default_count:
            # get json data
            try:
                load_data = json.loads(line[:-2])
            except Exception as e1:
                # If the format of the JSON line read in is not correct, exception will be output
                continue

            text = load_data['text']
            coordinate = load_data['coordinate']
            place = load_data['place']
            user_ID = load_data['userID']

            # TODO:get the city's name
            city_name = get_user_cityname(coordinate, place, user_ID, user_location)
            # TODO:analyse the twitter content
            if city_name != None and city_name != 'None':  # 只处理有位置的数据
                # initial the twitter analyse result
                if city_name not in twitter_result:
                    twitter_result[city_name] = {'total number': 0, 'keyword relation': 0,
                                                 'emotion proportion': {'pos': 0, 'neg': 0, 'neu': 0, 'compound': 0}}
                # 赋值
                twitter_result[city_name]['total number'] += 1
                # handle each text to get emotion and similarity analysis result
                analyse_emotion, analyse_similarity = analyse_content(text, keyword)  # very slow

                #  handle twitter数据相关
                if analyse_similarity > 0:  # 阈值
                    twitter_result[city_name]['keyword relation'] += 1

                    if analyse_emotion == 'pos':
                        twitter_result[city_name]['emotion proportion']['pos'] += 1
                    elif analyse_emotion == 'neg':
                        twitter_result[city_name]['emotion proportion']['neg'] += 1
                    elif analyse_emotion == 'neu':
                        twitter_result[city_name]['emotion proportion']['neu'] += 1
                    elif analyse_emotion == 'compound':
                        twitter_result[city_name]['emotion proportion']['compound'] += 1
            print(twitter_result)
        count +=1
        print(count)


    filename = 'twitter_result.json'
    with open(filename, 'w') as file_obj:
        json.dump(twitter_result, file_obj)

    '''
    filename = 'twitter_result.json'
    reader = open(filename,'r')
    twitter_result = json.load(reader)
    '''
    # put the result in the aurin dataset
    data = {}
    scenario_name = 'basic_scenario'
    data["_id"] = scenario_name
    data["data"] = twitter_result

    server = connect_to_server()
    try:
        dataset = server.create("analysis_scenario")
    except:
        dataset = server["analysis_scenario"]

    try:
        data_doc = dataset[scenario_name]
        data_doc["data"] = data["data"]
        dataset.save(data_doc)
    except:
        _id, _rec = dataset.save(data)
        data_doc = dataset[_id]