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
from os.path import splitext
from pyrogram.types import Message
from . import unzipper_db, unzipperbot, Config
from unzipper.helpers_nexa.utils import run_cmds_on_cr


thumb_db = unzipper_db["thumbnails_db"]


async def download_thumbnail(mid: int):
    msg = await unzipperbot.get_messages(Config.DB_CHANNEL, mid)
    dmsg = await msg.download()
    return dmsg


def prepare_thumb(ipath):
    tpath = f"{splitext(ipath)[0]}.thumb.jpg"
    with Image.open(ipath) as im:
        rim = im.convert("RGB")
        rim.thumbnail((320, 320))
        rim.save(tpath, "JPEG")
    return tpath


async def save_thumbnail(uid: int, message: Message):
    # Download the image
    ip = await message.download()
    thumb = await run_cmds_on_cr(prepare_thumb, ip)
    frwd_thumb = await unzipperbot.send_photo(Config.DB_CHANNEL, thumb)
    is_exist = await thumb_db.find_one({"_id": uid})
    if is_exist:
        await thumb_db.update_one({"_id": uid}, {"$set": {"path": frwd_thumb.id}})
    else:
        await thumb_db.insert_one({"_id": uid, "path": frwd_thumb.id})


async def get_thumbnail(user_id: int):
    gtm = await thumb_db.find_one({"_id": user_id})
    if gtm:
        return await download_thumbnail(gtm["path"])
    else:
        return None


async def del_thumbnail(user_id: int):
    is_exist = await thumb_db.find_one({"_id": user_id})
    if is_exist:
        await thumb_db.delete_one({"_id": user_id})
    else:
        return
