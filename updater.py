import os
import requests
import logging
import psutil
import time
from tkinter import Tk, messagebox
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

URL = "https://devbuilds.s.kaspersky-labs.com/kvrt/latest/full/kvrt.exe"
OUTPUT_FILE = "KVRT.exe"
TEMP_FILE = "temp_kvrt.exe"


def is_file_in_use(filepath):
    """Checks if the file is in use by another process."""
    for proc in psutil.process_iter(["pid", "name", "open_files"]):
        try:
            if any(filepath in file.path for file in proc.info["open_files"] or []):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def download_file(url, temp_file):
    """Downloads the file from the given URL and saves it to a temporary file."""
    logging.info(f"{Fore.LIGHTMAGENTA_EX}Starting downloading...{Style.RESET_ALL}")
    logging.info(f"{Fore.LIGHTCYAN_EX}URL:{Style.RESET_ALL} "
                 f"{Fore.LIGHTBLUE_EX}{url}{Style.RESET_ALL}")
    logging.info(f"{Fore.LIGHTCYAN_EX}TEMP FILE:{Style.RESET_ALL} "
                 f"{Fore.LIGHTBLUE_EX}{temp_file}{Style.RESET_ALL}")
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            with open(temp_file, "wb") as f, tqdm(
                desc="Downloading",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                colour="blue",
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
        logging.info(f"File downloaded to {temp_file}")
        print(f"{Fore.LIGHTGREEN_EX}File downloaded to {temp_file}{Style.RESET_ALL}")
    except requests.RequestException as e:
        logging.error(f"Error downloading file: {e}")
        print(f"{Fore.RED}Error downloading file: {e}{Style.RESET_ALL}")
        return False
    return True


def main():
    in_use_interval = 5
    print(
        f"{Fore.LIGHTCYAN_EX}KVRT Updater: "
        f"{Fore.LIGHTBLUE_EX}Updating...{Style.RESET_ALL}"
    )
    logging.info("Started KVRT update")

    root = Tk()
    root.withdraw()

    while True:
        try:
            if is_file_in_use(OUTPUT_FILE):
                logging.warning(f"File {OUTPUT_FILE} is in use by another process.")
                messagebox.showwarning(
                    "File in Use",
                    f"File {OUTPUT_FILE} is in use by another process. Please try again.",
                )
                print(
                    f"{Fore.RED}File {OUTPUT_FILE} is in use by another process. "
                    f"Please try again.{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.LIGHTYELLOW_EX}Waiting {in_use_interval} seconds...{Style.RESET_ALL}"
                )
                time.sleep(5)
                continue

            if not download_file(URL, TEMP_FILE):
                break

            try:
                os.replace(TEMP_FILE, OUTPUT_FILE)
                logging.info(f"File {OUTPUT_FILE} successfully updated")
                print(
                    f"{Fore.LIGHTGREEN_EX}File successfully updated as {OUTPUT_FILE}{Style.RESET_ALL}"
                )
            except OSError as e:
                logging.error(f"Error replacing files: {e}")
                print(f"{Fore.RED}Error replacing files: {e}{Style.RESET_ALL}")
                break

            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
            break

    print(f"\n{Fore.LIGHTCYAN_EX}-----------------------------{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX} Press ANYTHING to continue.{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}-----------------------------{Style.RESET_ALL}")
    logging.info("Finished KVRT update")
    print(
        f"{Fore.LIGHTCYAN_EX}KVRT Updater: "
        f"{Fore.LIGHTGREEN_EX}Completed!{Style.RESET_ALL}"
    )
    input()


if __name__ == "__main__":
    main()
