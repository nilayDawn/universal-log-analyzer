import logging
import warnings

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")

model = SentenceTransformer('all-MiniLM-L6-v2')


def run_semantic_detector(df):
    logger.info("Running Detector 1: Semantic Pipeline (MiniLM -> PCA -> IF)...")


    if len(df) < 20:
        logger.warning("Not enough logs for semantic detection.")
        return np.ones(len(df))


    embeddings = model.encode(
        df['details'].tolist(),
        show_progress_bar=True
    )

    n_comp = min(
        20,
        embeddings.shape[0],
        embeddings.shape[1]
    )

    pca = PCA(
        n_components=n_comp,
        random_state=42
    )

    compressed_embeddings = pca.fit_transform(
        embeddings
    )

    iso_forest = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    return iso_forest.fit_predict(
        compressed_embeddings
    )