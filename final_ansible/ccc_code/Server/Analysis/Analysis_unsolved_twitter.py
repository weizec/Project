import couchdb
import threading
import time
from Analysis.AnalysisScenario import analysis_twitter
TWITTEE_DATASET_NAME = 'unsolved_twitter'

def run_analysis_unsolved_twitter():
    scenario_name = 'unsolved_twitter'
    while (True):
        print("it is the time to analysis")
        analysis_twitter(scenario_name)
        time.sleep(3600)

if __name__ == '__main__':

    scenario_name = 'unsolved_twitter'
    while(True):
        analysis_twitter(scenario_name)
        time.sleep(3600)








