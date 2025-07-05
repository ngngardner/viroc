from pathlib import Path

import kaggle

kaggle.api.authenticate()

owner = "binh234"
ds_name = "ccpd-preprocess"

download_path = Path.home() / ".cache" / "kaggle" / "datasets" / owner / ds_name
download_path.mkdir(parents=True, exist_ok=True)
dataset_path = download_path / "CCPD2019" / "ccpd_base"


def download():
    kaggle.api.dataset_download_files(
        f"{owner}/{ds_name}",
        path=download_path,
        unzip=True,
        quiet=False,
    )
