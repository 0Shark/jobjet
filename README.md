# Career Services Chatbot - "JobJet"

Dema, Elmer, 22211551 <br>
Zaganjori, Juled, 22206337

Repository: https://mygit.th-deg.de/jz19337/speech-assistant

## Project description

JobJet is a career service chatbot that helps job seekers find the right job. It is built using Rasa and Python.

JobJet offers a login and registration option for users. After logging in, the user can choose between three different personas: a student, a recruiter, and a job poster. Each persona has different options and functionalities, which are described in the wiki.

Actions that the chatbot can perform include:
- View job offers
- Apply for jobs
- Post new jobs, scraped from LinkedIn
- Invite candidates
- View job candidates

You can learn everything about the chatbot at https://mygit.th-deg.de/jz19337/speech-assistant/-/wikis/Home. 

## Installation

### Requirements

- Python 3.10.13
- Rasa 3.6.12
- Rasa SDK 3.6.2

### Installation steps

1. Clone the repository
```
git clone https://mygit.th-deg.de/jz19337/speech-assistant.git
```
2. Create a virtual environment
```bash
python3 -m venv venv
```
3. Activate the virtual environment
```bash
.\venv\Scripts\activate
```
4. Install the requirements
```bash
pip install -r requirements.txt
```

## Basic Usage

First, you need to train the model
```bash
rasa train
```

After that, you need to start the action server
```bash
rasa run actions
```

In a new terminal, you need to start the API server.
Go to the directory `server` and run
```bash
cd server
python app.py
```

Then, you can run the chatbot on another terminal
```bash
rasa shell
```

## Implementation of the Requests

Requests are

- Check for right fit [DONE]
- 1 system persona and 3 user persona [DONE]
- At least 5 use cases [DONE]
- Find the technical prerequisites [DONE]
- For every persona at least 2 example dialogs [DONE]
- A dialog flow [DONE]
- Implementation in rasa (yaml and Python files) [DONE]

## Work done

### Juled Zaganjori

- [x] Create a repository on MyGit
- [x] Develop project structure and dialog flow
- [x] Implement login and registration system in Rasa
- [x] Implement view job offers and apply for jobs in Rasa
- [x] Implement invite candidates and view job candidates
- [x] Create job scraper for LinkedIn

### Elmer Dema

- [x] Maintain Wiki page
- [x] Develop project structure and dialog flow
- [x] Create a login and registration endpoints in flask API
- [x] Create view job offers and apply for jobs endpoints in flask API
- [x] Create invite candidates endpoint in flask API
- [x] Create view job candidates endpoint in flask API

## References

- [Rasa Documentation](https://rasa.com/docs/rasa/)
- [Google Conversation Design](https://developers.google.com/assistant/conversation-design/)
- [Rasa Chatbot Tutorial](https://www.youtube.com/playlist?list=PL75e0qA87dlEjGAc9j9v3a5h1mxI2Z9fi)