# GIU CMS Downloader

Automatically downloads new course files from the GIU CMS and keeps them organized the way you want.

## Setup

### 1. Download

Go to the [Releases page](https://github.com/MohabHindawy/giu-cms-downloader/releases), download the latest `.zip`, and extract it somewhere permanent.

For example:

```text
C:\GIU-Downloader\
```

Don't run the app directly from inside the `.zip` or from a temporary folder.

> **Windows may show a SmartScreen warning because the executable is currently unsigned.** If you downloaded it from the official GitHub Releases page, click **More info → Run anyway**.

### 2. Run the app

Open:

```text
giu-cms-downloader.exe
```

On the first launch, you'll be asked for:

- Your GIU username and password
- Where you want your downloaded files stored
- Whether files already on the CMS should be marked as downloaded, so they aren't downloaded again

After that, the main app will open and you can configure everything else from there.

## Using the app

The sidebar gives you access to the main settings:

- **Courses** lets you choose where each course is saved and how its folders are organized.
- **Structure** lets you customize folder structures for things like lectures, assignments, labs, and other files.
- **Blocking** lets you skip files based on rules such as file type or words in the file name.
- **Schedule** lets you enable or disable automatic background checks.
- **Update Login** lets you change your GIU username or password when needed.

You can also use **Run Now** anytime to immediately check the CMS for new files.

The downloader keeps track of what it has already downloaded, so files aren't downloaded again unless needed. New courses will also appear automatically and can be configured from inside the app.

## Troubleshooting

- **Nothing downloads or you get login errors:** make sure the same username and password work on the GIU CMS website. If your password changed, use **Update Login**.
- **Files are going to the wrong place:** open **Courses** and check that course's folder and structure.
- **A file is being skipped:** check your rules under **Blocking**.
- **Want to stop automatic checks:** disable them from the **Schedule** page.

## Disclaimer

This is an unofficial and independent tool. It works by reading the same CMS pages available to you when you're logged in through your browser.
