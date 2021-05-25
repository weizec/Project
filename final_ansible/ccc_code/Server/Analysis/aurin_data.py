
import json
import couchdb
import mmap
from Analysis.parameters import all_city,all_coordinates
from Analysis.AnalysisScenario import connect_to_server
from Analysis.location_analyse import get_location_long_la


def connect_to_server():
    counchDB_server = couchdb.Server('http://admin:8888@172.26.132.132:5984/')
    print("The connection to CouchDB is seccessed:"+str(counchDB_server))
    return counchDB_server

def read_aurindata(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            cur_map = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
            decode_data = cur_map.read().decode('utf-8')
            json_data = json.loads(decode_data)
            f.close()
        return json_data
    except Exception as e:
        print(e)


def put_result_to_couchdb(scenario_name,put_data):
    # put the result in the aurin dataset
    dataset_name = 'aurin_dataset'
    data = {}
    data["_id"] = scenario_name
    data["data"] = put_data

    server = connect_to_server()
    try:
        print("it is the try")
        dataset = server.create(dataset_name)
    except:
        dataset = server[dataset_name]

    try:
        data_doc = dataset[scenario_name]
        data_doc["data"] = data["data"]
        dataset.save(data_doc)
    except:
        _id, _rec = dataset.save(data)
        data_doc = dataset[_id]

    return data_doc


'''
Ssenario 1:不同地区公司（exit，entry，total）的数量
'''
def get_scenario_1_data():
    file_name = '../dataserver/jsonFile/scenario_1/businessnum.json'
    load_data = read_aurindata(file_name)

    area_business_data = []
    print(load_data)
    for each_value in load_data['features']:
        data = each_value['properties']

        city_name = data['sa3_name']
        for each_city in all_city:
            if each_city.lower() in city_name.lower():
                city_name = each_city.lower()

                business_data={}
                business_data['city_name'] = city_name
                business_data['total_bus'] = data['num_bus_tot']
                business_data['exist_bus'] = data['num_bus_entr_tot']
                business_data['entry_bus'] = data['num_bus_exit_tot']

                isset = False
                for each in area_business_data:
                    if each['city_name'] == city_name:
                        each['total_bus'] += data['num_bus_tot']
                        each['exist_bus'] += data['num_bus_entr_tot']
                        each['entry_bus'] += data['num_bus_exit_tot']
                        isset = True

                if isset == False:
                    area_business_data.append(business_data)
    print(area_business_data)

    scenario_name = 'scenario_1'
    data_doc = put_result_to_couchdb(scenario_name, area_business_data)

    return data_doc

'''
Scenario 2:不同地区的 alcohol相关的数据
'''

def get_scenario_2_data():
    file_name = '../dataserver/jsonFile/scenario_2/alcohol.json'
    load_data = read_aurindata(file_name)

    area_alcohol_num = []
    for each_data in load_data['features']:
        data = each_data['properties']

        alcohol_rate = data['alcohol']
        city_name = data['phn_name']

        alcohol_data = {}
        for each_city in all_city:
            if each_city.lower() in city_name.lower():
                city_name = each_city.lower()

                isset = False
                for each in area_alcohol_num:
                    if each['city_name'] == city_name:
                        each['alcohol_rate'] += alcohol_rate
                        each['area_num'] += 1
                        isset =True

                if isset == False:
                    alcohol_data['city_name'] = city_name
                    alcohol_data['alcohol_rate'] = alcohol_rate
                    alcohol_data['area_num'] = 1

                    area_alcohol_num.append(alcohol_data)

    print(area_alcohol_num)
    #handle the result data
    for each in area_alcohol_num:
        each['alcohol_rate'] = each['alcohol_rate']/each['area_num']
    print(area_alcohol_num)

    scenario_name = 'scenario_2'
    data_doc = put_result_to_couchdb(scenario_name,area_alcohol_num)

    return data_doc

'''
Scenario 3: education facilities(university and TAFE)的数量
'''
def get_scenario_3_data():
    file_name1 = '../dataserver/jsonFile/scenario_3/education_TAFE.json'
    load_data = read_aurindata(file_name1)
    education_data = {}
    for each in load_data['features']:
        data = each['properties']
        long = data['longitude']
        la = data['latitude']
        city_name = get_location_long_la(long,la)

        if city_name != None and city_name != '':
            if city_name not in education_data:
                education_data[city_name] = 1
            else:
                education_data[city_name] +=1

    file_name2= '../dataserver/jsonFile/scenario_3/education_Uni.json'
    load_data2 = read_aurindata(file_name2)
    for each in load_data['features']:
        data = each['properties']
        long = data['longitude']
        la = data['latitude']
        city_name = get_location_long_la(long,la)
        if city_name != None and city_name != '':
            if city_name not in education_data:
                education_data[city_name] = 1
            else:
                education_data[city_name] +=1
    print(education_data)

    scenario_name = 'scenario_3'
    data_doc = put_result_to_couchdb(scenario_name, education_data)

    return data_doc


def query_aurin_data(scenario_name):
    scenario_data = {}
    couchdb_server = connect_to_server()
    if scenario_name == 'scenario_1':
        view_name = 'view/scenario1'
    elif scenario_name == 'scenario_2':
        view_name = 'view/scenario2'
    elif scenario_name == 'scenario_3':
        view_name = 'view/scenario3'
    try:
        aurin_dataset = couchdb_server['aurin_dataset']
    except Exception as e:
        print("There is a exception" + str(e))

    view = aurin_dataset.view(view_name, reduce=False)
    for each in view:
        # each users' ID, and the location
        scenario_data[each.key] = each.value
    return scenario_data[scenario_name]

'''
if __name__ == '__main__':
    scenario_name ='scenario_1'
    data = query_aurin_data(scenario_name)
    print(type(data))
    print(data)
'''
