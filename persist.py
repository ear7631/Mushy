import json
import os
import entity
import hashlib
import uuid

"""
Because this is so light-weight, and subject to change, things will be stored
in a specific directory as JSON. This way, entries can be hand-modified if
this program changes, and requires no external packages.
"""


def initializeProfiles():
    if not os.path.exists("./profiles/"):
        os.mkdir("profiles")


def profileExists(username):
    return os.path.exists("./profiles/" + username + ".json")


def hashPassword(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    return salt, hashlib.sha512(password + salt).hexdigest()


def validate(username, password):
    if not profileExists(username):
        return False

    f = open("./profiles/" + username + ".json")
    j = f.read().strip()
    f.close()
    data = json.loads(j)
    hcode = data["hcode"]
    salt = data["salt"]

    salt, hcode_attempt = hashPassword(password, salt=salt)

    return hcode == hcode_attempt


def saveEntity(e):
    if profileExists(e.name):
        os.remove("./profiles/" + e.name + ".json")
    f = open("./profiles/" + e.name + ".json", "w")

    data = {}
    data["name"] = e.name
    data["hcode"] = e.hcode
    data["salt"] = e.salt

    tally_data = {}
    for key in e.tallies:
        if key in e.tallies_persist:
            tally_data[key] = e.tallies[key]
    data["tallies"] = tally_data

    bag_data = {}
    for key in e.bags:
        if key in e.bags_persist:
            bag_data[key] = e.bags[key]
    data["bags"] = bag_data

    data["facade"] = e.facade
    data["dm"] = e.dm

    data["languages"] = e.languages
    data["aliases"] = e.aliases
    data["settings"] = e.settings

    f.write(json.dumps(data))
    f.close()


def loadEntity(username):
    if not profileExists(username):
        raise IOError("Cannot load non-existing json for profile " + entity.name)

    f = open("./profiles/" + username + ".json")
    j = f.read().strip()
    f.close()
    data = json.loads(j)

    e = entity.Entity(name=username)
    e.tallies = data["tallies"]
    e.tallies_persist = e.tallies.keys()
    e.bags = data["bags"]
    e.bags_persist = e.bags.keys()
    e.hcode = data["hcode"]
    e.salt = data["salt"]
    e.dm = data["dm"]
    e.facade = data["facade"]
    e.languages = data["languages"]
    e.aliases = data["aliases"]
    e.settings = data["settings"]

    return e
