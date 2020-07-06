import os.path
from core.singleton import Singleton
import pickle
from core.config import Config
from core.singleton import Singleton
import hnswlib
import logging
from libs.utilities import Vividict


class FeatureManager(metaclass=Singleton):
    def __init__(self):
        self.path = Config().image_retrieval.get('feature_path')
        if not self.path:
            raise Exception('filepath not exist')
        self.features = dict()
        for category in os.listdir(self.path):
            self.features[category] = Vividict()
        self.load_feature()

    def load_feature(self):
        version = '1'
        for category in self.features.keys():
            base_path = os.path.join(self.path, category)
            for co_id in os.listdir(base_path):
                for item in os.listdir(os.path.join(base_path, co_id, version)):
                    name = item.split('.')[0]
                    if  not name == 'hnsw':
                        with open(os.path.join(base_path, co_id, version, item), 'rb') as f:
                            p = pickle.load(f)
                            self.features[category][co_id][name] = p

            for co_id in os.listdir(base_path):
                hnsw = hnswlib.Index(
                    space='cosine', dim=self.features[category][co_id]['pca'].n_components_)
                hnsw.load_index(os.path.join(base_path, co_id, version, 'hnsw.bin'))
                hnsw.set_ef(100)
                self.features[category][co_id]['hnsw'] = hnsw

    def update_feature(self, category, co_id):
        version = '1'
        base_path = os.path.join(self.path, category, co_id, version)
        if not os.path.exists(base_path):
            raise Exception('feature path not exist')

        for item in os.listdir(base_path):
            name = item.split('.')[0]
            if not name == 'hnsw':
                with open(os.path.join(base_path, item), 'rb') as f:
                    p = pickle.load(f)
                    self.features[category][co_id][name] = p

        hnsw = hnswlib.Index(
            space='cosine', dim=self.features[category][co_id]['pca'].n_components_)
        hnsw.load_index(os.path.join(base_path, 'hnsw.bin'))
        hnsw.set_ef(100)
        self.features[category][co_id]['hnsw'] = hnsw

        logging.info(
            'Feature updated, category: {}   co_id: {}'.format(category, co_id))

    def get_hnsw(self, category, co_id):
        return self.features[category][co_id]['hnsw']

    def get_pca(self, category, co_id):
        return self.features[category][co_id]['pca']

    def get_iid(self, category, co_id):
        return self.features[category][co_id]['iid']

    def get_label(self, category, co_id):
        return self.features[category][co_id]['label']