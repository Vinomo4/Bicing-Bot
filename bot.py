import telegram
import data
import random
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import os
import sys


# Starts the bot, generating a default graph.
def start(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id,
                     text="*Welcome to BCN Bicing Bot v 2.0!*",
                     parse_mode=telegram.ParseMode.MARKDOWN)
    user_data['G'] = data.create_graph(1000)


# List of commands available for the user.
def help(bot, update):
    intro = "*BotBicing* can execute the following commands:\n"
    start = ("/start \n Starts a new session with the bot."
             "*WARNING:* The current graph will be erased.\n")
    authors = "/authors \n Provides authors' names and e-mails.\n"
    graph = "/graph \n Generates a graph using the distance provided.\n"
    nodes = "/nodes \n Returns the number of nodes of  graph.\n"
    edges = "/edges \n Returns the number of edges of  graph.\n"
    components = ("/components \n Returns the number of connex "
                  "components of the graph.\n")
    plotgraph = ("/plotgraph \n Returns a .png image, representing "
                 "all the stations of the graph and their respective"
                 " connections.\n")
    route = ("/route \n Returns a .png image, with the shortest"
             " path between two coordinates. \n")
    distribute = ("/distribute \n Returns the cost of distributing"
                  " bikes given two parameters. \n")
    bot.send_message(chat_id=update.message.chat_id,
                     text=intro + start + authors + graph + nodes + edges +
                     components + plotgraph + route + distribute,
                     parse_mode=telegram.ParseMode.MARKDOWN)


# Authors of the project and their respective e-mails.
def authors(bot, update):
    version = "*BCN BicingBot v 2.0:*"
    first_author = "Victor Novelle Moriano: victor.novelle@est.fib.upc.edu"
    second_author = ("Carlos Hurtado Comin: carlos.hurtado"
                     ".comin@est.fib.upc.edu")
    licence = "_Univeristat Politecnica de Catalunya, 2019_"
    bot.send_message(chat_id=update.message.chat_id,
                     text=version + "\n" + first_author + "\n" +
                     second_author + "\n" + licence,
                     parse_mode=telegram.ParseMode.MARKDOWN)


# Generates the required graph for the user.
def graph(bot, update, args, user_data):
    if len(args) != 1 or float(args[0]) < 0:
        if len(args) == 0:
            msg = ("Since no range was given, a default "
                   "distance between stations of 1000m was used.")
            bot.send_message(chat_id=update.message.chat_id, text=msg)

        else:
            msg = ('Since an invalid range was given, a default distance '
                   'between stations of 1000m was used.')
            bot.send_message(chat_id=update.message.chat_id, text=msg)
        user_data['G'] = data.create_graph(1000)
    else:
        new_dist = float(args[0])
        user_data['G'] = data.create_graph(new_dist)
        bot.send_message(chat_id=update.message.chat_id,
                         text="*Graph created!*",
                         parse_mode=telegram.ParseMode.MARKDOWN)


def nodes(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id,
                     text=data.nodes(user_data['G']))


def edges(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id,
                     text=data.edges(user_data['G']))


def components(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id,
                     text=data.components(user_data['G']))


# Prints the actual graph.
def plotgraph(bot, update, user_data):
    bot.send_chat_action(chat_id=update.message.chat_id,
                         action=telegram.ChatAction.UPLOAD_PHOTO)
    name_file = "%d.png" % random.randint(1000000, 9999999)
    data.plotgraph(user_data['G'], name_file)
    bot.send_photo(chat_id=update.message.chat.id, photo=open(name_file, 'rb'))
    os.remove(name_file)


# Generates and prints the fastest route between the directions given.
def route(bot, update, args, user_data):
    try:
        bot.send_chat_action(chat_id=update.message.chat_id,
                             action=telegram.ChatAction.UPLOAD_PHOTO)
        addresses = ''
        for arg in args:
            addresses += arg + ' '
        name_file = "%d.png" % random.randint(1000000, 9999999)
        time = data.route(user_data['G'], name_file, addresses.lstrip())
        bot.send_photo(chat_id=update.message.chat.id,
                       photo=open(name_file, 'rb'))
        os.remove(name_file)
        bot.send_message(chat_id=update.message.chat_id,
                         text='The trip will take around %s minutes.' % time)

    except:
        bot.send_message(chat_id=update.message.chat_id,
                         text='No route can be found with the given addresses')


# Returns the cost of the required distribution and the bigger-cost movement.
def distribute(bot, update, args, user_data):
    if len(args) != 2 or int(args[0]) < 0 or int(args[1]) < 0:
        bot.send_message(chat_id=update.message.chat_id,
                         text='An invalid input was given.')
    else:
        nbikes, ndocks = int(args[0]), int(args[1])
        err, total_cost, Biggest_move = data.distribute(user_data['G'],
                                                        nbikes, ndocks)
        if err:
            msg = ('No possible solution could be found at this moment!')
            bot.send_message(chat_id=update.message.chat_id, text=msg)
        else:
            msg = ('Total cost of the distribution: %s km.'
                   % (round(total_cost, 4)))
            bot.send_message(chat_id=update.message.chat_id, text=msg)
            if not isinstance(Biggest_move, int):
                msg2 = ('The maximum cost is %s (km per bike) between station'
                        ' %d and station %d.' %
                        (round(Biggest_move[0], 4),
                         Biggest_move[1], Biggest_move[2]))
                bot.send_message(chat_id=update.message.chat_id, text=msg2)


# Informs user of an invalid command.
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I didn't understand.")

TOKEN = open('token2.txt').read().strip()

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('authors', authors))
dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True,
                                      pass_user_data=True))
dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data=True))
dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data=True))
dispatcher.add_handler(CommandHandler('components', components,
                                      pass_user_data=True))
dispatcher.add_handler(CommandHandler('plotgraph', plotgraph,
                                      pass_user_data=True))
dispatcher.add_handler(CommandHandler('route', route,
                                      pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('distribute', distribute,
                                      pass_args=True, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater.start_polling()
