import os
import praw
import json
import pick
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env

#Initiate the PRAW API
reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    username=os.environ['REDDIT_USERNAME'],
    password=os.environ['REDDIT_PASSWORD'],
    user_agent=os.environ.get('REDDIT_USER_AGENT', 'videogenerator')
)


def extractpost():
    url = input("Reddit post url: ")
    submission = reddit.submission(url=url)
    num_of_comments = int(input("Number of comments: "))
    options = ['best', 'top', 'new', 'controversial']
    option, index = pick.pick(options, "Choose a comment sorting option: ")
    print(f"You chose: {option} (index {index})")

    #Ensure all comments are loaded and flattened and comments are in a list
    submission.comment_sort = option
    submission.comments.replace_more(limit=0)
    comment_list = submission.comments.list()

    post_dict = dict(title = '', body = '', comments = [])

    post_dict["title"] = submission.title
    post_dict['body'] = submission.selftext

    # Looping through all of the comments and skipping deleted or removed comments
    for comment in comment_list[:num_of_comments]:
        if comment.body.lower() not in ['[deleted]', '[removed]']:
            post_dict['comments'].append(comment.body)
    
    post_json = json.dumps(post_dict, indent=2, ensure_ascii=False)
    with open("assets/post_data.json", "w") as f:
        f.write(post_json)

    print(post_dict)
    print(post_json)

if __name__ == "__main__":
    extractpost()






