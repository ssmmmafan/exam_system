from playwright.sync_api import sync_playwright


def test_teacher_exam_management():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        try:
            page.goto("http://localhost:5173/login", timeout=30000)
            page.wait_for_selector("#username", timeout=10000)
            page.fill("#username", "测试老师")
            page.fill("#password", "123456")
            page.get_by_role("button", name="教师").click()
            page.click(".login-btn")
            page.wait_for_url("**/teacher/dashboard**", timeout=30000)

            page.goto("http://localhost:5173/teacher/exams", timeout=30000)
            page.wait_for_selector("h1", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=15000)

            page.screenshot(path="teacher_exam_management.png", full_page=True)
            print(f"考试管理页截图已保存: teacher_exam_management.png")
            print(f"当前URL: {page.url}")
        except Exception as e:
            page.screenshot(path="teacher_exam_management_error.png", full_page=True)
            print(f"测试失败: {e}")
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    test_teacher_exam_management()
