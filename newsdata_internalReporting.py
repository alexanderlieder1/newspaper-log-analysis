#!/usr/bin/env python

"""
This is a script to create an internal reporting tool.

The internal reporting tool answers 3 business questions
and is based on a database named 'news', which keeps logs
of all http requests and contains information about
the articles read and the associated authors of those articles.
"""

# Importing necessary libaries
import psycopg2


# Writing helper function to connect to PostgreSQL database (db) with error handling
def connect(database_name):
    """Connect to db. Takes name as string. Returns db connection."""
    try:
        db = psycopg2.connect(database="{}".format(database_name))
        c = db.cursor()
        return db, c
    except psycopg2.Error as e:
        print "Unable to connect to database"
        sys.exit(1) # The easier method


# Creating functions to pull data and print results
def create_internal_report(query_input):
    """Create an internal report output."""
    db, c = connect("news")
    c.execute(query_input)
    results = c.fetchall()
    db.close()
    return results


def print_internal_report(data_input):
    """Print the internal report results."""
    for i in range(len(data_input)):
        for j in range(len(data_input[i])-1):
            print("{} - {}".format(data_input[i][j], data_input[i][j+1]))


# Writing queries that will act as an input for create_internal_report()

# SQL query for task 1: Identifying the most viewed articles
top_viewed_articles_query = """SELECT art.title
    , COUNT(log.id) || ' views' AS "views"

    FROM log

    JOIN (
    SELECT title, '/article/' || slug AS "path" FROM articles
    ) AS art
    ON art.path = log.path

    WHERE 1=1
    AND log.status = '200 OK'

    GROUP BY art.title
    ORDER BY views DESC

    LIMIT 3;"""

# SQL query for task 2: Identifying the most viewed authors
top_viewed_authors_query = """SELECT aut.name
    , COUNT(log.id) || ' views' AS "views"

    FROM log

    JOIN (
    SELECT author, title, '/article/' || slug AS "path" FROM articles
    ) AS art
    ON art.path = log.path

    JOIN (
    SELECT id, name FROM authors
    ) AS aut
    ON aut.id = art.author

    WHERE 1=1
    AND log.status = '200 OK'

    GROUP BY aut.name
    ORDER BY views DESC;"""

# SQL query for task 3: Identifying days of error HTTP requests >1%
error_requests_query = """WITH totalRequests AS (
    SELECT time::date AS Day_tot
    --SELECT to_char(time, 'DD Mon YYYY') AS Day_tot
    , COUNT(0) AS logs_tot

    FROM log

    GROUP BY Day_tot
    ), errorRequests AS (
    SELECT time::date AS Day_err
    , COUNT(0) AS logs_err

    FROM log

    WHERE 1=1
    AND status <> '200 OK'

    GROUP BY Day_err)

    SELECT to_char(Day_tot, 'FMMonth DD, YYYY') AS "Day"
    , ROUND((logs_err*100.0/logs_tot),2) || '% errors' AS "Error Percentage"

    FROM totalRequests
    JOIN errorRequests
    ON Day_tot=Day_err

    WHERE 1=1
    AND (logs_err*100.0/logs_tot) > 1;"""


# Functions to print results of internal report
def print_top_articles():
    """Print top articles."""
    data_art = create_internal_report(top_viewed_articles_query)
    print("\nWhat are the most popular three articles of all time?")
    print_internal_report(data_art)


def print_top_authors():
    """Print top authors."""
    data_authors = create_internal_report(top_viewed_authors_query)
    print("\nWho are the most popular article authors of all time?")
    print_internal_report(data_authors)


def print_top_error_days():
    """Print top error days."""
    data_errors = create_internal_report(error_requests_query)
    print("\nOn which days did more than 1% of requests lead to errors?")
    print_internal_report(data_errors)


# Running report when executing script
if __name__ == '__main__':
    print_top_articles()
    print_top_authors()
    print_top_error_days()
