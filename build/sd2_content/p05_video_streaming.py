"""Problem 5: Design video streaming."""
import sd2kit as k
from sd2 import scen, figure_of

STRIP = k.strip([
    {"title": "One big file", "kind": "warn",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 6, None, "warn") + k.badge(cx, cy + 38, "movie.mp4 3.9 GB", "warn"),
     "caption": "The first idea: send the whole file. The viewer waits for gigabytes before pressing play."},
    {"title": "A slow train", "kind": "bad",
     "scene": lambda cx, cy, w: k.phone(cx, cy - 6, None, "bad") + k.alert(cx, cy + 40, None, "bad"),
     "caption": "In a tunnel the speed drops from 5 Mbps to 0.3. A fixed 1080p stream freezes again and again."},
    {"title": "Small pieces", "kind": "ok",
     "scene": lambda cx, cy, w: k.phone(cx - 40, cy - 6, None, "ok") + k.badge(cx + 36, cy - 22, "4 s piece", "ok") + k.badge(cx + 36, cy + 6, "4 s piece", "ok") + k.badge(cx + 36, cy + 34, "4 s piece", "ok"),
     "caption": "Cut the film into 4 second pieces, in several qualities. The player picks one piece at a time."},
], "From one big file to small pieces", None)


def _small(parts, title, w=640, h=112):
    return k.figure(w, h, parts, title, None)


DESIGN = k.figure(720, 250, [
    k.person(50, 54, 1), k.flow(78, 54, 140, 54, "acc", "upload"),
    k.cloud(180, 52, "raw store", "acc"), k.flow(214, 54, 276, 54, "acc", "event"),
    k.queue(330, 54, "job queue", "acc"), k.flow(376, 54, 438, 54, "acc"),
    k.server(476, 54, "transcoders", "acc"), k.flow(506, 54, 568, 54, "acc", "segments"),
    k.cloud(610, 52, "segment store", "acc"),
    k.database(610, 170, "metadata", "acc"), k.flow(476, 86, 570, 160, "acc", "status", dash=True),
    k.cloud(330, 176, "CDN edges", "ok"), k.flow(570, 176, 380, 176, "ok", "fill on demand"),
    k.phone(120, 168, "player", "ok"), k.flow(290, 176, 150, 170, "ok", "segments"),
    k.note(360, 240, "Write path on the top row (slow, asynchronous). Read path on the bottom row (fast, from the edge).", ""),
], "Video streaming design", None)

