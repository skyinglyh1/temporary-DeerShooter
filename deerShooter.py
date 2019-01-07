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
REFERRAL_BONUS_PERCENTAGE_KEY = "G6"
TOTAL_ONG_FOR_ADMIN = "G7"

PLAYER_REFERRAL_KEY = "P1"
PLAYER_LAST_CHECK_IN_TIME = "P2"
ID_PLAYER_PAY_ONGAMOUNT_KEY = "P3"
ID_UNPAID_PLAYER_KEY = "P4"

def Main(operation, args):
    ######################## for Admin to invoke Begin ###############
    if operation == "init":
        return init()
    if operation == "setLuckyContractHash":
        Require(len(args) == 1)
        reversedLuckyContractHash = args[0]
        return setLuckyContractHash(reversedLuckyContractHash)
    if operation == "setLuckyToOngRate":
        Require(len(args) == 2)
        ong = args[0]
        lucky = args[1]
        return setLuckyToOngRate(ong, lucky)
    if operation == "setReferralBonusPercentage":
        Require(len(args) == 1)
        referralBonus = args[0]
        return setReferralBonusPercentage(referralBonus)
    if operation == "setParameters":
        Require(len(args) == 3)
        zp = args[0]
        A = args[1]
        B = args[2]
        return setParameters(zp, A, B)
    if operation == "endGame":
        Require(len(args) == 2)
        roundId = args[0]
        score = args[1]
        return endGame(roundId, score)
    if operation == "adminInvest":
        Require(len(args) == 1)
        ongAmount = args[0]
        return adminInvest(ongAmount)
    if operation == "adminWithdraw":
        Require(len(args) == 2)
        toAcct = args[0]
        ongAmount = args[1]
        return adminWithdraw(toAcct, ongAmount)
    if operation == "adminWithdrawLucky":
        Require(len(args) == 2)
        toAcct = args[0]
        luckyAmount = args[1]
        return adminWithdrawLucky(toAcct, luckyAmount)
    if operation == "migrateContract":
        Require(len(args) == 8)
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        newReversedContractHash = args[7]
        return migrateContract(code, needStorage, name, version, author, email, description, newReversedContractHash)
    ######################## for Admin to invoke End ###############
    ######################## for Player to invoke Begin ###############
    if operation == "payToPlay":
        Require(len(args) == 2)
        account = args[0]
        ongAmount = args[1]
        return payToPlay(account, ongAmount)
    if operation == "addReferral":
        Require(len(args) == 2)
        toBeReferred = args[0]
        referral = args[1]
        return addReferral(toBeReferred, referral)
    if operation == "checkIn":
        Require(len(args) == 1)
        account = args[0]
        return checkIn(account)
    ######################## for Player to invoke End ###############
    ####################### Global Info Start #####################
    if operation == "getTotalOngForAdmin":
        return getTotalOngForAdmin()
    if operation == "getLuckyContractHash":
        return getLuckyContractHash()
    if operation == "getLuckyToOngRate":
        return getLuckyToOngRate()
    if operation == "getReferralBonusPercentage":
        return getReferralBonusPercentage()
    if operation == "getParameters":
        return getParameters()
    if operation == "getCurrentRound":
        return getCurrentRound()
    if operation == "getRoundGameStatus":
        Require(len(args) == 1)
        roundId = args[0]
        return getRoundGameStatus(roundId)
    ####################### Global Info End #####################
    ####################### Player Info Start #####################
    if operation == "getReferral":
        Require(len(args) == 1)
        toBeReferred = args[0]
        return getReferral(toBeReferred)
    if operation == "canCheckIn":
        Require(len(args) == 1)
        account = args[0]
        return canCheckIn(account)
    ####################### Player Info End #####################
    if operation == "getTrialGameAward":
        Require(len(args) == 2)
        gamePayOng = args[0]
        score = args[1]
        return getTrialGameAward(gamePayOng, score)
    return False


####################### Methods that only Admin can invoke Start #######################
def init():
    RequireWitness(Admin)
    inited = Get(GetContext(), INIIT_KEY)
    if inited:
        Notify(["idiot admin, you have initialized the contract"])
        return False
    else:
        Put(GetContext(), INIIT_KEY, 1)
        setReferralBonusPercentage(10)
        setLuckyToOngRate(1, 2)
        # zp = 0.02, A = 0.7, B = 30, the pass in parameters should = (real parameters) * 100
        setParameters(2, 70, 3000)
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
    Put(GetContext(), LUCKY_TO_ONG_RATE_KEY, Div(Mul(lucky, Magnitude), ong))
    Notify(["setRate", ong, lucky])
    return True

