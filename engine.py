import pymongo
import hashlib
import time
from constants import *

def comp(x,y):

    if x[0] != y[0]:
        return x[0] - y[0]

    else:
        return int(y[1] - x[1])

STATIC_DIR = "static/"
SOL_DIR = "solutions/"

class Engine(object):

    def __init__(self):

        #self.connection = pymongo.MongoClient(MONGO_URI % (USER, PASSWORD))
        self.connection = pymongo.MongoClient(MONGO_URI)
        db = self.connection[MONGO_DB]

        self.userCollection = db[USER_COLLECTION]
        self.programCollection = db[PROGRAM_COLLECTION]
        self.miscCollection = db[MISC_COLLECTION]

        self.scores = {1:{True:70, False:30}, 2:{True:60, False:40}, 3:{True:100, False:0}, 4:{True:70, False:30}, 5:{True:70, False:30}} # Level NO: Score

    def isBlacklisted(self, ip):

        if self.miscCollection.find_one({"_id":ip}):

            return True

        return False

    def authenticate(self, username, password):

        u = self.userCollection.find_one({"username":username})

        if u:
            check_pwd = hashlib.sha512(password + SALT).hexdigest()

            if check_pwd==u['password']:
                return u['_id']

        return False

    def savefile(self, code, user_id, level):

        u = self.userCollection.find_one({"_id":user_id})['username']

        if not self.programCollection.find_one({"username":u, "level":level}):

            self.programCollection.insert_one({"username":u, "code":code, "level":level})

        else:

            self.programCollection.update_one({"username":u, "level":level}, {"$set":{"code":code}})


    def incrementScore(self, user_id, level, t, increment, large=False):

        user = self.userCollection.find_one({"_id":user_id})

        if large:
            solved_levels = "large_solved"
        else:
            solved_levels = "small_solved"

        if user:

            if level not in user[solved_levels]:

                if increment >= 0:
                    self.userCollection.update_one({"_id":user_id}, {"$inc":{"score":increment}, "$set":{"lastLevelTime":t}, "$push":{solved_levels:level}})
                else:
                    self.userCollection.update_one({"_id":user_id}, {"$inc":{"score":increment}, "$set":{"lastLevelTime":t}})

    def getleaderboard(self):

        return sorted([[record['score'], record['lastLevelTime'], str(record['username'])] for record in self.userCollection.find()], reverse=True, cmp=comp)

    def getTimes(self):

        return self.miscCollection.find_one({"_id":"times"})['times']

    def eval(self, user_id, output, level, large=False):

        directory = STATIC_DIR + SOL_DIR

        if large:
            directory += 'la_'
        else:
            directory += 'sm_'

        with open(directory + ("sol%d.out" % level)) as cor:
            correct = output.read().strip() == cor.read().strip()

        if correct:

            self.incrementScore(user_id=user_id, level=level, t=time.time(), increment=self.scores[level][large], large=large)

        return correct
