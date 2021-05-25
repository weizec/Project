import nltk
nltk.download("wordnet")
nltk.download("stopwords")
nltk.download("vader_lexicon")
from nltk.corpus import wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import time


TOPIC_KEYWORD = ['unemployed', 'job','lost job', 'income','unemployment', 'losing job', 'jobkeeper', 'get fired',
                 'no job', 'homeless', 'need a job', 'find a job','find jobs',
                 'jobseeker','seek job','need job','newstart allowance','got fired','no jobs',
                 'out of work','no income', 'in dry dock',' out of employment', 'get a job', 'don’t have job']


def return_keyword():
    synonyms = []
    for each in TOPIC_KEYWORD:
        for syn in wordnet.synsets(each):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())

    synonyms = synonyms+TOPIC_KEYWORD
    return synonyms

def emotion_analyse(text):
    try:
        sentiment = SentimentIntensityAnalyzer()
    except Exception as e:
        print(e)
    emotion_predict = {'pos':0,'neg':0,'neu':0,'compound':0}


    for token in text:
        emotion = sentiment.polarity_scores(token)
        for each_title in emotion:
            emotion_predict[each_title] += emotion[each_title]

    max_emotion = ''
    max_value = 0
    for each in emotion_predict:
        if max_value < emotion_predict[each]:
            max_value = emotion_predict[each]
            max_emotion = each



    return max_emotion

#keyword is a list, tokens is a list
def relation_analysis(keyword,tokens):
    #tokens =['i','no jobs']
    total_simi = 0
    for each_keyword in keyword:
        for each_token in tokens:

            total = 0
            for eachx in wordnet.synsets(each_keyword):
                for eachy in wordnet.synsets(each_token):
                    total += eachx.wup_similarity(eachy)
            if total != 0:
                total_simi += total
    return total_simi

def keyword_relation(keyword,tokens):

    total_relation = 0
    for each_keyword in keyword:
        if each_keyword in tokens:
            total_relation += 1
    return total_relation

def analyse_content(text,keyword):


    # 1.获得token
    tokens = [token for token in text.split()]
    # 2.去除stopwords
    for token in tokens:
        if token in stopwords.words('english'):
            tokens.remove(token)
    # TODO:从两个方面分析，情感方面，和关键词相关性
    # 3.positive and negative
    start_time = time.time()
    predict_emotion = emotion_analyse(tokens)
    print("the emotion end time is :" + str(time.time() - start_time))
    # 4.关键词相关性  ------ 一整个句子tokens和keyword之间的关系
    start_time = time.time()
    predict_similarity = keyword_relation(keyword,tokens)
    #predict_similarity = relation_analysis(keyword, tokens)
    print("the similarity end time is :" + str(time.time() - start_time))


    return predict_emotion,predict_similarity

