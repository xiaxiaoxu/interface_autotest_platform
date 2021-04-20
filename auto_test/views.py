from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from . import models
import traceback
from django.contrib import  auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from . import tasks

# Create your views here.


def get_paginator(request, data):
    paginator = Paginator(data, 10)
    paginator_pages = ""

    # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
    page = request.GET.get('page')
    try:
        paginator_pages = paginator.page(page)
    # todo: 注意捕获异常
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        paginator_pages = paginator.page(1)
    except InvalidPage:
        # 如果请求的页数不存在, 重定向页面
        return HttpResponse('找不到页面的内容')
    except EmptyPage:
        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
        paginator_pages = paginator.page(paginator.num_pages)
    print("----------------", paginator_pages)
    return paginator_pages

def index(request):
    pass
    return render(request, 'auto_test/index.html')


def login(request):
    if request.session.get('is_login',None):
        return redirect('/project')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    print("**********"*10,)
                    auth.login( request,user)
                    request.session['is_login']=True
                    return redirect('/project/')
                else:
                    message = "用户名不能存在或者密码不正确！"
            except:
                message = "登录程序出现错误"
                traceback.print_exc()

        return render(request, 'auto_test/login.html', locals())

    login_form = UserForm()
    return render(request, 'auto_test/login.html', locals())

@login_required
def project(request):
    print("login success!",request.user.is_authenticated)
    projects = models.Project.objects.filter().order_by('-id')
    print("projects:",projects)
    return render(request, 'auto_test/project.html', {'projects': get_paginator(request,projects) })


@login_required
def module(request):
    modules = ""
    if request.method == "GET":  # 请求get时候，id倒序查询所有的模块数据
        modules = models.Module.objects.filter().order_by('-id')
    else:  # 否则就是Post请求，会根据输入内容，使用模糊的方式查找所有的项目
        proj_name = request.POST['proj']
        projs = models.Project.objects.filter(name__contains=proj_name.strip())
        projs = [proj.id for proj in projs]
        modules = models.Module.objects.filter(belong_project__in=projs)  # 把项目中所有的模块都找出来
    return render(request, 'auto_test/module.html', {'modules': get_paginator(request, modules)})


@login_required
def testcase(request):
    testcases=""
    if request.method == "GET":
        testcases = models.TestCase.objects.filter().order_by('id')
        print("testcases in testcase: {}".format(testcases))
    elif request.method=="POST":
        testcases_list = request.POST.getlist('testcases_list')
        if testcases_list:
            print("testcases_list: {}".format(testcases_list))
            for testcase in testcases_list:
                test_case = models.TestCase.objects.filter(id=int(testcase))
                print("test_case: {}".format(test_case))
                print("test_case[0]: {}".format(test_case[0]))
                test_case_execute_record=models.TestCaseExecuteRecord.objects.create(test_case=test_case[0],status=0)
                tasks.interface_test_task(test_case[0])
                # task_id=tasks.web_test_task.apply_async((test_case_execute_record.id,test_case[0]),countdown=0)
                task_id=tasks.interface_test_task((test_case_execute_record.id, test_case[0]))
        else:
            print("运行测试用例失败")
            return HttpResponse("提交的运行测试用例为空，请选择用例后在提交！")
        testcases = models.TestCase.objects.filter().order_by('-id')
    return render(request, 'auto_test/testcase.html', {'testcases': get_paginator(request,testcases) })


@login_required
def module_testcases(request,module_id):
    testcases=""
    module=""
    if module_id:#访问的时候，会从url中提取模块的id，根据模块id查询到模块数据，在模板中展现
        module = models.Module.objects.get(id=int(module_id))
    if request.method=="POST":#如果是post方法，收到所有的测试用例id，提交给测试用例执行表
        testcases_list = request.POST.getlist('testcases_list')
        if testcases_list:
            for testcase in testcases_list:
                test_case = models.TestCase.objects.get(id=int(testcase))
                #把选中的用例添加到测试用例执行表中，用celery去执行
                execute_record=models.TestCaseExecuteRecord.objects.create(test_case=test_case,status=0)
                # task_id=tasks.web_test_task.apply_async((execute_record.id,test_case),countdown=0)
        else:
            print("运行测试用例失败")
            return HttpResponse("提交的运行测试用例为空，请选择用例后在提交！")
    testcases = models.TestCase.objects.filter(belong_module=module).order_by('-id')
    print("testcases in module_testcases: {}".format(module_testcases))
    return render(request, 'auto_test/testcase.html', {'testcases': get_paginator(request,testcases) })

