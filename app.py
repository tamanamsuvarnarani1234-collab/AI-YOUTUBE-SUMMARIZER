from flask import Flask, render_template, request
import re
import string
from collections import Counter

app = Flask(__name__)


# Extract YouTube video ID from different URL formats
def extract_video_id(url):
    patterns = [
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


# Fetch transcript from YouTube
def fetch_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        # Current API returns transcript snippets
        text = " ".join(
            snippet.text for snippet in transcript
        )

        return text

    except Exception as e:
        raise Exception(
            "Could not fetch transcript. "
            "The video may not have captions available."
        )


# Generate a simple summary without a paid API
def summarize_text(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 10
    ]

    if not sentences:
        return text[:500]

    stop_words = {
        "the", "is", "are", "was", "were", "a", "an",
        "and", "or", "but", "to", "of", "in", "on",
        "for", "with", "it", "this", "that", "as",
        "by", "be", "can", "will", "has", "have",
        "from", "at", "we", "you", "they", "their"
    }

    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    words = [
        word for word in words
        if word not in stop_words
    ]

    word_frequency = Counter(words)

    sentence_scores = {}

    for sentence in sentences:
        sentence_words = re.findall(
            r'\b[a-zA-Z]+\b',
            sentence.lower()
        )

        score = sum(
            word_frequency[word]
            for word in sentence_words
        )

        sentence_scores[sentence] = score

    top_sentences = sorted(
        sentence_scores,
        key=sentence_scores.get,
        reverse=True
    )[:4]

    # Preserve original sentence order
    summary_sentences = [
        sentence for sentence in sentences
        if sentence in top_sentences
    ]

    return " ".join(summary_sentences)


# Generate key takeaways
def generate_key_takeaways(summary):
    sentences = re.split(r'(?<=[.!?])\s+', summary)

    takeaways = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return takeaways[:5]


# Main webpage
@app.route("/", methods=["GET", "POST"])
def home():

    summary = ""
    key_takeaways = []
    revision = ""
    error = ""

    youtube_url = ""
    transcript = ""

    if request.method == "POST":

        youtube_url = request.form.get(
            "youtube_url", ""
        ).strip()

        transcript = request.form.get(
            "transcript", ""
        ).strip()

        try:

            # Option 1: Use pasted transcript
            if transcript:

                text_to_summarize = transcript

            # Option 2: Fetch transcript from YouTube
            elif youtube_url:

                video_id = extract_video_id(youtube_url)

                if not video_id:
                    raise Exception(
                        "Invalid YouTube URL. "
                        "Please enter a valid video link."
                    )

                text_to_summarize = fetch_transcript(
                    video_id
                )

            else:

                raise Exception(
                    "Please enter a YouTube URL "
                    "or paste a transcript."
                )

            # Generate summary
            summary = summarize_text(
                text_to_summarize
            )

            # Generate key takeaways
            key_takeaways = generate_key_takeaways(
                summary
            )

            # Generate revision notes
            revision = summary

        except Exception as e:

            error = str(e)

    return render_template(
        "index.html",
        youtube_url=youtube_url,
        transcript=transcript,
        summary=summary,
        key_takeaways=key_takeaways,
        revision=revision,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)