from flask import Flask, make_response, request, render_template, url_for, redirect

import datetime
import json
import requests

from api.settings.apisettings import API_SECRET
from api.settings.apisettings import AI_SERVICE_URL

from api.forms.LoginForm import LoginForm
from api.forms.RegisterForm import RegisterForm
from api.forms.LectureForm import LectureForm
from api.forms.ResourceForm import ResourceForm

from api.forms.LectureEditForm import LectureEditForm
from api.forms.ResourceEditForm import ResourceEditForm
from api.forms.GenerateLectureForm import GenerateLectureForm

from bll.services.UserService import UserService
from bll.services.LecturesService import LecturesService
from bll.services.ResourcesService import ResourcesService

from bll.dto.UserDTO import UserDTO
from bll.dto.LectureDTO import LectureDTO
from bll.dto.ResourceDTO import ResourceDTO


def date_converter(o):
    if isinstance(o, datetime.date):
        return datetime.datetime.combine(o, datetime.datetime.min.time()).strftime("%Y-%m-%d")


def serialize(obj):
    return json.dumps(obj.__dict__, default=date_converter)


def serialize_array(arr):
    return '\n'.join([serialize(element) for element in arr])


def ping_ai_service(theme):
    req = requests.post(AI_SERVICE_URL, json={'theme': theme})

    if req.status_code == 500:
        return "Sorry, generating service is not available now!"
    elif req.status_code == 400:
        return "Wrong input data!"
    else:
        response = req.content
        return response


def filter_pending_lectures(lectures):
    filtered_lectures = []

    for lecture in lectures:
        if lecture.Status == 'Pending':
            filtered_lectures.append(lecture)

    return filtered_lectures


app = Flask(__name__)
app.secret_key = API_SECRET

user_service = UserService(API_SECRET)
lecture_service = LecturesService()
resource_service = ResourcesService()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm(request.form)

    if request.method == 'POST':
        message, status = user_service.auth_user(UserDTO(
            login=form.Login.data,
            password=form.Password.data,
            role=None,
            registration_date=None
        ))

        if status == 400:
            return render_template('login.html',
                                   form=form,
                                   message=message)

        res = make_response("")
        res.set_cookie('user', form.Login.data, max_age=None)
        res.set_cookie('token', form.Password.data, max_age=None)
        res.headers['location'] = url_for('page')
        return res, 302

    if 'token' in request.cookies:
        return render_template('page.html', user=request.cookies['user'])
    else:
        return render_template('login.html',
                               form=form,
                               message="")


@app.route('/page', methods=['GET'])
def page():
    if 'token' in request.cookies:
        return render_template('page.html', user=request.cookies['user'])
    else:
        return redirect('/logout')


@app.route('/logout', methods=['GET'])
def logout():
    res = make_response("")
    res.set_cookie('user', '', max_age=0)
    res.set_cookie('token', '', max_age=0)
    res.headers['location'] = url_for('index')
    return res, 302


@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            return render_template('register.html',
                                   form=form,
                                   message="Input data is not valid!")

        message, status = user_service.register_user(UserDTO(
            login=form.Login.data,
            password=form.Password.data,
            role="default_user",
            registration_date=datetime.date.today()
        ))

        if status == 400:
            return render_template('register.html',
                                   form=form,
                                   message=message)
        else:
            return redirect('/')

    return render_template('register.html',
                           form=form,
                           message="")


@app.route('/lecture', methods=['GET', 'POST'])
def list_lectures():
    user_login = request.cookies['user']
    lectures = lecture_service.get_all_user_lectures(user_login)
    lectures_count = lecture_service.get_count_of_user_lectures(user_login)
    form = LectureForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            return render_template('lecture.html',
                                   lectures=lectures,
                                   form=form,
                                   user=user_login,
                                   lectures_count=lectures_count,
                                   message="Input data is not valid!")

        new_lecture = LectureDTO(
            header=form.Header.data,
            content=form.Content.data,
            status="Pending",
            creation_date=datetime.date.today()
        )
        message, status = lecture_service.add_lecture(user_login, new_lecture)

        if status != 200:
            return render_template('lecture.html',
                                   lectures=lectures,
                                   form=form,
                                   user=user_login,
                                   lectures_count=lectures_count,
                                   message=message)
        else:
            return redirect('/lecture')

    return render_template('lecture.html',
                           lectures=lectures,
                           form=form,
                           user=user_login,
                           lectures_count=lectures_count,
                           message="")


@app.route('/profile', methods=['GET'])
def profile():
    pending_lectures = []
    user_list = []

    user_login = request.cookies['user']

    count_of_resources = resource_service.get_count_of_user_resources(user_login)
    count_of_lectures = lecture_service.get_count_of_user_lectures(user_login)
    user = user_service.get_user_by_login(user_login)

    if user.Role == 'admin':
        user_list = user_service.get_all_users()
    elif user.Role == 'moderator':
        pending_lectures = filter_pending_lectures(lecture_service.get_pure_lectures())

    user.Role = ' '.join(user.Role.split('_')).upper()

    return render_template('profile.html',
                           user=user_login,
                           count_of_resources=count_of_resources,
                           count_of_lectures=count_of_lectures,
                           user_role=user.Role,
                           pending_lectures=pending_lectures,
                           user_list=user_list)


@app.route('/lecture/edit', methods=['GET', 'POST'])
def edit_lecture_page():
    user_login = request.cookies['user']
    lecture_to_edit = request.cookies['lecture_header']

    form = LectureEditForm()

    form.Content.data = lecture_service.get_lecture_by_login_and_header(user_login, lecture_to_edit)[0].Content
    return render_template('lecture_update.html',
                           form=form,
                           header=lecture_to_edit,
                           user=user_login)


