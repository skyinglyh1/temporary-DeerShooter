"""
DeerShooter Game
"""
from boa.interop.Ontology.Contract import Migrate
from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetScriptContainer
from boa.interop.Ontology.Native import Invoke
from boa.interop.Ontology.Runtime import GetCurrentBlockHash
from boa.builtins import ToScriptHash, concat, state, sha256
from boa.interop.System.Transaction import GetTransactionHash
from boa.interop.System.App import DynamicAppCall
"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True
"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeMath.py
"""

def Add(a, b):
    """
    Adds two numbers, throws on overflow.
    """
    c = a + b
    Require(c >= a)
    return c

def Sub(a, b):
    """
    Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a>=b)
    return a-b

def ASub(a, b):
    if a > b:
        return a - b
    if a < b:
        return b - a
    else:
        return 0

def Mul(a, b):
    """
    Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    if a == 0:
        return 0
    c = a * b
    Require(c / a == b)
    return c

def Div(a, b):
    """
    Integer division of two numbers, truncating the quotient.
    """
    Require(b > 0)
    c = a / b
    return c

def Pwr(a, b):
    """
    a to the power of b
    :param a the base
    :param b the power value
    :return a^b
    """
    c = 0
    if a == 0:
        c = 0
    elif b == 0:
        c = 1
    else:
        i = 0
        c = 1
        while i < b:
            c = Mul(c, a)
            i = i + 1
    return c

def Sqrt(a):
    """
    Return sqrt of a
    :param a:
    :return: sqrt(a)
    """
    c = Div(Add(a, 1), 2)
    b = a
    while(c < b):
        b = c
        c = Div(Add(Div(a, c), c), 2)
    return c

ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
Admin = ToScriptHash('AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p')
INIIT_KEY = "Inited"
LUCKY_CONTRACT_HASH_KEY = "LuckyContract"
ContractAddress = GetExecutingScriptHash()
LuckyMagnitude = 1000000000
ONGMagnitude = 1000000000
Magnitude = 1000000000000000000000000000000
ParameterMagnitude = 100
DaySeconds = 86400
RoundDuration = 45

ROUND_ID_NUMBER_KEY = "G1"
LUCKY_TO_ONG_RATE_KEY = "G2"
A_KEY = "G3"
B_KEY = "G4"
ZP_KEY = "G5"
ROUND_START_TIME_KEY = "G6"


PLAYER_REFERRAL_KEY = "P1"
PLAYER_LAST_CHECK_IN_TIME = "P2"
PLAYER_PAY_ONGAMOUNT_KEY = "P3"

def Main(operation, args):
    if operation == "init":
        return init()

    return False

def init():
    RequireWitness(Admin)
    inited = Get(GetContext(), INIIT_KEY)
    if inited:
        Notify(["idiot admin, you have initialized the contract"])
        return False
    else:
        Put(GetContext(), INIIT_KEY, 1)
        Notify(["Initialized contract successfully"])
    return True

def setLuckyContractHash(reversedLuckyContractHash):
    RequireWitness(Admin)
    Put(GetContext(), LUCKY_CONTRACT_HASH_KEY, reversedLuckyContractHash)
    Notify(["setLuckyContractHash", reversedLuckyContractHash])
    return True

def setLuckyToOngRate(ong, lucky):
    """
    Say, if the player puts 1 ONG and he can get 0.5 Lucky, then ong = 2, lucky =1, please neglect the decimals
    :param ong:
    :param lucky:
    :return:
    """
    RequireWitness(Admin)
    Put(GetContext(), LUCKY_TO_ONG_RATE_KEY, Div(Mul(Mul(lucky, LuckyMagnitude), Magnitude), Mul(ong, ONGMagnitude)))
    Notify(["setRate", ong, lucky])
    return True

def setParameters(zp, A, B):
    """
    Make sure zp, A, B should be 100 * (the actual values)
    :param zp:
    :param A:
    :param B:
    :return:
    """
    RequireWitness(Admin)
    Put(GetContext(), ZP_KEY, zp)
    Put(GetContext(), A_KEY, A)
    Put(GetContext(), B_KEY, B)
    Notify(["setParameters", zp, A, B])
    return True

def settleAccount(id, account, score):
    RequireWitness(Admin)
    playerPaidAmount = Get(GetContext(), concatKey(concatKey(id, PLAYER_PAY_ONGAMOUNT_KEY), account))
    odd = _calculateOdd(score)
    if odd > 0:
        payOut = Div(Mul(odd, playerPaidAmount), 100)
        Require(_transferONGFromContact(account, payOut))
        Notify(["win", id, account, score, payOut])
    return True


def play(account, ongAmount):
    RequireWitness(account)
    Require(ongAmount > 0)
    currentId = Get(GetContext(), ROUND_ID_NUMBER_KEY)
    nextID = Add(currentId, 1)

    Require(_transferONG(account, ContractAddress, ongAmount))
    Put(GetContext(), ROUND_ID_NUMBER_KEY, nextID)
    # Put(GetContext(), concatKey(nextID, ROUND_START_TIME_KEY), GetTime())
    Put(GetContext(), concatKey(concatKey(nextID, PLAYER_PAY_ONGAMOUNT_KEY), account), ongAmount)

    # deal with Lucky sending and referral Lucky sending


    Notify(["play", nextID, account, ongAmount])
    return True


def addReferral(toBeReferred, referral):
    RequireScriptHash(toBeReferred)
    RequireScriptHash(referral)
    if CheckWitness(Admin) or CheckWitness(toBeReferred):
        if not getReferrral(toBeReferred):
            Put(GetContext(), concatKey(PLAYER_REFERRAL_KEY, toBeReferred), referral)
            Notify(["addReferral", toBeReferred, referral])
            return True
    return False


def checkIn(account):
    RequireWitness(account)

    Require(canCheckIn(account) > 0)

    freeLuckyAmount = LuckyMagnitude
    params  = [ContractAddress, account, freeLuckyAmount]
    revesedContractAddress = Get(GetContext(), LUCKY_CONTRACT_HASH_KEY)
    res = DynamicAppCall(revesedContractAddress, "transfer", params)
    Require(res)
    Notify(["checkIn", account])
    return True



def getReferrral(toBeReferred):
    return Get(GetContext(), concatKey(PLAYER_REFERRAL_KEY, toBeReferred))

def canCheckIn(account):
    lastTimeCheckIn = Get(GetContext(), concatKey(PLAYER_LAST_CHECK_IN_TIME, account))
    if not lastTimeCheckIn:
        return Div(Sub(GetTime(), 1546272000), DaySeconds)
    now = GetTime()
    # 1546272000  <=> January 1, 2019 12:00:00 AM GMT+08:00
    days = Div(Sub(now, 1546272000), DaySeconds)
    if days > lastTimeCheckIn:
        return days
    else:
        return 0


# def getRandomX(zp, A, B, score):
#     p = random.randint(1, 1000000)/1000000
#     if 1-zp <= p:
#         return 1.00
#     fp = 1-A/(B*p+1)
#     tmp_x = fp/p
#     if tmp_x < 1.01:
#         tmp_x = 1.01
#     elif tmp_x > 5000:
#         tmp_x = 5000
#     x = 0
#     if score >= 0 and score < 20:
#         x = (tmp_x -1) * 0.2
#     elif score >=20 and score < 30:
#         x = (tmp_x -1) * 0.3
#     elif score >= 30 and score < 40:
#         x = (tmp_x - 1) * 0.4
#     elif score >=40 and score < 50:
#         x = (tmp_x -1) * 0.5
#     elif score >=50 and score < 70:
#         x = (tmp_x -1) * 0.7
#     elif score >=70 and score < 100:
#         x = (tmp_x -1) * 0.8
#     elif score >= 100:
#         x = (tmp_x - 1)
#     return round(x, 2)


def _calculateOdd(score):
    """
    Remember that zp, A, B are 100 * (the actual values), respectively.
    :param score:
    :return: 100 * (the actual odd)
    """
    zp = Get(GetContext(), ZP_KEY)
    A = Get(GetContext(), A_KEY)
    B = Get(GetContext(), B_KEY)
    zp = Mul(zp, 10000)
    A = Mul(A, 10000)
    B = Mul(B, 10000)
    blockHash = GetCurrentBlockHash()
    p = Add(blockHash % 1000000, 1)
    if Sub(1000000, zp) <= p:
        return 1
    const = (B*p+1)*p*100
    tmp_x = (B*p+1 - A) * 100
    minOdd = 101
    maxOdd = 500000
    if tmp_x < minOdd:
        return minOdd
    elif tmp_x > maxOdd:
        return maxOdd
    X = 0
    if score >=0 and score < 20:
        X = Div(Mul((tmp_x - const) * 2, 1000), const)
    if score >=20 and score < 30:
        X = Div(Mul((tmp_x - const) * 3, 1000), const)
    if score >=30 and score < 40:
        X = Div(Mul((tmp_x - const) * 4, 1000), const)
    if score >=40 and score < 50:
        X = Div(Mul((tmp_x - const) * 5, 1000), const)
    if score >=50 and score < 70:
        X = Div(Mul((tmp_x - const) * 7, 1000), const)
    if score >=70 and score < 100:
        X = Div(Mul((tmp_x - const) * 8, 1000), const)
    if score >=100:
        X = Div(Mul((tmp_x - const), 100), const)
    return X

def _transferONG(fromAcct, toAcct, amount):
    """
    transfer ONG
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    param = state(fromAcct, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def _transferONGFromContact(toAcct, amount):
    param = state(ContractAddress, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False


def concatKey(str1,str2):
    """
    connect str1 and str2 together as a key
    :param str1: string1
    :param str2:  string2
    :return: string1_string2
    """
    return concat(concat(str1, '_'), str2)


































































