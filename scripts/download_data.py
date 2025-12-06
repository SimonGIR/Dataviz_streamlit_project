# scripts/download_data.py
from utils.io import download_all


def main():
    print("Downloading all resources into data/ ...")
    download_all(overwrite=False)
    print("Done.")


if __name__ == "__main__":
    main()
