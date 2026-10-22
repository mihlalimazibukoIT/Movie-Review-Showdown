"""Movie Review Sentiment Dashboard (fun edition)
Run with:  streamlit run app.py
Install:   pip install streamlit pandas vaderSentiment
"""
import os
import re
from collections import Counter
from pathlib import Path

import requests

import pandas as pd
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Movie Review Showdown", page_icon="🎬", layout="wide")

st.markdown(
    """
<style>
.hero {background: linear-gradient(90deg,#ff512f,#dd2476,#6a11cb); padding: 28px 32px;
       border-radius: 18px; color: white; margin-bottom: 18px;}
.hero h1 {margin: 0; font-size: 2.2rem;}
.hero p {margin: 6px 0 0 0; opacity: .92;}
.card {border-radius: 16px; padding: 16px 18px; color: #1a1a1a; height: 100%;}
.card h3 {margin: 0 0 4px 0; font-size: 1rem;}
.card .big {font-size: 1.6rem; font-weight: 700;}
.love {background: #d9f7e4; border: 2px solid #34c76b;}
.roast {background: #ffe1df; border: 2px solid #ff5a4f;}
.fun {background: #fff4cc; border: 2px solid #ffc833;}
.quote {border-left: 5px solid; padding: 8px 12px; margin: 8px 0; border-radius: 6px; font-size: .95rem;}
.q-love {border-color: #34c76b; background: #f2fcf6;}
.q-roast {border-color: #ff5a4f; background: #fff6f5;}
</style>
<div class="hero"><h1>🎬 Movie Review Showdown</h1>
<p>Who's swooning, who's ranting, and what exactly are they fighting about?</p></div>
""",
    unsafe_allow_html=True,
)

STOPWORDS = set(
    "the a an and or but if of to in on at for with as is it its this that was were be been "
    "are i you he she they we my your his her their our not no so very just from by about "
    "have has had do does did will would can could there what which who when than then them "
    "movie film films movies one br really also more get got even much into out all only some "
    "any these those how why too over after before while her him she's it's don't isn't".split()
)

ASPECTS = {
    "🎭 Acting": ["acting", "actor", "actress", "performance", "performances", "cast"],
    "📖 Story & plot": ["plot", "story", "script", "storyline", "writing"],
    "🎬 Directing": ["director", "directing", "direction"],
    "🎵 Music": ["music", "soundtrack", "score", "song", "songs"],
    "👀 Visuals": ["visual", "visuals", "cinematography", "effects", "scenery", "photography"],
    "🏁 Ending": ["ending", "finale", "conclusion"],
    "⏱️ Pacing": ["pacing", "slow", "boring", "dragged", "predictable"],
    "😂 Humor": ["funny", "humor", "comedy", "hilarious", "laugh", "laughs"],
    "🧑‍🤝‍🧑 Characters": ["character", "characters"],
    "💬 Dialogue": ["dialogue", "dialog", "lines"],
}


@st.cache_data
def load(file):
    return pd.read_csv(file)


@st.cache_data
def score(texts):
    analyzer = SentimentIntensityAnalyzer()
    return [analyzer.polarity_scores(t)["compound"] for t in texts]


def label(c):
    return "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral"


def clean(t):
    return re.sub(r"<[^>]+>", " ", t)  # IMDb reviews contain <br /> tags


def top_words(texts, n=12):
    words = Counter()
    for t in texts:
        words.update(w for w in re.findall(r"[a-z']{3,}", t.lower()) if w not in STOPWORDS)
    return pd.DataFrame(words.most_common(n), columns=["word", "count"]).set_index("word")


def card(css, title, big, small=""):
    return f'<div class="card {css}"><h3>{title}</h3><div class="big">{big}</div>{small}</div>'


# ---------- Review any movie (search by title) ----------
TMDB = "https://api.themoviedb.org/3"


@st.cache_resource
def get_analyzer():
    return SentimentIntensityAnalyzer()


def get_token():
    """TMDB key: Streamlit secret first, then environment, then the sidebar box."""
    try:
        t = st.secrets.get("TMDB_TOKEN", "")
    except Exception:
        t = ""
    return t or os.environ.get("TMDB_TOKEN", "") or st.session_state.get("tmdb_token_box", "")


def _headers(token):
    return {"Authorization": f"Bearer {token}", "accept": "application/json"}