def setReferralBonusPercentage(referralBonus):
    RequireWitness(Admin)
    Require(referralBonus >= 0)
    Require(referralBonus <= 100)
    Put(GetContext(), REFERRAL_BONUS_PERCENTAGE_KEY, referralBonus)
    Notify(["setReferralBonus", referralBonus])
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

def endGame(roundId, score):
    RequireWitness(Admin)
    account = Get(GetContext(), concatKey(roundId, ID_PLAYER_PAY_ONGAMOUNT_KEY))
    playerUnpaidAmount = Get(GetContext(), concatKey(roundId, account))
    Require(playerUnpaidAmount > 0)
    Delete(GetContext(), concatKey(roundId, ID_PLAYER_PAY_ONGAMOUNT_KEY))
    odd = _calculateOdd(score)
    if odd > 0:
        payOut = Div(Mul(odd, playerUnpaidAmount), 100)
        Require(_transferONGFromContact(account, payOut))
        Notify(["win", roundId, account, score, payOut])
    Notify(["endGame", roundId])
    return True

def adminInvest(ongAmount):
    RequireWitness(Admin)
    Require(_transferONG(Admin, ContractAddress, ongAmount))
    Put(GetContext(), TOTAL_ONG_FOR_ADMIN, Add(getTotalOngForAdmin(), ongAmount))
    Notify(["adminInvest", ongAmount])
    return True

def adminWithdraw(toAcct, ongAmount):
    RequireWitness(Admin)
    roundId = getCurrentRound()
    roundUnpaidPlayer = Get(GetContext(), concatKey(roundId, ID_UNPAID_PLAYER_KEY))
    Require(not roundUnpaidPlayer)
    totalOngForAdmin = getTotalOngForAdmin()
    Require(ongAmount <= totalOngForAdmin)
    Put(GetContext(), TOTAL_ONG_FOR_ADMIN, Sub(getTotalOngForAdmin(), ongAmount))

    Require(_transferONGFromContact(toAcct, ongAmount))
    Notify(["adminWithdraw", toAcct, ongAmount])
    return True

def adminWithdrawLucky(toAcct, luckyAmount):
    RequireWitness(Admin)
    revesedContractAddress = getLuckyContractHash()
    params = [ContractAddress]
    totalLuckyAmount = DynamicAppCall(revesedContractAddress, "balanceOf", params)
    if luckyAmount <= totalLuckyAmount:
        params = [ContractAddress, toAcct, luckyAmount]
        res = DynamicAppCall(revesedContractAddress, "transfer", params)
        Require(res)
    Notify(["adminWithdrawLucky", toAcct, luckyAmount])
    return True

def migrateContract(code, needStorage, name, version, author, email, description, newReversedContractHash):
    RequireWitness(Admin)
    param = state(ContractAddress)
    totalOngAmount = Invoke(0, ONGAddress, 'balanceOf', param)
    if totalOngAmount > 0:
        res = _transferONGFromContact(newReversedContractHash, totalOngAmount)
        Require(res)
    revesedContractAddress = Get(GetContext(), LUCKY_CONTRACT_HASH_KEY)
    params = [ContractAddress]
    totalLuckyAmount = DynamicAppCall(revesedContractAddress, "balanceOf", params)
    if totalLuckyAmount > 0:
        params = [ContractAddress, newReversedContractHash, totalLuckyAmount]
        res = DynamicAppCall(revesedContractAddress, "transfer", params)
        Require(res)
    res = Migrate(code, needStorage, name, version, author, email, description)
    Require(res)
    Notify(["Migrate Contract successfully"])
    return True
####################### Methods that only Admin can invoke End #######################


######################## Methods for Players Start ######################################
def payToPlay(account, ongAmount):
    RequireWitness(account)
    Require(ongAmount > 0)
    currentId = Add(getCurrentRound(), 1)

    Require(_transferONG(account, ContractAddress, ongAmount))
    Put(GetContext(), ROUND_ID_NUMBER_KEY, currentId)

    # Put(GetContext(), concatKey(concatKey(currentId, PLAYER_PAY_ONGAMOUNT_KEY), account), ongAmount)

    Put(GetContext(), concatKey(currentId, ID_UNPAID_PLAYER_KEY), account)

    Put(GetContext(), concatKey(currentId, ID_PLAYER_PAY_ONGAMOUNT_KEY), ongAmount)

    Put(GetContext(), TOTAL_ONG_FOR_ADMIN, Add(getTotalOngForAdmin(), ongAmount))
    # deal with Lucky sending and referral Lucky sending
    _referralLuckyBalanceToBeAdd = 0
    acctLuckyBalanceToBeAdd = Div(Mul(ongAmount, getLuckyToOngRate()), Magnitude)
    ############### Transfer Lucky TWO times to account and referral ###############
    # transfer LUCKY to account
    params = [ContractAddress, account, acctLuckyBalanceToBeAdd]
    revesedContractAddress = Get(GetContext(), LUCKY_CONTRACT_HASH_KEY)
    res = DynamicAppCall(revesedContractAddress, "transfer", params)
    Require(res)
    referral = getReferral(account)
    if len(referral) == 20:
        # transfer LUCKY to referral
        _referralLuckyBalanceToBeAdd = Div(Mul(acctLuckyBalanceToBeAdd, getReferralBonusPercentage()), 100)
        params = [ContractAddress, referral, _referralLuckyBalanceToBeAdd]
        res = DynamicAppCall(revesedContractAddress, "transfer", params)
        Require(res)

    Notify(["payToPlay", currentId, account, ongAmount])
    return True


