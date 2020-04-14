import pymongo
from pymongo import MongoClient
import config
import re


class mongo:

    def __init__(self):
        '''
        initiate connection to the database
        '''
        self.database_name = config.database
        self.collection_name = config.collection
        self.collection2_name = config.collection2
        self.collection3_name = config.collection3
        self.settings = {'host': '127.0.0.1:27017', 'options': 'ssl=false'}

        try:
            self.conn = MongoClient(
                "mongodb://{host}/?{options}".format(**self.settings))
            self.database = self.conn[self.database_name]
            # checked links
            self.collection = self.database[self.collection_name]
            # all links
            self.collection2 = self.database[self.collection2_name]
            # keywords by category
            self.collection3 = self.database[self.collection3_name]
        except Exception as ex:
            print("connetion to database failed")
            print(ex)
            exit(1)

    def __del__(self):
        self.conn.close()

    def is_link_exist(self, link):
        '''
        check if a link domain is already exists in the database
        '''
        onion_pattern = re.compile(r"[^\s]+\.onion")
        documents = self.collection.find({})
        tmp_link = link
        try:
            link = onion_pattern.findall(link)[0]
        except:
            self.collection2.update_one(
                {'link': tmp_link}, {"$set": {'checked': True}})
            return True
        for doc in documents:
            try:
                doc['link'] = onion_pattern.findall(doc['link'])[0]
            except:
                doc['link'] = None

            if doc['link'] == link:
                self.collection2.update_one(
                    {'link': tmp_link}, {"$set": {'checked': True}})
                return True
        return False

    def insert_link_info(self, link, title, description, emails, telegram_links, bitcoin_wallets, gathered_links, tags, date):
        '''
        insert link data to the database.
        insert gathered links into links database.
        update checked field.
        '''
        if len(gathered_links) > 0:
            self.collection2.insert_many(
                [{'link': i, 'checked': False} for i in gathered_links])
        self.collection.insert_one({'link': link,
                                    'title': title,
                                    'description': description,
                                    'emails': emails,
                                    'telegram_links': telegram_links,
                                    'bitcoin_wallets': bitcoin_wallets,
                                    'gathered_links': gathered_links,
                                    'tags': tags,
                                    'date': date
                                    })
        self.collection2.update_many(
            {'link': link}, {"$set": {'checked': True}})

    def add_tags(self, page):
        '''
        add tags of category by keywords
        '''
        documents = self.collection3.find({})
        tags = []
        for doc in documents:
            category = doc['category']
            keywords = doc['keywords']
            # check if any of the keywords are in the page
            if any(re.search(key, page, re.IGNORECASE) for key in keywords):
                tags.append(category)
                continue
        return tags

    def add_tags_by_title(self):
        '''
        add tags by title and description to existing db
        '''
        documents = self.collection.find({})
        documents2 = self.collection3.find({})
        for doc in documents:
            tags = []
            title = ''
            if doc['title']:
                title += doc['title']
            title += ' '
            if doc['description']:
                title += doc['description']
            documents2 = self.collection3.find({})
            for d in documents2:
                category = d['category']
                keywords = d['keywords']
                if any(re.search(i, title, re.IGNORECASE) for i in keywords):
                    tags.append(category)
                    continue
            self.collection.update_one({'link': doc['link']}, {
                                       '$set': {'tags': tags}})

    def get_unchecked_links(self):
        '''
        return list of unchecked links
        '''
        return [i['link'] for i in self.collection2.find({'checked': False})]

    def get_gathered_links(self):
        '''
        return full list of links gathered from each checked link
        '''
        all_links = []
        glinks = self.collection.find({})
        for document in glinks:
            all_links += document['gathered_links']
        return all_links

    def sort_unique(self):
        '''
        sort unique links (not from the same domain) from the database
        '''
        onion_pattern = re.compile(r"[^\s]+\.onion")
        documents = self.collection.find({})
        unique_documents = []
        for doc in documents:
            try:
                doc['link'] = onion_pattern.findall(doc['link'])[0]
            except:
                doc['link'] = None
            if doc['link']:
                flag = False
                if len(unique_documents) > 0:
                    for i in unique_documents:
                        if i['link'] == doc['link']:
                            flag = True
                            break
                if not flag:
                    unique_documents.append(doc)
                    print(doc['link'])
        print(len(unique_documents))
        # self.collection.insert_many(unique_documents)

    def insert_from_file(self, path):
        '''
        insert links to database from a file
        '''
        with open(path, 'r') as f:
            onion_pattern = re.compile(r"[^\s]+\.onion")
            links = onion_pattern.findall(f.read())
            print(self.collection2.count_documents({}))
            self.collection2.insert_many(
                [{'link': i, 'checked': False} for i in links])
            print(self.collection2.count_documents({}))
