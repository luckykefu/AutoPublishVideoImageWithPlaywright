import asyncio
import json
import os
import random
from playwright.async_api import Playwright, async_playwright, expect
from dotenv import load_dotenv
import re

load_dotenv()

async def init_browser(playwright): 
    print('init browser')
    browser = await playwright.chromium.launch_persistent_context(# 打开浏览器
    user_data_dir=None,# 浏览器数据保存路径
    executable_path=os.getenv('CHROME_BIN'),# 指定浏览器路径
    accept_downloads=True,# 接受下载
    headless=False,# 无头模式
    bypass_csp=True,# 绕过CSP
    slow_mo=10,# 慢速模式
    args=['--disable-blink-features=AutomationControlled'] #跳过检测
    )
    browser.set_default_timeout(60*1000)
    return browser

async def load_cookies(cookie_file, browser):
    print('load cookies')
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
        await browser.add_cookies(cookies)
       
async def save_cookies(cookie_file, page):
    print('save cookies')
    cookies = await page.context.cookies()
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f)

async def bjh(**kwargs):
    async with async_playwright() as p:
        browser=await init_browser(p)

        cookies = os.getenv('COOKIES_BJH')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://baijiahao.baidu.com/'
        await page.goto(url)
        await page.wait_for_load_state('load')
        
        is_login2=await page.locator(".author").is_visible()
        print("""是否登录创作服务平台:""",is_login2)
        if not is_login2:
            print('未登录创作服务平台, 开始登录')
            try:
                # await page.locator("div.btnlogin--bI826").click()
                await page.get_by_text("注册/登录百家号").click()
                await page.locator('.author').wait_for()
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录创作服务平台成功')
        await save_cookies(cookies, page)
        await page.wait_for_load_state('load')
        
        # go to publish page
        await page.locator("div.nav-switch-btn").first.click()
        await page.get_by_role("button",  name= "发布" ).hover()
        await page.locator("li.edit-video").click()
        await page.wait_for_load_state("load")
        print('发布页面打开成功')
        
        video= kwargs.get('file_path')
        print("视频地址:",video)
        await page.locator('section.video-wrap input').set_input_files(video)
        await page.locator(".control-bar-play").wait_for()
        print('上传视频成功')
        
        title= kwargs.get('title')
        await page.get_by_placeholder("请输入标题").clear()
        await page.get_by_placeholder("请输入标题").fill(title)
        print('填写标题成功')
        

        # tags
        tag=kwargs.get('tags')
        tag=tag.replace('#','')
        await page.locator('div.form-inner-wrap input').last.fill(tag)
        page.keyboard.press("Enter")
        print('填写标签成功')
        
        # 描述
        description=kwargs.get('description')
        await page.locator("textarea").last.fill(description+title)
        print('填写描述成功')
        
        # 发布
        await page.locator(".cover").first.wait_for()
        await page.pause()

        await page.get_by_role("button").first.click()
        print('发布成功')
            



async def sph(**kwargs):
    async with async_playwright() as p:
        browser=await init_browser(p)

        cookies = os.getenv('COOKIES_SPH')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://channels.weixin.qq.com/platform/post/create'
        await page.goto(url)
        await page.wait_for_load_state('load')

        await page.wait_for_timeout(3000)
        is_login2=await page.locator("img.avatar").is_visible()
        if not is_login2:
            print('未登录微信, 开始登录')
            try:
                await page.wait_for_selector('img.avatar')
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录微信成功')
        await save_cookies(cookies, page)
        
        await page.wait_for_load_state('load')

        video=kwargs.get('file_path')
        print("视频地址:",video)
        await page.locator('input[type="file"]').set_input_files(video)
        await page.get_by_text("删除").first.wait_for(timeout=120*1000)
        print('上传视频成功')

        description=kwargs.get('description')
        tag=kwargs.get('tags')
        await page.locator(".input-editor").fill(description+'\n'+tag)
        print('填写描述成功')

        title = kwargs.get('title')
        await page.locator("div.post-short-title-wrap  input[type='text']").fill(title)
        print('填写标题成功')



        # 发布
        await page.wait_for_timeout(3000)
        await page.pause()

        await page.get_by_role("button", name="发表").click()
        print('发布成功')

