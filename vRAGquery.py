import requests
import json
import re
from urllib.parse import quote

def extract_bw_tags(text, start_tag, end_tag):
    start_index = text.find(start_tag)
    end_index = text.find(end_tag, start_index)
    return text[start_index+len(start_tag):end_index-len(end_tag)]

class RAGQueryVect():
    def __init__(self, api_key: str, customer_id: str, corpus_ids: list[str], prompt_name: str = None):
        self.customer_id = customer_id
        self.corpus_ids = corpus_ids
        self.api_key = api_key
        self.prompt_name = "vectara-experimental-summary-ext-2023-10-23-med" #vectara-summary-ext-v1.2.0"
        self.conv_id = None

    def promptquery(self, query_str: str):
        corpora_key_list = [{
                'customer_id': self.customer_id, 'corpus_id': corpus_id, 'lexical_interpolation_config': {'lambda': 0.025} #CorpusKeySemantics
            } for corpus_id in self.corpus_ids
        ]

        endpoint = f"https://api.vectara.io/v1/query"
        start_tag = "%START_SNIPPET%"
        end_tag = "%END_SNIPPET%"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "customer-id": self.customer_id,
            "x-api-key": self.api_key,
            "grpc-timeout": "30S"
        }
        body = {
            'query': [
                { 
                    'query': query_str,
                    'start': 0,
                    'numResults': 10,
                    'corpusKey': corpora_key_list,
                    'context_config': {
                        'charsBefore': 10,
                        'charsAfter': 10,
                        'sentencesBefore': 10,
                        'sentencesAfter': 10,
                        'startTag': start_tag,
                        'endTag': end_tag,
                    },
                    'rerankingConfig':
                    {
                        'rerankerId': 252525252, 
                        'mmrConfig': {
                            'diversityBias': 0.1
                        }
                    },
                    'summary': [
                        {
                            'responseLang': 'eng',
                            'maxSummarizedResults': 9,
                            'summarizerPromptName': self.prompt_name, #optional - default to best summarizer with acc type
                            'chat': {
                                'store': True,
                                'conversationId': self.conv_id
                            },
                            'debug': True,
                            "factual_consistency_score": True
                        },
                    ],
                }, 
            ],
        }
        
        response = requests.post(endpoint, data=json.dumps(body), verify=True, headers=headers)    
        if response.status_code != 200:
            print(f"Query failed with code {response.status_code}, reason {response.reason}, text {response.text}")
            return "Sorry, something went wrong in my little brain. Please try again later."

        res = response.json()
        print(res)

        top_k = 11
        summary = res['responseSet'][0]['summary'][0]['text']
        responses = res['responseSet'][0]['response'][:top_k]
        docs = res['responseSet'][0]['document']
        chat = res['responseSet'][0]['summary'][0]['chat']
        print(summary)

    
        
        if chat is not None and chat['status'] != None:
            st_code = chat['status']
            print(f"Chat query failed with code {st_code}")
            # ... rest of your code handling chat failure
            if st_code == 'RESOURCE_EXHAUSTED':
                self.conv_id = None
                return 'Sorry, Vectara chat turns exceeds plan limit.'
            return 'Sorry, something went wrong in my little brain. Please try again later.'
        elif 'responseSet' in res and res['responseSet'] and len(res['responseSet']) > 0:
            # Check if responseSet exists, is not empty, and has at least one element
            first_response = res['responseSet'][0]
            if 'summary' in first_response and first_response['summary'] and len(first_response['summary']) > 0:
                # Check if summary exists, is not empty, and has at least one element
                first_summary = first_response['summary'][0]
                if 'chat' in first_summary and first_summary['chat'] is not None:
                    self.conv_id = first_summary['chat']['conversationId']
        else:
            # Handle the case where none of the checks pass (unexpected response structure)
            print("Unexpected response format from Vectara API")
            return "Sorry, something went wrong in my little brain. Please try again later."

        
        pattern = r'\[\d{1,2}\]'
        matches = [match.span() for match in re.finditer(pattern, summary)]

        # figure out unique list of references
        refs = []
        for match in matches:
            start, end = match
            response_num = int(summary[start+1:end-1])
            doc_num = responses[response_num-1]['documentIndex']
            metadata = {item['name']: item['value'] for item in docs[doc_num]['metadata']}
            text = extract_bw_tags(responses[response_num-1]['text'], start_tag, end_tag)
            if 'url' in metadata.keys():
                url = f"{metadata['url']}#:~:text={quote(text)}"
                if url not in refs:
                    refs.append(url)

        # replace references with markdown links
        refs_dict = {url:(inx+1) for inx,url in enumerate(refs)}
        for match in reversed(matches):
            start, end = match
            response_num = int(summary[start+1:end-1])
            doc_num = responses[response_num-1]['documentIndex']
            metadata = {item['name']: item['value'] for item in docs[doc_num]['metadata']}
            text = extract_bw_tags(responses[response_num-1]['text'], start_tag, end_tag)
            #url = f"{metadata['url']}#:~:text={quote(text)}"
            url = metadata.get('url')
            if url:
                url = f"{url}#:~:text={quote(text)}"
            else:
                url = "https://console.vectara.com/console/corpus/3/data"  # Or you can set as None
            #citation_inx = refs_dict[url]
            #summary = summary[:start] + f'[\[{citation_inx}\]]({url})' + summary[end:]
            
            citation_inx = refs_dict.get(url)
            if citation_inx:
                summary = summary[:start] + f'[\[{citation_inx}\]]({url})' + summary[end:]
            else:
                # Handle the case where url is None (e.g., skip adding a link)
                summary = summary[:start] + f'[Citation]' + summary[end:]  # Or any placeholder


        return summary