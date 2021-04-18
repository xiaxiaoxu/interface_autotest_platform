from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import models


import os
import time
import traceback
from selenium import webdriver
import time



def get_element(driver,locator_method,locator_exp):
    element = driver.find_element( locator_method, locator_exp)
    return element

def open_browser(browser_name):
    
    if "ie" in browser_name.lower():
        driver  = webdriver.Ie(executable_path="e:\\IEDriverServer")
    elif "chrome" in browser_name.lower():
        driver  = webdriver.Chrome(executable_path="e:\\chromedriver")
    else:
        driver = webdriver.Firefox(executable_path="e:\\geckodriver")
    return driver

def visit(driver,url):
    
    driver.get(url)

def input(driver,locator_method,locator_exp,content):
    #global  driver
    element = get_element(driver,locator_method,locator_exp)
    element.send_keys(content)

def click(driver,locator_method,locator_exp):
    #global  driver
    element = get_element(driver,locator_method,locator_exp)
    element.click()

def sleep(driver,seconds):
    time.sleep(float(seconds))

def assert_word(driver,expected_word):
    #global  driver
    assert expected_word in driver.page_source

def switch_to(driver,locator_method,locator_exp):
    
    element = get_element(driver,locator_method,locator_exp)
    driver.switch_to.frame(element)

def switch_back(driver):
    
    driver.switch_to.default_content()

def quit(driver):
    
    driver.quit()

def take_pic(driver,file_path):
    print("***************",driver)
    try:
        '''
        调用get_screenshot_as_file(file_path)方法，对浏览器当前打开页面
        进行截图,并保为C盘下的screenPicture.png文件。
        '''
        result = driver.get_screenshot_as_file(file_path)
        print(result)
    except IOError as e:
        print(e)


'''
@shared_task
def add(x, y):
    return x + y
'''

@shared_task
def mul(x, y):
    return x * y


@shared_task
def web_test_task(execute_id,testcase_id):
    test_steps = models.CaseStep.objects.filter(test_case=testcase_id)
    execute_record = models.TestCaseExecuteRecord.objects.get(id=execute_id)
    execute_record.execute_start_time=time.strftime("%Y-%m-%d %H:%M:%S")
    execute_record.save()
    steps = []
    driver = ""
    for test_step in test_steps:
        temp = []
        print("---------",test_step.id,test_step.key_word,test_step.locator_method,
                           test_step.locator_exp,test_step.test_data)
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
        test_step_result=""
        test_step_exception_info=""
        test_step_capture_screen=""
        case_step_info=""
        command=""
        try:
            if key_word=="open_browser":
                driver = open_browser(value)
                print("启动浏览器%s成功" %value)
                test_step_result="成功"
                step_id=test_step[0]
                case_step_info = models.CaseStep.objects.get(id=step_id)
                models.TestCaseStepExecuteRecord.objects.create(
                test_case_execute_record=execute_record,case_step=case_step_info,result=test_step_result)
                continue
            if locator_method is None  and value is not None:
                command = '''%s(driver,"%s")''' %(key_word,value)
            elif locator_method is None  and value is None :
                command = '''%s(driver)''' %(key_word)
            elif locator_method is not None  and value is not  None:
                print("****************")
                command = '''%s(driver,"%s","%s","%s")'''  %(key_word,locator_method,locator_exp,value)
            elif locator_method is not None and value is None:
                print("----------------")
                command = '''%s(driver,"%s","%s")'''   %(key_word,locator_method,locator_exp)
                
            eval(command)
            #1/0
            print("执行测试步骤 %s 成功" %command)
            test_step_result="成功"
        except:
            print("执行测试步骤 %s 失败" %command)
            traceback.print_exc()
            execute_record.exception_info=traceback.format_exc()
            test_step_exception_info=traceback.format_exc()
            execute_record.result="失败"
            file_path = get_pic_path()[0]
            sava_path = get_pic_path()[1]
            take_pic(driver,file_path)
            execute_record.capture_screen = sava_path
            test_step_capture_screen=sava_path
            test_step_result="失败"
            execute_record.save()
            try:
                driver.quit()
            except:
                print("关闭浏览器失败")  
            
        print("Done!")
        #execute_record = models.ExecuteRecord.objects.get(execute_id=execute_id)
        step_id=test_step[0]
        case_step_info = models.CaseStep.objects.get(id=step_id)
        step_result=models.TestCaseStepExecuteRecord.objects.create(
        test_case_execute_record=execute_record,case_step=case_step_info,result=test_step_result,
        exception_info=test_step_exception_info,capture_screen=test_step_capture_screen)
        print("++++++++++++++",step_result)
        if test_step_result=="失败":
            break
    else:
        execute_record.result="成功"
        execute_record.save()        
    
    print("done!!!!")   
    execute_record.status=1
    execute_record.execute_end_time=time.strftime("%Y-%m-%d %H:%M:%S")   
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).split(".")[0])
    execute_record.save()
