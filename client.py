# PROJECR FLUSH V.1
# TYPE: SELF
from linepy import LINE, OEPoll
from linepy.next import LineNext
from linepy.asynckick import AsyncKick
from akad.ttypes import TalkException, OpType

import asyncio
import time
import traceback
import os
import random
import sys
import threading

from tools import LiveJSON, FixJSON
from datetime import datetime
from dateutil.relativedelta import relativedelta

settings = LiveJSON("settings.json")
FixJSON(settings, {"token": "#", "bots": {}, "limit":{}, "blacklist": {}, "prefix": {"self": "/", "kicker": "f"}})

kicker = {}
client = LINE()#LineNext('win10')
try:
    client.login(settings["token"])
except:
    client.login(showQr=True)
settings["token"] = client.authToken
poll = OEPoll(client)

def command(text, prefix):
    return None if not text.lower().startswith(prefix.lower()) else text.split(" ")[0][:len(prefix)].lower() == prefix.lower()

def formatTime(sec):
    mins, secs = divmod(sec, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    result = ""
    if days != 00: result += "%d days " % (days)
    if hours != 00: result += "%d hours " % (hours)
    if mins != 00: result += "%d mins " % (mins)
    result += "%d secs" % (secs)
    return result

cutOp = [13, 17, 19, 32]
threadOp = [25]

def __execute(op):
    global cutOp
    global threadOp

    for mid in settings["bots"]:
        if mid not in settings["limit"]: continue
        if int(time.mktime(datetime.now().timetuple())) >= int(settings["limit"][mid]):
            del settings["limit"][mid]

    if op.type == 13:
        op.param3 = op.param3.split('\x1e')
        group = None
        if len([mid for mid in op.param3 if mid in settings["blacklist"]]):
            group = client.getCompactGroup(op.param1)
        for cmid in op.param3:
            if cmid in settings["bots"]:
                try:
                    kicker[cmid].acceptGroupInvitation(op.param1)
                except:
                    if group == None:
                        group = client.getCompactGroup(op.param1)
                    members = [m.mid for m in group.members]
                    event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
                    out = [mid for mid in settings["bots"] if mid not in settings["limit"] and mid not in members]
                    c = 0
                    while c < len(event):
                        try:
                            if out != []:
                                event[c].inviteIntoGroup(group.id, out)
                            break
                        except TalkException as err:
                            if err.code == 35:
                                settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                            c += 1
                            print(err)
                            continue
                    
            elif cmid in settings["blacklist"] and op.param2 not in settings["bots"] and op.param2 != client.profile.mid:
                settings["blacklist"][op.param2] = op.param1
                if group == None:
                    group = client.getCompactGroup(op.param1)
                members = [m.mid for m in group.members]
                event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
                c = 0
                if event == []: return
                while c < len(event):
                    try:
                        event[c].cancelGroupInvitation(group.id, cmid)
                        break
                    except TalkException as err:
                        if err.code == 35:
                            settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                        c += 1
                        print(err)
                        continue

    if op.type == 17:
        if op.param2 in settings["blacklist"]:
            group = client.getCompactGroup(op.param1)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
            out = [mid for mid in settings["bots"] if mid not in settings["limit"] and mid not in members]
            black = [mid for mid in members if mid in settings["blacklist"]]
            c = 0
            if event == []: return
            if len(event) <= int((len(kicker)/2)/2):
                AsyncKick(asyncio.get_event_loop(), event[c], group.id, black)
                c += 1
            while c < len(event):
                try:
                    if out != []:
                        event[c].inviteIntoGroup(group.id, out)
                        out = []
                    for mid in black:
                        event[c].kickoutFromGroup(group.id, [mid])
                        black.remove(mid)
                    break
                except TalkException as err:
                    if err.code == 35:
                        settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                    c += 1
                    print(err)
                    continue
        if op.param2 in settings["bots"]:
            group = kicker[op.param2].getCompactGroup(op.param1)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
            out = [mid for mid in settings["bots"] if mid not in settings["limit"] and mid not in members]
            black = [mid for mid in members if mid in settings["blacklist"]]
            c = 0
            while c < len(event):
                try:
                    if out != []:
                        event[c].inviteIntoGroup(group.id, out)
                        out = []
                    for mid in black:
                        event[c].kickoutFromGroup(group.id, [mid])
                        black.remove(mid)
                    break
                except TalkException as err:
                    if err.code == 35:
                        settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                    c += 1
                    print(err)
                    continue

    if op.type == 19:
        if op.param3 in settings["bots"] and op.param2 not in settings["bots"] and op.param2 != client.profile.mid:
            settings["blacklist"][op.param2] = op.param1
            group = client.getCompactGroup(op.param1)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
            out = [mid for mid in settings["bots"] if mid not in settings["limit"] and mid not in members]
            black = [mid for mid in members if mid in settings["blacklist"]]
            c = 0
            if event == []: return
            if len(event) <= int((len(kicker)/2)/2):
                AsyncKick(asyncio.get_event_loop(), event[c], group.id, black)
                c += 1
            while c < len(event):
                try:
                    if out != []:
                        event[c].inviteIntoGroup(group.id, out)
                        out = []
                    for mid in black:
                        event[c].kickoutFromGroup(group.id, [mid])
                        black.remove(mid)
                    break
                except TalkException as err:
                    if err.code == 35:
                        settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                    c += 1
                    print(err)
                    continue

    if op.type == 32:
        if op.param3 in settings["bots"] or op.param3 == client.profile.mid:
            settings["blacklist"][op.param2] = op.param1
            group = None
            if op.param3 == client.profile.mid:
                for c in event:
                    try:
                        group = event[c].getCompactGroup(op.param1)
                    except:
                        continue 
            else:
                group = client.getCompactGroup(op.param1)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
            out = [mid for mid in settings["bots"] if mid not in settings["limit"] and mid not in members] + [client.profile.mid] if op.param3 == client.profile.mid else []
            black = [mid for mid in members if mid in settings["blacklist"]]
            c = 0
            if event == []: return
            if len(event) <= int((len(kicker)/2)/2):
                AsyncKick(asyncio.get_event_loop(), event[c], group.id, black)
                c += 1
            while c < len(event):
                try:
                    if out != []:
                        event[c].inviteIntoGroup(group.id, out)
                        out = []
                    for mid in black:
                        event[c].kickoutFromGroup(group.id, [mid])
                        black.remove(mid)
                    break
                except TalkException as err:
                    if err.code == 35:
                        settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                    c += 1
                    print(err)
                    continue

    if op.type == 25:
        msg = op.message
        text = msg.text
        to = msg.to
        if text == None: return
        text = msg.text.strip(" ").strip("\n").strip(" ")
        cmds = msg.text.split(" & ")
        if len(cmds) == 1: cmds = None
        if not cmds == None:
            for cmd in cmds:
                op.message.text = cmd
                __execute(op)
            return
        scmd = command(text, settings["prefix"]["self"])
        kcmd = command(text, settings["prefix"]["kicker"])
        if kcmd and len(text.split(" ")) != 1:
            kcmd = text.split(" ")[1]
        if scmd:
            scmd = text.split(" ")[0][len(settings["prefix"]["self"]):]

        if kcmd == "clear":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            if event == []: return
            if settings["blacklist"] == {}:
                return event[0].sendSuperText(group.id, "blacklist empty")
            event[0].sendSuperText(group.id, "%s blacklist cleared" % (len(settings["blacklist"])))
            settings["blacklist"] = {}
 
        if kcmd == "reset":
            settings["limit"] = {}
 
        if kcmd == "boost":
            for c in kicker:
                kicker[c].getProfile()
 
        if kcmd == "kick":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"] and mid not in settings["limit"]]
            if event == []: return
            event = event[0]
            midslist = []
            if "MENTION" in msg.contentMetadata:
                mentioness = eval(msg.contentMetadata["MENTION"])
                print(mentioness)
                midslist = [mention["M"] for mention in mentioness["MENTIONEES"] if mention["M"] not in settings["bots"]]
            for mid in midslist:
                try:
                    event.kickoutFromGroup(group.id, [mid])
                except TalkException as err:
                    if err.code == 35:
                        settings["limit"][event[c].profile.mid] = str(int(time.mktime((datetime.now() + relativedelta(days=1)).timetuple())))
                    continue

        if kcmd == "dpn":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            if event == []: return
            sep = msg.text.split(" ")
            if len(sep) <= 2: return
            sep.pop(0)
            sep.pop(0)
            for c in event:
                p = c.getProfile()
                p.displayName = " ".join(sep)
                c.updateProfile(p)
 
        if scmd == "speed":
            s = time.time()
            print("*")
            e = time.time() - s
            client.sendMentionV2(to, "@!", [client.profile.mid])
            client.sendSuperText(to, "%s secs [ %s ms ]" % (e, int(e*1000)))
 
        if kcmd == "speed":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            if event == []: return
            for c in event:
                s = time.time()
                c.getProfile()
                c.sendSuperText(group.id, "%s secs [ %s ms ]" % (time.time() - s, int((time.time() - s)*1000)))
 
        if kcmd == "status":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            if event == []: return
            for c in event:
                if c.profile.mid not in settings["limit"]:
                    c.sendSuperText(group.id, "kick & inivte: ready")
                    continue
                c.sendSuperText(group.id, "kick & invite: limit\nwill ready when arrive %s" % (formatTime(int(settings["limit"][c.profile.mid]) - int(time.mktime(datetime.now().timetuple())))))
 
        if kcmd == "join":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            out = [kicker[mid] for mid in settings["bots"] if mid not in members]
            if event == []: event = [client]
            if out == []: return event[0].sendSuperText(group.id, "already on group.")
            i = group.preventedJoinByTicket
            if i:
                group.preventedJoinByTicket = False
                event[0].updateGroup(group)
            ticket = event[0].reissueGroupTicket(group.id)
            for c in out:
                c.acceptGroupInvitationByTicket(group.id, ticket)
            if i:
                group.preventedJoinByTicket = True
                event[0].updateGroup(group)
            if not event[0].profile.mid == client.profile.mid: event[0].sendSuperText(group.id, "ready")

        if kcmd == "leave":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            if event == []: return
            for c in event:
                c.leaveGroup(group.id)

        if kcmd == "response":
            group = client.getCompactGroup(to)
            members = [m.mid for m in group.members]
            event = [kicker[mid] for mid in members if mid in settings["bots"]]
            if event == []: return
            for c in event:
                m = []
                for x in settings["bots"]:
                    m.append(x)
                    if x == c.profile.mid: break
                c.sendSuperText(group.id, len(m))
            
        if scmd == "reboot":
            os.execl(sys.executable, sys.executable, *sys.argv)
            
        if scmd == "logout":
            sys.exit(1)

__tokenKicker = [i for i in os.listdir(f"{os.path.dirname(os.path.abspath(__file__))}//kicker")]
settings["bots"] = []
for i in __tokenKicker:
    tem = LINE()#LineNext('win10')#LINE()
    auth = LiveJSON("kicker/%s" % i)
    try:
        #tem.login(token=auth["token"])
        tem.login(auth["token"])
    except:
        try:
            #tem.login(mail=auth["mail"], passwd=auth["pass"])
            tem.login(auth["mail"], auth["pass"])
        except:
            continue
    auth["token"] = tem.authToken
    kicker[tem.profile.mid] = tem
    settings["bots"].append(tem.profile.mid)

for event in kicker:
    contants = kicker[event].getAllContactIds()
    for mid in list(settings["bots"]) + [client.profile.mid]:
        if mid != kicker[event].profile.mid:
            if mid not in contants:
                try:
                    kicker[event].findAndAddContactsByMid(mid)
                except: pass

#async def main():
def main():
    while True:
        try:
            #ops = await client.poll.longpoll()
            #for op in ops:#[13, 17, 19]):
            #   await __execute(op)
            for op in poll.cutOperation(poll.longPoll(), cutOp):
                __execute(op)
        except TalkException as err:
            if err.code == 8:
                try:
                    client.getProfile()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                except:
                    print("client LOG_OUT")
                    sys.exit(1)
        except Exception as err:
            traceback.print_exc()
            print(err)
            
if __name__ == "__main__":
    main()
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())