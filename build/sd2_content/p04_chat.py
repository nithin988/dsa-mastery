"""Problem 4: Design a chat system."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "Order mix-up", "kind": "warn",
     "scene": lambda cx, cy, w: k.phone(cx - 56, cy - 14, None, "warn") + k.phone(cx + 56, cy - 14, None, "warn") + k.badge(cx, cy - 14, "yes? / no!", "warn") + k.note(cx, cy + 50, "answers arrive before questions", "warn"),
     "caption": "ShopKart adds chat between buyers and sellers. Two replies cross on the network and show up in the wrong order."},
    {"title": "The double send", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx - 60, cy - 14, None, "bad") + k.flow(cx - 36, cy - 14, cx + 26, cy - 14, "bad", "send x2") + k.cloud(cx + 62, cy - 14, None, "bad") + k.note(cx, cy + 50, "no ack, so it retried", "bad"),
     "caption": "A phone on a weak signal sends a message, hears nothing back and sends it again. The seller sees it twice."},
    {"title": "Numbered messages", "kind": "ok",
     "scene": lambda cx, cy, w: k.badge(cx, cy - 40, "1  hi", "ok") + k.badge(cx, cy - 8, "2  hello", "ok") + k.badge(cx, cy + 24, "3  are you there?", "ok") + k.note(cx, cy + 60, "the server numbers them", "ok"),
     "caption": "The server gives every message a number in its conversation. Order and duplicates stop being guesses."},
], "From mixed up to numbered", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 200, [
    k.phone(50, 60, "Alice"), k.flow(70, 60, 130, 60, "acc", "send"),
    k.balancer(160, 60, "gateway", "acc"), k.flow(186, 60, 250, 60, "acc"),
    k.server(280, 60, "chat server"), k.flow(310, 60, 390, 60, "acc", "seq + save"),
    k.database(430, 60, "messages", "acc"), k.flow(280, 90, 280, 130, "ok"),
    k.cache(280, 150, "who is where", "ok"), k.flow(306, 150, 430, 150, "ok", "push to gateway"),
    k.balancer(470, 150, "gateway", "ok"), k.flow(496, 150, 560, 150, "ok"),
    k.phone(600, 150, "Bob", "ok"), k.flow(460, 100, 560, 70, "warn", "offline: sync later", dash=True),
    k.cloud(610, 60, "push alert", "warn"),
], "Chat system design", None)

DATA = dict(
    time="35 minutes",
    seen_at="A staple for messaging and social companies",
    tagline="Chat looks like sending text. The interview is about three promises: messages stay in order, never appear twice, and reach a phone that was offline.",
    story=dict(
        title="Buyers want to talk to sellers",
        paras=[
            "After checkout, ShopKart buyers ask sellers small questions: is it in stock, can it ship to my city. Email is slow, so the team adds chat. The first version posts each message to a server that stores it and shows it to the other side.",
            "Within a week the complaints arrive. Two replies show up in the wrong order and the conversation makes no sense. On a train, one buyer taps send, sees no confirmation, taps again, and the seller reads the same question twice. A seller who closed the app misses a message entirely. Each problem has a standard fix, and the interview is about knowing all three.",
        ],
        strip=STRIP),
    requirements=["Functional: send and receive one to one and group messages; see history; get messages that arrived while offline; delivery and read marks. Non-functional: messages are never lost once acknowledged; order is the same for everyone in a conversation; delivery feels instant when both people are online; many devices per person."],
    numbers=[
        ("Assumptions", "1 billion users, 100 billion messages a day, groups up to 1,000 people, media stored separately. Confirm these with the interviewer."),
        ("Message rate", "100 billion / 86,400 seconds is about **1.2 million messages per second** (peak around 3 million)."),
        ("Storage", "At 100 bytes of text each, 100 billion messages is about **10 TB a day**. Media goes to object storage, not here."),
        ("Connections", "If 500 million people are online at once and one gateway machine holds 100,000 idle connections, you need about **5,000 gateway machines**."),
        ("The shape", "Writes are constant and small, and connections are enormous. The hard part is holding connections and keeping order, not raw storage speed."),
    ],
    numbers_try=[],
    design_figure=DESIGN,
    design=[
        ("The server owns the order", "Each conversation has one counter. When a message arrives, the server adds one to the counter and stores the message with that number. Clients sort by the number, never by their own clocks, which can be wrong.",
         _small([k.phone(50, 48, None), k.flow(70, 48, 140, 48, "acc", "send"), k.server(170, 48, "chat server"), k.flow(200, 48, 280, 48, "acc"), k.badge(340, 48, "conv 7: next = 3", "acc"), k.flow(400, 48, 470, 48, "acc", "store"), k.database(510, 48, "messages", "acc"), k.note(590, 52, "seq 3", "ok")], "Server assigned sequence")),
        ("A retry must be safe", "Each message carries an id made by the sending phone. If the same id arrives twice, the server returns the first sequence number and stores nothing new. So a phone can retry as often as it needs to.",
         _small([k.phone(50, 48, None), k.flow(70, 48, 150, 48, "warn", "id a-1"), k.server(180, 48, "chat server"), k.flow(210, 48, 290, 48, "warn", "seen a-1?"), k.database(330, 48, "messages", "warn"), k.flow(356, 48, 450, 48, "ok", "same seq"), k.badge(520, 48, "1 stored", "ok"), k.note(595, 52, "no second copy", "ok")], "Idempotent send")),
        ("Offline phones catch up by number", "A phone remembers the last sequence it saw. When it reconnects it asks for everything after that number and gets the missing messages in order. A brand new device asks from zero.",
         _small([k.phone(50, 48, "offline", "warn"), k.flow(76, 48, 150, 48, "acc", "after seq 2"), k.server(180, 48, "sync"), k.flow(210, 48, 290, 48, "acc"), k.database(330, 48, "messages", "acc"), k.flow(356, 48, 450, 48, "ok", "3, 4, 5"), k.badge(520, 48, "in order", "ok")], "Offline sync")),
        ("Push when online, alert when not", "Each phone keeps one long connection to a gateway, and a fast lookup remembers which gateway holds whom. For an online person the message is pushed down that connection. For an offline one, a mobile push alert says something is waiting, and the data comes by sync.",
         _small([k.server(60, 48, "chat server"), k.flow(90, 48, 170, 48, "ok", "who?"), k.cache(200, 48, "directory", "ok"), k.flow(226, 48, 310, 48, "ok", "gateway 12"), k.balancer(345, 48, "gateway", "ok"), k.flow(372, 48, 450, 48, "ok", "push"), k.phone(480, 48, None, "ok"), k.cloud(580, 48, "alert", "warn")], "Push and alert")),
    ],
    hard_title="The hard part: order, duplicates and the offline gap",
    hard_paras=[
        "These three problems share one answer: a number per conversation, assigned by one owner. The experiment below builds exactly that store and shows the retry returning the same number and a reconnecting phone fetching only what it missed.",
        "For real time delivery the simplest option is a long lived connection. Server sent events keep one HTTP connection open and stream messages down it; WebSockets do the same in both directions. Either way the gateway is stateful, so spread connections across many machines and keep the user to gateway map in a fast store.",
    ],
    **{"try": [("fd", 1, 0, 0, "Sequence numbers, idempotent sends and offline sync"), ("fd", 1, 0, 1, "A long lived connection that pushes messages")]},
    scale=[
        ("A gateway machine dies", "Its 100,000 phones reconnect to other gateways and sync from their last number. Nothing is lost because messages were stored before they were pushed.", "ok"),
        ("Hot conversations", "Partition storage by conversation id so one huge group does not overload a shard, and cap group size so a single send does not fan out without limit.", ""),
        ("Group messages", "Store the message once, give it one number, and deliver to each member. Small groups push directly; very large ones fan out through a queue.", ""),
        ("Two devices, one person", "Track the last seen number per device, not per user. Each device syncs on its own.", ""),
        ("Read receipts flood the system", "Batch them and send only the latest number read per conversation instead of one event per message.", "bad"),
    ],
    scenario=scen("fd", 1),
    who="A staple messaging question: reported by candidates, not official.",
    real=[
        dict(company="MDN Web Docs", text="The documentation describes server sent events as a way for a server to push updates to a browser over one long lived HTTP connection, with automatic reconnection and a last event id the client can send back after a drop.", url="https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events", source="MDN: Server-sent events"),
    ],
    recap=dict(
        points=["Three promises: ordered, never duplicated, reaches offline phones.",
                "Order comes from a per conversation sequence number the server assigns, never from client clocks.",
                "A client generated message id makes retries safe: same id, same sequence number.",
                "Offline sync is 'give me everything after number N'.",
                "Hold long lived connections on gateways and keep a user to gateway map in a fast store.",
                "Numbers to quote: about 1.2 million messages a second and about 5,000 gateway machines at 500 million online."],
        quick=[("Why not order messages by timestamp?", "Phone clocks differ and can be wrong. A server counter per conversation gives one agreed order."),
               ("How do you stop a retry from showing twice?", "Give each message a client id that is unique in the conversation and return the original sequence number if it repeats."),
               ("What does a mobile push alert carry?", "Only a wake up. The phone then syncs the real messages over its own connection.")]),
    deeper=[("Chat, full lesson", "S28_feeds_chat_notifications.html#l2"), ("Queues and async work", "S20_queues_streams_async.html#l1")],
)
