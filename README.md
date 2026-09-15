# GIU CMS Downloader

Automatically downloads new course files from the GIU CMS and organizes them into folders you choose.

## Setup

### 1. Download

Go to the [Releases page](https://github.com/MohabHindawy/giu-cms-downloader/releases), download the latest `.zip`, and extract it somewhere permanent, for example `C:\GIU-Downloader`. Don't run it from inside your Downloads folder or a temporary location.

### 2. Run the setup wizard

Run `setup-wizard.exe`.

The wizard will walk you through everything:

- Your GIU username and password
- Where you want your files saved overall
- For each of your courses: what to name its folder, exactly where that folder should be, and whether files should be sorted into subfolders like "Lectures" and "Assignments" or kept all together
- Whether to schedule it to check for new files automatically, every hour

### 3. You're done

If you chose automatic scheduling, the downloader now runs quietly in the background every hour, checking each course for new files and saving them where you told it to.

## Checking it manually

Run `giu-cms-downloader.exe` anytime to check for new files immediately, without waiting for the next scheduled run. A window will open showing its progress and close when finished.

## Changing anything later

Run `setup-wizard.exe` again, for any of these:

- **Your password expires every 3 months**, just run the wizard, and when it asks for your password, type the new one.
- Adding/renaming a course folder, changing where a course saves to, or switching between flat and sorted-by-type folders.
- A new semester's courses will show up automatically, the wizard will ask you to configure them the next time you run it.

Every question shows your current setting as the default, press Enter to leave it unchanged, or type something new to update just that one thing. Nothing else needs to be touched or reinstalled.

## Troubleshooting

- **Nothing downloads / login errors** — double check your username and password by logging into the CMS website directly in your browser with the same credentials.
- **Files aren't going where expected**, run `setup-wizard.exe` again and check the folder path shown for that course.
- **Want to stop automatic checks**, open **Task Scheduler** (search for it in the Start menu), find **"GIU CMS Downloader"** in the list, right-click, and select **Disable** or **Delete**.

## Disclaimer

This is an unofficial and independent tool. It works by reading the same pages your browser already shows you when logged into the CMS.
