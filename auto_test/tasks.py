from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import models
from .utils.api_request import api_request
from .utils.dataHandler import data_handler, assert_result
import os
import json
import traceback
import time
from dateutil.parser import parse

ip = "39.100.104.214"
port = "8000"



def web_test_task(execute_id, testcase_id):
    test_steps = models.CaseStep.objects.filter(test_case=testcase_id)
    execute_record = models.TestCaseExecuteRecord.objects.get(id=execute_id)
    execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    execute_record.save()
    steps = []
    driver = ""
    for test_step in test_steps:
        temp = []
        print("---------", test_step.id, test_step.key_word, test_step.locator_method,
              test_step.locator_exp, test_step.test_data)
        temp.append(test_step.id)
        temp.append(test_step.key_word)
        temp.append(test_step.locator_method)
        temp.append(test_step.locator_exp)
        temp.append(test_step.test_data)
        steps.append(temp)

    for test_step in steps:
        key_word = test_step[1].name
        locator_method = test_step[2]
        locator_exp = test_step[3]
        value = test_step[4]
        test_step_result = ""
        test_step_exception_info = ""
        test_step_capture_screen = ""
        case_step_info = ""
        command = ""
        try:
            if key_word == "open_browser":
                driver = open_browser(value)
                print("启动浏览器%s成功" % value)
                test_step_result = "成功"
                step_id = test_step[0]
                case_step_info = models.CaseStep.objects.get(id=step_id)
                models.TestCaseStepExecuteRecord.objects.create(
                    test_case_execute_record=execute_record, case_step=case_step_info, result=test_step_result)
                continue
            if locator_method is None and value is not None:
                command = '''%s(driver,"%s")''' % (key_word, value)
            elif locator_method is None and value is None:
                command = '''%s(driver)''' % (key_word)
            elif locator_method is not None and value is not None:
                print("****************")
                command = '''%s(driver,"%s","%s","%s")''' % (key_word, locator_method, locator_exp, value)
            elif locator_method is not None and value is None:
                print("----------------")
                command = '''%s(driver,"%s","%s")''' % (key_word, locator_method, locator_exp)

            eval(command)
            # 1/0
            print("执行测试步骤 %s 成功" % command)
            test_step_result = "成功"
        except:
            print("执行测试步骤 %s 失败" % command)
            traceback.print_exc()
            execute_record.exception_info = traceback.format_exc()
            test_step_exception_info = traceback.format_exc()
            execute_record.result = "失败"
            file_path = get_pic_path()[0]
            sava_path = get_pic_path()[1]
            take_pic(driver, file_path)
            execute_record.capture_screen = sava_path
            test_step_capture_screen = sava_path
            test_step_result = "失败"
            execute_record.save()
            try:
                driver.quit()
            except:
                print("关闭浏览器失败")

        print("Done!")
        # execute_record = models.ExecuteRecord.objects.get(execute_id=execute_id)
        step_id = test_step[0]
        case_step_info = models.CaseStep.objects.get(id=step_id)
        step_result = models.TestCaseStepExecuteRecord.objects.create(
            test_case_execute_record=execute_record, case_step=case_step_info, result=test_step_result,
            exception_info=test_step_exception_info, capture_screen=test_step_capture_screen)
        print("++++++++++++++", step_result)
        if test_step_result == "失败":
            break
    else:
        execute_record.result = "成功"
        execute_record.save()

    print("done!!!!")
    execute_record.status = 1
    execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S:%M")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).split(".")[0])
    execute_record.save()

@shared_task
def interface_test_task(test_case_id_list, server_address):
    os.environ['global_vars'] = '{}'
    for test_case_id in test_case_id_list:
        test_case = models.TestCase.objects.filter(id=int(test_case_id))[0]
        print("######执行用例: {}".format(test_case))
        execute_record = models.TestCaseExecuteRecord.objects.create(belong_test_case=test_case)

        execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
        print("execute_start_time: {}".format(execute_start_time))
        execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_start_time))
        print("execute_record.execute_start_time: {}".format(execute_record.execute_start_time))
        execute_record.save()
        '''
        interface_name = models.CharField('接口名称', max_length=50, null=False)  # register
        belong_project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目')
        belong_module = GroupedForeignKey(Module, "belong_project", on_delete=models.CASCADE, verbose_name='所属模块')
        request_data = models.CharField('请求数据', max_length=1024, null=False)
        assert_key = models.CharField('断言内容', max_length=1024, null=True)
        maintainer = models.CharField('编写人员', max_length=1024, null=False)
        extract_var = models.CharField('提取变量表达式', max_length=1024, null=True)  # userid||userid": (\d+)
        if_execute = models.CharField('是否执行', max_length=1024, null=False)
        status = models.IntegerField(null=True, help_text="0：表示有效，1：表示无效，用于软删除")
        created_time = models.DateTimeField('创建时间', auto_now_add=True)
        updated_time = models.DateTimeField('更新时间', auto_now=True, null=True)
        user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户', null=True)
    
        '''
        request_data = test_case.request_data
        extract_var = test_case.extract_var
        assert_key = test_case.assert_key
        interface_name = test_case.uri
        belong_project = test_case.belong_project
        belong_module = test_case.belong_module
        maintainer = test_case.maintainer
        request_method = test_case.request_method
        print("request_data: {}".format(test_case.request_data))
        print("extract_var: {}".format(extract_var))
        print("assert_key: {}".format(assert_key))
        print("interface_name: {}".format(interface_name))
        print("belong_project: {}".format(belong_project))
        print("belong_module: {}".format(belong_module))
        print("maintainer: {}".format(maintainer))
        print("request_method: {}".format(request_method))
        url = "{}/{}".format(server_address, interface_name)
        print("url: {}".format(url))
        code, request_data, error_msg = data_handler(str(request_data))
        print("request_data: {}".format(request_data))
        if code != 0:
            print("数据处理异常，error: {}".format(error_msg))
            execute_record.execute_result = "失败"
            execute_record.status = 1
            execute_record.exception_info = error_msg
            execute_end_time = time.time()
            execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
            execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
            execute_record.save()
        execute_record.request_data = request_data
        try:
            res_data = api_request(url, request_method, json.loads(request_data))
            print("res_data.json(): {}".format(res_data.json()))
            if assert_result(res_data, assert_key):
            # if res_data.json().get("code", "") == "00":
                print("用例执行成功")
                execute_record.execute_result = "成功"
                execute_record.response_data = res_data.json()
                execute_record.status = 1
                execute_end_time = time.time()
                print("execute_end_time: {}".format(execute_end_time))
                execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
                print("int((execute_end_time - execute_start_time) * 1000): {}".format(int((execute_end_time - execute_start_time) * 1000)))
                execute_record.execute_total_time = int((execute_end_time - execute_start_time) * 1000)
                print("execute_record.execute_total_time.microseconds: {}".format(execute_record.execute_total_time))
                execute_record.save()
            else:
                print("用例执行失败")
                execute_record.execute_result = "失败"
                execute_record.response_data = res_data.json()
                execute_record.status = 1
                execute_end_time = time.time()
                execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
                execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
                print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
                execute_record.save()
        except Exception as e:
            print("接口请求异常，error: {}".format(e))
            execute_record.execute_result = "失败"
            execute_record.exception_info = e
            execute_record.status = 1
            execute_end_time = time.time()
            execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
            execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
            execute_record.save()


