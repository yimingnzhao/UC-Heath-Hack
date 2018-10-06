import webapp2
import json
import os
import jinja2
from datetime import datetime, timedelta
import time
import math
import logging
from user_database import User
from google.appengine.ext import ndb
from google.appengine.api import users






current_jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
            welcome_template = current_jinja_environment.get_template('templates/welcome.html')
            self.response.write(welcome_template.render())



class LoginHandler(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()


        if loggedin_user:
            current_users = User.query().filter(User.id == str(loggedin_user.user_id())).fetch()
            x = []
            if current_users == x:
                template = current_jinja_environment.get_template('templates/signup.html')
                self.response.write(template.render())
            else:
                #template = current_jinja_environment.get_template('templates/home.html')
                #self.response.write(template.render({'logout_link': users.create_logout_url('/')}))
                self.redirect('/homepage')
        else:
            login_prompt_template = current_jinja_environment.get_template('templates/login.html')
            self.response.write(login_prompt_template.render({'login_link': users.create_login_url('/login-page')}))


class MakeUserHandler(webapp2.RequestHandler):
    def post(self):
        if self.request.get('person') == "patient":
            user = User( id = str(users.get_current_user().user_id()), first_name = self.request.get('fname'), last_name = self.request.get('lname'), is_doctor = False, list = [], exit_date = datetime.utcnow())
        else:
            user = User( id = str(users.get_current_user().user_id()), first_name = self.request.get('fname'), last_name = self.request.get('lname'), is_doctor = True, list = [])
        user.put()
        time.sleep(4)
        self.redirect('/homepage')

class HomePageHandler(webapp2.RequestHandler):
    def get(self):
            if User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0].is_doctor:
                self.redirect('/doctor-homepage')
            template_vars = {}
            template_vars['logout_link'] = users.create_logout_url('/')
            template_vars['username'] =  User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0].first_name
            print(User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0].first_name)
            html = ""
            message_query = User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0].list
            logging.info(len(message_query))
            for message in message_query:
                html+="<tr>"
                html+="<td><i class='fa fa-user w3-text-blue w3-large'></i></td>"
                html+="<td>" + message + "</td>"
                html+="</tr>"
            template_vars['code'] = html

            home_template = current_jinja_environment.get_template('templates/home.html')
            self.response.write(home_template.render(template_vars))


class HomePageDoctorHandler(webapp2.RequestHandler):
    def get(self):
        template_vars = {}
        template_vars['logout_link'] = users.create_logout_url('/')
        template_vars['username'] =  User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0].last_name
        home_template = current_jinja_environment.get_template('templates/doctor-homepage.html')
        self.response.write(home_template.render(template_vars))

class AddPatientHandler(webapp2.RequestHandler):
    def get(self):
        template_vars = {}
        home_template = current_jinja_environment.get_template('templates/add-patient.html')
        self.response.write(home_template.render(template_vars))


class CheckHandler(webapp2.RequestHandler):
    def post(self):
        user_query = User.query().filter(User.first_name == self.request.get('fname') and User.last_name == self.request.get('lname')).fetch()
        if not len(user_query) == 0 and user_query[0].is_doctor == False:
            doctor = User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0]
            doctor.list.append(user_query[0].id)
            doctor.put()

        self.redirect('/doctor-homepage')


class SendMessageHandler(webapp2.RequestHandler):
    def get(self):
        template_vars = {}

        doctor = User.query().filter(User.id == str(users.get_current_user().user_id())).fetch()[0]
        code = "";

        for id in doctor.list:
            patient = User.query().filter(User.id == str(id)).fetch()[0]
            code+= "<option value='" + patient.id + "'>" + patient.first_name + " " + patient.last_name + "</option>"
        template_vars['code'] = code
        template_vars['name'] = doctor.first_name + " " + doctor.last_name;
        home_template = current_jinja_environment.get_template('templates/send-message.html')
        self.response.write(home_template.render(template_vars))



class CheckMessageHandler(webapp2.RequestHandler):
    def post(self):
        user = User.query().filter(User.id == str(self.request.get('patient-id'))).fetch()[0]
        user.list.append(self.request.get('doctor-name') + " - " + self.request.get('message'))
        user.put()
        self.redirect('/doctor-homepage')


app = webapp2.WSGIApplication([
    #('/', MainHandler),
    ('/', WelcomeHandler),
    ('/login-page', LoginHandler),
    ('/homepage', HomePageHandler),
    ('/make-user', MakeUserHandler),
    ('/doctor-homepage', HomePageDoctorHandler),
    ('/add-patient', AddPatientHandler),
    ('/send-message', SendMessageHandler),
    ('/check-add-patient', CheckHandler),
    ('/check-message', CheckMessageHandler)
])