@login_required
def test_case_detail(request,testcase_id):
    testcase_id=int(testcase_id)
    test_case =  models.TestCase.objects.get(id=testcase_id)
    print("test_case: {}".format(test_case))
    print("test_case.id: {}".format(test_case.id))
    print("test_case.belong_project: {}".format(test_case.belong_project))
    print("test_case: {}".format(test_case))
    #print("**********",test_case)
    # teststeps = models.CaseStep.objects.filter(test_case = test_case).order_by('id')
    #print("**********",teststeps)

    return render(request, 'auto_test/testCaseDetail.html', {'testcase': test_case})



def register(request):
    pass
    return render(request, 'auto_test/register.html')


def logout(request):
    pass
    return redirect('/index/')


@login_required
def testsuit(request):
    if request.method == "POST":
        count_down_time = 0
        if request.POST['delay_time']:
            try:
                count_down_time = int(request.POST['delay_time'])
            except:
                print("输入的延迟时间是非数字！")
        else:
            print("没有输入延迟时间")
        testsuits = request.POST.getlist('testsuits_list')
        if testsuits:
            print("------********", testsuits)
            for testsuit in testsuits:
                test_suit = models.TestSuit.objects.get(id=int(testsuit))
                username = request.user.username
                test_suit_record = models.TestSuitExecuteRecord.objects.create(test_suit=test_suit,
                                                                               run_time_interval=count_down_time,
                                                                               creator=username)
                # task_id = tasks.web_suit_task.apply_async((test_suit_record.id, int(testsuit)),
                #                                           countdown=count_down_time)
                # web_suit_task
        else:
            print("运行测试集合用例失败")
            return HttpResponse("运行的测试集合为空，请选择测试集合后再运行！")
    testsuits = models.TestSuit.objects.filter()
    return render(request, 'auto_test/testsuit.html', {'testsuits': get_paginator(request, testsuits)})


@login_required
def testrecord(request):
    testrecords = models.TestCaseExecuteRecord.objects.filter().order_by('-id')
    return render(request, 'auto_test/testrecord.html', {'testrecords': get_paginator(request,testrecords) })

@login_required
def show_test_suit_record(request):
    test_suit_records = models.TestSuitExecuteRecord.objects.filter().order_by('-id')
    return render(request, 'auto_test/testsuitrecord.html', {'test_suit_records': get_paginator(request,test_suit_records)})

@login_required
def show_testsuit_cases(request,suit_id):
    test_suit = models.TestSuit.objects.get(id=suit_id)
    testcases = models.TestSuitTestCases.objects.filter(test_suit=test_suit)
    if request.method=="POST":
        testcases_list = request.POST.getlist('testcases_list')
        if testcases_list:
            print("------********",testcases_list)
            for testcase in testcases_list:
                test_case = models.TestCase.objects.get(id=int(testcase))
                models.TestSuitTestCases.objects.filter(test_suit=test_suit,test_case=test_case).first().delete()
        else:
            print("删除测试集合的测试用例失败")
            return HttpResponse("删除的运行测试用例为空，请选择用例后再进行删除！")
    test_suit = models.TestSuit.objects.get(id=suit_id)
    testcases = models.TestSuitTestCases.objects.filter(test_suit=test_suit)
    return render(request, 'auto_test/suitcases.html', {'testcases': get_paginator(request,testcases),'test_suit':test_suit})

@login_required
def managesuit(request,suit_id):
    test_suit = models.TestSuit.objects.get(id=suit_id)
    if request.method == "GET":
        testcases = models.TestCase.objects.filter().order_by('-id')
        print("testcases:",testcases)
    elif request.method=="POST":
        testcases_list = request.POST.getlist('testcases_list')
        if testcases_list:
            print("------********",testcases_list)
            for testcase in testcases_list:
                test_case = models.TestCase.objects.get(id=int(testcase));
                suitcase=models.TestSuitTestCases.objects.create(test_suit=test_suit,test_case=test_case)
        else:
            print("添加测试用例失败")
            return HttpResponse("添加的运行测试用例为空，请选择用例后再添加！")
        testcases = models.TestCase.objects.filter().order_by('-id')
    return render(request, 'auto_test/managesuit.html', {'testcases': get_paginator(request,testcases),'test_suit':test_suit })
