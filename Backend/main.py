import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import nltk
nltk.data.path.append(r"C:\Users\Joel Zerubabel\AppData\Roaming\nltk_data")
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import TreebankWordTokenizer
from sentence_transformers import SentenceTransformer,util


from nltk.stem import PorterStemmer
import numpy as np
import tensorflow as tf
import random
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from collections import Counter

BASE_DIR=os.path.dirname(__file__)

class Chatbox:
    def __init__(self):
        self.tokenize = TreebankWordTokenizer()
        self.stemmer=LancasterStemmer()
        self.porterstemmer=PorterStemmer()
        self.tfidfvectorizer=TfidfVectorizer(ngram_range=(1,2),min_df=1,max_df=0.9,sublinear_tf=True)
        #self.spacyy=spacy.load('en')
        self.multinomialnb=MultinomialNB()
        self.logics=LogisticRegression(max_iter=3000,penalty='l2',C=0.5,solver="saga",class_weight='balanced',n_jobs=-1)
        self.svc=LinearSVC(C=1.0,
        class_weight="balanced",max_iter=5000)
        self.data=self.file()
        self.labels=[]
        self.sentence=[]
        self.response={}
        self.words_to_classify()
        self.ml_works()
        self.model=SentenceTransformer('all-MiniLM-L6-v2')
        self.SLM()
        
    def file(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(BASE_DIR, "intents.json")

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

        
    def getting_input(self,word):
        #getting example sentence first from user
        #word=input(('Hello drop your question eg:hello,good morining  '))
        tokens=self.tokenize.tokenize(word)

        return ' '.join(self.porterstemmer.stem(t.lower()) for t in tokens)
    
    
    def words_to_classify(self):  
        for intent in self.data['intents']:
            tag=intent['tag']
            self.response[tag]=intent['responses']  

            for pattern in intent['patterns']:
                
                self.sentence.append(self.getting_input(pattern))
                self.labels.append(tag)
    
    def ml_works(self):
        X = self.tfidfvectorizer.fit_transform(self.sentence)
        y = self.labels
        X_train,_, y_train,_ = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        self.multinomialnb.fit(X_train, y_train)
        self.logics.fit(X_train, y_train)
        self.svc.fit(X_train, y_train)
        #self.logics(X_train,y_train)


                
    def giving_output(self,input):
        processed=self.getting_input(input)
        '''tokens=self.getting_input()
            joined=' '.join(tokens)'''
        vectorize=self.tfidfvectorizer.transform([processed])
        nb=self.multinomialnb.predict(vectorize)[0]
        svc=self.svc.predict(vectorize)[0]
        logics=self.logics.predict(vectorize)[0]

        probs=self.logics.predict_proba(vectorize)[0]
        confidence=max(probs)
        if confidence < 0.45 and nb!=svc:
            return ' i am not sure can you rephrase'

        intent=Counter([nb,svc,logics]).most_common(1)[0][0]
            #print('replied',self.response[intent])
            #print("Predicted intent:", intent)
        return random.choice(self.response[intent])

    def SLM(self):
        self.pattern=[]
        self.tags=[]
        
        for intent in self.data['intents']:
            for pattern in intent['patterns']:
                self.pattern.append(pattern)
                self.tags.append(intent['tag'])

        self.pattern_embedding=self.model.encode(self.pattern,convert_to_tensor=True)
            #print(self.pattern)

    def evaluate_slm(self,user_input):
        #SLM Part
        input_embedding=self.model.encode(user_input,convert_to_tensor=True)
        score_slm=util.cos_sim(input_embedding,self.pattern_embedding)
        best_match_idx_slm=int(np.argmax(score_slm))
        best_match_conf_slm=float(score_slm[0][best_match_idx_slm])       
        slm_tags_slm=self.tags[best_match_idx_slm]

        #ML Part
        '''tfid_ml=self.tfidfvectorizer.transform([user_input])
        ml_probs_ml=self.logics.predict_proba(tfid_ml)
        best_match_idx_ml=int(np.argmax(ml_probs_ml))
        best_match_conf_ml=float(ml_probs_ml[0][best_match_idx_ml])
        ml_tags_ml=self.logics.classes_[best_match_idx_ml]'''

        processed = self.getting_input(user_input)
        tfid_ml = self.tfidfvectorizer.transform([processed])
        ml_probs = self.logics.predict_proba(tfid_ml)
        best_match_idx_ml = int(np.argmax(ml_probs))
        best_match_conf_ml = float(ml_probs[0][best_match_idx_ml])
        ml_tag = self.logics.classes_[best_match_idx_ml]

        if best_match_conf_slm>=0.60:
            #and ml_tags_ml>=best_match_ml

            final_tag=slm_tags_slm
            final_confidence=best_match_conf_slm
            model_used='SLM'

        elif best_match_conf_ml >= 0.50:
            final_tag = ml_tag
            final_confidence = best_match_conf_ml
            model_used = "ML"

        else:
            return "I am not sure, can you rephrase?", 0.0, "Fallback"

        for intent in self.data['intents']:
            if intent['tag'] == final_tag:
                return random.choice(intent['responses']), final_confidence, model_used

        return "I have no idea", 0.0, "Fallback"
    
    def save_models(self):
        pickle.dump(self.logics,open('logics_train.pkl','wb'))
        pickle.dump(self.multinomialnb,open('multi_train.pkl','wb'))
        pickle.dump(self.svc,open('svc_train.pkl','wb'))
        pickle.dump(self.tfidfvectorizer,open('tfid_train.pkl','wb'))


    def chat(self, user_input, departments=None, doctors=None):
        user_input_lower = user_input.lower()
        if departments and doctors:
            dept_names = [d.name.lower() for d in departments]
            import difflib
            match = difflib.get_close_matches(user_input_lower, dept_names, n=1, cutoff=0.6)
            if match:
                dept_name = match[0]
                doctor = next((d for d in doctors if d.department.lower() == dept_name), None)
                if doctor:
                    return {
                        "response": f"👨‍⚕️ {doctor.name} is available in {dept_name.title()} department.",
                        "confidence": 1.0,
                        "model": "RULE"
                    }
                else:
                    return {
                        "response": f"No doctors available in {dept_name.title()} department.",
                        "confidence": 1.0,
                        "model": "RULE"
                    }
        response, confidence, model_used = self.evaluate_slm(user_input)
        return {
            "response": response,
            "confidence": round(confidence, 3),
            "model": model_used
        }