@st.cache_data(ttl=3600, show_spinner=False)
def tmdb_search(query, token):
    r = requests.get(f"{TMDB}/search/movie", params={"query": query, "include_adult": "false"},
                     headers=_headers(token), timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])[:6]


@st.cache_data(ttl=3600, show_spinner=False)
def tmdb_reviews(movie_id, token, max_pages=3):
    out = []
    for page in range(1, max_pages + 1):
        r = requests.get(f"{TMDB}/movie/{movie_id}/reviews", params={"page": page},
                         headers=_headers(token), timeout=10)
        r.raise_for_status()
        data = r.json()
        out += [x["content"] for x in data.get("results", []) if x.get("content")]
        if page >= data.get("total_pages", 1):
            break
    return out


def show_movie_report(title, reviews, poster_url=None, subtitle=""):
    az = get_analyzer()
    rv = pd.DataFrame({"review": [clean(r).strip() for r in reviews]})
    rv["score"] = [az.polarity_scores(t)["compound"] for t in rv["review"]]
    rv["label"] = rv["score"].apply(label)
    n = len(rv)
    counts = rv["label"].value_counts().reindex(["Positive", "Neutral", "Negative"]).fillna(0).astype(int)
    pos_share, neg_share = counts["Positive"] / n, counts["Negative"] / n

    if pos_share >= 0.6:
        verdict, vcss = "😍 Mostly loved", "love"
    elif neg_share >= 0.5:
        verdict, vcss = "😡 Mostly roasted", "roast"
    else:
        verdict, vcss = "🤔 Opinions are split", "fun"

    head_l, head_r = st.columns([1, 4]) if poster_url else (None, st)
    if poster_url:
        head_l.image(poster_url, width=130)
    head_r.markdown(card(vcss, f"{title} {subtitle}", verdict,
                         f"<br>based on {n} review{'s' if n != 1 else ''} · average mood {rv['score'].mean():+.2f}"),
                    unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.markdown(card("love", "😍 Positive", f"{pos_share:.0%}", f"<br>{counts['Positive']} reviews"), unsafe_allow_html=True)
    b.markdown(card("fun", "😐 Neutral", f"{counts['Neutral'] / n:.0%}", f"<br>{counts['Neutral']} reviews"), unsafe_allow_html=True)
    c.markdown(card("roast", "😡 Negative", f"{neg_share:.0%}", f"<br>{counts['Negative']} reviews"), unsafe_allow_html=True)

    st.bar_chart(counts, color="#6a11cb")

    best, worst = st.columns(2)
    with best:
        st.caption("Most glowing")
        for _, r in rv.nlargest(2, "score").iterrows():
            st.markdown(f'<div class="quote q-love">“{r["review"][:300]}…”<br><b>score {r["score"]:+.2f}</b></div>', unsafe_allow_html=True)
    with worst:
        st.caption("Harshest")
        for _, r in rv.nsmallest(2, "score").iterrows():
            st.markdown(f'<div class="quote q-roast">“{r["review"][:300]}…”<br><b>score {r["score"]:+.2f}</b></div>', unsafe_allow_html=True)
    if n < 10:
        st.caption("Only a handful of reviews are available for this film, so treat the result as a rough guide.")


st.sidebar.text_input("TMDB key (site owner only)", type="password", key="tmdb_token_box",
                      help="Visitors don't need this. The site owner can store it as a Streamlit secret named TMDB_TOKEN.")

st.subheader("🎥 Review any movie")
st.caption("Type a movie title and the AI reads what audiences have written about it.")
tab_search, tab_paste = st.tabs(["🔎 Search a movie", "📋 Paste reviews"])

with tab_search:
    query = st.text_input("Movie title", placeholder="e.g. Inception, Black Panther, The Lion King")
    if query.strip():
        token = get_token()
        if not token:
            st.warning("Movie search is being set up and isn't switched on yet. "
                       "You can still paste reviews in the next tab.")
        else:
            try:
                results = tmdb_search(query.strip(), token)
            except Exception:
                results = None
                st.error("Couldn't reach the movie database just now. Please try again in a moment.")
            if results is not None:
                if not results:
                    st.info("No movies found with that title. Check the spelling or try another one.")
                else:
                    names = [f"{m.get('title', 'Untitled')} ({(m.get('release_date') or '')[:4] or 'year unknown'})" for m in results]
                    idx = st.selectbox("Which one do you mean?", list(range(len(results))), format_func=lambda i: names[i])
                    m = results[idx]
                    try:
                        revs = tmdb_reviews(m["id"], token)
                    except Exception:
                        revs = None
                        st.error("Couldn't load reviews for that movie. Please try again in a moment.")
                    if revs is not None:
                        if not revs:
                            st.info("This movie has no audience reviews yet. Try another film, or paste reviews in the next tab.")
                        else:
                            poster = f"https://image.tmdb.org/t/p/w185{m['poster_path']}" if m.get("poster_path") else None
                            year = (m.get("release_date") or "")[:4]
                            show_movie_report(m.get("title", "Untitled"), revs, poster, f"({year})" if year else "")
        st.caption("Movie data and reviews provided by TMDB. This app is not endorsed or certified by TMDB.")

with tab_paste:
    p_title = st.text_input("Movie name (optional)", key="paste_title", placeholder="Whatever film you're reviewing")
    pasted = st.text_area("Paste one review per line", height=150, key="paste_reviews",
                          placeholder="Paste reviews here, one per line or separated by a blank line")
    lines = [x.strip() for x in re.split(r"\n\s*\n|\n", pasted) if len(x.strip()) > 3]
    if lines:
        show_movie_report(p_title.strip() or "Your movie", lines)
    else:
        st.caption("Paste a few reviews from anywhere (IMDb, Rotten Tomatoes, Google) and I'll sum up the mood.")

st.divider()

# ---------- Try it yourself (works for everyone, no files needed) ----------
st.subheader("✍️ Check a single review")
st.caption("Type or paste any movie review (or any sentence) and see how the AI reads it.")
user_text = st.text_area(
    "Your review",
    value="I expected to hate it, but the acting was brilliant and the ending moved me.",
    height=90,
    label_visibility="collapsed",
)
if user_text.strip():
    az = get_analyzer()
    c = az.polarity_scores(user_text)["compound"]
    lab = label(c)
    css, emoji = {"Positive": ("love", "😍"), "Negative": ("roast", "😡"), "Neutral": ("fun", "😐")}[lab]
    t1, t2 = st.columns([1, 2])
    t1.markdown(card(css, f"{emoji} The AI says", lab, f"<br>score {c:+.2f} (from -1 to +1)"), unsafe_allow_html=True)
    with t2:
        st.progress((c + 1) / 2)
        seen, hits = set(), []
        for w in re.findall(r"[A-Za-z']+", user_text):
            k = w.lower()
            if k in az.lexicon and k not in seen:
                seen.add(k)
                hits.append((k, az.lexicon[k]))
        hits.sort(key=lambda x: -abs(x[1]))
        if hits:
            st.write("**Words that moved the score:** " + ", ".join(f"{w} ({v:+.1f})" for w, v in hits[:8]))
        else:
            st.write("No strongly emotional words found, so it reads as neutral.")
st.divider()

# ---------- Load data ----------
SAMPLE = Path(__file__).with_name("sample_reviews.csv")

DEMO_ROWS = [
    ("The acting was brilliant and the story kept me hooked from the first minute.", "positive"),
    ("A beautiful film with a moving soundtrack. I cried at the ending.", "positive"),
    ("Hilarious from start to finish. The whole cast is wonderful and the humor lands every time.", "positive"),
    ("Stunning visuals and a clever plot. One of the best films I have seen this year.", "positive"),
    ("Great characters, sharp dialogue and a satisfying ending. Loved it!", "positive"),
    ("The director did a fantastic job. Every scene felt intentional and the pacing was perfect.", "positive"),
    ("Warm, funny and surprisingly emotional. The performances are excellent.", "positive"),
    ("I was gripped the whole time. The story twists were smart and the music was amazing.", "positive"),
    ("A delightful movie the whole family enjoyed. Wonderful acting by the young cast.", "positive"),
    ("Powerful, honest and beautifully shot. The ending stayed with me for days.", "positive"),
    ("Brilliant script and a great cast. I laughed, I cried, I want to watch it again.", "positive"),
    ("An inspiring story with superb acting and gorgeous scenery.", "positive"),
    ("Thrilling and well paced, with characters you actually care about.", "positive"),
    ("The soundtrack alone is worth the ticket. A genuinely great film.", "positive"),
    ("Smart, touching and perfectly cast. Highly recommended.", "positive"),
    ("The plot made no sense and the ending was a complete letdown.", "negative"),
    ("Boring and predictable. The pacing dragged and I nearly fell asleep.", "negative"),
    ("Terrible acting and awful dialogue. I wanted my money back.", "negative"),
    ("The special effects looked cheap and the characters were flat and annoying.", "negative"),
    ("A waste of a good cast. The story was a mess and the script was lazy.", "negative"),
    ("Painfully slow with a pointless ending. I would not recommend it.", "negative"),
    ("The director clearly had no idea what he wanted. Confusing and dull.", "negative"),
    ("Cringeworthy humor and wooden performances. Hard to sit through.", "negative"),
    ("Loud, messy and forgettable. The music was irritating and the plot was thin.", "negative"),
    ("I hated the ending. After two hours of nothing happening, it just stopped.", "negative"),
    ("Poorly written and badly acted. One of the worst films I have watched.", "negative"),
    ("The characters made stupid decisions and the story fell apart halfway through.", "negative"),
    ("Disappointing. Great trailer, but the movie itself was boring and bland.", "negative"),
    ("Overlong, overhyped and just not funny. The dialogue was painful.", "negative"),
    ("An awful movie with a terrible script. I regret watching it.", "negative"),
]

uploaded = st.sidebar.file_uploader("📂 Upload your own CSV (optional)", type="csv")

if uploaded:
    df = load(uploaded)
    source = "your uploaded file"
elif SAMPLE.exists():
    df = load(str(SAMPLE))
    source = "the built-in sample of IMDb reviews"
else:
    df = pd.DataFrame(DEMO_ROWS, columns=["review", "sentiment"])
    source = "a tiny demo set of 30 reviews"

st.info(f"Showing results for {source}. Upload the full IMDb 50K CSV in the sidebar to analyse more reviews.")

default_idx = list(df.columns).index("review") if "review" in df.columns else 0
text_col = st.sidebar.selectbox("Review text column", df.columns, index=default_idx)
if len(df) >= 1000:
    sample_size = st.sidebar.slider("Reviews to analyse", 500, min(10000, len(df)), min(2000, len(df)), step=500)
else:
    sample_size = len(df)
df = df.dropna(subset=[text_col]).drop_duplicates(subset=[text_col])
df = df.sample(min(sample_size, len(df)), random_state=42).reset_index(drop=True)
df[text_col] = df[text_col].astype(str).apply(clean)

df["compound"] = score(tuple(df[text_col]))
df["predicted"] = df["compound"].apply(label)
df["words"] = df[text_col].str.split().str.len()
df["exclaims"] = df[text_col].str.count("!")
df["shouting"] = df[text_col].str.contains(r"\b[A-Z]{4,}\b", regex=True)

pos = df[df["predicted"] == "Positive"]
neg = df[df["predicted"] == "Negative"]
neu = df[df["predicted"] == "Neutral"]

tab1, tab2, tab3, tab4 = st.tabs(
    ["🎭 The Showdown", "😍 Love Letters", "😡 Roast Corner", "🎯 Is the AI right?"]
)

# ---------- Tab 1: overview ----------
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.markdown(card("love", "😍 Fans", f"{len(pos)/len(df):.0%}", f"<br>{len(pos):,} positive reviews"), unsafe_allow_html=True)
    c2.markdown(card("roast", "😡 Critics", f"{len(neg)/len(df):.0%}", f"<br>{len(neg):,} negative reviews"), unsafe_allow_html=True)
    c3.markdown(card("fun", "😐 On the fence", f"{len(neu)/len(df):.0%}", f"<br>{len(neu):,} neutral reviews"), unsafe_allow_html=True)

    st.write("")
    st.subheader("🔥 Fun facts: fans vs critics")
    f1, f2, f3, f4 = st.columns(4)
    f1.markdown(card("fun", "📝 Longer rants",
                     "Critics" if neg["words"].mean() > pos["words"].mean() else "Fans",
                     f"<br>{neg['words'].mean():.0f} vs {pos['words'].mean():.0f} words (critics vs fans)"), unsafe_allow_html=True)
    f2.markdown(card("fun", "❗ Exclamation marks",
                     "Critics" if neg["exclaims"].mean() > pos["exclaims"].mean() else "Fans",
                     f"<br>{neg['exclaims'].mean():.2f} vs {pos['exclaims'].mean():.2f} per review"), unsafe_allow_html=True)
    f3.markdown(card("fun", "📢 ALL-CAPS shouting",
                     "Critics" if neg["shouting"].mean() > pos["shouting"].mean() else "Fans",
                     f"<br>{neg['shouting'].mean():.0%} vs {pos['shouting'].mean():.0%} of reviews"), unsafe_allow_html=True)
    f4.markdown(card("fun", "🌡️ Overall mood", f"{df['compound'].mean():+.2f}", "<br>scale: -1 grumpy to +1 delighted"), unsafe_allow_html=True)

    st.write("")
    st.subheader("🎞️ What are they actually talking about?")
    lower = df[text_col].str.lower()
    rows = []
    for name, kws in ASPECTS.items():
        mask = lower.str.contains(r"\b(?:" + "|".join(kws) + r")\b", regex=True)
        if mask.sum() == 0:
            continue
        rows.append({
            "aspect": name,
            "In fan reviews (%)": round(mask[df["predicted"] == "Positive"].mean() * 100, 1) if len(pos) else 0,
            "In critic reviews (%)": round(mask[df["predicted"] == "Negative"].mean() * 100, 1) if len(neg) else 0,
            "mood": df.loc[mask, "compound"].mean(),
            "mentions": int(mask.sum()),
        })
    asp = pd.DataFrame(rows).set_index("aspect")
    st.bar_chart(asp[["In fan reviews (%)", "In critic reviews (%)"]], color=["#34c76b", "#ff5a4f"])

    best, worst = asp["mood"].idxmax(), asp["mood"].idxmin()
    a1, a2 = st.columns(2)
    a1.markdown(card("love", "🏆 Most loved topic", best, f"<br>avg mood {asp.loc[best,'mood']:+.2f} across {asp.loc[best,'mentions']} reviews"), unsafe_allow_html=True)
    a2.markdown(card("roast", "💣 Most roasted topic", worst, f"<br>avg mood {asp.loc[worst,'mood']:+.2f} across {asp.loc[worst,'mentions']} reviews"), unsafe_allow_html=True)

    st.subheader("📈 Mood spread")
    spread = pd.cut(df["compound"], bins=20).value_counts().sort_index()
    spread.index = [str(round(i.mid, 2)) for i in spread.index]
    st.bar_chart(spread, color="#6a11cb")

# ---------- Tab 2 / 3: love & roast ----------
def side(tab, data, emoji, css, qcss, title, ascending):
    with tab:
        st.subheader(f"{emoji} {title}")
        st.caption(f"Most common words ({len(data):,} reviews)")
        st.bar_chart(top_words(data[text_col]), color="#34c76b" if css == "love" else "#ff5a4f")
        st.caption("The most extreme ones")
        picks = data.nsmallest(5, "compound") if ascending else data.nlargest(5, "compound")
        for _, r in picks.iterrows():
            st.markdown(f'<div class="quote {qcss}">“{r[text_col][:350]}…”<br><b>score {r["compound"]:+.2f}</b></div>', unsafe_allow_html=True)

side(tab2, pos, "😍", "love", "q-love", "Love Letters: what the fans are gushing about", False)
side(tab3, neg, "😡", "roast", "q-roast", "Roast Corner: what the critics can't stand", True)

# ---------- Tab 4: accuracy ----------
with tab4:
    st.subheader("🎯 How well does the AI judge match the humans?")
    if "sentiment" in df.columns:
        truth = df["sentiment"].str.capitalize()
        mask = df["predicted"] != "Neutral"
        acc = (truth[mask] == df["predicted"][mask]).mean()
        st.metric("Agreement with the dataset's labels", f"{acc:.1%}")
        st.write("Rows are what the reviewer chose, columns are what the AI predicted:")
        st.dataframe(pd.crosstab(truth, df["predicted"]))
        st.caption("Neutral predictions are excluded from the accuracy figure. Mixed or sarcastic reviews are where VADER slips.")
    else:
        st.write("This dataset has no 'sentiment' label column, so accuracy can't be checked.")

st.download_button("⬇️ Download results (CSV)", df.drop(columns=["shouting"]).to_csv(index=False), "sentiment_results.csv")
