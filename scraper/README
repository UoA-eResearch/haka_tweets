**TIP: You should really use [Treeverse](https://treeverse.app/) instead as it's easy to use, compatible with the new Twitter frontend/API v2, and visualises the data in a tree view. The data is also available in that tool as JSON.**

----

## Scraper for Twitter replies
Scrapes replies to a particular Tweet, including nested replies to deleted replies. The scraped results are saved to a JSON file and the log for scraping is saved as well - useful for potential data audit or debugging. 

You can see a sample of the scraped result and log file in the `samples/` folder. They are Tweet IDs that can be "hydrated" with [Twarc](https://github.com/DocNow/twarc) so you can get the full text, favourite and retweet counts etc.

This tool depends on the old frontend of Twitter (the one that shows a Tweet as an overlay on top of the Tweet writer's profile). Twitter introduced a new frontend built with React back in 2018. The old frontend seems to be being phased out, As Twitter only shows it when you are signed out, and randomises which frontend to show even then. As a temporary workaround, this tool sends a client ID that ensures the old frontend is consistently presented. The ID expires after a while, however.

### Instructions
If you want to use this tool, follow these instructions.

1. Clone this repository and `cd` into this directory.
2. Install the Python dependencies
```pip install -r requirements.txt```
3. You will also need to install the Firefox WebDriver driver. In Ubuntu for example, you can install:
```sudo apt install firefox-geckodriver```
4. Extract the client ID for a session when Twitter presents the old UI. To do this, you will need to open a Tweet in your browser's Private Window/Private Browsing mode while you are signed out from Twitter in there. If the Tweet is presented in the new React frontend, you will need to close the window (ensure it's closed fully to clear cookies) and retry until it is presented in the old UI. You can tell it's the old UI if the Tweet and its replies are overlaid on top of the Tweeter's profile page. The profile page should be darkened. Once you find it in the old UI, use the Developer Tools in your browser to extract the value for the browser cookie "guest_id". It should start with "v1%".
5. Edit the scraper.py file and add the value you extracted in step 4 to the `OLD_UI_CLIENT_ID` variable in top of the file.
6. Also, adjust the `LOG_FILE`, `TWEET_TO_EXTRACT` and `OUTPUT_FILE` variables to what is required.
7. Run the scraper - `python scraper.py`