async def wb(**kwargs):
    async with async_playwright() as p:
        browser=await init_browser(p)

        cookies = os.getenv('COOKIES_WB')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://weibo.com/upload/channel'
        await page.goto(url)
        await page.wait_for_load_state('load')

        await page.wait_for_timeout(3000)
        is_login2=await page.get_by_role("button", name="立即 登录").is_visible()
        if is_login2:
            print('未登录微博, 开始登录')
            try:
                await page.get_by_role("button", name="立即 登录").click()
                await page.get_by_role("button", name="上传视频").wait_for()
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录微博成功')
        await save_cookies(cookies, page)
        
        video=kwargs.get('file_path')
        print("视频地址:",video)
        page.once("filechooser", lambda file_chooser: file_chooser.set_files(video))
        await page.get_by_role("button", name="上传视频").click()
        await page.get_by_text("上传完成").first.wait_for(timeout=120*1000)
        print('上传视频成功')

        await page.get_by_text("原创").click()
        print('选择原创成功')

        title=kwargs.get('title')
        await page.locator("input[type='text']").first.fill(title)
        print('填写标题成功')

        description=kwargs.get('description')
        tag=kwargs.get('tags')
        await page.locator("textarea").first.fill(description+'\n'+tag)
        print('填写描述成功')

        # 发布
        await page.pause()

        await page.wait_for_timeout(3000)
        await page.get_by_role("button", name="发布").click()
        print('发布成功')
            


async def dy(**kwargs):
    async with async_playwright() as p:
        browser=await init_browser(p)

        cookies = os.getenv('COOKIES_DY')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://creator.douyin.com'
        await page.goto(url)
        await page.wait_for_load_state('load')

        is_login2=await page.locator("span.login").is_visible()
        print("""未登录创作服务平台:""",is_login2)
        if is_login2:
            print('未登录创作服务平台, 开始登录')
            try:
                await page.locator('span.login').click()
                await page.get_by_role("tab", name="手机号登录").click()
                await page.get_by_placeholder("请输入手机号").fill(os.getenv('PHONE'))
                await page.get_by_label("手机号登录").locator("img").click()
                await page.get_by_text("发送验证码").click()
                await page.wait_for_selector('#douyin-creator-master-side-upload')
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录创作服务平台成功')
        await save_cookies(cookies, page)
        
        await page.get_by_text("发布视频").click()
        await page.wait_for_load_state('load')
        
        video = kwargs.get('file_path')
        print("视频地址:",video)
        await page.locator('label input').set_input_files(video)
        await page.get_by_text("重新上传").wait_for()
        print('上传视频成功')
        
        title= kwargs.get('title')
        await page.locator("div.editor-kit-editor-container input").fill(title)
        print('填写标题成功')
        
        # 描述
        description=kwargs.get('description')
        tag=kwargs.get('tags')
        await page.locator(".zone-container").fill(description+'\n'+tag)
        print('填写描述成功')
        
        # 同步其他平台
        await page.get_by_role("switch").click()
        print('同步其他平台成功')
        
        # 发布
        await page.wait_for_timeout(3000)
        await page.pause()

        await page.get_by_role("button", name="发布", exact=True).click()
        print('发布成功')
            


async def blbl(**kwargs):
     async with async_playwright() as p:
        browser=await init_browser(p)
        cookies = os.getenv('COOKIES_BLBL')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://www.bilibili.com/'
        await page.goto(url)
        await page.wait_for_load_state('load')


        is_login2=await page.get_by_text("登录", exact=True).is_visible()
        print("""未登录创作服务平台:""",is_login2)
        if is_login2:
            print('未登录创作服务平台, 开始登录')
            try:
                await page.get_by_text("登录", exact=True).click()
                await page.get_by_text("短信登录").click()
                await page.get_by_placeholder("请输入手机号").fill(os.getenv('PHONE'))
                await page.get_by_text("获取验证码").click()
                await page.wait_for_selector('li.header-avatar-wrap picture img')
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录创作服务平台成功')
        await save_cookies(cookies, page)

        await page.wait_for_load_state('load')
        
        # t投稿
        async with page.expect_popup() as p1_info:
            await page.get_by_role("link", name="投稿", exact=True).click()
        page1 = await p1_info.value
        await page1.wait_for_load_state('load')
        print('投稿页面打开成功')
        
        video = kwargs.get('file_path')
        print("视频地址:",video)
        await page1.locator('div.upload-wrp input').set_input_files(video)
        if await page1.get_by_text("知道了", exact=True).is_visible():
            await page1.get_by_text("知道了", exact=True).click()
        await page1.get_by_text("上传完成", exact=True).wait_for()
        print('上传视频成功')
        
        title= kwargs.get('title')
        await page1.locator('input.input-val').first.clear()
        await page1.locator('input.input-val').first.fill(title)
        print('填写标题成功')
        
        # tags
        tags=kwargs.get('tags')
        tags=tags.replace('#','')
        await page1.locator('div.tag-input-wrp input.input-val').first.fill(tags)
        await page1.keyboard.press("Enter")
        print('填写标签成功')
        
        # 描述
        description=kwargs.get('description')
        await page1.locator(".ql-editor > p").first.fill(description)
        print('填写描述成功')
        
        # 发布
        await page1.wait_for_timeout(3000)
        await page1.pause()
        await page1.get_by_text("立即投稿").click()
        print('发布成功')
            
        

