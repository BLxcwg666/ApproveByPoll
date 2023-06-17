import asyncio
import os
from loguru import logger
from aiogram import Bot, Dispatcher, executor, types

logger.level("INFO")
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
	await message.reply("~\(≧▽≦)/~")


@dp.chat_join_request_handler()
async def join(request: types.ChatJoinRequest):
	user_id = request.from_user.id
	username = request.from_user.username
	chat_id = request.chat.id
	logger.info(f"{username}({user_id}) is requesting to join {chat_id}.")
	message = await bot.send_message(chat_id, f"@{username}({user_id}) is requesting to join this group.")
	await bot.pin_chat_message(chat_id, message.message_id)
	polling = await bot.send_poll(
		chat_id,
		"Approve this user?",
		["Yes", "No"],
		is_anonymous=True,
		allows_multiple_answers=False,
		reply_to_message_id=message.message_id,
	)
	await asyncio.sleep(300)
	await bot.unpin_chat_message(chat_id, message.message_id)
	polling = await bot.stop_poll(chat_id, polling.message_id)

	if polling.total_voter_count == 0:
		await message.reply("没有人投票哦~")
		await bot.send_message(user_id, "暂时没有人投票哦，请等一会再来申请吧~")
		logger.info(f"没人给 {username}({user_id}) 在 {chat_id} 投票")
		await request.decline()
	elif polling.options[0].voter_count > polling.options[1].voter_count:
		await message.reply("通过~")
		await bot.send_message(user_id, "已经通过申请了喵~")
		logger.info(f"{username}({user_id}) 已经在群组 {chat_id} 被批准加入")
		await request.approve()
	elif polling.options[0].voter_count == polling.options[1].voter_count:
		await message.reply("没有结果~")
		await bot.send_message(user_id, "投票没有分出胜负哦，请等一会再来申请吧~")
		logger.info(f"对于 {username}({user_id}) 在 {chat_id} 的投票没有结果")
		await request.decline()
	else:
		await message.reply("拒绝！")
		await bot.send_message(user_id, "你被拒绝加入啦！")
		logger.info(f"{username}({user_id}) 已经在群组 {chat_id} 被拒绝加入")
		await request.decline()


if __name__ == '__main__':
	executor.start_polling(dp)
