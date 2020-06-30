import os.path
from core.singleton import Singleton
import pickle
from core.config import Config
from core.singleton import Singleton
import hnswlib
import logging


class FeatureManager(metaclass=Singleton):
    def __init__(self):
        self.path = Config().image_retrival.get('feature_path')
        self.features = dict()
        for category in os.listdir(self.path):
            t = dict()
            t['hnsw'] = dict()
            t['pca'] = dict()
            t['label'] = dict()
            t['iid'] = dict()
            self.features[category] = t
        self.load_feature()

    def load_feature(self):
        if not self.path:
            raise Exception('filepath is required')

        # load fetures
        for category in self.features.keys():
            pca_path = os.path.join(self.path, category, 'pca')
            for _file in os.listdir(pca_path):
                file_name = _file.split('.')[0]
                with open(os.path.join(pca_path, _file), 'rb') as f:
                    pca = pickle.load(f)
                    self.features[category]['pca'][file_name] = pca

            iid_path = os.path.join(self.path, category, 'iid')
            for _file in os.listdir(iid_path):
                file_name = _file.split('.')[0]
                with open(os.path.join(iid_path, _file), 'rb') as f:
                    iid = pickle.load(f)
                    self.features[category]['iid'][file_name] = iid

            label_path = os.path.join(self.path, category, 'label')
            for _file in os.listdir(label_path):
                file_name = _file.split('.')[0]
                with open(os.path.join(label_path, _file), 'rb') as f:
                    label = pickle.load(f)
                    self.features[category]['label'][file_name] = label

            hnsw_path = os.path.join(self.path, category, 'hnsw')
            for _file in os.listdir(hnsw_path):
                file_name = _file.split('.')[0]
                hnsw = hnswlib.Index(
                    space='cosine', dim=self.features[category]['pca'][file_name].n_components_)
                hnsw.load_index(os.path.join(hnsw_path, _file),
                                max_elements=len(self.features[category]['iid'][file_name][0]))
                hnsw.set_ef(100)
                self.features[category]['hnsw'][file_name] = hnsw

    def get_hnsw(self, category, co_id):
        return self.features[category]['hnsw'][co_id]

    def get_pca(self, category, co_id):
        return self.features[category]['pca'][co_id]

    def get_iid(self, category, co_id):
        return self.features[category]['iid'][co_id]

    def get_label(self, category, co_id):
        return self.features[category]['label'][co_id]

    def update_feature(self, category, co_id):
        pca_path = os.path.join(self.path, category, 'pca', co_id + '.bin')
        if not os.path.exists(pca_path):
            raise Exception('feature path not exist')
        with open(pca_path, 'rb') as f:
            pca = pickle.load(f)
            self.features[category]['pca'][co_id] = pca

        iid_path = os.path.join(self.path, category, 'iid', co_id + '.bin')
        with open(iid_path, 'rb') as f:
            iid = pickle.load(f)
            self.features[category]['iid'][co_id] = iid

        label_path = os.path.join(self.path, category, 'label', co_id + '.bin')
        with open(label_path, 'rb') as f:
            label = pickle.load(f)
            self.features[category]['label'][co_id] = label

        hnsw_path = os.path.join(self.path, category, 'hnsw', co_id + '.bin')
        hnsw = hnswlib.Index(
            space='cosine', dim=self.features[category]['pca'][co_id].n_components_)
        hnsw.load_index(hnsw_path, max_elements=len(
            self.features[category]['iid'][co_id][0]))
        hnsw.set_ef(100)
        self.features[category]['hnsw'][co_id] = hnsw

        logging.info(
            'Feature updated, category: {}   co_id: {}'.format(category, co_id))
