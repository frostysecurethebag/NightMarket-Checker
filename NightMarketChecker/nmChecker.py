import requests
import json
import re
import urllib3
import csv
import cloudscraper


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

path = "./NightMarket-Checker/NightMarketChecker/"

with open(path+"info.gg", encoding='utf-8') as f:
    x = f.readline().rstrip("\n").split("=")
region = str(x[1])
j = 0


class nmChecker:

    def __init__(self) -> None:
        self.name = ""
        self.lines = ("-"*150)

    def getCookie(self):

        self.sess = cloudscraper.CloudScraper(browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        })
        headers = {}
        headers['Content-Type'] = 'application/json'
        body = json.dumps({"client_id": "play-valorant-web-prod", "nonce": "1", "redirect_uri": "https://playvalorant.com/opt_in", "response_type": "token id_token"
                           })
        response = self.sess.post(
            "https://auth.riotgames.com/api/v1/authorization", data=body, headers=headers)
        return(response.json())

    def getToken(self, username, password):
        headers = {}
        data = json.dumps({
            "type": "auth",
            "username": username,
            "password": password,
            "remember": False,
            "language": "en_US"
        })
        headers['Content-Type'] = 'application/json'
        try:
            response = self.sess.put(
                "https://auth.riotgames.com/api/v1/authorization", data=data, headers=headers)
            cap = response.json()
            ggwp = re.split('#|&', cap['response']['parameters']['uri'])
            ggez = (ggwp[1]).split("=")
            return (str(ggez[1]))
        except KeyError:
            print(f"Credentials Invalid =====> {self.name}")
            exit()

    def getEntitle(self, token):
        headers = {}
        headers['Authorization'] = 'Bearer '+token
        headers['Content-Type'] = 'application/json'
        response = self.sess.post(
            "https://entitlements.auth.riotgames.com/api/token/v1", headers=headers)
        ggwp = response.json()
        headers['X-Riot-Entitlements-JWT'] = ggwp["entitlements_token"]

        return(headers)

    def getPuuid(self, headers):
        response = self.sess.get(
            "https://auth.riotgames.com/userinfo", headers=headers)
        ggwp = response.json()
        ggez = ggwp['sub']

        return ([ggez, headers])

    def getNight(self, puid, headers):
        price = []
        skinid = []
        response = self.sess.get("https://pd.{region}.a.pvp.net/store/v2/storefront/{puuid}".format(
            puuid=puid, region=region), headers=headers)
        ggwp = response.json()
        for i in ggwp['BonusStore']['BonusStoreOffers']:
            [price.append(k) for k in i['DiscountCosts'].values()]

        for i in ggwp['BonusStore']['BonusStoreOffers']:
            [skinid.append(k['ItemID']) for k in i['Offer']['Rewards']]

        return self.getSkinPrice(skinid, price)

    def getSkinPrice(self, skinid, price):
        skin = []
        both = []
        for i in skinid:
            response = requests.get(
                f"https://valorant-api.com/v1/weapons/skinlevels/{i}")
            ggwp = response.json()
            skin.append(ggwp['data']['displayName'])
        print(f"{self.lines}\n{self.name} {dict(zip(skin, price))}\n{self.lines}")
        [both.append((str(skin[i])+":"+str(price[i])))
            for i in range(len(skin))]

        return (both)

    # def csvWrite(self, all):
    #     with open("output.csv", 'a+', newline="\n") as csvfile:
    #         write = csv.writer(csvfile)
    #         write.writerows([all])

    def loop(self, acc):
        price = [acc[0]]
        self.getCookie()
        self.name = acc[0]
        token = self.getToken(acc[0], acc[1])
        entitle = self.getEntitle(token)
        puuid = self.getPuuid(entitle)
        price = [acc[0]] + (self.getNight(puuid[0], puuid[1]))
        # self.csvWrite(price)
