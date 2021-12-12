import requests
import json
import re
import urllib3
import csv


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("info.gg", encoding='utf-8') as f:
    x = f.readline().rstrip("\n").split("=")
region = str(x[1])


def getCookie():
    global sess
    sess = requests.Session()
    headers = {}
    headers['Content-Type'] = 'application/json'
    body = json.dumps({"client_id": "play-valorant-web-prod", "nonce": "1", "redirect_uri": "https://playvalorant.com/opt_in", "response_type": "token id_token"
                       })
    response = sess.post(
        "https://auth.riotgames.com/api/v1/authorization", data=body, headers=headers)
    return(response.json())


def getToken(username, password):
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
        response = sess.put(
            "https://auth.riotgames.com/api/v1/authorization", data=data, headers=headers)
        cap = response.json()
        ggwp = re.split('#|&', cap['response']['parameters']['uri'])
        ggez = (ggwp[1]).split("=")
        return (str(ggez[1]))
    except KeyError:
        print("Credentials Invalid")
        exit()


def getEntitle(token):
    headers = {}
    headers['Authorization'] = 'Bearer '+token
    headers['Content-Type'] = 'application/json'
    response = sess.post(
        "https://entitlements.auth.riotgames.com/api/token/v1", headers=headers)
    ggwp = response.json()
    headers['X-Riot-Entitlements-JWT'] = ggwp["entitlements_token"]

    return(headers)


def getPuuid(headers):
    response = sess.get("https://auth.riotgames.com/userinfo", headers=headers)
    ggwp = response.json()
    ggez = ggwp['sub']

    return ([ggez, headers])


def getNight(puid, headers):
    price = []
    skinid = []
    response = sess.get("https://pd.{region}.a.pvp.net/store/v2/storefront/{puuid}".format(
        puuid=puid, region=region), headers=headers, verify=False)
    ggwp = response.json()
    for i in ggwp['BonusStore']['BonusStoreOffers']:
        [price.append(k) for k in i['DiscountCosts'].values()]

    for i in ggwp['BonusStore']['BonusStoreOffers']:
        [skinid.append(k['ItemID']) for k in i['Offer']['Rewards']]

    return getSkinPrice(skinid, price)


def getSkinPrice(skinid, price):
    skin = []
    both = []
    for i in skinid:
        response = requests.get(
            f"https://valorant-api.com/v1/weapons/skinlevels/{i}")
        ggwp = response.json()
        skin.append(ggwp['data']['displayName'])
    print(dict(zip(skin, price)))
    [both.append((str(skin[i])+":"+str(price[i]))) for i in range(len(skin))]

    return (both)


def csvWrite(all):
    with open("output.csv", 'a+', newline="\n") as csvfile:
        write = csv.writer(csvfile)
        topcol = ['Account', 'Offer1', 'Offer2',
                  'Offer3', 'Offer4', 'Offer5', 'Offer6']
        write.writerow(topcol)
        for i in all:
            write.writerow(i)
        write.writerow("\n")
        print("-"*50)
        print("Saved all accounts informations in output.csv")


def main():
    all = []
    print("-"*150)
    with open("accounts.txt", encoding='utf-8') as f:
        for i in f.readlines():
            acc = i.rstrip("\n").split(";")
            getCookie()
            print(acc[0], end=" ")
            token = getToken(acc[0], acc[1])
            entitle = getEntitle(token)
            puuid = getPuuid(entitle)
            price = getNight(puuid[0], puuid[1])
            price.insert(0, acc[0])
            all.append(price)
    csvWrite(all)


main()
