# Baklava

## Dev set up

Mac Users

1. Make sure you have python3 installed.
2. git clone https://github.com/RichardNgKongYeow/Baklava.git
3. cd Baklava
4. git fetch -all (to get all remote branches then checkout the version/branch)
5. Install virtual env. `python3 -m pip install --user virtualenv`
6. Create virtual env. `python3 -m venv env`
7. Activate virtual env `source env/bin/activate`
8. Install dependencies `pip install -r requirements.txt`
9. git clone https://github.com/falcons-x/fx-py-sdk.git
10. cd fx-py-sdk
11. python3 setup.py install
12. cd ..
13. add a .env file in 
14. Run `python3 index.py`

Windows Users
1. env\Scripts\activate


To add tokens
1. ensure tokens exist in both marginx and baklava
2. add info to Pairs.py in chain_ids & pairs if not already added (uncomment them)
3. update info in Configs.config.yaml
4. run test.py first 