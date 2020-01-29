from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
import time
import logging
import random
import csv
from collections import namedtuple

# Configuration
OLD_UI_CLIENT_ID="v1%3A158033262680275022"
LOG_FILE="scrape-firefox.log"
TWEET_TO_EXTRACT="espn/status/1058853098108739584"
OUTPUT_FILE="espn-tweets-firefox2.csv"

logger = logging.getLogger("tweetrepliesscraper")
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    filename=LOG_FILE,
                    datefmt='%Y-%m-%d %H:%M:%S')

ExtractedTweet = namedtuple('ExtractedTweet', ['type','id', 'reply_count', 'permalink_path'])


def TweetReply(id,reply_count,permalink_path):
    return ExtractedTweet("tweet",id,reply_count,permalink_path)


def extract_reply(reply_elem):
    id = reply_elem.get_attribute('data-tweet-id')
    reply_count = reply_elem.find_element_by_class_name('ProfileTweet-actionCountForPresentation').text
    if reply_count is '':
        reply_count = 0
    reply_count = int(reply_count)
    permalink_path = reply_elem.get_attribute('data-permalink-path')
    return TweetReply(id, reply_count, permalink_path)


def extract_first_reply(reply_thread_elem):
    reply_elem = reply_thread_elem.find_elements_by_class_name('tweet')
    if len(reply_elem) == 0:
        return []
    return [extract_reply(reply_elem[0])]


def extract_all_replies(reply_thread_elem):
    # First, check if there are more Tweets to load
    show_more_btn = reply_thread_elem.find_elements_by_class_name("ThreadedConversation-moreReplies")
    if len(show_more_btn) > 0:
        show_more_btn[0].click()
        time.sleep(1)
    replies_elem = reply_thread_elem.find_elements_by_class_name('tweet')
    return [extract_reply(reply_elem) for reply_elem in replies_elem]


def is_first_stream_item_tombstone(thread_elem):
        first_item = thread_elem.find_elements_by_css_selector('ol > div:first-child .Tombstone')
        return len(first_item) > 0


def to_hashmap(list,hash_field):
    map = {}
    for item in list:
        map[item.id] = item
    return map


def fetch_replies(permalink_path, driver):
    driver.get("https://twitter.com/%s" % permalink_path)
    wait = WebDriverWait(driver, 5)
    wait.until(visibility_of_element_located((By.CSS_SELECTOR, '.permalink-container')))

    # Extract ancestors as Twitter's old frontend has a bug that displays ancestors in the reply-to stream.
    ancestors_list = driver.find_elements_by_css_selector("#ancestors #stream-items-id")
    ancestors = {}
    if len(ancestors_list) > 0:
        ancestors = to_hashmap(extract_all_replies(ancestors_list[0]),"id")
        logger.debug("Found %s items for ancestors" % len(ancestors))

    while len(driver.find_elements_by_css_selector('.timeline-end.has-more-items')) > 0:
         logger.info("More Tweets available, scrolling")
         driver.execute_script(
         # TODO This depends on jQuery that's shipped with page. Best to remove reliance on this.
             """
         $('#permalink-overlay').scrollTop(($('.permalink-container').height()));
             """
         )
         time.sleep(1)
    # Some Tweets contain replies that Twitter considers low-value. They are hidden behind a "Show More Replies"
    # button. Can retrieve them by clicking the button.
    try:
        more_threads_button = driver.find_element_by_css_selector(
            '#stream-items-id > .ThreadedConversation-showMoreThreads button'
        )
        more_threads_button.click()
        time.sleep(1)
    except NoSuchElementException:
        pass

    # TODO "Show More Replies" may produce more lazily-loaded Tweets. May have to handle this.

    # TODO Twitter now has a "Hidden Replies" feature which allows original Tweet author to hide some replies.
    # Need to fetch those tweets too.


    # Only select the replies to this Tweet.
    reply_list_elems = driver.find_elements_by_css_selector("#descendants #stream-items-id > li")
    logger.info("We found %s threads in reply" % len(reply_list_elems))
    replies = []
    for idx, reply_thread_elem in enumerate(reply_list_elems,0):
        logger.debug("Iterating through threads, now processing thread #%s" % idx)
        if is_first_stream_item_tombstone(reply_thread_elem):
            # Extract replies to tombstone Tweets.
            extracted_replies = extract_all_replies(reply_thread_elem)
            logger.info("Scraped %s replies to tombstone" % len(extracted_replies))
        else:
            extracted_replies = extract_first_reply(reply_thread_elem)
        for reply in extracted_replies:
            if ancestors.get(reply.id) is not None:
                # Do not put Tweet into list of replies if it is one of the ancestors.
                # Twitter's old frontend has a bug that shows the ancestors as replies-to a Tweet.
                continue
            replies.append(reply)
    return replies


def drive_fetch_replies(permalink):
    all_tweets_count = 0
    to_do = [permalink]
    with webdriver.Firefox() as driver:
        # Ensure it is the old UI.
        driver.get('https://twitter.com')
        driver.add_cookie({"name": "guest_id", "value": OLD_UI_CLIENT_ID})

        while len(to_do) > 0:
            logger.info("There are now %s Tweets to fetch replies for. Processing the first from list." % len(to_do))
            logger.info("Processing %s" % to_do[0])
            replies = fetch_replies(to_do.pop(0),driver)
            logger.info("Found %s Tweets in reply." % len(replies))
            fetch_needed = [reply.permalink_path for reply in replies if reply.reply_count > 0]
            logger.info("Found %s more Tweets with replies, adding them to to do list." % len(fetch_needed))
            to_do.extend(fetch_needed)
            yield replies
            all_tweets_count += len(replies)
            time.sleep(random.random()*0.3)
    logger.info("Fetch finished with %s Tweets scraped." % all_tweets_count)


def fetch_tweets_to_csv(permalink,output_filename):
    for replies in drive_fetch_replies(permalink):
        logger.info("Opening file to write files")
        with open(output_filename, "a") as out_file:
            writer = csv.writer(out_file)
            for reply in replies:
                writer.writerow(reply)


fetch_tweets_to_csv(TWEET_TO_EXTRACT, OUTPUT_FILE)