@app.route('/api/lecture', methods=['POST'])
def api_lecture():
    user_login = request.cookies['user']
    lecture_header = request.cookies['lecture_header']
    lecture_to_edit = lecture_service.get_lecture_by_login_and_header(user_login, lecture_header)[0]

    form = LectureEditForm(request.form)

    lecture = LectureDTO(
        header=lecture_to_edit.Header,
        content=form.Content.data,
        status=lecture_to_edit.Status,
        creation_date=lecture_to_edit.Creation_Date
    )

    message, status = lecture_service.edit_lecture(user_login, lecture_to_edit.Header, lecture)
    if status == 200:
        res = make_response("")
        res.set_cookie('lecture_header', '', max_age=0)
        res.headers['location'] = url_for('list_lectures')
        return res, 302
    else:
        return redirect('/lecture/edit')


@app.route('/lecture/delete', methods=['GET', 'POST'])
def delete_lecture():
    user_login = request.cookies['user']
    lecture_to_delete = request.cookies['lecture_header']
    lecture_service.delete_lecture(user_login, lecture_to_delete)
    res = make_response("")
    res.set_cookie('lecture_header', '', max_age=0)
    res.headers['location'] = url_for('list_lectures')
    return res, 302


@app.route('/new_lecture', methods=['GET', 'POST'])
def lecture_generator():
    form = GenerateLectureForm()
    user_login = request.cookies['user']
    return render_template('new_lecture.html',
                           form=form,
                           user=user_login)


@app.route('/make_lecture', methods=['POST'])
def make_lecture():
    form = GenerateLectureForm(request.form)
    if form.Header.data:
        return ping_ai_service(form.Header.data)
    else:
        return ""


@app.route('/resources', methods=['GET', 'POST'])
def list_resources():
    user_login = request.cookies['user']
    resources = resource_service.get_all_user_resources(user_login)
    resource_count = resource_service.get_count_of_user_resources(user_login)

    form = ResourceForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            return render_template('resource.html',
                                   resources=resources,
                                   form=form,
                                   user=user_login,
                                   resource_count=resource_count,
                                   message="Input data is not valid!")

        new_resource = ResourceDTO(
            url=form.URL.data,
            description=form.Description.data,
            times_visited=0,
            creation_date=datetime.date.today()
        )
        message, status = resource_service.add_resource(user_login, new_resource)

        if status != 200:
            return render_template('resource.html',
                                   resources=resources,
                                   form=form,
                                   user=user_login,
                                   resource_count=resource_count,
                                   message=message)
        else:
            return redirect('/resources')

    return render_template('resource.html',
                           resources=resources,
                           form=form,
                           user=user_login,
                           resource_count=resource_count,
                           message="")


@app.route('/resource/edit', methods=['GET'])
def edit_resource_page():
    url = request.cookies['resource_url']
    user_login = request.cookies['user']
    form = ResourceEditForm()

    form.Description.data = resource_service.get_all_resource_by_login_and_url(user_login, url)[0].Description

    return render_template('resource_update.html',
                           form=form,
                           resource_url=url,
                           user=user_login)


@app.route('/api/resource', methods=['POST'])
def update_resource():
    url = request.cookies['resource_url']
    user_login = request.cookies['user']
    resource_to_edit = resource_service.get_all_resource_by_login_and_url(user_login, url)[0]

    form = ResourceEditForm(request.form)

    resource = ResourceDTO(
        url=resource_to_edit.URL,
        description=form.Description.data,
        times_visited=resource_to_edit.TimesVisited,
        creation_date=resource_to_edit.Creation_Date
    )

    message, status = resource_service.edit_resource(user_login, resource.URL, resource)

    if status == 200:
        res = make_response("")
        res.set_cookie('resource_url', '', max_age=0)
        res.headers['location'] = url_for('list_resources')
        return res, 302
    else:
        return redirect('/resource/edit')


@app.route('/resource/delete', methods=['GET'])
def delete_resource():
    url = request.cookies['resource_url']
    user_login = request.cookies['user']
    resource_service.delete_resource(user_login, url)
    res = make_response("")
    res.set_cookie('resource_url', '', max_age=0)
    res.headers['location'] = url_for('list_resources')
    return res, 302


@app.route('/api/lecture/approve', methods=['GET'])
def approve_lecture():
    user_login = request.cookies['lecture_user']
    lecture_header = request.cookies['lecture_header']

    lecture_to_edit = lecture_service.get_lecture_by_login_and_header(user_login, lecture_header)[0]

    lecture_to_edit.Status = "Approved"

    message, status = lecture_service.edit_lecture(user_login, lecture_to_edit.Header, lecture_to_edit)

    if status == 200:
        res = make_response("")
        res.set_cookie('lecture_header', '', max_age=0)
        res.set_cookie('lecture_user', '', max_age=0)
        res.headers['location'] = url_for('profile')
        return res, 302
    else:
        return redirect('/profile')


@app.route('/api/lecture/decline', methods=['GET'])
def decline_lecture():
    user_login = request.cookies['lecture_user']
    lecture_header = request.cookies['lecture_header']

    lecture_to_edit = lecture_service.get_lecture_by_login_and_header(user_login, lecture_header)[0]

    lecture_to_edit.Status = "Declined"

    message, status = lecture_service.edit_lecture(user_login, lecture_to_edit.Header, lecture_to_edit)

    if status == 200:
        res = make_response("")
        res.set_cookie('lecture_header', '', max_age=0)
        res.set_cookie('lecture_user', '', max_age=0)
        res.headers['location'] = url_for('profile')
        return res, 302
    else:
        return redirect('/profile')
