# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

from app import app
from app.utils.secrets import getSecrets
import requests
from flask import render_template, flash, redirect, url_for
import requests
from flask_login import current_user
from app.classes.data import Report
from app.classes.forms import ReportForm
from flask_login import login_required
import datetime as dt


@app.route('/report/map')
@login_required
def reportMap():

    reports = Report.objects()

    return render_template('reportlocator.html',reports=reports)

@app.route('/report/list')
@login_required
def reportList():

    reports = Report.objects()

    return render_template('report.html',reports=reports)


@app.route('/report/<reportID>')
@login_required
def report(reportID):

    thisReport = report.objects.get(id=reportID)

    return render_template('report.html',report=thisReport)


@app.route('/report/delete/<reportID>')
@login_required
def reportDelete(reportID):
    deleteReport = report.objects.get(id=reportID)

    deleteReport.delete()
    flash('The report was deleted.')
    return redirect(url_for('reportList'))

def updateLatLon(report):
    # get your email address for the secrets file
    secrets=getSecrets()
    # call the maps API with the address
    url = f"https://nominatim.openstreetmap.org/search?street={report.streetAddress}&city={report.city}&state={report.state}&postalcode={report.zipcode}&format=json&addressdetails=1&email={secrets['MY_EMAIL_ADDRESS']}"
    # get the response from the API
    r = requests.get(url)
    # Find the lat/lon in the response
    try:
        r = r.json()
    except:
        flash("unable to retrieve lat/lon")
        return(report)
    else:
        if len(r) != 0:
            # update the database
            report.update(
                lat = float(r[0]['lat']),
                lon = float(r[0]['lon'])
            )
            flash(f"report lat/lon updated")
            return(report)
        else:
            flash('unable to retrieve lat/lon')
            return(report)

@app.route('/report/new', methods=['GET', 'POST'])
@login_required
def reportNew():
    form = ReportForm()

    if form.validate_on_submit():

        newReport = Report(
            name = form.name.data,
            streetAddress = form.streetAddress.data,
            city = form.city.data,
            state = form.state.data,
            zipcode = form.zipcode.data,
            description = form.description.data,
            author = current_user.id,
            modifydate = dt.datetime.utcnow,
        )
        newReport.save()

        newRepor = updateLatLon(newReport)

        import requests

        return redirect(url_for('report',reportID=newReport.id))

    return render_template('reportform.html',form=form)

@app.route('/report/edit/<reportID>', methods=['GET', 'POST'])
@login_required
def reportEdit(reportID):
    editReport = Report.objects.get(id=reportID)

    if current_user != editReport.author:
        flash("You can't edit a post you don't own.")
        return redirect(url_for('report',reportID=reportID))

    form = ReportForm()
    if form.validate_on_submit():
        editReport.update(
            name = form.name.data,
            streetAddress = form.streetAddress.data,
            city = form.city.data,
            state = form.state.data,
            zipcode = form.zipcode.data,            
            description = form.description.data,
            modifydate = dt.datetime.utcnow,
        )
        editReport = updateLatLon(editReport)
        return redirect(url_for('report',reportID=ReportID))

    form.name.data = editReport.name
    form.streetAddress.data = editReport.streetAddress
    form.city.data = editReport.city
    form.state.data = editReport.state
    form.zipcode.data = editReport.zipcode
    form.description.data = editReport.description

    return render_template('reportform.html',form=form)
