Imports Required Libraries – Uses pyodbc for database connection, pandas for data handling, and playwright for web scraping.

Establishes SQL Server Connection – Connects to a local SQL Server database (scrapped_wuzzuf_project) using Windows Authentication.

Scrapes Wuzzuf Jobs – Navigates Wuzzuf.net, extracts job details, and processes posting dates into standard formats.

Handles Pagination – Iterates through multiple pages (up to 10) to collect job data efficiently.

Processes Data – Cleans and structures job data into a list, handling missing values and errors.

Inserts Data into SQL – Saves job listings into the JobListings table while managing potential SQL errors.

Final Execution – Runs the scraper, inserts data into SQL, and closes the database connection.








