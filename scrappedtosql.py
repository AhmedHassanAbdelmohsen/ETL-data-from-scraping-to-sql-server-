import pyodbc
import pandas as pd
from playwright.sync_api import sync_playwright
import time
from datetime import datetime, timedelta

# SQL Server Connection (Windows Authentication)
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-29DB4TN;"
    "DATABASE=scrapped_wuzzuf_project;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()


def scrape_wuzzuf():
    """Scrapes job listings from Wuzzuf.net and stores them in a list."""
    job_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://wuzzuf.net/search/jobs/?q=data%20&a=hpb", timeout=60000)

        for _ in range(10):  # Scrape first 10 pages
            jobs = page.query_selector_all("div.css-1gatmva.e1v1l3u10")

            for job in jobs:
                try:
                    title_elem = job.query_selector("h2 a")
                    company_elem = job.query_selector("div.css-d7j1kk a")
                    location_elem = job.query_selector("span.css-5wys0k")
                    date_elem = job.query_selector("div.css-4c4ojb")

                    job_title = title_elem.inner_text().strip() if title_elem else "N/A"
                    company = company_elem.inner_text().strip() if company_elem else "N/A"
                    location = location_elem.inner_text().strip() if location_elem else "N/A"
                    date_posted = date_elem.inner_text().strip() if date_elem else "N/A"

                    job_relative_url = title_elem.get_attribute("href") if title_elem else None
                    job_link = f"https://wuzzuf.net{job_relative_url}" if job_relative_url else "N/A"

                    posting_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Ensure valid datetime

                    # ✅ Convert 'X days ago' to actual date format
                    if "days ago" in date_posted:
                        days_ago = int(date_posted.split()[0])
                        date_posted = (datetime.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                    elif "Yesterday" in date_posted:
                        date_posted = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
                    else:
                        date_posted = datetime.today().strftime("%Y-%m-%d")  # Default to today

                    job_list.append([job_title, company, location, date_posted, job_link, posting_time])
                except Exception as e:
                    print(f"⚠️ Error processing job: {e}")

            # Click next page if available
            next_button = page.query_selector("a.css-zye1os.ezfki8j0")
            if next_button:
                next_button.click()
                page.wait_for_load_state("domcontentloaded")  # Wait for page load
            else:
                break

        browser.close()

    return job_list


def insert_into_sql(job_list):
    """Inserts scraped job listings into SQL Server table JobListings."""
    for job in job_list:
        try:
            cursor.execute("""
                INSERT INTO JobListings (JobTitle, Company, Location, DatePosted, JobLink, PostingTime)
                VALUES (?, ?, ?, ?, ?, ?)
            """, job)
        except pyodbc.DataError as e:
            print(f"⚠️ Data Error while inserting {job}: {e}")
        except pyodbc.Error as e:
            print(f"❌ SQL Error: {e}")

    conn.commit()
    print(f"✅ {len(job_list)} jobs inserted into SQL Server!")


# Run Scraper & Save Data to SQL
jobs = scrape_wuzzuf()
if jobs:
    insert_into_sql(jobs)
else:
    print("⚠️ No jobs found.")

# Close connection
cursor.close()
conn.close()
print("✅ Database connection closed.")
ec