# Baklava

## Dev set up

Mac Users

1. Make sure you have python3 installed.
2. Install virtual env. `python3 -m pip install --user virtualenv`
3. Create virtual env. `python3 -m venv env`
4. Activate virtual env `source env/bin/activate`
5. git clone https://github.com/RichardNgKongYeow/Baklava.git
6. Install dependencies `pip install -r requirements.txt`
7. cd Baklava
8. git clone https://github.com/falcons-x/fx-py-sdk.git
9. cd fx-py-sdk
10. pip install -r requirements.txt
11. python3 setup.py install
12. add a .env file in 
13. Run `python3 index.py`

Windows Users
1. env\Scripts\activate


To add tokens
1. ensure tokens exist in both marginx and baklava
2. add info to Pairs.py in chain_ids & pairs if not already added (uncomment them)
3. update info in Configs.config.yaml