async def ks(**kwargs):
    async with async_playwright() as p:
        browser=await init_browser(p)

        cookies = os.getenv('COOKIES_KS')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://cp.kuaishou.com/article/publish/video'
        await page.goto(url)
        await page.wait_for_load_state('load')

        await page.wait_for_timeout(3000)
        is_login2=await page.locator("a.login").is_visible()
        print("""未登录创作服务平台:""",is_login2)
        if is_login2:
            print('未登录创作服务平台, 开始登录')
            try:
                await page.locator('a.login').click()
                await page.get_by_text("验证码登录").click()
                await page.get_by_placeholder("请输入手机号").fill(os.getenv('PHONE'))
                await page.locator("div").filter(has_text=re.compile(r"^获取验证码$")).click()

                await page.wait_for_selector('div.publish-button')
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录创作服务平台成功')
        await save_cookies(cookies, page)
        
        video=kwargs.get('file_path')
        print("视频地址:",video)
        page.once("filechooser", lambda file_chooser: file_chooser.set_files(video))
        # await page.locator('div.drag-over input').set_input_files(video)
        await page.get_by_role("button", name="上传视频").click()
        await page.get_by_text("上传成功").wait_for()
        print('上传视频成功')
        
        title= kwargs.get('title')
        description=kwargs.get('description')
        tag=kwargs.get('tags')
        await page.locator("div").filter(has_text=re.compile(r"^0/500$")).locator("div").fill(title+'\n'+description+'\n'+tag)
        print('填写标题成功')
        
        # # 发布
        await page.pause()
        await page.wait_for_timeout(3000)
        await page.get_by_role("button", name="发布").click()
        print('发布成功')
            
        


async def xhs(**kwargs):
    async with async_playwright() as p:
        browser=await init_browser(p)

        cookies = os.getenv('COOKIES_XHS')
        if os.path.exists(cookies):
            await load_cookies(cookies, browser)
            
        page=await browser.new_page()

        url='https://creator.xiaohongshu.com/'
        await page.goto(url)
        await page.wait_for_load_state('load')
        
        await page.wait_for_timeout(3000)
        is_login2=await page.locator("a.btn").is_visible()
        print("未登录创作服务平台:",is_login2)
        if not is_login2:
            print('未登录创作服务平台, 开始登录')
            try:
                await page.get_by_placeholder("手机号").fill(os.getenv('PHONE'))
                await page.get_by_text("发送验证码").click()

                await page.wait_for_selector('a.btn')
            except Exception as e:
                print(e)
                return
            
        await page.wait_for_load_state('load')
        print('登录创作服务平台成功')
        await save_cookies(cookies, page)
        
        await page.locator('a.btn').click()
        
        await page.wait_for_load_state('load')
        video=kwargs.get('file_path')
        print("视频地址:",video)
        await page.locator('div.drag-over input').set_input_files(video)
        await page.get_by_role("button", name="详情").wait_for(timeout=180*1000)
        print('上传视频成功')
        
        title= kwargs.get('title')
        await page.locator('div.titleInput input').first.fill(title)
        print('填写标题成功')
        
        # 描述
        # description=os.getenv('TITLE')
        description=kwargs.get('description')
        tag=kwargs.get('tags')
        await page.locator('#post-textarea').fill(description+'\n'+tag)
        print('填写描述成功')
        
        # 发布
        await page.wait_for_timeout(3000)
        await page.pause()
        await page.get_by_role("button", name="发布").click()
        print('发布成功')
            
        



# if __name__ == '__main__':