@shared_task
def web_suit_task(test_suit_record, test_suit):
    os.environ['global_vars'] = '{}'
    server_address = "http://39.100.104.214:8000"
    test_suit_test_cases = models.TestSuitTestCases.objects.filter(test_suit=test_suit).order_by('id')
    print("test_suit_test_cases: {}".format(test_suit_test_cases))
    test_suit_record.test_result = "成功"
    test_suit_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    for test_suit_test_case in test_suit_test_cases:
        test_case = test_suit_test_case.test_case
        print("######执行用例: {}".format(test_case))
        suite_case_execute_record = models.TestSuitTestCaseExecuteRecord.objects.create(test_suit_record=test_suit_record,
                                                                             test_case=test_case)
        execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
        print("execute_start_time: {}".format(execute_start_time))
        suite_case_execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_start_time))
        print("suite_case_execute_record.execute_start_time: {}".format(suite_case_execute_record.execute_start_time))
        suite_case_execute_record.save()
        request_data = test_case.request_data
        extract_var = test_case.extract_var
        assert_key = test_case.assert_key
        interface_name = test_case.uri
        belong_project = test_case.belong_project
        belong_module = test_case.belong_module
        maintainer = test_case.maintainer
        request_method = test_case.request_method
        print("request_data: {}".format(test_case.request_data))
        print("extract_var: {}".format(extract_var))
        print("assert_key: {}".format(assert_key))
        print("interface_name: {}".format(interface_name))
        print("belong_project: {}".format(belong_project))
        print("belong_module: {}".format(belong_module))
        print("maintainer: {}".format(maintainer))
        print("request_method: {}".format(request_method))
        url = "{}/{}".format(server_address, interface_name)
        print("url: {}".format(url))
        code, request_data, error_msg = data_handler(str(request_data))
        print("request_data: {}".format(request_data))
        if code != 0:
            print("数据处理异常，error: {}".format(error_msg))
            suite_case_execute_record.execute_result = "失败"
            suite_case_execute_record.status = 1
            suite_case_execute_record.exception_info = error_msg
            execute_end_time = time.time()
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
            test_suit_record.test_result = "失败"

        suite_case_execute_record.request_data = request_data
        try:
            res_data = api_request(url, request_method, json.loads(request_data))
            print("res_data.json(): {}".format(res_data.json()))
            if assert_result(res_data, assert_key):
                # if res_data.json().get("code", "") == "00":
                print("用例执行成功")
                suite_case_execute_record.execute_result = "成功"
                suite_case_execute_record.response_data = res_data.json()
                suite_case_execute_record.status = 1
                execute_end_time = time.time()
                print("execute_end_time: {}".format(execute_end_time))
                suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
                print("int((execute_end_time - execute_start_time) * 1000): {}".format(
                    int((execute_end_time - execute_start_time) * 1000)))
                suite_case_execute_record.execute_total_time = int((execute_end_time - execute_start_time) * 1000)
                print("suite_case_execute_record.execute_total_time.microseconds: {}".format(suite_case_execute_record.execute_total_time))
                suite_case_execute_record.save()

            else:
                print("用例执行失败")
                suite_case_execute_record.execute_result = "失败"
                suite_case_execute_record.response_data = res_data.json()
                suite_case_execute_record.status = 1
                execute_end_time = time.time()
                suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
                suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
                print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
                suite_case_execute_record.save()
                test_suit_record.test_result = "失败"
        except Exception as e:
            print("接口请求异常，error: {}".format(e))
            suite_case_execute_record.execute_result = "失败"
            suite_case_execute_record.exception_info = e
            suite_case_execute_record.status = 1
            execute_end_time = time.time()
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
            test_suit_record.test_result = "失败"

    test_suit_record.status = 1  # 执行完了
    test_suit_record.save()