DATA = dict(
    time="30 minutes",
    seen_at="A staple at media and large consumer companies",
    tagline="Looks like a file download problem. It is really a delivery cost problem with a processing pipeline in front.",
    story=dict(
        title="The film that froze on the train",
        paras=[
            "ShopKart launches a small video section: product demos, around 3 minutes each. The first version stores one MP4 per video and serves it from the web server. In the office it works. Then a customer opens a demo on a commuter train and sends a screenshot of a spinner that has been turning for a minute.",
            "The team learns two things at once. Phones have wildly different speeds, and a single file cannot adapt to any of them. And the bandwidth bill for the demos is already bigger than the bill for everything else. The question becomes: how would you do this for the whole internet, the way YouTube or Netflix do?",
        ],
        strip=STRIP),
    requirements=["Functional: upload a video; process it so it plays on any device; stream it with fast start and no freezing; seek anywhere. Non-functional: playback starts in a second or two, quality adapts to the connection, uploads never get lost, and delivery cost stays under control. Assume video on demand, not live."],
    numbers=[
        ("Upload volume", "500 hours of video arrive every minute (the scenario's assumption). That is 30,000 hours per hour, or **720,000 hours of source video per day**."),
        ("Storage per title", "The recorded ladder below stores one 2 hour film in four qualities: 0.21 + 0.68 + 1.57 + 3.87 = **6.3 GB**, about 3.15 GB per hour. At 720,000 hours a day that is roughly **2.3 PB of new renditions per day** before replication. This is our estimate, not a published figure."),
        ("Delivery volume", "Assume a billion hours watched per day at an average of 3 Mbps. 3 Mbps is 0.375 MB per second, so one hour is 1.35 GB. Times a billion: about **1.4 exabytes per day**. Delivery dwarfs storage."),
        ("What it means", "Storage is cheap compared with delivery, so we happily store many copies of each title. The design goal is to serve almost every viewer from a cache close to them, and to keep the origin nearly idle."),
        ("Segments", "A 2 hour film in 4 second segments is **1,800 segments per rendition**. Small enough to cache and retry, large enough to avoid a flood of tiny requests."),
    ],
    numbers_try=[("ex", 0, 0, 0, "A manifest and the storage cost of a bitrate ladder")],
    design_figure=DESIGN,
    design=[
        ("Upload straight to storage, in resumable parts", "The API checks the user and quota, then hands back a presigned URL (a temporary address that lets the client write to the store directly). The client uploads in parts, and if the connection drops it resumes where it stopped. The video bytes never pass through your app servers.",
         _small([k.person(60, 48, 1), k.flow(88, 48, 170, 48, "acc", "ask URL"), k.server(206, 48, "API"), k.flow(236, 48, 320, 48, "acc", "presigned"), k.phone(350, 48, None, "acc"), k.flow(378, 48, 480, 48, "acc", "parts"), k.cloud(520, 46, "raw store", "acc")], "Resumable upload")),
        ("Transcode in parallel into a ladder", "Transcoding means re-encoding the video into other sizes and bitrates. A workflow splits the source into chunks, a pool of workers encodes chunks in parallel into a ladder of 240p, 480p, 720p and 1080p, and the results are cut into segments. If a worker dies, only its chunk runs again.",
         _small([k.cloud(60, 46, "source", "acc"), k.flow(94, 48, 160, 48, "acc", "split"), k.queue(214, 48, "chunk jobs", "acc"), k.flow(260, 48, 330, 48, "acc"), k.server(366, 48, "workers", "acc"), k.flow(396, 48, 470, 48, "acc", "encode"), k.badge(530, 22, "240p  480p", "ok"), k.badge(530, 50, "720p  1080p", "ok"), k.note(530, 84, "four renditions", "")], "Parallel transcoding")),
        ("A manifest tells the player what exists", "A manifest is a small text file that lists every quality and every segment address. The player downloads it first, then asks for segments one by one. The first segment is chosen small and low quality so the picture starts fast.",
         _small([k.phone(60, 48, "player", "ok"), k.flow(88, 48, 180, 48, "ok", "1 manifest"), k.badge(240, 30, "480p index", "acc"), k.badge(240, 58, "1080p index", "acc"), k.flow(300, 48, 390, 48, "ok", "2 segments"), k.badge(450, 22, "seg0000.ts", "ok"), k.badge(450, 48, "seg0001.ts", "ok"), k.badge(450, 74, "seg0002.ts", "ok")], "Manifest and segments", h=116)),
        ("Serve from a CDN, not from your origin", "A CDN (content delivery network) is a fleet of caches near viewers. The first viewer of a segment causes one fetch from the origin; the next thousand are answered by the edge. Popular new releases can be copied to the edges before anyone asks.",
         _small([k.crowd(70, 44, 3, 26, .7), k.flow(120, 48, 210, 48, "ok", "segment"), k.cache(250, 48, "edge", "ok"), k.flow(276, 48, 380, 48, "warn", "miss only", dash=True), k.cloud(420, 46, "origin store", "acc"), k.note(560, 52, "hit ratio is the cost lever", "")], "CDN delivery")),
    ],
    hard_title="The hard part: adaptive playback and the cost of delivery",
    hard_paras=[
        "The player measures how fast the last segment arrived and chooses the quality of the next one. This is adaptive bitrate streaming (ABR). Fast network: climb the ladder. Tunnel: step down before the buffer empties. Because each segment is a separate small request, switching costs nothing.",
        "The second hard part is money. Because delivery is about 1.4 exabytes a day in our estimate, the CDN hit ratio is the biggest cost lever. Short segments adapt faster but create more requests; longer ones are cheaper to serve but react slowly. Say which you picked and why. Newer codecs save bandwidth but not every device can play them, so you often encode more than one.",
    ],
    **{"try": [("ex", 0, 0, 1, "Always high quality, always low quality, or adaptive: who stalls?")]},
    scale=[
        ("Processing falls behind", "A burst of uploads fills the queue. Playback of existing videos is unaffected; only new videos wait. Add workers, prioritise short and popular uploads, and show a clear processing status.", ""),
        ("A new release is hot", "Millions ask for the same first segments in the same minute. Pre-warm the edges, and use an origin shield (one mid-tier cache that collapses many edge misses into one origin request).", ""),
        ("A CDN region fails", "Players retry another edge or another CDN named in the manifest. Keep the manifest short-lived so you can steer traffic.", "ok"),
        ("Lost uploads", "Resumable multipart upload plus a completion call that verifies size and hash. Never mark a video ready until every rendition exists.", ""),
        ("Piracy and abuse", "Use DRM (encrypted segments with licensed keys) for protected content, signed URLs that expire, and safety scanning in the pipeline before publishing.", "bad"),
    ],
    scenario=scen("ex", 0),
    who="A staple media question: reported by candidates, not official.",
    real=[
        dict(company="Netflix", text="Netflix describes **Open Connect**, its own content delivery network, with caching servers placed inside internet service provider networks so that video travels a short distance to the viewer.", url="https://openconnect.netflix.com/", source="Netflix Open Connect"),
        dict(company="Netflix", text="The Netflix Tech Blog has written about **per-title encoding**: choosing the bitrate ladder for each title based on how complex it is, instead of using one fixed ladder for everything.", url="https://netflixtechblog.com/per-title-encode-optimization-7e99442b62a2", source="Netflix Tech Blog: Per-Title Encode Optimization"),
    ],
    recap=dict(
        points=["Delivery is the cost: about 1.4 exabytes a day in our estimate. Design for the CDN.",
                "Upload straight to object storage with presigned URLs and resumable parts.",
                "A queue and parallel workers turn one source into a ladder of renditions and segments.",
                "A manifest lists the qualities and segments; the player adapts one segment at a time.",
                "Adaptive playback stalls far less than fixed 1080p in the recorded run (2 stalls against 43).",
                "Processing can lag without hurting playback; say how you pre-warm a hot release."],
        quick=[("Why cut video into 4 second segments?", "Each is a small cacheable request, the player can change quality between segments, and a failed piece is cheap to retry."),
               ("Why not stream through your own app servers?", "Delivery is the dominant cost; a CDN serves most requests from the edge and keeps the origin nearly idle."),
               ("What does the manifest contain?", "The list of renditions with their bitrates, and the addresses of each segment.")]),
    deeper=[("Video streaming, full lesson", "S29_media_files_streaming.html#l1"), ("Object storage and blobs", "S21_search_blob_special_stores.html#l2"), ("Caching and CDNs", "S17_caching_and_cdns.html#l1")],
)
