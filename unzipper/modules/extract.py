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

from re import match
from time import time
from os import path, remove

from config import Config
from pyrogram import filters
from unzipper import unzip_client
from pyrogram.types import Message
from unzipper.lib.extractor import Extractor
from unzipper.helpers_nexa.buttons import Buttons
from unzipper.lib.downloader import Downloader, dl_regex
from unzipper.helpers_nexa.utils import (TimeFormatter, get_files,
                                         progress_for_pyrogram)
from unzipper.database.split_arc import del_split_arc_user, get_split_arc_user


@unzip_client.on_message(filters.incoming & filters.private & filters.regex(dl_regex) | filters.document)
@unzip_client.handler_func
async def extract_dis_archive(_, message: Message):
    unzip_msg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    user_id = message.from_user.id
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    is_url = message.text and (match(dl_regex, message.text))
    is_doc = message.document

    # Splitted files
    is_spl, lfn, ps = await get_split_arc_user(user_id)
    if is_spl:
        fn = path.basename(message.text)
        await unzip_msg.edit(await unzip_client.get_string("alert_downloading_part"))
        # File extension
        taext = path.splitext(is_doc.file_name if is_doc else fn)[1]
        if not taext.replace(".", "").isnumeric():
            return await unzip_msg.edit(await unzip_client.get_string("no_splitted_arc"))
        arc_name = f"{download_path}/archive_from_{user_id}_{is_doc.file_name if is_doc else fn}"
        if path.isfile(arc_name):
            return await unzip_msg.edit(await unzip_client.get_string("alert_part_exists"))
        # Download the file
        s_time = time()
        if is_url:
            await Downloader().from_direct_link(message.text, arc_name, unzip_msg)
        else:
            await message.download(
                file_name=arc_name,
                progress=progress_for_pyrogram, progress_args=(
                    "**Trying to Download!** \n", unzip_msg, s_time)
            )
        e_time = time()
        await unzip_msg.edit((await unzip_client.get_string("ok_download")).format(fn, TimeFormatter(round(e_time-s_time) * 1000)))
        return

    if path.isdir(download_path):
        return await unzip_msg.edit(await unzip_client.get_string("alert_process_running_already"))
    if is_url:
        await unzip_msg.edit(await unzip_client.get_string("ask_what_you_want"), reply_markup=Buttons.EXTRACT_URL)
    elif is_doc:
        await unzip_msg.edit(await unzip_client.get_string("ask_what_you_want"), reply_markup=Buttons.EXTRACT_FILE)
    else:
        await unzip_msg.edit(await unzip_client.get_string("no_archive"))


@unzip_client.on_message(filters.private & filters.command("done"))
@unzip_client.handler_func
async def extracted_dis_spl_archive(_, message: Message):
    spl_umsg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    user_id = message.from_user.id
    # Retrive data from database
    is_spl, lfn, ps = await get_split_arc_user(user_id)
    ext_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}/extracted"
    arc_path = path.dirname(lfn)
    # Path checks
    if not is_spl:
        return await spl_umsg.edit("`Bruh, why are you sending this command 🤔?`")
    if not path.isdir(arc_path):
        await spl_umsg.edit(await unzip_client.get_string("alert_empty_files"))
        return await del_split_arc_user(user_id)
    # Remove user record from the database
    await del_split_arc_user(user_id)
    # Extract the archive
    ext = Extractor()
    s_time = time()
    await ext.extract(lfn, ext_path, ps, True)
    extdarc = f"{ext_path}/{path.splitext(path.basename(lfn))[0]}"
    await ext.extract(extdarc, ext_path, ps)
    e_time = time()
    await spl_umsg.edit((await unzip_client.get_string("ok_extract")).format(TimeFormatter(round(e_time-s_time) * 1000)))
    # Try to remove merged archive
    try:
        remove(extdarc)
    except:
        pass
    paths = await get_files(ext_path)
    i_e_btns = await Buttons.make_keyboard(paths, user_id, message.chat.id)
    await spl_umsg.edit(await unzip_client.get_string("select_files"), reply_markup=i_e_btns)