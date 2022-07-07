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

from os import remove
from pyrogram import filters
from unzipper import unzip_client
from pyrogram.types import Message
from unzipper.helpers_nexa.buttons import Buttons
from unzipper.database.thumbnail import save_thumbnail, get_thumbnail, del_thumbnail


@unzip_client.on_message(filters.private & filters.command("start"))
@unzip_client.handler_func
async def start_bot(_, message: Message):
    await message.reply_text((await unzip_client.get_string("start")).format(message.from_user.mention), reply_markup=Buttons.START, disable_web_page_preview=True)


@unzip_client.on_message(filters.private & filters.command(["save", "set_thumb"]))
@unzip_client.handler_func
async def save_dis_thumb(_, message: Message):
    prs_msg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    rply = message.reply_to_message
    if not rply or not rply.photo:
        return await prs_msg.edit(await unzip_client.get_string("no_replied_msg"))
    await save_thumbnail(message.from_user.id, rply)
    await prs_msg.edit(await unzip_client.get_string("ok_saving_thumb"))


@unzip_client.on_message(filters.private & filters.command(["thget", "get_thumb"]))
@unzip_client.handler_func
async def give_my_thumb(_, message: Message):
    prs_msg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    gthumb = await get_thumbnail(message.from_user.id)
    if not gthumb:
        return await prs_msg.edit(await unzip_client.get_string("no_thumb"))
    await prs_msg.delete()
    await message.reply_photo(gthumb)
    remove(gthumb)


@unzip_client.on_message(filters.private & filters.command(["thdel", "del_thumb"]))
@unzip_client.handler_func
async def delete_my_thumb(_, message: Message):
    prs_msg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    texist = await get_thumbnail(message.from_user.id)
    if not texist:
        return await prs_msg.edit(await unzip_client.get_string("no_thumb"))
    await del_thumbnail(message.from_user.id)
    remove(texist)
    await prs_msg.edit(await unzip_client.get_string("ok_deleting_thumb"))


@unzip_client.on_message(filters.private & filters.command("backup"))
@unzip_client.handler_func
async def do_backup_files(_, message: Message):
    prs_msg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    await prs_msg.edit(await unzip_client.get_string("select_provider"), reply_markup=Buttons.BACKUP)


@unzip_client.on_message(filters.private & filters.command("clean"))
@unzip_client.handler_func
async def clean_ma_files(_, message: Message):
    prs_msg = await message.reply(await unzip_client.get_string("processing"), reply_to_message_id=message.id)
    await prs_msg.edit(await unzip_client.get_string("ask_clean"), reply_markup=Buttons.CLN_BTNS)