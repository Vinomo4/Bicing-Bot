# Bicing® Bot

> Telegram® bot that provides useful information about Bicing® stations and their respective status in a user-friendly interface.

This project consists of a [Telegram](https://www.upc.edu/ca)®  bot developed in Python which answers either
with text or images to questions related to geometric graphs defined over the
[Bicing](https://www.bicing.barcelona/es)® stations in the city of Barcelona. 

<p align="center">
  <img src='chat.jpeg'  width='250'/>
</p>

## Instructions

In order to chat with the bot, one must first install the Telegram application. Once it is installed, the user must write `@BCN_BicingBot` and open a
conversation with the bot. Once this is done, the `/start` command will
automatically trigger, allowing the introduction of the following instructions.

<p align="center">
  <img src='commands.jpeg'  width='250'/>
</p>


### `/start`

Initiates conversation with the bot, which includes the creation of a graph with
a distance of 1000m. The meaning of this value will be explained as follows.

### `/help`

This will trigger a short list of every available command, as well as a brief
description of each one of them.

### `/authors`

Sends a message with the authors of the project, as well as the current version
of the bot and the university where it has been developed at.

### `/graph ⟨distance⟩`

Given a value which represents the maximum distance (in meters) allowed between stations, it will create a geometric graph with the bike stations as nodes and edges between the stations that are within the introduced distance. This graph will be used from now on by the following commands. 

*Note: If an invalid distance is given,(<0 or None), 1000 meters will be used.*

### `/nodes`

Writes the number of nodes in the graph.

### `/edges`

Writes the number of edges in the graph.

### `/components`

Writes the number of connected components in the graph.

### `/plotgraph`

Shows a map of the city of Barcelona with the stations and edges in the graph.

### `/route origin, destination`

Given an origin address and a destination address, will print a map of the
fastest path from origin to destination with the structure *origin* → *station* →
*[...]* → *station* → *destination*.

*Note: This is followed by an estimated time of the trip.*

### `/distribute required_bikes required_docks`

Given a number of required bikes and docks per station, returns (if such request
is possible) the cost of doing it, as well as the most expensive
*transaction* of bikes between two stations.

## Architecture

The project folder contains four files, one being this Readme; a second one used
for the installation; and two more files directly related to the code of the bot.
The `data.py` contains all the code related to the data acquisition, graph
construction and calculations over the said graph. On the other hand, `bot.py`
has the code related to the Telegram functionality of the bot.

## Installation

In order to have access to the libraries used in this bot the user must write
the line `pip install -r requirements.txt` in the command line window while
being inside the project folder.

## Sources

* [Telegram Jutge Lessons](https://lliçons.jutge.org/python/telegram.html)

* [Python Files Jutge Lessons](https://lliçons.jutge.org/python/fitxers-i-formats.html)

* [NetworkX Documentation](https://networkx.github.io/documentation/stable/tutorial.html)

* [Pandas Documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)

## Team

This bot was developed by:
| [![Vinomo4](https://avatars2.githubusercontent.com/u/49389601?s=60&v=4)](https://github.com/Vinomo4) | [![CarlOwOs](https://avatars3.githubusercontent.com/u/49389491?s=60&u=b239b67c3f064bf2dae05e08ae9965b7c7e34c36&v=4)](https://github.com/CarlOwOs) |
| --- | --- |
| [Victor Novelle Moriano](https://github.com/Vinomo4) | [Carlos Hurtado Comin](https://github.com/CarlOwOs) |


Students of Data Science and Engineering at [UPC](https://www.upc.edu/ca).



