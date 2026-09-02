from urllib.parse import urljoin
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from playwright.async_api import async_playwright

from .forms import CourseForm
from .models import Course, Enrollment, Lesson

# ==========================================
# 1. LMS CORE VIEWS
# ==========================================

def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all()
    is_enrolled = False
    
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        
    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "is_enrolled": is_enrolled
    })


@login_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect("courses:course_detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect("courses:course_detail", pk=pk)


@login_required
def dashboard(request):
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)
    return render(request, "courses/dashboard.html", {"courses": enrolled_courses})


# ==========================================
# 2. SCRAPER UTILITIES & API
# ==========================================

BASE_URL = "https://www.radioechoes.com"


async def safe_text(locator):
    try:
        if await locator.count() == 0:
            return "N/A"
        text = await locator.first.inner_text()
        return text.strip() if text else "N/A"
    except Exception:
        return "N/A"


async def safe_attribute(locator, attribute):
    try:
        if await locator.count() == 0:
            return "N/A"
        value = await locator.first.get_attribute(attribute)
        return value.strip() if value else "N/A"
    except Exception:
        return "N/A"


def radioechoes_scraper_api(request):
    target_url = request.GET.get(
        "url",
        "https://www.radioechoes.com/?page=series&genre=OTR&series_name=Suspense",
    )

    async def run_scraper():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(
                target_url, wait_until="networkidle", timeout=60000
            )

            series_name = await safe_text(page.locator("h1"))
            episodes = page.locator(
                "tr:has(a[href*='mp3']), tr:has(a[href*='play'])"
            )
            total = await episodes.count()

            scraped_data = []
            for i in range(total):
                ep = episodes.nth(i)
                title = await safe_text(ep.locator("td").nth(0))
                date = await safe_text(ep.locator("td").nth(1))
                play = await safe_attribute(
                    ep.locator("a[href*='play']"), "href"
                )
                download = await safe_attribute(
                    ep.locator("a[href*='.mp3']"), "href"
                )

                if download != "N/A":
                    download = urljoin(BASE_URL, download)
                if play != "N/A":
                    play = urljoin(BASE_URL, play)

                if title != "N/A":
                    scraped_data.append(
                        {
                            "Series Name": series_name,
                            "Episode Name": title,
                            "Original Broadcast Date": date,
                            "Download Link": download,
                            "Play Link": play,
                        }
                    )

            await browser.close()
            return scraped_data

    try:
        results = async_to_sync(run_scraper)()
        return JsonResponse(
            {
                "status": "success",
                "scraped_url": target_url,
                "total_episodes": len(results),
                "data": results,
            },
            safe=False,
        )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)}, status=500
        )
    import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .scraper import run_scraper_for_url

@csrf_exempt
def scraper_api_view(request):
    """
    API endpoint: URL parameter receive karta hai aur scraper ka result return karta hai.
    """
    target_url = request.GET.get('url')

    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            target_url = body.get('url', target_url)
        except Exception:
            target_url = request.POST.get('url', target_url)

    if not target_url:
        return JsonResponse({
            "status": "error",
            "message": "Query parameter 'url' is required. Example: /api/scraper/?url=https://example.com"
        }, status=400)

    # Scraper call
    data = run_scraper_for_url(target_url)
    return JsonResponse(data, safe=False)