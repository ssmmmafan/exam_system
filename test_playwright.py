from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        # 启动浏览器（headless=False 显示窗口）
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 导航到登录页
            print("正在访问登录页面...")
            page.goto("http://localhost:5173/login", timeout=30000)
            
            # 等待页面加载
            page.wait_for_selector("#username", timeout=10000)
            print("页面加载成功")
            
            # 输入用户名和密码
            print("正在输入账号信息...")
            page.fill("#username", "测试老师")
            page.fill("#password", "123456")
            
            # 选择教师角色并点击登录
            page.click(".role-btn:last-child")
            page.click(".login-btn")
            
            # 等待跳转
            page.wait_for_load_state("networkidle", timeout=30000)
            print(f"当前URL: {page.url}")
            
            # 截图保存
            page.screenshot(path="test_result.png")
            print("测试完成，截图已保存")
            
        except Exception as e:
            print(f"测试出错: {e}")
            page.screenshot(path="error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    test_login()
