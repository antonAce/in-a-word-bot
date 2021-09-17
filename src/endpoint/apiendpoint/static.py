from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, text, link, italic
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from .settings import REPO_LINK, DEV_LINK

# STATIC MESSAGES
BOT_TITLE = emojize(text(*[
    "Hi there! Finding the right information in the ", italic("digital era"),
    " may be the real challenge nowadays because it's growing ", bold("exponentially"),
    " day by day! Whether you are a student preparing an essay or a researcher working ",
    "with the knowledge base, you spend a lot of time searching, filtering, and summarizing ",
    "text. ", link("Google", "https://www.google.com/"), " can assist you with the first two steps, "
                                                         "but I will help with the last one!", " Send me a ",
    bold("plain text"), ", ", bold("file"),
    ", or ", bold("link to an external resource"), ", and I will summarize it for you in a word :grin:.\n\n",
    "I'm an open-source project, and you can find my ", link("source code here", REPO_LINK), ". ",
    "If you want to report an issue or have some suggestions for improvement, contact the ",
    link("maintainer", DEV_LINK), "."], sep=''))

CHOOSE_AVAILABLE_OPTIONS = emojize(text(*["Choose the available options below:"], sep=''))

SUMMARY_OPTION_TITLE = emojize(text(*[
    "Choose the type of text summarization you need:\n\n",
    bold("Extractive"), " - summary is being formed by copying parts of source text through a measure of importance and then combining those parts of the sentences together to render a summary.\n",
    bold("Abstractive"), " - the process involves generating new phrases, by reshaping or using words that weren’t originally there in the original text.\n\n",
], sep=''))

SENDING_REQUEST = emojize(text(*[
    ":outbox_tray:", "Sending request to the web resource..."
], sep=' '))

PROCESSING_FILE = emojize(text(*[
    ":floppy_disk:", "Processing uploaded file..."
], sep=' '))

COMMAND_CANCELLED = emojize(text(*[
    ":warning:", "The command has been cancelled."
], sep=' '))

GENERATING_SUMMARY = emojize(text(*[
    ":notebook_with_decorative_cover:", "Generating summary..."
], sep=' '))

# STATIC REPLY-KEYBOARD OPTIONS
SUMMARY_FROM_PLAIN_TEXT_OPTION = emojize(text(*['Text', ':notebook_with_decorative_cover:']))
SUMMARY_FROM_FILE_OPTION = emojize(text(*['File', ':floppy_disk:']))
SUMMARY_FROM_WEB_RESOURCE_OPTION = emojize(text(*['Webpage', ':globe_with_meridians:']))

MAIN_MENU_OPTIONS = [SUMMARY_FROM_PLAIN_TEXT_OPTION, SUMMARY_FROM_FILE_OPTION, SUMMARY_FROM_WEB_RESOURCE_OPTION]

SUMMARIZE_EXTRACTIVE_OPTION = emojize(text(*['Extractive']))
SUMMARIZE_ABSTRACTIVE_OPTION = emojize(text(*['Abstractive']))

SUMMARIZE_BY_CRITERIA_OPTIONS = [SUMMARIZE_EXTRACTIVE_OPTION, SUMMARIZE_ABSTRACTIVE_OPTION]

CHOSEN_SUMMARY_RESPONSES = {
    SUMMARY_FROM_PLAIN_TEXT_OPTION: emojize(text(*[
        'Good! Now send me directly the text you want to summarize.\n\n',
        ':warning:', bold('WARNING'), ': Maximum message length in Telegram is only 4096 characters.'
    ], sep='')),
    SUMMARY_FROM_FILE_OPTION: emojize(text(*[
        'Good! Now send me the file, which contains text you want to summarize.\n\n',
        ':warning:', bold('WARNING'), ':\n',
        '1) For now the only accepted file format is ".', bold('TXT'), '".\n',
        '2) Max file size is ', bold('50kB'), '.'
    ], sep='')),
    SUMMARY_FROM_WEB_RESOURCE_OPTION: emojize(text(*[
        'Good! Now send me an URL to external web resource to parse and summarize.\n\n',
        ':warning:', bold('WARNING'), ': JavaScript content will not be handled.'
    ], sep=''))
}

# STATIC REPLY-KEYBOARDS
main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(*MAIN_MENU_OPTIONS)
summarize_by_criteria_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(*SUMMARIZE_BY_CRITERIA_OPTIONS)
empty_keyboard = ReplyKeyboardRemove()

# ERROR MESSAGES
NO_SUMMARIZATION_CRITERIA_ERROR = emojize(text(*[':no_entry:', 'The summarization criteria was not specified.']))
WEB_CRAWLER_HTTP_ERROR = emojize(text(*[':no_entry:', 'Failed to parse web resource content by the given URL.']))
FILE_SIZE_EXCEEDED_LIMIT_ERROR = emojize(text(*[':no_entry:', 'Uploaded file size is bigger than 20 kB.']))
FILE_WRONG_EXTENSION_ERROR = emojize(text(*[':no_entry:', 'Uploaded file has wrong extension.']))
INCORRECT_HTTP_FORMAT_ERROR = emojize(text(*[':no_entry:', 'Web resource link has incorrect format.']))
