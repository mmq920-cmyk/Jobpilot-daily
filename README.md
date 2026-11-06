# JobPilot — daily 70+ CV-fit jobs in Germany

A self-hosted job-search dashboard with a scheduled refresh **every day at 10:00 Europe/Berlin**. It runs when the browser is closed, once published using GitHub Actions and GitHub Pages.

## What it does

- Generates a new `jobs.json` file from public jobs feeds every morning at **10:00 Berlin time**, with daylight-saving changes handled by GitHub's timezone-aware schedule.
- Searches Germany only, with a rolling 14-day publication window and a rule-based CV match of **70/100 or higher**.
- Searches seven categories: Project Management, Operations, Business Analysis, Strategy & Consulting, Product Management, Programme Coordination, Marketing & Growth. Includes graduate, entry-level, junior and associate full-time roles and graduate-accessible internships; excludes detected mandatory German/other-language requirements, excessive seniority and unrelated jobs. It requires explicit English-language evidence.
- Publishes the dashboard and current jobs as a GitHub Pages site. The dashboard reads the newest `jobs.json` when loaded and when refreshed.
- Provides `Not Applied`, `Applied`, `In Progress`, and `Rejected` tracking, interview notes, application/follow-up dates, and CSV/JSON exports.

**Important accuracy caveat:** The public feeds' dates usually mark publication/indexing on the job board, which may not equal the employer's original posting date. Language/qualification matching is automated and can be wrong. Employer pages must still be checked before applying. If feeds are unavailable, the dashboard will show the error and may keep still-recent previously published items.

## Publishing for automatic updates (one-time setup)

1. On GitHub, create a **public** repository named e.g. `jobpilot-daily`. Do **not** upload your CV, applications, or sensitive personal information to it.
2. Unzip this package. Commit **all** the files, including the hidden `.github/workflows/update-and-deploy.yml` file, to that repository's `main` branch. The simplest option is GitHub Desktop or a Git terminal:

   ```bash
   cd jobpilot_daily_10am
   git init
   git add .
   git commit -m "Set up daily JobPilot dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/jobpilot-daily.git
   git push -u origin main
   ```

3. On GitHub, open the repository's **Settings → Pages → Build and deployment → Source**, and choose **GitHub Actions**.
4. Open the **Actions** tab, find **Update JobPilot at 10 AM Berlin**, choose **Run workflow** once to publish immediately. If necessary, approve GitHub Actions for this new repository in Settings → Actions.
5. After a successful deployment, open the site URL displayed in the workflow deployment or on the repository's Pages settings. It will usually follow this format: `https://YOUR_GITHUB_USERNAME.github.io/jobpilot-daily/`.

From then on, GitHub Actions will fetch and publish current matching jobs daily at **10:00 local Berlin time**, even if your computer is off. GitHub may start scheduled runs later than the configured minute due to service load. You can also run the workflow manually from the Actions tab or use the website's **Check latest update** button to read the latest published result.

## Application tracker / privacy

Your application statuses and notes are saved in **that browser's localStorage**, not in GitHub and not in the public site. They persist if you revisit the *same hosted URL in the same browser*, but they do **not** synchronize automatically between devices or with your original standalone HTML dashboard. Use **Export JSON** and **Import backup** to move data.

This is a personal tool and does not require a login, database or API key. As a public GitHub Pages site, the source and filtered job listings are visible to anyone who knows the site address. The repository must not contain private candidate documents. If you want private/synced status tracking, that requires an authenticated backend and changes to this project.

## Technical notes

- Scheduled publishing: `.github/workflows/update-and-deploy.yml` using `cron: '0 10 * * *'`, `timezone: Europe/Berlin`.
- Job filtering: `update_jobs.py` (Python standard library, no dependencies).
- Dashboard: `index.html`, a single-page browser app.
- Output: `jobs.json`, generated as part of every deployment; the repository's placeholder is replaced by the pipeline artifact.
- Sources: Arbeitnow public job API and (where accessible) workingstudentjobs.de English-internship API. Missing providers are reported rather than silently pretending to be comprehensive.
- Public APIs and their terms can change. If a provider stops working, inspect the warnings in the dashboard and the GitHub Actions logs.

## Troubleshooting

**Site says no scheduled scan:** Open GitHub → Actions → Update JobPilot at 10 AM Berlin → Run workflow. Ensure Settings → Pages source is GitHub Actions.

**Site shows zero jobs:** The current feeds might have no roles satisfying all of the strict filters. This is more accurate than filling with undated/unknown-language jobs.

**Daily update stopped:** Check repository Actions logs and GitHub schedule health. GitHub may disable scheduled workflows in public repos with prolonged inactivity. Running the workflow or making a commit can re-enable it.

**Old HTML tracker missing after switching to website:** Export a JSON backup from the old dashboard and import it into this one.
