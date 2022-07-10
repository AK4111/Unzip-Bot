# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                  #
# See the GNU General Public License for more details.                  #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>   #
# ===================================================================== #

from PIL import Image
from . import unzipper_db
from requests import post
from os import path, remove
from pyrogram.types import Message
from unzipper.lib.downloader import Downloader
from unzipper.helpers_nexa.utils import run_cmds_on_cr, run_shell_cmds


thumb_db = unzipper_db["thumbnails_db"]


def upload_thumbnail(img: str):
    with open(img, "rb") as file:
        rs = post(
            "https://telegra.ph/upload",
            files={"file": file}
        ).json()[0]
        return f"https://telegra.ph{rs['src']}"


def prepare_thumb(ipath):
    tpath = f"{path.splitext(ipath)[0]}.thumb.jpg"
    with Image.open(ipath) as im:
        rim = im.convert("RGB")
        rim.thumbnail((320, 320))
        rim.save(tpath, "JPEG")
    return tpath


async def save_thumbnail(uid: int, message: Message):
    # Download the image
    ip = await message.download()
    thumb = await run_cmds_on_cr(prepare_thumb, ip)
    up_thumb = await run_cmds_on_cr(upload_thumbnail, thumb)
    is_exist = await thumb_db.find_one({"_id": uid})
    if is_exist:
        await thumb_db.update_one({"_id": uid}, {"$set": {"url": up_thumb}})
    else:
        await thumb_db.insert_one({"_id": uid, "url": up_thumb})


async def get_thumbnail(user_id: int, download: bool = False):
    gtm = await thumb_db.find_one({"_id": user_id})
    if gtm:
        if download:
            dimg = f"Dump/thumbnail_{path.basename(gtm['url'])}"
            await Downloader().from_direct_link(gtm["url"], dimg, "image/")
            return dimg
        return gtm["url"]
    else:
        return None


async def del_thumbnail(user_id: int):
    is_exist = await thumb_db.find_one({"_id": user_id})
    if is_exist:
        await thumb_db.delete_one({"_id": user_id})
    else:
        return


async def get_or_gen_thumb(uid: int, doc_f: str, isvid: bool = False):
    """
    Get saved thumbnail from the database. If there isn't any thumbnail saved, None will be returned.
    For video files, a thumbnail will be generated using ffmpeg

    Parameters:

        - `uid` - User id
        - `doc_f` - File path
        - `isvid` - Pass True if file is a video
    """
    dbthumb = await get_thumbnail(int(uid), True)
    if dbthumb:
        return dbthumb
    elif isvid:
        thmb_pth = f"Dump/thumbnail_{path.basename(doc_f)}.jpg"
        if path.exists(thmb_pth):
            remove(thmb_pth)
        await run_shell_cmds(f"ffmpeg -ss 00:00:01.00 -i {doc_f} -vf 'scale=320:320:force_original_aspect_ratio=decrease' -vframes 1 {thmb_pth}")
        return thmb_pth
    else:
        return None