def addReferral(toBeReferred, referral):
    RequireScriptHash(toBeReferred)
    RequireScriptHash(referral)
    if CheckWitness(Admin) or CheckWitness(toBeReferred):
        if not getReferral(toBeReferred):
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
######################## Methods for Players End ######################################


################## Global Info Start #######################
def getTotalOngForAdmin():
    return Get(GetContext(), TOTAL_ONG_FOR_ADMIN)

def getLuckyContractHash():
    """
    :return: the reversed Lucky contract hash
    """
    return Get(GetContext(), LUCKY_CONTRACT_HASH_KEY)

def getLuckyToOngRate():
    """
    Div(Mul(Mul(lucky, LuckyMagnitude), Magnitude), Mul(ong, ONGMagnitude))
     lucky
    ------- * Magnitude
     ong
    :return:
    """
    return Get(GetContext(), LUCKY_TO_ONG_RATE_KEY)

def getReferralBonusPercentage():
    return Get(GetContext(), REFERRAL_BONUS_PERCENTAGE_KEY)

def getParameters():
    zp = Get(GetContext(), ZP_KEY)
    A = Get(GetContext(), A_KEY)
    B = Get(GetContext(), B_KEY)
    return [zp, A, B]

def getCurrentRound():
    return Get(GetContext(), ROUND_ID_NUMBER_KEY)

def getRoundGameStatus(roundId):
    """
    :param roundId:
    :return:
    0 means roundId have not started yet
    1 means roundId have started, not ended yet.
    2 means roundId have ended
    """
    account = Get(GetContext(), concatKey(roundId, ID_PLAYER_PAY_ONGAMOUNT_KEY))
    if not account:
        return 0
    playerUnpaidAmount = Get(GetContext(), concatKey(roundId, account))
    if playerUnpaidAmount:
        return 1
    return 2

################## Global Info End #######################


####################### Player Info Start #####################
def getReferral(toBeReferred):
    return Get(GetContext(), concatKey(PLAYER_REFERRAL_KEY, toBeReferred))

def canCheckIn(account):
    """
    :param account:
    :return: return == 0 => can NOT check in.
              return > 0 => can check in.
    """
    lastTimeCheckIn = Get(GetContext(), concatKey(PLAYER_LAST_CHECK_IN_TIME, account))
    if not lastTimeCheckIn:
        return Div(GetTime(), DaySeconds)
    now = GetTime()
    days = Div(now, DaySeconds)
    if days > lastTimeCheckIn:
        return days
    else:
        return 0
####################### Player Info End #####################

def getTrialGameAward(gamePayOng, score):
    odd = _calculateOdd(score)
    if odd > 0:
        return Div(Mul(odd, gamePayOng), 100)
    return 0

######################### Utility Methods Start #########################

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
    p = Add(abs(blockHash) % 1000000, 1)
    if Sub(1000000, zp) <= p:
        return 100
    const = (B*p+1)*p
    tmp_x = (B*p+1 - A) * 100
    const1 = (B * p + 1) * p * 101
    const2 = (B * p + 1) * p * 500000
    if tmp_x < const1:
        tmp_x = const1
    elif tmp_x > const2:
        tmp_x = const2
    X = 0
    if score >=0 and score < 20:
        X = Div(Mul((tmp_x - const * 100) * 2, 10), const)
    if score >=20 and score < 30:
        X = Div(Mul((tmp_x - const * 100) * 3, 10), const)
    if score >=30 and score < 40:
        X = Div(Mul((tmp_x - const * 100) * 4, 10), const)
    if score >=40 and score < 50:
        X = Div(Mul((tmp_x - const * 100) * 5, 10), const)
    if score >=50 and score < 70:
        X = Div(Mul((tmp_x - const * 100) * 7, 10), const)
    if score >=70 and score < 100:
        X = Div(Mul((tmp_x - const * 100) * 8, 10), const)
    if score >=100:
        X = Div((tmp_x - const * 100), const)
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
######################### Utility Methods End #########################

