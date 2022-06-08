import time
import html
import asyncio
import aiohttp
import feedparser
from telegram.ext import run_async, CommandHandler
from telegram import ParseMode
from bot import dispatcher
from urllib.parse import quote as urlencode, urlsplit
from pyrogram import Client, filters
from pyrogram.parser import html as pyrogram_html
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.helper import custom_filters
from bot import app
session = aiohttp.ClientSession()
search_lock = asyncio.Lock()
search_info = {False: dict(), True: dict()}
def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)
async def return_search(query, page=1, movie=False):
    page -= 1
    query = query.lower().strip()
    used_search_info = search_info[movie]
    async with search_lock:
        results, get_time = used_search_info.get(query, (None, 0))
        if (time.time() - get_time) > 3600:
            results = []
            async with session.get(f'https://ensub.herokuapp.com/jackett.php?cat={"movie" if movie else ""}&q={urlencode(query)}') as resp:
                d = feedparser.parse(await resp.text())
            text = ''
            a = 0
            parser = pyrogram_html.HTML(None)
            for i in sorted(d['entries'], key=lambda i: int(i['seeders']['value']), reverse=True):
                if i['size'].startswith('0'):
                    continue
                if not int(i['seeders']['value']):
                    break
                link = i['link']
                site = i['comments']
                splitted = urlsplit(link)
                if splitted.scheme == 'magnet' and splitted.query:
                    link = f'<code>{link}</code>'
                else:
                    link = f'<a href="{link}">Clickme</a>'
                newtext = f'''{a + 1}. {html.escape(i["title"])}
<b>Link:</b> {link}
<b>Size:</b> {humanbytes(i["size"])}
<b>Seeders:</b> {i["seeders"]["value"]}
<b>Peers:</b> {i["peers"]["value"]}
<b>Indexer:</b> <a href="{site}">{i["jackettindexer"]["id"]}</a>\n\n'''
                futtext = text + newtext
                if (a and not a % 10) or len((await parser.parse(futtext))['message']) > 4096:
                    results.append(text)
                    futtext = newtext
                text = futtext
                a += 1
            results.append(text)
        ttl = time.time()
        used_search_info[query] = results, ttl
        try:
            return results[page], len(results), ttl
        except IndexError:
            return '', len(results), ttl

message_info = dict()
ignore = set()
@app.on_message(filters.command(['ts', 'search', 'jackett']))
async def nyaa_search(client, message):
    text = message.text.split(' ')
    text.pop(0)
    query = ' '.join(text)
    await init_search(client, message, query, False)

@app.on_message(filters.command(['mov', 'movie']))
async def nyaa_search_sukebei(client, message):
    text = message.text.split(' ')
    text.pop(0)
    query = ' '.join(text)
    await init_search(client, message, query, True)

async def init_search(client, message, query, movie):
    await message.reply_text('Searching..... Please wait!')
    result, pages, ttl = await return_search(query, movie=movie)
    if not result:
        await message.reply_text('No results found')
    else:
        buttons = [InlineKeyboardButton(f'1/{pages}', 'nyaa_nop'), InlineKeyboardButton('Next', 'nyaa_next')]
        if pages == 1:
            buttons.pop()
        reply = await message.reply_text(result, reply_markup=InlineKeyboardMarkup([
            buttons
        ]))
        message_info[(reply.chat.id, reply.message_id)] = message.from_user.id, ttl, query, 1, pages, movie

@app.on_callback_query(custom_filters.callback_data('nyaa_nop'))
async def nyaa_nop(client, callback_query):
    await callback_query.answer(cache_time=3600)

callback_lock = asyncio.Lock()
@app.on_callback_query(custom_filters.callback_data(['nyaa_back', 'nyaa_next']))
async def nyaa_callback(client, callback_query):
    message = callback_query.message
    message_identifier = (message.chat.id, message.message_id)
    data = callback_query.data
    async with callback_lock:
        if message_identifier in ignore:
            await callback_query.answer()
            return
        user_id, ttl, query, current_page, pages, movie = message_info.get(message_identifier, (None, 0, None, 0, 0, None))
        og_current_page = current_page
        if data == 'nyaa_back':
            current_page -= 1
        elif data == 'nyaa_next':
            current_page += 1
        if current_page < 1:
            current_page = 1
        elif current_page > pages:
            current_page = pages
        ttl_ended = (time.time() - ttl) > 3600
        if ttl_ended:
            text = getattr(message.text, 'html', 'Search expired')
        else:
            if callback_query.from_user.id != user_id:
                await callback_query.answer('...no', cache_time=3600)
                return
            text, pages, ttl = await return_search(query, current_page, movie)
        buttons = [InlineKeyboardButton('Back', 'nyaa_back'), InlineKeyboardButton(f'{current_page}/{pages}', 'nyaa_nop'), InlineKeyboardButton('Next', 'nyaa_next')]
        if ttl_ended:
            buttons = [InlineKeyboardButton('Search Expired', 'nyaa_nop')]
        else:
            if current_page == 1:
                buttons.pop(0)
            if current_page == pages:
                buttons.pop()
        if ttl_ended or current_page != og_current_page:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                buttons
            ]))
        message_info[message_identifier] = user_id, ttl, query, current_page, pages, movie
        if ttl_ended:
            ignore.add(message_identifier)
    await callback_query.answer()

@run_async
def searchhelp(update, context):
    help_string = '''
Global Search
• /ts <i>[search query]</i>
• /search <i>[search query]</i>
• /jackett <i>[search query]</i>
Movie Only (no Series)
• /mov <i>[search query]</i>
• /movie <i>[search query]</i>
'''
    update.effective_message.reply_text(help_string, parse_mode=ParseMode.HTML)


SEARCHHELP_HANDLER = CommandHandler("tshelp", searchhelp)
dispatcher.add_handler(SEARCHHELP_HANDLER)
