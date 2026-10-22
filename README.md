
# 🎬 Movie Review Showdown
### A Sentiment Analysis and Movie Review Exploration Application

Movie Review Showdown is a Python-based web application designed to help users explore movie reviews, understand audience opinions, and make more informed viewing decisions. Built with Streamlit, the application combines sentiment analysis, review exploration, and an interactive question-and-answer interface in a user-friendly environment.

The project demonstrates how Natural Language Processing (NLP) techniques can be used to analyse textual data and extract meaningful insights from movie reviews.

## ✨ Features

- **📊 Sentiment Analysis:** Classifies movie reviews into positive, negative, and neutral categories using VADER sentiment analysis.
- **💬 Interactive Movie Q&A:** Allows users to ask questions about movie reviews through a chat-style interface.
- **🔎 Movie Search:** Integrates with The Movie Database (TMDB) API to search for movies and retrieve available audience reviews.
- **📝 Review Insights:** Highlights positive and critical reviews to help users understand different audience perspectives.
- **📈 Visual Analytics:** Displays sentiment distributions, average sentiment scores, and frequently occurring words.
- **📂 CSV Upload:** Allows users to upload their own movie-review datasets for analysis.
- **⬇️ Export Results:** Enables users to download analysed review data as a CSV file.
- **🎨 User-Friendly Interface:** Provides an interactive dashboard with clear visualisations and accessible controls.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application interface |
| Pandas | Data processing and manipulation |
| VADER Sentiment | Sentiment scoring and classification |
| Matplotlib-free Streamlit charts | Data visualisation using Streamlit's built-in chart components |
| Requests | Communication with the TMDB API |
| TMDB API | Movie search and available audience reviews |

## ⚙️ How It Works

1. **Upload data:** The user uploads a CSV file containing movie reviews.
2. **Select columns:** The user selects the column containing review text and, optionally, a movie-title column.
3. **Analyse sentiment:** The application processes the review text and calculates sentiment scores.
4. **Visualise results:** The dashboard presents sentiment distributions, average scores, and common words in positive and negative reviews.
5. **Ask questions:** Users can ask questions about the available review data using the interactive chat interface.
6. **Explore movies:** With a TMDB API Read Access Token, users can search for movies and analyse available English-language audience reviews.
7. **Export findings:** Users can download the analysed dataset for further exploration.

## 🚀 Getting Started

### Prerequisites

Before running the application, ensure that you have:

- Python 3.10 or later
- pip installed
- Git installed (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your actual GitHub username and repository name.

### 2. Navigate to the project directory

```bash
cd YOUR-REPOSITORY
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser, usually at `http://localhost:8501`.

## 🔑 Configuring TMDB

The application can use TMDB to search for movies beyond the reviews in an uploaded dataset.

1. Create an account at [The Movie Database](https://www.themoviedb.org/).
2. Visit the [TMDB API settings](https://www.themoviedb.org/settings/api).
3. Obtain your API Read Access Token.
4. Enter the token into the application's sidebar under **Movie-wide Q&A**.

The token is optional. Without it, questions are answered using the uploaded dataset. Movie review availability through TMDB varies, and some movies may not have accessible user reviews.

Keep API credentials private and never commit secrets to GitHub.

## 📁 Project Structure

```text
Movie-Review-Showdown/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Files excluded from version control (recommended)
```

## 📦 Dependencies

The application's main dependencies are:

- `streamlit`
- `pandas`
- `vaderSentiment`
- `requests`

These dependencies are listed in `requirements.txt` and can be installed together using pip.

## 🎯 Project Objectives

The main objectives of Movie Review Showdown are to:

- Apply sentiment analysis techniques to real-world textual data.
- Transform unstructured movie reviews into understandable insights.
- Develop an interactive application that improves the way users explore audience feedback.
- Demonstrate data processing, visualisation, and API integration using Python.
- Explore how sentiment analysis can support movie discovery and viewing decisions.

## ⚠️ Limitations

- Sentiment classifications are estimates and may not accurately capture sarcasm, irony, or complex opinions.
- The question-answering functionality uses rule-based logic rather than a generative AI language model.
- Movie-wide analysis depends on the availability of reviews from TMDB.
- Results from uploaded datasets represent only the reviews included in those datasets.
- Audience sentiment should not be treated as a definitive measure of a movie's quality.

## 🔮 Future Improvements

Potential future enhancements include:

- Integrating a large language model for more flexible, conversational answers.
- Improving movie-title detection and follow-up question handling.
- Adding movie comparisons and personalised recommendations.
- Supporting additional review sources and datasets.
- Implementing more advanced NLP techniques and model evaluation.
- Adding richer movie information, posters, ratings, and interactive visualisations.

## 👩‍💻 Project Purpose

Movie Review Showdown was developed as a practical Python project exploring sentiment analysis, data visualisation, and interactive application development. It demonstrates how data-driven techniques can make textual information more accessible and useful to everyday users.

---

**Built with Python, Streamlit, and NLP. 🎬**
