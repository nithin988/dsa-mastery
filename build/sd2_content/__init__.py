"""Course map and content loader for the System Design course (v2)."""
import importlib
import os

CHAPTERS = [
    ("01-numbers", "Think in numbers", "How big will this get? Answer before drawing a single box.", "ch01_numbers"),
    ("02-load-balancing", "One server is not enough", "Launch day: the only server falls over, and every customer sees an error.", "ch02_load_balancing"),
    ("03-caching", "Make it fast", "Black Friday: the database melts because it answers the same question thousands of times.", "ch03_caching"),
    ("04-databases", "Where the data lives", "A slow query, a lost order, and two buyers for the last item.", "ch04_databases"),
    ("05-scaling-data", "When one database is not enough", "Writes and data outgrow one machine; the copies disagree.", "ch05_scaling_data"),
    ("06-queues", "Do not make people wait", "Signup sends email and resizes photos, and takes four seconds.", "ch06_queues"),
    ("07-failure", "When things fail", "A timeout that charges the card twice.", "ch07_failure"),
    ("08-reliability", "Keep it up", "A bad release at 3 p.m. and a dead server at 3 a.m.", "ch08_reliability"),
    ("09-security", "Keep it safe", "A guessable id shows one customer another customer's invoice.", "ch09_security"),
]

PROBLEMS = [
    ("url-shortener", "Design a URL shortener", "Turn a long link into a short one and redirect a million clicks.", "p01_url_shortener"),
    ("rate-limiter", "Design a rate limiter", "Stop one client from using everyone's capacity.", "p02_rate_limiter"),
    ("news-feed", "Design a news feed", "Show each person the latest posts from the people they follow.", "p03_news_feed"),
    ("chat", "Design a chat system", "Deliver messages in order, even when phones go offline.", "p04_chat"),
    ("video-streaming", "Design video streaming", "Play a video smoothly on any connection, anywhere.", "p05_video_streaming"),
    ("file-storage", "Design file storage and sync", "Store billions of files and keep every device in step.", "p06_file_storage"),
    ("ride-hailing", "Design ride hailing and nearby search", "Find the closest driver among millions that keep moving.", "p07_ride_hailing"),
    ("search-autocomplete", "Design search and autocomplete", "Find the right result as the user types.", "p08_search_autocomplete"),
    ("notifications", "Design a notification system", "Reach people on the right channel without annoying them.", "p09_notifications"),
    ("booking-payments", "Design booking and payments", "Never sell the same seat twice, never charge twice.", "p10_booking_payments"),
]

def _exists(m):
    return bool(m) and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), m + ".py"))


COURSE = {
    "chapters": [dict(slug=s, num=i + 1, title=t, pain=p, live=_exists(m), mod=m) for i, (s, t, p, m) in enumerate(CHAPTERS)],
    "problems": [dict(slug=s, num=i + 1, title=t, pain=p, live=_exists(m), mod=m) for i, (s, t, p, m) in enumerate(PROBLEMS)],
}


def load(slug):
    for row in COURSE["chapters"] + COURSE["problems"]:
        if row["slug"] == slug:
            return importlib.import_module("sd2_content." + row["mod"]).DATA
    raise KeyError(slug)
