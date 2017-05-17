#!/isr/bin/env python

import argparse
import datetime
import httplib2 # used to perform the get request to the Google API
import json
import os
import pdb
import sys
import textwrap
import time
import webbrowser

from apiclient import discovery
from datetime import time
from datetime import timedelta
from model.google_connection import Google_Connection
from model.meeting import Meeting
from model.report import Report
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


help = textwrap.dedent("""
    """ )

#  for Flask - MAKE SURE TO TURN ON THE LAST LINE, TOO!

from flask import Flask
from flask import render_template
app = Flask(__name__)


def get_meeting_report():

    gc = Google_Connection()
    meetings = gc.meetings
    #  _print_entire_google_calendar_results_as_json(meetings)

    rep = Report(meetings)

    data = rep.printable_data
    rep.write_report_html(data)

    #  rep.post_report_to_slack()
    #
    #  rep.write_db_to_csv()
    #  rep.write_csv_to_json()
    #
    generate_charts(data)
    open_charts_in_browser()


def open_charts_in_browser():
    webbrowser.open('http://localhost:5000/percent_pie')
    webbrowser.open('http://localhost:5000/percent_pie_split_2')
    webbrowser.open('http://localhost:5000/percent_pie_split_1')
    webbrowser.open('http://localhost:5000/when_you_meet_most')
    webbrowser.open('file:///Users/drew-sullivan/codingStuff/i_heart_meetings/i_heart_meetings/templates/report.html')


def _print_entire_google_calendar_results_as_json(meetings):
    print(json.dumps(meetings, indent=4, sort_keys=True))


def generate_charts(data):

    @app.route("/when_you_meet_most")
    def chart():
        legend = 'test'
        # X axis - list
        labels = data[17]
        # Y axis - list
        values = list(data[18].values())
        return render_template('when_you_meet_most_line.html', values=values, labels=labels, legend=legend)

    @app.route('/percent_pie')
    def percent_pie():
        current_costs = 'Current Costs: {0} and {1} yearly'.format(
            data[3], data[2])
        ideal_costs = 'Ideal Meeting Investment: {0} and {1}'.format(
            data[12], data[11])
        savings = 'Potential Savings: {0} and {1}'.format(data[15],
            data[16])
        remainder = 100 - data[19]
        recovered_costs = data[19] - data[20]
        legend = 'Percentage of Time Spent in Meetings'
        labels = [current_costs, 'Non-Meetings', ideal_costs, savings]
        values = [data[19], remainder, data[20], recovered_costs]
        return render_template('percent_pie.html', values=values, labels=labels, legend=legend)

    @app.route('/percent_pie_split_1')
    def percent_pie_split_1():
        current_costs = 'Current Costs: {0} and {1} yearly'.format(
            data[3], data[2])
        ideal_costs = 'Ideal Meeting Investment: {0} and {1}'.format(
            data[12], data[11])
        savings = 'Potential Savings: {0} and {1}'.format(data[15],
            data[16])
        remainder = 100 - data[19]
        recovered_costs = data[19] - data[20]
        legend = 'Percentage of Time Spent in Meetings'
        labels = [current_costs, 'Non-Meetings']
        values = [data[19], remainder]
        return render_template('percent_pie_split_1.html', values=values, labels=labels, legend=legend)

    @app.route('/percent_pie_split_2')
    def percent_pie_split_2():
        current_costs = 'Current Costs: {0} and {1} yearly'.format(
            data[3], data[2])
        ideal_costs = 'Ideal Meeting Investment: {0} and {1}'.format(
            data[12], data[11])
        savings = 'Potential Savings: {0} and {1}'.format(data[15],
            data[16])
        remainder = 100 - data[19]
        recovered_costs = data[19] - data[20]
        legend = 'Percentage of Time Spent in Meetings'
        labels = ['Non-Meetings', ideal_costs, savings]
        values = [remainder, data[20], recovered_costs]
        return render_template('percent_pie_split_2.html', values=values, labels=labels, legend=legend)

    @app.route('/slack_printout_test')
    def slack_printout_test():
        weekly_cost_in_seconds_readable = data[0]
        return render_template('slack_printout_test.html', weekly_cost_in_seconds=weekly_cost_in_seconds)

    @app.route('/summary')
    def summary():
        weekly_costs = [data[1], data[0]]
        return render_template('summary.html', weekly_costs=weekly_costs)

    #Plug-and-play templates

    #@app.route("/line_chart_2")
    #def chart_2():
    #    legend = 'Meeting Durations'
    #    # X axis - list
    #    labels = list_of_meeting_summaries
    #    # Y axis - list
    #    values = list_of_meeting_durations
    #    return render_template('line.html', values=values, labels=labels, legend=legend)

    #@app.route("/bar_chart")
    #def bar_chart():
    #    legend = 'Meeting Durations'
    #    #labels = list_of_meeting_ids
    #    labels = list_of_meeting_summaries
    #    values = list_of_meeting_durations
    #    return render_template('bar.html', values=values, labels=labels, legend=legend)

    #@app.route('/radar_chart')
    #def radar_chart():
    #    legend = 'Meeting Durations'
    #    #labels = list_of_meeting_ids
    #    labels = list_of_meeting_summaries
    #    values = list_of_meeting_durations
    #    return render_template('radar.html', values=values, labels=labels, legend=legend)

    #@app.route('/polar_chart')
    #def polar_chart():
    #    legend = 'Meeting Durations'
    #    labels = list_of_meeting_ids
    #    values = list_of_meeting_durations
    #    return render_template('polar.html', values=values, labels=labels, legend=legend)

    #@app.route('/pie_chart')
    #def pie_chart():
    #    current_costs = 'Current Costs: {0} and {1} yearly'.format(
    #        data[3], data[2])
    #    ideal_costs = 'Ideal Meeting Investment: {0} and {1}'.format(
    #        data[12], data[11])
    #    savings = 'Potential Savings: {0} and {1}'.format(data[15],
    #        data[16])
    #    legend = 'Meeting Durations'
    #    labels = [current_costs, 'Non-Meetings', ideal_costs, savings]
    #    values = [data[19],9,8,15]
    #    return render_template('pie.html', values=values, labels=labels, legend=legend)

    #@app.route('/doughnut_chart')
    #def doughnut_chart():
    #    legend = 'Meeting Durations'
    #    labels = list_of_meeting_ids
    #    values = list_of_meeting_durations
    #    return render_template('doughnut.html', values=values, labels=labels, legend=legend)


if __name__ == '__main__':
    get_meeting_report()
    app.run(debug=False)
