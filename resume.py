from google.cloud import datastore


datastore_client = datastore.Client()

class Data:

    def __init__(self, name):
        self.name = name
        self.entity = datastore.Entity(key=self.key)

    @property
    def kind(self):
        return self.__class__.__name__

    @property
    def key(self):
        return datastore_client.key(self.kind, self.name)

    def set(self, key_name, value):
        self.entity[key_name] = value

    def save(self):
        return datastore_client.put(self.entity)

    # def get(self):
        # `datastore.Entity(key=self.key)` と同じ
        # return datastore_client.get(self.key)

    @classmethod
    def get_or_create(cls, name):
        return cls(name)

    @classmethod
    def list(cls):
        return list(datastore_client.query(kind=cls.__name__).fetch())


class Resume(Data):
    pass


print(Resume.list())
