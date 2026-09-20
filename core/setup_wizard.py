import subprocess
import sys
from pathlib import Path

from core.course_config import (
    load_mapping,
    save_mapping,
    read_env,
    write_env,
    CourseConfig,
)
from paths import get_app_dir


def prompt(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{question}{suffix}: ").strip()
    return answer or default


def prompt_password(question: str, has_existing: bool) -> str:
    suffix = " (leave blank to keep current)" if has_existing else ""
    return input(f"{question}{suffix}: ").strip()


def prompt_yes_no(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix}: ").strip().lower()

    if not answer:
        return default

    return answer.startswith("y")


def configure_credentials() -> dict[str, str]:
    print("=== GIU CMS Login ===\n")

    env = read_env()

    username = prompt(
        "GIU username",
        env.get("GIU_USERNAME", ""),
    )

    existing_password = env.get("GIU_PASSWORD", "")
    entered_password = prompt_password(
        "GIU password",
        bool(existing_password),
    )

    password = entered_password or existing_password

    default_root = env.get("DOWNLOAD_ROOT", "")

    print("\nWhere should your root downloads folder go?")
    print("(Leave blank to use Downloads/GIU)")

    download_root = prompt(
        "Folder",
        default_root,
    )

    new_env = {
        "GIU_USERNAME": username,
        "GIU_PASSWORD": password,
        "DOWNLOAD_ROOT": download_root,
    }

    write_env(new_env)

    print("\nSaved to .env\n")

    return new_env


def configure_course(
    course,
    existing: CourseConfig | None,
    download_root: str,
) -> CourseConfig:
    print(f"\n--- {course.code} - {course.name} ---")

    default_name = (
        existing.display_name
        if existing
        else course.name
    )

    display_name = prompt(
        "Folder name for this course",
        default_name,
    )

    root = (
        download_root
        or str(Path.home() / "Downloads" / "GIU")
    )

    default_folder = (
        existing.folder
        if existing
        else str(Path(root) / display_name)
    )

    folder = prompt(
        "Full folder path",
        default_folder,
    )

    default_flat = (
        existing.template_name == "Flat"
        if existing
        else False
    )

    flat = not prompt_yes_no(
        "Organize into subfolders by type "
        "(Lectures, Assignments, etc.)?",
        default=not default_flat,
    )

    return CourseConfig(
        display_name=display_name,
        folder=folder,
        template_name="Flat" if flat else "Default",
    )


def configure_courses(env: dict[str, str]):
    from core.auth import get_session
    from core.scraper import get_courses
    from core.config import BASE_URL

    print("\n=== Course Setup ===")
    print("Logging in and fetching your courses...")

    session = get_session(
        env["GIU_USERNAME"],
        env["GIU_PASSWORD"],
    )

    courses = get_courses(
        session,
        BASE_URL,
    )

    mapping = load_mapping()

    print(
        f"\nFound {len(courses)} courses. "
        "Configure each one below."
    )

    print(
        "Press Enter on any question to accept "
        "the default shown in [brackets].\n"
    )

    for course in courses:
        existing = mapping.get(course.code)

        mapping[course.code] = configure_course(
            course,
            existing,
            env.get("DOWNLOAD_ROOT", ""),
        )

    save_mapping(mapping)

    print(
        f"\nSaved configuration for "
        f"{len(mapping)} courses."
    )


def install_scheduled_task():
    print("\n=== Automatic Scheduling ===")

    if not prompt_yes_no(
        "Set this up to run automatically every hour?",
        default=True,
    ):
        print(
            "Skipped. You can run this wizard "
            "again anytime to enable it."
        )
        return

    app_dir = get_app_dir()
    downloader_exe = app_dir / "giu-downloader.exe"

    result = subprocess.run(
        [
            "schtasks",
            "/Create",
            "/TN",
            "GIU CMS Downloader",
            "/TR",
            f'"{downloader_exe}"',
            "/SC",
            "HOURLY",
            "/RL",
            "LIMITED",
            "/F",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(
            "Scheduled! This will now run "
            "automatically every hour."
        )
    else:
        print(
            "Could not set up automatic scheduling. "
            "Details:"
        )
        print(result.stderr)


def main():
    print("GIU CMS Downloader — Setup Wizard\n")

    env = configure_credentials()

    configure_courses(env)

    if sys.platform == "win32":
        install_scheduled_task()
    else:
        print(
            "\nAutomatic scheduling isn't set up "
            "by this wizard on non-Windows systems."
        )

    print(
        "\nAll done! Run 'giu-downloader.exe' "
        "anytime to check for new files manually."
    )


if __name__ == "__main__":
    main()