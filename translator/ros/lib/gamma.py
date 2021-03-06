import requests
import json
import logging
from ros.framework import Operator

logger = logging.getLogger("gamma")
logger.setLevel(logging.WARNING)

class Gamma(Operator):
    def __init__(self):
        super(Gamma, self).__init__("gamma")
        self.robokop_url = 'http://robokop.renci.org/api'
        self.max_results = 50
        
    def quick(self, question):
        url=f'http://robokop.renci.org:80/api/simple/quick/'
        response = requests.post(url,json=question)
        logger.debug ( f"Return Status: {response.status_code}" )
        if response.status_code == 200:
            return response.json()
        return response

    def make_N_step_question(self, types,curies):
        question = {
            'machine_question': {
                'nodes': [],
                'edges': []
            }
        }
        for i,t in enumerate(types):
            newnode = {'id': i, 'type': t}
            if curies[i] is not None:
                newnode['curie'] = curies[i]
            question['machine_question']['nodes'].append(newnode)
            if i > 0:
                question['machine_question']['edges'].append( {'source_id': i-1, 'target_id': i})
        return question

    def extract_final_nodes(self, returnanswer):
        nodes = [{
            'node_name': answer['nodes'][2]['name'],
            'node_id': answer['nodes'][2]['id'] }
            for answer in returnanswer['answers']
        ]
        return pd.DataFrame(nodes)

    def synonymize(self, nodetype,identifier):
        url=f'{self.robokop_url}/synonymize/{identifier}/{nodetype}/'
        #print (url)
        
        response = requests.post(url)
        #print( f'Return Status: {response.status_code}' )
        if response.status_code == 200:
            return response.json()
        return []

    def module_wf1_mod3 (self, event):
        """ Execute module 3 of workflow one. """
        response = None
        
        """ Query the graph for conditions. """

        diseases = event.select (
            query = "$.[*].result_list.[*].[*].result_graph.node_list.[*]",
            graph = event.conditions)
        assert len(diseases) > 0, "Found no diseases"

        """ Invoke the API. """
        disease = diseases[0]['name']
        api_call = f"{self.robokop_url}/wf1mod3a/{disease}/?max_results={self.max_results}"
        logger.debug (api_call)
        response = requests.get(api_call, json={}, headers={'accept': 'application/json'})
        
        """ Process the response. """
        status_code = response.status_code
        
        if not status_code == 200:
            logger.debug ("********** * broken * **********")
            
        return response.json() if status_code == 200 else event.context.tools.kgs (nodes=[])

    def wf1_module3 (self, graph):
        pass #curl -X GET "http://robokop.renci.org/api/wf1mod3a/DOID:9352/?max_results=5" -H "accept: application/json"

    def invoke (self, event):
        if event.op:
            return getattr(self,event.op) (event)
        else:
            """ todo. """
            url = "http://robokop.renci.org:6011/api/now?max_results=250"
            response = requests.post (
                url = url,
                data = machine_question,
                headers = { "Content-Type" : "application/json" }).json ()


