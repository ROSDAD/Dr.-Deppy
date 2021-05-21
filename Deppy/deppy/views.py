#%tensorflow_version 1.14
from django.shortcuts import render,redirect
from django.http import HttpResponse
#from deppy.deppy import Chatbotclass
 
import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy
import tensorflow as tf
import random
import tflearn
import pandas as pd
import json
import ijson
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy
import tensorflow as tf
import random
import tflearn
import pandas as pd
import json
import ijson 
from .models import Users
from .models import Chats


data = pd.read_json('deppy/intents_2.json')
#with open('intents.json', encoding='utf-8') as f:
#   data = json.load(f)
#data = ijson.parse(open("intents.json"))
#pd.DataFrame.from_dict(data, orient='index').T.set_index('index')
#df_json = globals()['intents.json'].to_json(orient='split')
#data=pd.read_json(df_json, orient='split')
#Extracting data
data=dict(data)
#print(data)
words = []
labels = []
docs_x = []
docs_y = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        wrds = nltk.word_tokenize(pattern)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent["tags"])
        
    if intent['tags'] not in labels:
        labels.append(intent['tags'])

words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

labels = sorted(labels)

training = []
output = []

out_empty = [0 for _ in range(len(labels))]

for x, doc in enumerate(docs_x):
    bag = []

    wrds = [stemmer.stem(w.lower()) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)

    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)

training = numpy.array(training)
output = numpy.array(output)

#model
tf.compat.v1.reset_default_graph()
#tf.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

#model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
#model.save("model.tflearn")
model.load("model.tflearn")
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)
def chat(inp):
    while True:
        
        if inp.lower() == "quit":
            return "Nice talking to you! Have a good day!"
            break

        results = model.predict([bag_of_words(inp, words)])
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        for tg in data["intents"]:
            if tg['tags'] == tag:
                responses = tg['responses']

        return random.choice(responses)

def index(request):
    if "username" in request.session or "email" in request.session:
        obj = Chats.objects.all().filter(email=request.session['email'])
        
        return render(request,"deppy.html",{"obj":obj})
    else:
        return render(request,"login.html")

def chatpost(request):
    if request.method=="POST":
        obj = Chats()
        message = request.POST["message"]
        chatreply = chat(message)
        obj.email = request.session['email']
        obj.inpchat = message
        obj.replychat = chatreply
        obj.save()
        return HttpResponse(chatreply)
def signup(request):
    if request.method=="POST":
        if request.POST["signupuname"]!="":
            uname = request.POST["signupuname"]
        else:
            return render(request,"login.html")
        if request.POST["signupemail"]!="":
            email = request.POST["signupemail"]
        else:
            return render(request,"login.html") 
        if request.POST["signuppass"]!="":
            signuppass = request.POST["signuppass"]
        else:
            return render(request,"login.html")
        if request.POST["signupcnfpass"]!="":
            signupcnfpass = request.POST["signupcnfpass"]
        else:
            return render(request,"login.html")        
        if signuppass==signupcnfpass:
            
            obj = Users.objects.all().filter(email=email)
            if len(obj) == 0:
                users = Users()
                users.name = uname
                users.email = email
                users.password = signuppass

                users.save()
                
                request.session['email'] = email
                
            return redirect("/")
                

def signin(request):
    if request.method=="POST":
        if request.POST["signinemail"]!="":
            uemail = request.POST["signinemail"]
        else:
            return render(request,"login.html")
        if request.POST["signinpass"]!="":
            password = request.POST["signinpass"]
        else:
            return render(request,"login.html") 
        user = Users.objects.all().filter(email=uemail,password=password)
        if len(user) != 0:
            
            request.session['email'] = uemail
        return redirect("/")
            
        
def logout(request):
    if request.method == "POST":
        if request.POST['action']=="logout":
            del request.session['email']
            
            return HttpResponse("logoutsuccessful")
def showprofile(request):
    if request.session.get('email', None):
        return render(request,"profile.html")
    else:
        return render(request,"login.html")
        